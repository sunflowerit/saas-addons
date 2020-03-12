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


class SaasPortalDatabase(models.Model):
    _name = 'saas_portal.database'

    name = fields.Char('Instance Name', readonly=False)
    client_id = fields.Char('Database UUID')
    server_id = fields.Many2one(
        'saas.server', ondelete='restrict',
        string='Server', readonly=True)
    state = fields.Selection([('draft', 'New'),
                              ('open', 'In Progress'),
                              ('cancelled', 'Cancelled'),
                              ('pending', 'Pending'),
                              ('deleted', 'Deleted'),
                              ('template', 'Template'),
                              ],
                             'State', default='draft',
                             track_visibility='onchange')
    host = fields.Char('Host', compute='_compute_host')
    public_url = fields.Char(compute='_compute_public_url')
    password = fields.Char()

    @api.multi
    def _compute_host(self):
        for this in self:
            this.host = 'test.sunflowerodoo.nl'

    @api.multi
    def _compute_public_url(self):
        for record in self:
            scheme = record.server_id.request_scheme
            host = record.host
            record.public_url = scheme + host

    @api.multi
    def delete_database_server(self, **kwargs):
        self.ensure_one()
        return self._delete_database_server(**kwargs)

    @api.multi
    def _delete_database_server(self, force_delete=False):
        for database in self:
            state = {
                'd': database.name,
                'client_id': database.client_id,
            }
            if force_delete:
                state['force_delete'] = 1
            req, req_kwargs = database.server_id._request_server(
                path='/saas_server/delete_database',
                state=state, client_id=database.client_id)
            res = requests.Session().send(req, **req_kwargs)
            _logger.info('delete database: %s', res.text)
            if res.status_code != 500:
                database.state = 'deleted'

    @api.multi
    def show_upgrade_wizard(self):
        obj = self[0]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'saas.config',
            'target': 'new',
            'context': {
                'default_action': 'upgrade',
                'default_database': obj.name
            }
        }



