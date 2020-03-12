from urllib.parse import urlencode
import odoo
from odoo import exceptions
from odoo.tools.translate import _
from odoo import http
from odoo.http import request
from odoo.addons.saas_base.exceptions import MaximumDBException, MaximumTrialDBException
import werkzeug

import logging
_logger = logging.getLogger(__name__)


class SignupError(Exception):
    pass


class SaasPortal(http.Controller):

    @http.route(['/saas_portal/trial_check'], type='json', auth='public', website=True)
    def trial_check(self, **post):
        if self.exists_database(post['dbname']):
            return {"error": {"msg": "database already taken"}}
        return {"ok": 1}

    @http.route(['/saas_portal/add_new_client'], type='http', auth='public', website=True)
    def add_new_client(self, redirect_to_signup=False, **post):
        uid = request.session.uid
        if not uid:
            url = '/web/signup' if redirect_to_signup else '/web/login'
            redirect = str('/saas_portal/add_new_client?' + urlencode(post))
            query = {'redirect': redirect}
            return http.local_redirect(path=url, query=query)

        dbname = self.get_full_dbname(post.get('dbname'), post)
        user_id = request.session.uid
        partner_id = None
        if user_id:
            user = request.env['res.users'].browse(user_id)
            partner_id = user.partner_id.id
        plan = self.get_plan(int(post.get('plan_id', 0) or 0))
        trial = bool(post.get('trial', False))
        try:
            res = plan.create_new_database(dbname=dbname,
                                           user_id=user_id,
                                           partner_id=partner_id,
                                           trial=trial,)
        except MaximumDBException:
            _logger.info("MaximumDBException")
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumdb', '/')
            return werkzeug.utils.redirect(url)
        except MaximumTrialDBException:
            _logger.info("MaximumTrialDBException")
            url = request.env['ir.config_parameter'].sudo().get_param('saas_portal.page_for_maximumtrialdb', '/')
            return werkzeug.utils.redirect(url)

        # TODO: Redirect to site create successfully!
        return werkzeug.utils.redirect('/web/login')

    def get_config_parameter(self, param):
        config = request.env['ir.config_parameter']
        full_param = 'saas_portal.%s' % param
        return config.sudo().get_param(full_param)

    def get_full_dbname(self, dbname, post):
        if not dbname:
            return None
        server_id = post.get('domain')
        if server_id:
            server = request.env['saas.server'].sudo().browse(int(server_id))
            if server:
                domain = server.name
            else:
                domain = self.get_config_parameter('base_saas_domain')
        full_dbname = '%s.%s' % (dbname, domain)
        return full_dbname.replace('www.', '')

    def get_plan(self, plan_id=None):
        plan_obj = request.env['saas_portal.plan']
        if not plan_id:
            domain = [('state', '=', 'confirmed')]
            plans = request.env['saas_portal.plan'].search(domain)
            if plans:
                return plans[0]
            else:
                raise exceptions.Warning(_('There is no plan configured'))
        return plan_obj.sudo().browse(plan_id)

    def exists_database(self, dbname):
        full_dbname = self.get_full_dbname(dbname)
        return odoo.service.db.exp_db_exist(full_dbname)
