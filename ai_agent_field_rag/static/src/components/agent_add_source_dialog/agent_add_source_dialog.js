/** @odoo-module **/

import { AgentSourceAddDialog } from "@ai/components/agent_add_source_dialog/agent_add_source_dialog";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { FieldRagConfigDialog } from "../field_rag_config_dialog/field_rag_config_dialog";


patch(AgentSourceAddDialog.prototype, {
    /**
     * Override cardsData to add the Model Field source card.
     */
    get cardsData() {
        const cards = super.cardsData;
        cards.push({
            icon: "fa-database",
            title: _t("Model Field"),
            onClick: () => this.onAddFieldRagSourceClick(),
        });
        return cards;
    },

    /**
     * Open the Field RAG configuration dialog.
     */
    onAddFieldRagSourceClick() {
        this.dialog.add(FieldRagConfigDialog, {
            agentId: this.agentId,
        });
    },
});
