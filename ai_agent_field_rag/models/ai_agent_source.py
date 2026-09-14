# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class AIAgentSource(models.Model):
    _name = 'ai.agent.source'
    _inherit = ['ai.agent.source']

    # Link to field RAG configuration
    field_rag_config_id = fields.Many2one(
        'ai.field.rag.config',
        string="Field RAG Configuration",
        ondelete='cascade',
        index=True,
    )

    # Source record reference
    source_record_id = fields.Integer(
        string="Source Record ID",
        index=True,
        help="ID of the record this source was created from",
    )
    source_record_ref = fields.Char(
        string="Source Record Reference",
        help="Reference in format 'model,id' for the source record",
    )
    source_record_write_date = fields.Datetime(
        string="Source Record Write Date",
        help="write_date of the source record when last synced, used to skip unchanged records",
    )

    # Extend type selection
    type = fields.Selection(
        selection_add=[('field_rag', 'Model Field')],
        ondelete={'field_rag': lambda recs: recs.write({'type': 'binary'})}
    )

    # Related fields for display
    source_model_name = fields.Char(
        related='field_rag_config_id.model_id.name',
        string="Source Model",
    )
    source_field_name = fields.Char(
        related='field_rag_config_id.field_id.field_description',
        string="Source Field",
    )
    config_name = fields.Char(
        related='field_rag_config_id.name',
        string="Configuration",
    )

    @api.depends_context('uid')
    @api.depends('field_rag_config_id')
    def _compute_user_has_access(self):
        """Override to check if user has read access to the source model."""
        field_rag_sources = self.filtered(lambda s: s.type == 'field_rag')

        for source in field_rag_sources:
            if source.field_rag_config_id and source.field_rag_config_id.model_name:
                try:
                    model_name = source.field_rag_config_id.model_name
                    self.env[model_name].check_access('read')
                    source.user_has_access = True
                except AccessError:
                    source.user_has_access = False
            else:
                source.user_has_access = False

        super(AIAgentSource, self - field_rag_sources)._compute_user_has_access()

    def _update_name(self):
        """Override to update name from source record."""
        if not self:
            return

        source = self[0]
        if source.type != 'field_rag':
            return super()._update_name()

        if source.source_record_ref and source.field_rag_config_id:
            try:
                model_name, record_id = source.source_record_ref.split(',')
                record = self.env[model_name].browse(int(record_id))
                if record.exists():
                    new_name = f"{record.display_name} [{model_name}:{record_id}]"
                    if source.name != new_name:
                        source.name = new_name
            except Exception as e:
                _logger.debug("Failed to update source name: %s", e)

    def action_access_source(self):
        """Override to open the source record."""
        self.ensure_one()
        if self.type != 'field_rag' or not self.source_record_ref:
            return super().action_access_source()

        try:
            model_name, record_id = self.source_record_ref.split(',')
            return {
                'type': 'ir.actions.act_window',
                'res_model': model_name,
                'res_id': int(record_id),
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception:
            return super().action_access_source()

    def _cron_process_sources(self):
        """
        Override to handle field_rag sources separately.

        The base implementation groups sources by URL and fetches content once per URL.
        This doesn't work for field_rag sources since each source references a different
        record and needs its own unique content. We process field_rag sources individually.
        """
        # First, process field_rag sources individually (not grouped by URL)
        field_rag_sources = self.env['ai.agent.source'].search([
            ('type', '=', 'field_rag'),
            ('status', '=', 'processing'),
        ])

        trigger_embeddings_cron = False
        if field_rag_sources:
            trigger_embeddings_cron = self._process_field_rag_sources(field_rag_sources)

        # Then call super to process URL-based sources normally
        super()._cron_process_sources()

        if trigger_embeddings_cron:
            self.env.ref('ai.ir_cron_generate_embedding')._trigger()

    def _process_field_rag_sources(self, sources):
        """
        Process field_rag sources individually, creating unique attachments for each.

        :param sources: recordset of field_rag sources to process
        :return: True if embeddings need to be generated, False otherwise
        """
        trigger_embeddings_cron = False
        indexed_sources = self.env['ai.agent.source']
        sources_to_update_status = self.env['ai.agent.source']
        failed_by_error = defaultdict(lambda: self.env['ai.agent.source'])

        for source in sources:
            # Fetch content for this individual source
            result = self._fetch_content(source)
            if not result or not result.get('content'):
                error_msg = result.get('error', _("Failed to fetch the content of the source."))
                failed_by_error[error_msg] |= source
                continue

            updated_content = result['content'].encode()
            updated_content_checksum = self.env['ir.attachment']._compute_checksum(updated_content)

            # Create attachment if source doesn't have one
            if not source.attachment_id:
                attachment = self.env['ir.attachment'].create({
                    'name': f"{source.name}",
                    'res_model': 'ai.agent.source',
                    'res_id': source.id,
                    'raw': updated_content,
                    'mimetype': 'text/plain',
                })
                source.attachment_id = attachment.id
            elif source.attachment_id.checksum != updated_content_checksum:
                # Update existing attachment if content changed
                # First delete old embeddings
                self.env['ai.embedding'].search([
                    ('attachment_id', '=', source.attachment_id.id)
                ]).unlink()
                source.attachment_id.write({'raw': updated_content})

            # Check indexing state for this source
            src_indexed, src_to_update, src_trigger = self._get_sources_indexing_state(
                source, updated_content_checksum
            )
            indexed_sources |= src_indexed
            sources_to_update_status |= src_to_update
            trigger_embeddings_cron |= src_trigger

        # Update statuses
        self._update_sources_status(indexed_sources, sources_to_update_status, failed_by_error)

        return trigger_embeddings_cron

    def _fetch_content(self, source):
        """Override to fetch content from model field configuration."""
        if source.type != 'field_rag':
            return super()._fetch_content(source)

        config = source.field_rag_config_id
        if not config:
            return {"content": None, "error": _("Field RAG configuration not found.")}

        if not source.source_record_ref:
            return {"content": None, "error": _("Source record reference not found.")}

        try:
            model_name, record_id = source.source_record_ref.split(',')
            record = self.env[model_name].browse(int(record_id))

            if not record.exists():
                return {"content": None, "error": _("Source record no longer exists.")}

            content = config._extract_record_content(record)

            if not content or not content.strip():
                return {"content": None, "error": _("No content found in the record.")}

            return {"content": content, "error": None}

        except Exception as e:
            _logger.warning("Failed to fetch content for field_rag source %s: %s", source.id, e)
            return {"content": None, "error": str(e)}

    @api.model
    def create_from_field_rag_config(self, config_id, agent_id):
        """
        Create AI agent sources from a field RAG configuration.
        This is typically called from the frontend dialog.

        :param config_id: ID of ai.field.rag.config
        :param agent_id: ID of ai.agent
        :return: created config record
        """
        config = self.env['ai.field.rag.config'].browse(config_id)
        if not config.exists():
            return self.env['ai.field.rag.config'].browse()

        # Ensure config is linked to the agent
        if config.agent_id.id != agent_id:
            config.write({'agent_id': agent_id})

        # Sync will create the sources
        config.action_sync()

        return config

    def action_sync_field_rag_source(self):
        """Manually trigger sync for a field_rag source's configuration."""
        self.ensure_one()
        if self.type != 'field_rag' or not self.field_rag_config_id:
            return

        self.field_rag_config_id.action_sync()

        return {
            'type': 'ir.actions.client',
            'tag': 'soft_reload',
        }

    def action_retry_failed_source(self):
        """
        Override to handle field_rag sources.

        The base implementation doesn't handle field_rag sources because they
        have neither url nor attachment_id initially (when failed due to no content).
        """
        self.ensure_one()
        if self.type != 'field_rag':
            return super().action_retry_failed_source()

        if self.status != 'failed':
            return

        # Delete existing embeddings if attachment exists
        if self.attachment_id:
            source_chunks = self.env['ai.embedding'].search([
                ('checksum', '=', self.attachment_id.checksum),
                ('embedding_model', '=', self.agent_id._get_embedding_model())
            ])
            if source_chunks:
                source_chunks.unlink()

        # Mark for reprocessing and trigger cron
        self.write({
            'status': 'processing',
            'is_active': False,
            'error_details': False,
        })
        self.env.ref('ai.ir_cron_process_sources')._trigger()
