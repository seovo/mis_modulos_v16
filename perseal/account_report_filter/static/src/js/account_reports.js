odoo.define('account_report_filter.account_report', function (require) {
    'use strict';

    var AccountReportsWidget = require('account_reports.account_report');

    AccountReportsWidget.include({

        events: _.extend({}, AccountReportsWidget.prototype.events, {
            'input .o_account_reports_filter_input_custom': 'filter_accounts_custom',
            'input .o_account_reports_filter_input_vencido': 'filter_accounts_vencido',
        }),

        filter_accounts_custom: function(e) {
            console.log('entro al filter_accounts_custom')
            var self = this;
            var query = e.target.value.trim().toLowerCase();
            this.filterOn = false;
            const reportLines = this.el.querySelectorAll('.o_account_reports_table tbody tr');

            let lastKnownParent = null;
            let isLastParentHidden = null;
            let lastIndexParent = 0;
            let index = 0;
            for (let reportLine of reportLines) {
                const isParent = reportLine.classList.contains("o_account_searchable_line");
                const isChild = reportLine.classList.contains("o_js_account_report_inner_row");
                if (isParent) {
                    lastIndexParent = index;
                }
                if(isChild){
                    const lineNameEl = reportLine.querySelector('td:nth-child(3) > span');
                    const displayNameAccount = lineNameEl.innerHTML.replace(/[\r\n]/g, "").trim().toLowerCase();
                    const queryFound = displayNameAccount.includes(query);
                    reportLine.classList.toggle("o_account_reports_filtered_lines", !queryFound);
                    reportLines[lastIndexParent].classList.toggle("o_account_reports_filtered_lines", true);
                    lastKnownParent = reportLine.cells[0].getAttribute('data-id');
                    isLastParentHidden = !queryFound;
                    if (!queryFound) {
                        this.filterOn = true;
                    }
                }
                index ++;
            }

            // Make sure all ancestors are displayed.
            const $matchingChilds = this.$('tr[data-parent-id]:not(.o_account_reports_filtered_lines)');
            $($matchingChilds.get().reverse()).each(function(index, el) {
                const id = $.escapeSelector(String(el.dataset.parentId));
                const $parent = self.$('.o_account_report_line[data-id="' + id + '"]');
                $parent.closest('tr').toggleClass('o_account_reports_filtered_lines', false);
            });
            if (this.filterOn) {
                this.$('.o_account_reports_level1.total').hide();
            }
            else {
                this.$('.o_account_reports_level1.total').show();
            }

            this.report_options['filter_accounts'] = query;
            this.render_footnotes();
        },

        render: function() {
            this._super.apply(this, arguments);
            const self = this;
            setTimeout(function () {
                const idFilterCustom = document.getElementById('filtro_cuenta_personalizado');
                if(idFilterCustom){
                    console.log('Ingresando....')
                    let filas = $('.o_account_reports_table tbody tr').find('td:first-child');
                    console.log('filas: ', filas.length);
                    filas.each(function(idx, element){
                        const regex = /^partner_\d+$/;
                        const regex_sec = /^partner_id-res\.partner-\d+$/;
                        const line = $(this);
                        if(regex.test(line.data('id')) || regex_sec.test(line.data('id'))){
                                var method = self.unfold(line);
                                Promise.resolve(method).then(function() {
                                    self.render_footnotes();
                                    self.persist_options();
                                });
                        }
                    });
                }
            }, 500);
        },

        unfold: function(line) {
            console.log('entro al unfold')
            const idFilterCustom = document.getElementById('filtro_cuenta_personalizado');
            if(idFilterCustom){
                var self = this;
                var line_id = line.data('id');
                line.toggleClass('folded');
                self.report_options.unfolded_lines.push(line_id);
                var $lines_in_dom = this.$el.find('tr[data-parent-id="'+$.escapeSelector(String(line_id))+'"]');
                if ($lines_in_dom.length > 0) {
                    $lines_in_dom.find('.js_account_report_line_footnote').removeClass('folded');
                    $lines_in_dom.show();
                    line.find('.o_account_reports_caret_icon .fa-caret-right').toggleClass('fa-caret-right fa-caret-down');
                    line[0].dataset.unfolded = 'True';
                    this._add_line_classes();
                    return true;
                }
                else {
                    return this._rpc({
                            model: this.report_model,
                            method: 'get_html',
                            args: [self.financial_id, self.report_options, line.data('id')],
                            context: self.odoo_context,
                        })
                        .then(function(result){
                            $(line).parent('tr').replaceWith(result);
                            self._add_line_classes();
                            var displayed_table = $('.o_account_reports_table:not(#table_header_clone)')
                            displayed_table.find('.js_account_report_foldable').each(function() {
                                if(!$(this).data('unfolded')) {
                                    self.fold($(this));
                                }
                            });

                            const key = `td[data-id="${line.attr("data-id")}"] span.account_report_line_name`
                            $('table.o_account_reports_table').find(key).click()
                        });
                }
            } else {
                this._super.apply(this, arguments);
            }
        },

        filter_accounts_vencido: function(e) {
            console.log('entro al filter_accounts_vencido')
            var self = this;
            var query = e.target.value.trim().toLowerCase();
            this.filterOn = false;
            const reportLines = this.el.querySelectorAll('.o_account_reports_table tbody tr');

            let lastKnownParent = null;
            let isLastParentHidden = null;
            let lastIndexParent = 0;
            let index = 0;
            for (let reportLine of reportLines) {
                const isParent = reportLine.classList.contains("o_account_searchable_line");
                const isChild = reportLine.classList.contains("o_js_account_report_inner_row");
                if (isParent) {
                    lastIndexParent = index;
                }
                if(isChild){
                    console.log(reportLine);
                    const lineNameEl = reportLine.querySelector('td:nth-child(5) > span');
                    console.log(lineNameEl);
                    const displayNameAccount = lineNameEl.innerHTML.replace(/[\r\n]/g, "").trim().toLowerCase();
                    const queryFound = displayNameAccount.includes(query);
                    reportLine.classList.toggle("o_account_reports_filtered_lines", !queryFound);
                    reportLines[lastIndexParent].classList.toggle("o_account_reports_filtered_lines", true);
                    lastKnownParent = reportLine.cells[0].getAttribute('data-id');
                    isLastParentHidden = !queryFound;
                    if (!queryFound) {
                        this.filterOn = true;
                    }
                }
                index ++;
            }

            const $matchingChilds = this.$('tr[data-parent-id]:not(.o_account_reports_filtered_lines)');
            $($matchingChilds.get().reverse()).each(function(index, el) {
                const id = $.escapeSelector(String(el.dataset.parentId));
                const $parent = self.$('.o_account_report_line[data-id="' + id + '"]');
                $parent.closest('tr').toggleClass('o_account_reports_filtered_lines', false);
            });
            if (this.filterOn) {
                this.$('.o_account_reports_level1.total').hide();
            }
            else {
                this.$('.o_account_reports_level1.total').show();
            }

            this.report_options['filter_accounts'] = query;
            this.render_footnotes();
        },

    });

});