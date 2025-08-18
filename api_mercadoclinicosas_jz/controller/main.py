import logging
import pprint
from odoo import http
from odoo.http import request
from odoo import _, fields, models
from datetime import datetime, timedelta

from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.tools import lazy, str2bool
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError
import odoo
import uuid
from odoo.addons.payment.controllers import portal as payment_portal

from odoo.addons.website.models.ir_http import sitemap_qs2dom
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools import lazy, str2bool
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo import fields, http, SUPERUSER_ID, tools, _

#class WebsiteSaleClinicos(payment_portal.PaymentPortal):
class WebsiteSaleClinicos(WebsiteSale):

    #@http.route(['/apiclinicosx/shop'], type='json', auth="public", methods=['POST'],
    #            website=True, csrf=False)
    #def apiclinicos_signup(self, **post):
    #    return {}



    #como referencia ya no usar
    def apiclinicos_sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '/apiclinicos/shop',
        '/apiclinicos/shop/page/<int:page>',
        '/apiclinicos/shop/category/<model("product.public.category"):category>',
        '/apiclinicos/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='json', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop, csrf=False, methods=['POST'])
    def shop_clinicos(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        website = request.env['website'].get_current_website()
        website_domain = website.website_domain()
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = website.shop_ppg or 20

        ppr = website.shop_ppr or 4

        request_args = request.httprequest.args
        attrib_list = request_args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        filter_by_tags_enabled = website.is_view_active('website_sale.filter_products_tags')
        if filter_by_tags_enabled:
            tags = request_args.getlist('tags')
            # Allow only numeric tag values to avoid internal error.
            if tags and all(tag.isnumeric() for tag in tags):
                post['tags'] = tags
                tags = {int(tag) for tag in tags}
            else:
                post['tags'] = None
                tags = {}

        keep = QueryURL('/apiclinicos/shop',
                        **self._shop_get_query_url_kwargs(category and int(category), search, min_price, max_price,
                                                          **post))

        now = datetime.timestamp(datetime.now())
        pricelist = website.pricelist_id
        if 'website_sale_pricelist_time' in request.session:
            # Check if we need to refresh the cached pricelist
            pricelist_save_time = request.session['website_sale_pricelist_time']
            if pricelist_save_time < now - 60 * 60:
                request.session.pop('website_sale_current_pl', None)
                website.invalidate_recordset(['pricelist_id'])
                pricelist = website.pricelist_id
                request.session['website_sale_pricelist_time'] = now
                request.session['website_sale_current_pl'] = pricelist.id
        else:
            request.session['website_sale_pricelist_time'] = now
            request.session['website_sale_current_pl'] = pricelist.id

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = website.company_id.currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(
                company_currency, website.currency_id, request.website.company_id, fields.Date.today())
        else:
            conversion_rate = 1

        url = '/apiclinicos/shop'
        if search:
            post['search'] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            display_currency=website.currency_id,
            **post
        )
        fuzzy_search_term, product_count, search_product = self._shop_lookup_products(attrib_set, options, post, search,
                                                                                      website)

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            # TODO Find an alternative way to obtain the domain through the search metadata.
            Product = request.env['product.template'].with_context(bin_size=True)
            domain = self._get_shop_domain(search, category, attrib_values)

            # This is ~4 times more efficient than a search for the cheapest and most expensive products
            query = Product._where_calc(domain)
            Product._apply_ir_rules(query, 'read')
            from_clause, where_clause, where_params = query.get_sql()
            query = f"""
                    SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
                      FROM {from_clause}
                     WHERE {where_clause}
                """
            request.env.cr.execute(query, where_params)
            available_min_price, available_max_price = request.env.cr.fetchone()

            if min_price or max_price:
                # The if/else condition in the min_price / max_price value assignment
                # tackles the case where we switch to a list of products with different
                # available min / max prices than the ones set in the previous page.
                # In order to have logical results and not yield empty product lists, the
                # price filter is set to their respective available prices when the specified
                # min exceeds the max, and / or the specified max is lower than the available min.
                if min_price:
                    min_price = min_price if min_price <= available_max_price else available_min_price
                    post['min_price'] = min_price
                if max_price:
                    max_price = max_price if max_price >= available_min_price else available_max_price
                    post['max_price'] = max_price

        ProductTag = request.env['product.tag']
        if filter_by_tags_enabled and search_product:
            all_tags = ProductTag.search(
                expression.AND([
                    [('product_ids.is_published', '=', True), ('visible_on_ecommerce', '=', True)],
                    website_domain
                ])
            )
        else:
            all_tags = ProductTag

        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain
            ).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = lazy(lambda: Category.search(categs_domain))

        if category:
            url = "/apiclinicos/shop/category/%s" % slug(category)

        pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=5, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = lazy(lambda: ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ]))
        else:
            attributes = lazy(lambda: ProductAttribute.browse(attributes_ids))

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
            request.session['website_sale_shop_layout_mode'] = layout_mode

        # Try to fetch geoip based fpos or fallback on partner one
        fiscal_position_sudo = website.fiscal_position_id.sudo()
        products_prices = lazy(lambda: products._get_sales_prices(pricelist, fiscal_position_sudo))


        ###formateoo
        categ_format = []
        for catg in categs:
            categ_format.append({
                'id': catg.id ,
                'name': catg.display_name ,
                'description': catg.display_name ,
                'image': 'https://images.icon-icons.com/37/PNG/512/purchaseorderapplication_compra_orde_4474.png'
            })

        products_format = []

        url_base = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')])


        for prt in products:
            img_product = f'''{url_base.value}/web/image/product.template/{prt.id}/image_512'''
            #https://mercadoclinicosas-mercado-vpm-18386037.dev.odoo.com/web/image/product.template/846/image_512
            dx = {
                'id': prt.id ,
                'name': prt.display_name ,
                'description': prt.display_name ,
                'image1': img_product ,
                'image2': img_product ,
                'id_category': prt.categ_id.id ,
                'quantity': 1

            }

            products_pricex = products_prices[prt.id]
            if products_pricex:
                dx.update(products_pricex)
                dx.update({
                    'price': dx['price_reduce']
                })


            products_format.append(dx)




        search_product_format = []
        for prt in products:
            img_product = f'''{url_base.value}/web/image/product.template/{prt.id}/image_512'''
            # https://mercadoclinicosas-mercado-vpm-18386037.dev.odoo.com/web/image/product.template/846/image_512
            search_product_format.append({
                'id': prt.id,
                'name': prt.display_name,
                'url_image': img_product
            })

        attributes_format = []
        for at in attributes:
            attributes_format.append({
                'id': at.id ,
                'name': at.display_name
            })

        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'order': post.get('order', ''),
            'category': {'id': category.id , 'name': category.display_name} if category else {} ,
            #'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': {'id': pricelist.id , 'name': pricelist.display_name} if pricelist else {},
            'fiscal_position': {'id': fiscal_position_sudo.id , 'name': fiscal_position_sudo.display_name} if fiscal_position_sudo else {},
            'add_qty': add_qty,
            'products': products_format,
            'search_product': search_product_format,
            'search_count': product_count,  # common for all searchbox
            'bins': lazy(lambda: TableCompute().process(products, ppg, ppr)),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categ_format,
            'attributes': attributes_format,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'products_prices': products_prices,
            #'get_product_prices': lambda product: lazy(lambda: products_prices[product.id]),
            #'get_product_prices': products_prices[product.id] if product else {},
            'float_round': tools.float_round,
        }
        if filter_by_price_enabled:
            values['min_price'] = min_price or available_min_price
            values['max_price'] = max_price or available_max_price
            values['available_min_price'] = tools.float_round(available_min_price, 2)
            values['available_max_price'] = tools.float_round(available_max_price, 2)
        if filter_by_tags_enabled:
            values.update({'all_tags': all_tags, 'tags': tags})
        if category:
            values['main_object'] = category
        values.update(self._get_additional_shop_values(values))
        #values.update(WebsiteSale._get_additional_shop_values(values))

        return values

        #return request.render("website_sale.products", values)




class ApiClinicos(http.Controller):



    @http.route(['/apiclinicos/signup'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def apiclinicos_signup(self, **post):
        #db = http.request.env.cr.dbname
        data = http.request.httprequest.get_json()

        #values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}

        #partner = request.env['res.partner'].sudo().create({
        #    'name':
        #})

        values = {
            'name': data['name'] ,
            'email':  data['email'] ,
            'login': data['email'],
            'password': data['password'] ,
            'lang': 'es_AR'
        }

        #if not values:
        #    raise UserError(_("The form was not properly filled in."))

        ########

        login, password = request.env['res.users'].sudo().signup(values)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        pre_uid = request.session.authenticate(request.db, login, password)
        if not pre_uid:
            return False
            #raise SignupError(_('Authentication Failed.'))

        return True

    @http.route(['/apiclinicos/inactive/uuid/<string:token>'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def apiclinicos_inactive_uuid(self, token, **post):
        exist = request.env['clinicos.web.services'].sudo().search([('token', '=', token)])

        if exist:
            exist.active = False
            return True
        else:
            return False


    @http.route(['/apiclinicos/validate/uuid/<string:token>'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def apiclinicos_validate_uuid(self, token , **post):
        exist = request.env['clinicos.web.services'].sudo().search([('token','=',token)])

        if exist:
            return True
        else:
            return False

    @http.route(['/apiclinicos/login'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def apiclinicos_validate_login(self, **post):

        db = http.request.env.cr.dbname

        data = http.request.httprequest.get_json()


        values = {}


        try:
            uid = request.session.authenticate(db, data['login'], data['password'])
            user = request.env['res.users'].sudo().search([('id','=',uid)])
            url_image =  f'''/web/image?model=res.users&id={uid}&field=avatar_128'''

            roles = []
            for group in user.sudo().groups_id:
                # Busca el xml_id correspondiente
                xml_id = request.env['ir.model.data'].sudo().search([
                    ('model', '=', group._name),
                    ('res_id', '=', group.id)
                ], limit=1)

                if xml_id:
                    if xml_id.complete_name == 'base.group_user':
                        roles.append({
                            'id': xml_id.complete_name,
                            'name': group.display_name,
                            'image': 'https://cdn-icons-png.flaticon.com/512/1077/1077063.png',
                            'created_at': group.create_date,
                            'updated_at': group.write_date,
                            'route': 'admin/home'
                        })

                    if xml_id.complete_name == 'base.group_portal':
                        roles.append({
                            'id': 'CLIENT',
                            'name': group.display_name,
                            'image': 'https://cdn-icons-png.flaticon.com/512/1077/1077063.png',
                            'created_at': group.create_date,
                            'updated_at': group.write_date,
                            'route': 'client/home'
                        })


            values.update({
                'login_success': True ,
                'uid': uid ,
                'user': {
                    'id': uid ,
                    'name': user.name ,
                    'lastname': '',
                    'email': user.partner_id.sudo().email ,
                    'phone': user.partner_id.sudo().phone ,
                    'image': url_image ,
                    'password': '' ,
                    'notificationToken': '',
                    'roles': roles

                }
            })

            #generar codigo token uid

            unique_id = str(uuid.uuid4())  # Genera un UUID único

            request.env['clinicos.web.services'].sudo().create({
                'name': unique_id ,
                'token': unique_id
            })

            values.update({
                'uuid': unique_id ,
                'token': unique_id ,
            })



            #request.params['login_success'] = True
            #return request.redirect(self._login_redirect(uid, redirect=redirect))
        except odoo.exceptions.AccessDenied as e:
            if e.args == odoo.exceptions.AccessDenied().args:
                values.update({
                    'error': "Incorrecto usuario/contraseña"
                })
                #values['error'] = _("Wrong login/password")
            else:
                values.update({
                    'error': e.args[0]
                })
                #values['error'] = e.args[0]

        return values

    @http.route('/apiclinicos/websites', type="json", auth='public',
                website=True, methods=['POST', 'GET'], csrf=False, save_session=False)
    def apiclinicos_websites(self, **data):
        websites = request.env['website'].sudo().search([('show_app','=',True)])
        data = []
        for website in websites:


            if website.company_id.country_id:
                #ir.config_parameter
                url_base = request.env['ir.config_parameter'].sudo().search([('key','=','web.base.url')])
                img_country = f'''{url_base.value}{website.company_id.country_id.image_url}'''
                data.append({
                    'id': website.id,
                    'name': website.display_name,
                    'country_name': website.company_id.country_id.name ,
                    'country_image': img_country ,
                    'url': website.domain

                })

        return {'websites': data}


    #address
    @http.route('/apiclinicos/address', type="json", auth='public',
                website=True, methods=['POST', 'GET'], csrf=False, save_session=False)
    def apiclinicos_address(self, **data):
        data = http.request.httprequest.get_json()

        usuario = request.env['res.partner'].sudo().create({
            'name': data['name'] ,
            'street': data['address'] ,
            'city': data['neighborhood'],
            'email': data['email'],
            'phone': data['phone'],
            'country_id': int(data['country']),
            'state_id':  int(data['state']),
        })

        return {
            'data': {

                'id': usuario.id ,
                'name': usuario.name ,
                'city': usuario.city ,
                'street': usuario.street ,
                'phone': usuario.phone ,
                'email': usuario.email  ,
                'country_id': usuario.country_id.id ,
                'state_id': usuario.state_id.id  ,
            }
        }




    @http.route('/apiclinicos/contries', type="json", auth='public',
                website=True, methods=['POST', 'GET'], csrf=False, save_session=False)
    def apiclinicos_contries(self, **data):
        contries = request.env['res.country'].sudo().search([])
        data = []
        for country in contries:
            # ir.config_parameter
            url_base = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')])
            img_country = f'''{url_base.value}{country.image_url}'''
            country_name =  country.name

            if len(country_name) > 30:
                country_name =  country_name[:30]

            data.append({
                'id': country.id,
                'name': country_name,
                'country_name': '',
                'country_image': img_country,
                'url': ''

            })


        return {'contries': data}







