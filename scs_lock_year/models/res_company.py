from odoo import fields, models,api


class ResCompany(models.Model):
    _inherit = "res.company"

    closing_date_model_ids = fields.One2many(
        'lock.date.model',
        'company_id',
        string="Year Lock Models"
    )
    


