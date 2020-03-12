import simplejson
import werkzeug
import requests
import random
import pytz
from datetime import datetime, timedelta

from odoo import api, exceptions, fields, models
from odoo.tools import scan_languages
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.saas_base.exceptions import MaximumTrialDBException
from odoo.addons.saas_base.exceptions import MaximumDBException
from werkzeug.exceptions import Forbidden

import logging
_logger = logging.getLogger(__name__)


@api.multi
def _compute_host(self):
    base_saas_domain = self.env['ir.config_parameter'].sudo(
    ).get_param('saas_portal.base_saas_domain')
    for r in self:
        host = r.name
        if base_saas_domain and '.' not in r.name:
            host = '%s.%s' % (r.name, base_saas_domain)
        r.host = host


class SaasPortalServer(models.Model):
    _name = 'saas.server'
    _description = 'SaaS Server'
    _rec_name = 'domain'

    _inherit = ['mail.thread']

    name = fields.Char(related='domain')
    domain = fields.Char('Domain', required=True)
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)
    request_scheme = fields.Selection(
        [('http', 'http'), ('https', 'https')], 'Scheme', default='http', required=True)
    client_ids = fields.One2many(
        'saas_portal.client', 'server_id', string='Clients')
    host = fields.Char('Host IP')
    provider = fields.Char("Provider")

    @api.multi
    def action_redirect_to_server(self):
        r = self[0]
        url = '{scheme}://{saas_server}:{port}{path}'.format(
            scheme=r.request_scheme, saas_server=r.host, port=r.request_port, path='/web')
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'name': 'Redirection',
            'url': url
        }

    @api.model
    def get_saas_server(self):
        p_server = self.env['saas.server']
        saas_server_list = p_server.sudo().search([])
        return saas_server_list[random.randint(0, len(saas_server_list) - 1)]




