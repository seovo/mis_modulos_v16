/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { Domain } from "@web/core/domain";
import { useService, useOwnedDialogs } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { RecordAutocomplete } from "@web/core/record_selectors/record_autocomplete";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";


export class FieldRagConfigDialog extends Component {
    static template = "ai_agent_field_rag.FieldRagConfigDialog";
    static components = { Dialog, RecordAutocomplete, MultiRecordSelector };
    static props = {
        agentId: Number,
        close: { type: Function },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.actionService = useService("action");
        this.addDialog = useOwnedDialogs();

        this.state = useState({
            name: "",
            modelId: null,
            modelName: "",
            modelDisplayName: "",
            fieldId: null,
            fieldName: "",
            fieldDisplayName: "",
            filterDomain: "[]",
            contextFieldIds: [],
            loading: false,
            recordCount: 0,
            countLoading: false,
        });
    }

    // Model selection callback (RecordAutocomplete returns array of IDs)
    async onModelSelected(ids) {
        if (ids && ids.length) {
            const modelId = ids[0];
            // Get model details
            const models = await this.orm.searchRead(
                "ir.model",
                [["id", "=", modelId]],
                ["id", "model", "name"],
                { limit: 1 }
            );
            if (models.length) {
                this.state.modelId = models[0].id;
                this.state.modelName = models[0].model;
                this.state.modelDisplayName = models[0].name;
            }
        } else {
            this.state.modelId = null;
            this.state.modelName = "";
            this.state.modelDisplayName = "";
        }
        // Reset dependent fields when model changes
        this.state.fieldId = null;
        this.state.fieldName = "";
        this.state.fieldDisplayName = "";
        this.state.contextFieldIds = [];
        this.state.filterDomain = "[]";
        this.state.recordCount = 0;
        this._updateRecordCount();
    }

    getModelIds() {
        return this.state.modelId ? [this.state.modelId] : [];
    }

    // Field domain for RecordAutocomplete - text content fields only
    get fieldDomain() {
        if (!this.state.modelId) {
            return [["id", "=", false]]; // No results
        }
        return [
            ["model_id", "=", this.state.modelId],
            ["ttype", "in", ["text", "char", "html"]],
        ];
    }

    // Field selection callback
    async onFieldSelected(ids) {
        if (ids && ids.length) {
            const fieldId = ids[0];
            this.state.fieldId = fieldId;
            // Get field details
            const fields = await this.orm.searchRead(
                "ir.model.fields",
                [["id", "=", fieldId]],
                ["name", "field_description", "ttype"],
                { limit: 1 }
            );
            if (fields.length) {
                this.state.fieldName = fields[0].name;
                this.state.fieldDisplayName = `${fields[0].field_description} (${fields[0].ttype})`;
            }
        } else {
            this.state.fieldId = null;
            this.state.fieldName = "";
            this.state.fieldDisplayName = "";
        }
    }

    getFieldIds() {
        return this.state.fieldId ? [this.state.fieldId] : [];
    }

    // Context fields domain - these fields are prepended to the main content in each source attachment.
    // Record identifier (name, id, display_name) is automatically included for semantic search.
    get contextFieldDomain() {
        if (!this.state.modelId) {
            return [["id", "=", false]];
        }
        return [
            ["model_id", "=", this.state.modelId],
            ["name", "not in", ["name", "id", "display_name"]],
            ["ttype", "in", ["char", "text", "selection", "many2one", "date", "datetime", "integer", "float", "boolean"]],
        ];
    }

    // Context fields update callback
    onContextFieldsUpdate(ids) {
        this.state.contextFieldIds = [...ids];
    }

    // Open domain selector dialog
    onOpenDomainSelector() {
        if (!this.state.modelName) {
            return;
        }
        // DomainSelectorDialog expects and returns domain as a string
        this.addDialog(DomainSelectorDialog, {
            resModel: this.state.modelName,
            domain: this.state.filterDomain,
            title: _t("Filter Domain"),
            onConfirm: (domain) => {
                // Domain is already a string from the dialog
                this.state.filterDomain = domain;
                this._updateRecordCount();
            },
        });
    }

    async _updateRecordCount() {
        if (!this.state.modelName) {
            this.state.recordCount = 0;
            return;
        }

        this.state.countLoading = true;
        try {
            // Use Odoo's Domain class to parse the domain string
            // This handles Python-style domain syntax like [("field", "=", "value")]
            const domainObj = new Domain(this.state.filterDomain || "[]");
            const domain = domainObj.toList();
            this.state.recordCount = await this.orm.searchCount(
                this.state.modelName,
                domain
            );
        } catch (e) {
            this.state.recordCount = 0;
        }
        this.state.countLoading = false;
    }

    get recordCountClass() {
        if (this.state.recordCount < 100) {
            return "text-success";
        } else if (this.state.recordCount < 500) {
            return "text-warning";
        } else {
            return "text-danger";
        }
    }

    get recordCountMessage() {
        if (this.state.recordCount < 100) {
            return _t("Good - focused dataset");
        } else if (this.state.recordCount < 500) {
            return _t("Consider adding filters for better relevance");
        } else {
            return _t("Large dataset - may reduce retrieval accuracy");
        }
    }

    async onConfirm() {
        if (!this.state.name) {
            this.notification.add(_t("Please enter a name for the configuration."), { type: "warning" });
            return;
        }
        if (!this.state.modelId) {
            this.notification.add(_t("Please select a model."), { type: "warning" });
            return;
        }
        if (!this.state.fieldId) {
            this.notification.add(_t("Please select a content field."), { type: "warning" });
            return;
        }

        this.state.loading = true;

        try {
            // Create the configuration
            await this.orm.create("ai.field.rag.config", [{
                name: this.state.name,
                agent_id: this.props.agentId,
                model_id: this.state.modelId,
                field_id: this.state.fieldId,
                filter_domain: this.state.filterDomain,
                context_field_ids: [[6, 0, this.state.contextFieldIds]],
            }]);

            this.notification.add(
                _t("Field RAG configuration created. Sources are being synced."),
                { type: "success" }
            );

            this.props.close();
            return this.actionService.doAction({ type: "ir.actions.client", tag: "soft_reload" });
        } catch (e) {
            this.notification.add(
                _t("Failed to create configuration: ") + (e.message || e),
                { type: "danger" }
            );
            this.state.loading = false;
        }
    }
}
