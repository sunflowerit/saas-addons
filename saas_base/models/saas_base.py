from odoo import fields
from odoo import models


class SaasClient(models.AbstractModel):
    _name = 'saas_base.client'

    file_storage = fields.Integer('File storage (MB)', readonly=True)
    db_storage = fields.Integer('DB storage (MB)', readonly=True)
    total_storage_limit = fields.Integer('Total storage limit (MB)', readonly=True, default=0)
    trial = fields.Boolean('Trial', help='indication of trial clients', default=False, readonly=True)
