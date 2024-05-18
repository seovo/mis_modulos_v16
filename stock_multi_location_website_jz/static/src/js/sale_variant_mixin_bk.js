/** @odoo-module **/

import { KeepLast } from "@web/core/utils/concurrency";
import { memoize, uniqueId } from "@web/core/utils/functions";
import { throttleForAnimation } from "@web/core/utils/timing";
import { insertThousandsSep } from "@web/core/utils/numbers";
import { _t } from "@web/core/l10n/translation";
import { localization } from "@web/core/l10n/localization";
import { jsonrpc } from "@web/core/network/rpc_service";

//alert('hola');

var VariantMixin = {
    events: {

         'change [data-attribute_exclusions]'         : 'onChangeVariant' ,
         'change .js_add_cart_variants input:checked' : 'onChangeVariant',
         'change .js_add_cart_variants  select'       : 'onChangeVariant',
    },

    onChangeVariant: function (ev) {
        alert('hola');
        var $parent = $(ev.target).closest('.js_product');
        if (!$parent.data('uniqueId')) {
            $parent.data('uniqueId', uniqueId());
        }
        this._throttledGetCombinationInfo(this, $parent.data('uniqueId'))(ev);
    },

    _throttledGetCombinationInfo: memoize(function (self, uniqueId) {
        const keepLast = new KeepLast();
        var _getCombinationInfo = throttleForAnimation(self._getCombinationInfo.bind(self));
        return (ev, params) => keepLast.add(_getCombinationInfo(ev, params));
    }),


    /**
     * @see onChangeVariant
     *
     * @private
     * @param {Event} ev
     * @returns {Deferred}
     */
    _getCombinationInfo: function (ev) {

        alert('hola');

        if ($(ev.target).hasClass('variant_custom_value')) {
            return Promise.resolve();
        }

        const $parent = $(ev.target).closest('.js_product');
        if(!$parent.length){
            return Promise.resolve();
        }
        const combination = this.getSelectedVariantValues($parent);
        let parentCombination;

        if ($parent.hasClass('main_product')) {
            parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
            const $optProducts = $parent.parent().find(`[data-parent-unique-id='${$parent.data('uniqueId')}']`);

            for (const optionalProduct of $optProducts) {
                const $currentOptionalProduct = $(optionalProduct);
                const childCombination = this.getSelectedVariantValues($currentOptionalProduct);
                const productTemplateId = parseInt($currentOptionalProduct.find('.product_template_id').val());
                jsonrpc('/website_sale/get_combination_info', {
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($currentOptionalProduct),
                    'combination': childCombination,
                    'add_qty': parseInt($currentOptionalProduct.find('input[name="add_qty"]').val()),
                    'parent_combination': combination,
                    'context': this.context,
                    ...this._getOptionalCombinationInfoParam($currentOptionalProduct),
                }).then((combinationData) => {
                    this._onChangeCombination(ev, $currentOptionalProduct, combinationData);
                    this._checkExclusions($currentOptionalProduct, childCombination, combinationData.parent_exclusions);
                });
            }
        } else {
            parentCombination = this.getSelectedVariantValues(
                $parent.parent().find('.js_product.in_cart.main_product')
            );
        }

        return jsonrpc('/website_sale/get_combination_info', {
            'product_template_id': parseInt($parent.find('.product_template_id').val()),
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt($parent.find('input[name="add_qty"]').val()),
            'parent_combination': parentCombination,
            'context': this.context,
            ...this._getOptionalCombinationInfoParam($parent),
        }).then((combinationData) => {
            this._onChangeCombination(ev, $parent, combinationData);
            this._checkExclusions($parent, combination, combinationData.parent_exclusions);
        });
    },







    /**
     * Hook to add optional info to the combination info call.
     *
     * @param {$.Element} $product
     */
    _getOptionalCombinationInfoParam($product) {
        return {};
    },

    /**
     * Will add the "custom value" input for this attribute value if
     * the attribute value is configured as "custom" (see product_attribute_value.is_custom)
     *
     * @private
     * @param {MouseEvent} ev
     */
    handleCustomValues: function ($target) {
        var $variantContainer;
        var $customInput = false;
        if ($target.is('input[type=radio]') && $target.is(':checked')) {
            $variantContainer = $target.closest('ul').closest('li');
            $customInput = $target;
        } else if ($target.is('select')) {
            $variantContainer = $target.closest('li');
            $customInput = $target
                .find('option[value="' + $target.val() + '"]');
        }

        if ($variantContainer) {
            if ($customInput && $customInput.data('is_custom') === 'True') {
                var attributeValueId = $customInput.data('value_id');
                var attributeValueName = $customInput.data('value_name');

                if ($variantContainer.find('.variant_custom_value').length === 0
                        || $variantContainer
                              .find('.variant_custom_value')
                              .data('custom_product_template_attribute_value_id') !== parseInt(attributeValueId)) {
                    $variantContainer.find('.variant_custom_value').remove();

                    const previousCustomValue = $customInput.attr("previous_custom_value");
                    var $input = $('<input>', {
                        type: 'text',
                        'data-custom_product_template_attribute_value_id': attributeValueId,
                        'data-attribute_value_name': attributeValueName,
                        class: 'variant_custom_value form-control mt-2'
                    });

                    $input.attr('placeholder', attributeValueName);
                    $input.addClass('custom_value_radio');
                    $variantContainer.append($input);
                    if (previousCustomValue) {
                        $input.val(previousCustomValue);
                    }
                }
            } else {
                $variantContainer.find('.variant_custom_value').remove();
            }
        }
    },


    getSelectedVariantValues: function ($container) {
        var values = [];
        var unchangedValues = $container
            .find('div.oe_unchanged_value_ids')
            .data('unchanged_value_ids') || [];

        var variantsValuesSelectors = [
            'input.js_variant_change:checked',
            'select.js_variant_change'
        ];
        $container.find(variantsValuesSelectors.join(', ')).toArray().forEach((el) => {
            values.push(+$(el).val());
        });

        return values.concat(unchangedValues);
    },

    /**
     * Will return a promise:
     *
     * - If the product already exists, immediately resolves it with the product_id
     * - If the product does not exist yet ("dynamic" variant creation), this method will
     *   create the product first and then resolve the promise with the created product's id
     *
     * @param {$.Element} $container the container to look into
     * @param {integer} productId the product id
     * @param {integer} productTemplateId the corresponding product template id
     * @param {boolean} useAjax wether the rpc call should be done using jsonrpc or using _rpc
     * @returns {Promise} the promise that will be resolved with a {integer} productId
     */
    selectOrCreateProduct: function ($container, productId, productTemplateId, useAjax) {
        productId = parseInt(productId);
        productTemplateId = parseInt(productTemplateId);
        var productReady = Promise.resolve();
        if (productId) {
            productReady = Promise.resolve(productId);
        } else {
            var params = {
                product_template_id: productTemplateId,
                product_template_attribute_value_ids:
                    JSON.stringify(VariantMixin.getSelectedVariantValues($container)),
            };

            var route = '/sale/create_product_variant';
            if (useAjax) {
                productReady = jsonrpc(route, params);
            } else {
                productReady = this.rpc(route, params);
            }
        }

        return productReady;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Will disable attribute value's inputs based on combination exclusions
     * and will disable the "add" button if the selected combination
     * is not available
     *
     * This will check both the exclusions within the product itself and
     * the exclusions coming from the parent product (meaning that this product
     * is an option of the parent product)
     *
     * It will also check that the selected combination does not exactly
     * match a manually archived product
     *
     * @private
     * @param {$.Element} $parent the parent container to apply exclusions
     * @param {Array} combination the selected combination of product attribute values
     * @param {Array} parentExclusions the exclusions induced by the variant selection of the parent product
     * For example chair cannot have steel legs if the parent Desk doesn't have steel legs
     */
    _checkExclusions: function ($parent, combination, parentExclusions) {
        var self = this;
        var combinationData = $parent
            .find('ul[data-attribute_exclusions]')
            .data('attribute_exclusions');

        if (parentExclusions && combinationData.parent_exclusions) {
            combinationData.parent_exclusions = parentExclusions;
        }
        $parent
            .find('option, input, label, .o_variant_pills')
            .removeClass('css_not_available')
            .attr('title', function () { return $(this).data('value_name') || ''; })
            .data('excluded-by', '');

        // exclusion rules: array of ptav
        // for each of them, contains array with the other ptav they exclude
        if (combinationData.exclusions) {
            // browse all the currently selected attributes
            Object.values(combination).forEach((current_ptav) => {
                if (combinationData.exclusions.hasOwnProperty(current_ptav)) {
                    // for each exclusion of the current attribute:
                    Object.values(combinationData.exclusions[current_ptav]).forEach((excluded_ptav) => {
                        // disable the excluded input (even when not already selected)
                        // to give a visual feedback before click
                        self._disableInput(
                            $parent,
                            excluded_ptav,
                            current_ptav,
                            combinationData.mapped_attribute_names
                        );
                    });
                }
            });
        }
        // combination exclusions: array of array of ptav
        // for example a product with 3 variation and one specific variation is disabled (archived)
        //  requires the first 2 to be selected for the third to be disabled
        if (combinationData.archived_combinations) {
            combinationData.archived_combinations.forEach((excludedCombination) => {
                const ptavCommon = excludedCombination.filter((ptav) => combination.includes(ptav));
                if (
                    !!ptavCommon
                    && (combination.length === excludedCombination.length)
                    && (ptavCommon.length === combination.length)
                ) {
                    // Selected combination is archived, all attributes must be disabled from each other
                    combination.forEach((ptav) => {
                        combination.forEach((ptavOther) => {
                            if (ptav === ptavOther) {
                                return;
                            }
                            self._disableInput(
                                $parent,
                                ptav,
                                ptavOther,
                                combinationData.mapped_attribute_names,
                            );
                        })
                    })
                } else if (
                    !!ptavCommon
                    && (combination.length === excludedCombination.length)
                    && (ptavCommon.length === (combination.length - 1))
                ) {
                    // In this case we only need to disable the remaining ptav
                    const disabledPtav = excludedCombination.find((ptav) => !combination.includes(ptav));
                    excludedCombination.forEach((ptav) => {
                        if (ptav === disabledPtav) {
                            return;
                        }
                        self._disableInput(
                            $parent,
                            disabledPtav,
                            ptav,
                            combinationData.mapped_attribute_names,
                        )
                    });
                }
            });
        }

        // parent exclusions (tell which attributes are excluded from parent)
        for (const [excluded_by, exclusions] of Object.entries(
            combinationData.parent_exclusions || {}
        )) {
            // check that the selected combination is in the parent exclusions
            exclusions.forEach((ptav) => {
                // disable the excluded input (even when not already selected)
                // to give a visual feedback before click
                self._disableInput(
                    $parent,
                    ptav,
                    excluded_by,
                    combinationData.mapped_attribute_names,
                    combinationData.parent_product_name
                );
            });
        }
    },
    /**
     * Extracted to a method to be extendable by other modules
     *
     * @param {$.Element} $parent
     */
    _getProductId: function ($parent) {
        return parseInt($parent.find('.product_id').val());
    },
    /**
     * Will disable the input/option that refers to the passed attributeValueId.
     * This is used for showing the user that some combinations are not available.
     *
     * It will also display a message explaining why the input is not selectable.
     * Based on the "excludedBy" and the "productName" params.
     * e.g: Not available with Color: Black
     *
     * @private
     * @param {$.Element} $parent
     * @param {integer} attributeValueId
     * @param {integer} excludedBy The attribute value that excludes this input
     * @param {Object} attributeNames A dict containing all the names of the attribute values
     *   to show a human readable message explaining why the input is disabled.
     * @param {string} [productName] The parent product. If provided, it will be appended before
     *   the name of the attribute value that excludes this input
     *   e.g: Not available with Customizable Desk (Color: Black)
     */
    _disableInput: function ($parent, attributeValueId, excludedBy, attributeNames, productName) {
        var $input = $parent
            .find('option[value=' + attributeValueId + '], input[value=' + attributeValueId + ']');
        $input.addClass('css_not_available');
        $input.closest('label').addClass('css_not_available');
        $input.closest('.o_variant_pills').addClass('css_not_available');

        if (excludedBy && attributeNames) {
            var $target = $input.is('option') ? $input : $input.closest('label').add($input);
            var excludedByData = [];
            if ($target.data('excluded-by')) {
                excludedByData = JSON.parse($target.data('excluded-by'));
            }

            var excludedByName = attributeNames[excludedBy];
            if (productName) {
                excludedByName = productName + ' (' + excludedByName + ')';
            }
            excludedByData.push(excludedByName);

            $target.attr('title', _t('Not available with %s', excludedByData.join(', ')));
            $target.data('excluded-by', JSON.stringify(excludedByData));
        }
    },
    /**
     * @see onChangeVariant
     *
     * @private
     * @param {MouseEvent} ev
     * @param {$.Element} $parent
     * @param {Array} combination
     */
    _onChangeCombination: function (ev, $parent, combination) {
        var self = this;
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
        $price.text(self._priceToStr(combination.price));
        $default_price.text(self._priceToStr(combination.list_price));

        var isCombinationPossible = true;
        if (typeof combination.is_combination_possible !== "undefined") {
            isCombinationPossible = combination.is_combination_possible;
        }
        this._toggleDisable($parent, isCombinationPossible);

        if (combination.has_discounted_price && !combination.compare_list_price) {
            $default_price
                .closest('.oe_website_sale')
                .addClass("discount");
            $optional_price
                .closest('.oe_optional')
                .removeClass('d-none')
                .css('text-decoration', 'line-through');
            $default_price.parent().removeClass('d-none');
        } else {
            $default_price
                .closest('.oe_website_sale')
                .removeClass("discount");
            $optional_price.closest('.oe_optional').addClass('d-none');
            $default_price.parent().addClass('d-none');
        }

        var rootComponentSelectors = [
            'tr.js_product',
            '.oe_website_sale',
            '.o_product_configurator'
        ];

        // update images only when changing product
        // or when either ids are 'false', meaning dynamic products.
        // Dynamic products don't have images BUT they may have invalid
        // combinations that need to disable the image.


        $parent
            .find('.product_id')
            .first()
            .val(combination.product_id || 0)
            .trigger('change');

        $parent
            .find('.product_display_name')
            .first()
            .text(combination.display_name);

        $parent
            .find('.js_raw_price')
            .first()
            .text(combination.price)
            .trigger('change');

        $parent
            .find('.o_product_tags')
            .first()
            .html(combination.product_tags);

        this.handleCustomValues($(ev.target));
    },

    /**
     * returns the formatted price
     *
     * @private
     * @param {float} price
     */
    _priceToStr: function (price) {
        var precision = 2;

        if ($('.decimal_precision').length) {
            precision = parseInt($('.decimal_precision').last().data('precision'));
        }
        var formatted = price.toFixed(precision).split(".");
        const { thousandsSep, decimalPoint, grouping } = localization;
        formatted[0] = insertThousandsSep(formatted[0], thousandsSep, grouping);
        return formatted.join(decimalPoint);
    },
    /**
     * Returns a throttled `_getCombinationInfo` with a leading and a trailing
     * call, which is memoized per `uniqueId`, and for which previous results
     * are dropped.
     *
     * The uniqueId is needed because on the configurator modal there might be
     * multiple elements triggering the rpc at the same time, and we need each
     * individual product rpc to be executed, but only once per individual
     * product.
     *
     * The leading execution is to keep good reactivity on the first call, for
     * a better user experience. The trailing is because ultimately only the
     * information about the last selected combination is useful. All
     * intermediary rpc can be ignored and are therefore best not done at all.
     *
     * The keepLast is to make sure we only consider the result of the last call, when several
     * (asynchronous) calls are done in parallel.
     *
     * @private
     * @param {string} uniqueId
     * @returns {function}
     */

    /**
     * Toggles the disabled class depending on the $parent element
     * and the possibility of the current combination.
     *
     * @private
     * @param {$.Element} $parent
     * @param {boolean} isCombinationPossible
     */
    _toggleDisable: function ($parent, isCombinationPossible) {
        $parent.toggleClass('css_not_available', !isCombinationPossible);
        if ($parent.hasClass('in_cart')) {
            const primaryButton = $parent.parents('.modal-content').find('.modal-footer .btn-primary');
            primaryButton.prop('disabled', !isCombinationPossible);
            primaryButton.toggleClass('disabled', !isCombinationPossible);
        }
    },
    /**
     * Updates the product image.
     * This will use the productId if available or will fallback to the productTemplateId.
     *
     * @private
     * @param {$.Element} $productContainer
     * @param {boolean} displayImage will hide the image if true. It will use the 'invisible' class
     *   instead of d-none to prevent layout change
     * @param {integer} product_id
     * @param {integer} productTemplateId
     */


    /**
     * Highlight selected color
     *
     * @private
     * @param {MouseEvent} ev
     */
    _onChangeColorAttribute: function (ev) {
        var $parent = $(ev.target).closest('.js_product');
        $parent.find('.css_attribute_color')
            .removeClass("active")
            .filter(':has(input:checked)')
            .addClass("active");
    },

    _onChangePillsAttribute: function (ev) {
        var $parent = $(ev.target).closest('.js_product');
        $parent.find('.o_variant_pills')
            .removeClass("active")
            .filter(':has(input:checked)')
            .addClass("active");
    },

    /**
     * Extension point for website_sale
     *
     * @private
     * @param {string} uri The uri to adapt
     */
    _getUri: function (uri) {
        return uri;
    }
};

export default VariantMixin;

