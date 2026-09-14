# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.ai.utils.html_extractor import HTMLExtractor

_logger = logging.getLogger(__name__)


class AIFieldRagConfig(models.Model):
    _name = 'ai.field.rag.config'
    _description = 'AI Field RAG Configuration'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    agent_id = fields.Many2one(
        'ai.agent',
        string="Agent",
        required=True,
        ondelete='cascade',
        index=True,
    )

    # Model selection
    model_id = fields.Many2one(
        'ir.model',
        string="Model",
        required=True,
        domain=[('transient', '=', False)],
        ondelete='cascade',
    )
    model_name = fields.Char(
        related='model_id.model',
        store=True,
        string="Model Name",
    )

    # Field selection - text content fields only
    field_id = fields.Many2one(
        'ir.model.fields',
        string="Content Field",
        required=True,
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['text', 'char', 'html'])]",
        ondelete='cascade',
    )
    field_name = fields.Char(related='field_id.name', store=True)
    field_type = fields.Selection(related='field_id.ttype', store=True)

    # Context fields - additional fields to include for context
    # Note: 'name', 'id', and 'display_name' are excluded as they are automatically
    # included in the record header for optimal semantic search
    context_field_ids = fields.Many2many(
        'ir.model.fields',
        relation='ai_field_rag_config_context_fields_rel',
        column1='config_id',
        column2='field_id',
        string="Context Fields",
        domain="[('model_id', '=', model_id), "
               "('name', 'not in', ['name', 'id', 'display_name']), "
               "('ttype', 'in', ['char', 'text', 'selection', 'many2one', 'date', 'datetime', 'integer', 'float', 'boolean'])]",
        help="Additional fields to include in the indexed content for semantic search context. "
             "Record identifier (model, ID, name) is automatically included.",
    )

    # Domain filter
    filter_domain = fields.Char(
        string="Filter Domain",
        default="[]",
        help="Domain to filter which records to include as sources",
    )

    # Linked sources (one per matching record)
    source_ids = fields.One2many(
        'ai.agent.source',
        'field_rag_config_id',
        string="Sources",
    )

    # Sync tracking
    last_sync_date = fields.Datetime(string="Last Sync", readonly=True)
    synced_record_ids = fields.Text(
        string="Synced Record IDs",
        default="[]",
        help="JSON list of record IDs that have been synced",
    )
    auto_sync = fields.Boolean(
        string="Auto Sync",
        default=True,
        help="When enabled, an hourly scheduled action detects new, changed, or removed records and updates sources automatically",
    )

    # Computed fields
    record_count = fields.Integer(
        compute='_compute_record_count',
        string="Matching Records",
    )
    source_count = fields.Integer(
        compute='_compute_source_count',
        string="Created Sources",
    )
    indexed_count = fields.Integer(
        compute='_compute_indexed_count',
        string="Indexed Sources",
    )

    @api.depends('model_name', 'filter_domain')
    def _compute_record_count(self):
        for config in self:
            if config.model_name and config.model_name in self.env:
                try:
                    domain = safe_eval(config.filter_domain or '[]')
                    config.record_count = self.env[config.model_name].search_count(domain)
                except Exception:
                    config.record_count = 0
            else:
                config.record_count = 0

    @api.depends('source_ids')
    def _compute_source_count(self):
        for config in self:
            config.source_count = len(config.source_ids)

    @api.depends('source_ids.status')
    def _compute_indexed_count(self):
        for config in self:
            config.indexed_count = len(config.source_ids.filtered(lambda s: s.status == 'indexed'))

    def _get_filtered_records(self):
        """Get records matching the domain filter."""
        self.ensure_one()
        if not self.model_name or self.model_name not in self.env:
            return self.env['base'].browse()
        try:
            domain = safe_eval(self.filter_domain or '[]')
            return self.env[self.model_name].search(domain)
        except Exception as e:
            _logger.warning("Failed to get filtered records for config %s: %s", self.name, e)
            return self.env[self.model_name].browse()

    def _extract_record_content(self, record):
        """
        Extract text content from a single record for vector embedding and semantic search.

        The content is structured with a header containing record identifiers (model, ID, name)
        followed by context fields and the main content field. This structure ensures:
        - Record can be found by ID, name, or model type queries
        - Context fields enrich semantic matching (e.g., "tasks assigned to John")
        - Main content provides the primary searchable text

        :param record: record to extract content from
        :return: content string or None if no content
        """
        self.ensure_one()

        content_parts = []

        # Add record identifier header for semantic searchability
        # This allows queries like "task 123" or "project tasks" to match
        content_parts.append(f"Record Type: {self.model_id.name}")
        content_parts.append(f"Record ID: {record.id}")
        content_parts.append(f"Name: {record.display_name}")

        # Add context fields
        for field in self.context_field_ids:
            try:
                value = record[field.name]
                if value:
                    if field.ttype == 'many2one':
                        value = value.display_name
                    elif field.ttype in ('date', 'datetime'):
                        value = str(value)
                    elif field.ttype == 'selection':
                        # Get selection label - handle callable selections
                        selection_field = self.env[self.model_name]._fields[field.name]
                        selection = selection_field.selection
                        if callable(selection):
                            selection = selection(self.env[self.model_name])
                        value = dict(selection).get(value, value)
                    content_parts.append(f"{field.field_description}: {value}")
            except Exception as e:
                _logger.debug("Failed to extract context field %s: %s", field.name, e)

        # Extract main content field
        main_content = None

        if self.field_type == 'html':
            # HTML field - extract text using HTMLExtractor
            html_content = record[self.field_name]
            if html_content:
                extractor = HTMLExtractor(self.env)
                result = extractor.extract_from_html(html_content)
                main_content = result.get('content', '')

        elif self.field_type in ('text', 'char'):
            # Text/char field - direct content
            main_content = record[self.field_name] or ''

        if main_content:
            content_parts.append(main_content)
        else:
            # No main content - don't index records without primary content
            return None

        return '\n\n'.join(content_parts)

    def _get_synced_record_ids(self):
        """Get list of record IDs that have been synced."""
        self.ensure_one()
        try:
            return set(json.loads(self.synced_record_ids or '[]'))
        except (json.JSONDecodeError, TypeError):
            return set()

    def _set_synced_record_ids(self, record_ids):
        """Set list of synced record IDs."""
        self.ensure_one()
        self.synced_record_ids = json.dumps(list(record_ids))

    def _compute_sync_diff(self, current_records):
        """
        Compare current records with synced sources to determine changes.

        :param current_records: recordset of records matching current domain
        :return: dict with 'to_create', 'to_delete', 'to_check' record IDs
        """
        self.ensure_one()

        current_ids = set(current_records.ids)
        synced_ids = self._get_synced_record_ids()

        # Also get IDs from existing sources
        source_record_ids = set(self.source_ids.mapped('source_record_id'))

        to_create = current_ids - source_record_ids
        to_delete = source_record_ids - current_ids
        to_check = current_ids & source_record_ids  # Check for content changes

        return {
            'to_create': to_create,
            'to_delete': to_delete,
            'to_check': to_check,
        }

    def action_sync(self):
        """
        Synchronize sources with current domain results.

        Creates sources for new records, deletes sources for removed records,
        and marks changed content sources for reprocessing.
        """
        self.ensure_one()

        if not self.model_name or self.model_name not in self.env:
            raise UserError(_("Invalid model configuration."))

        records = self._get_filtered_records()
        diff = self._compute_sync_diff(records)

        sources_created = 0
        sources_deleted = 0
        sources_updated = 0

        # Delete sources for records no longer in domain
        if diff['to_delete']:
            sources_to_delete = self.source_ids.filtered(
                lambda s: s.source_record_id in diff['to_delete']
            )
            sources_deleted = len(sources_to_delete)
            sources_to_delete.unlink()

        # Create sources for new records
        if diff['to_create']:
            records_to_create = records.filtered(lambda r: r.id in diff['to_create'])
            for record in records_to_create:
                try:
                    self._create_source_for_record(record)
                    sources_created += 1
                except Exception as e:
                    _logger.warning("Failed to create source for record %s: %s", record.id, e)

        # Check existing sources for content changes or failed sources that now have content
        if diff['to_check']:
            records_to_check = records.filtered(lambda r: r.id in diff['to_check'])
            sources_by_record_id = {s.source_record_id: s for s in self.source_ids}

            for record in records_to_check:
                source = sources_by_record_id.get(record.id)
                if not source:
                    continue

                # Performance optimization: skip records that haven't changed since last sync
                # by comparing write_date before extracting content
                record_write_date = record.write_date if hasattr(record, 'write_date') else None
                if (source.attachment_id and source.status == 'indexed'
                        and source.source_record_write_date
                        and record_write_date
                        and record_write_date <= source.source_record_write_date):
                    # Record hasn't changed since last sync - skip expensive content extraction
                    continue

                content = self._extract_record_content(record)

                if source.attachment_id:
                    # Has attachment - check for content changes
                    if content:
                        new_checksum = self.env['ir.attachment']._compute_checksum(content.encode())
                        if new_checksum != source.attachment_id.checksum:
                            # Content changed - mark for reprocessing
                            source.write({
                                'status': 'processing',
                                'is_active': False,
                                'source_record_write_date': record_write_date,
                            })
                            sources_updated += 1
                        elif record_write_date and source.source_record_write_date != record_write_date:
                            # Content same but write_date changed (other fields changed) - update tracking
                            source.write({'source_record_write_date': record_write_date})
                elif content and source.status == 'failed':
                    # No attachment (previously failed) but now has content - retry
                    source.write({
                        'status': 'processing',
                        'is_active': False,
                        'error_details': False,
                        'source_record_write_date': record_write_date,
                    })
                    sources_updated += 1

        # Update sync tracking
        self.write({
            'last_sync_date': fields.Datetime.now(),
        })
        self._set_synced_record_ids(set(records.ids))

        # Trigger processing cron
        if sources_created or sources_updated:
            self.env.ref('ai.ir_cron_process_sources')._trigger()

        _logger.info(
            "Sync completed for config '%s': %d created, %d deleted, %d updated",
            self.name, sources_created, sources_deleted, sources_updated
        )

        return {
            'created': sources_created,
            'deleted': sources_deleted,
            'updated': sources_updated,
        }

    def _create_source_for_record(self, record):
        """Create an ai.agent.source for a single record."""
        self.ensure_one()

        source_name = f"{record.display_name} [{self.model_name}:{record.id}]"
        record_write_date = record.write_date if hasattr(record, 'write_date') else None

        source = self.env['ai.agent.source'].create({
            'name': source_name,
            'agent_id': self.agent_id.id,
            'field_rag_config_id': self.id,
            'source_record_id': record.id,
            'source_record_ref': f"{self.model_name},{record.id}",
            'source_record_write_date': record_write_date,
            'type': 'field_rag',
        })

        return source

    def action_view_sources(self):
        """Open the sources linked to this configuration."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sources: %s", self.name),
            'res_model': 'ai.agent.source',
            'view_mode': 'list,form',
            'domain': [('field_rag_config_id', '=', self.id)],
            'context': {'default_field_rag_config_id': self.id},
        }

    def action_view_records(self):
        """Open the records matching the domain filter."""
        self.ensure_one()
        if not self.model_name or self.model_name not in self.env:
            raise UserError(_("Invalid model configuration."))

        domain = safe_eval(self.filter_domain or '[]')
        return {
            'type': 'ir.actions.act_window',
            'name': _("Source Records: %s", self.name),
            'res_model': self.model_name,
            'view_mode': 'list,form',
            'domain': domain,
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Trigger initial sync after creation."""
        configs = super().create(vals_list)
        for config in configs:
            config.action_sync()
        return configs

    def write(self, vals):
        """Re-sync if domain or field changes."""
        result = super().write(vals)
        if 'filter_domain' in vals or 'field_id' in vals or 'model_id' in vals:
            for config in self:
                config.action_sync()
        return result

    @api.model
    def _cron_auto_sync(self):
        """
        Scheduled action to auto-sync configurations.

        Finds all configurations with auto_sync enabled and syncs them
        to detect new, removed, or changed records.
        """
        configs = self.search([('auto_sync', '=', True)])
        _logger.info("Auto-syncing %d field RAG configurations", len(configs))

        for config in configs:
            try:
                result = config.action_sync()
                if result['created'] or result['deleted'] or result['updated']:
                    _logger.info(
                        "Auto-sync '%s': %d created, %d deleted, %d updated",
                        config.name, result['created'], result['deleted'], result['updated']
                    )
            except Exception as e:
                _logger.warning("Auto-sync failed for config '%s': %s", config.name, e)
