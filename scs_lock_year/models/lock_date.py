from odoo import fields, models,api
from odoo.exceptions import ValidationError,UserError
from datetime import datetime



class LockDateModel(models.Model):
    _name = "lock.date.model"
    _description = "Lock Date Models"

    company_id = fields.Many2one('res.company',string="Company",)
    model_id = fields.Many2one('ir.model',string="Model",required=True,ondelete='cascade')
    lock_date = fields.Date()
    warning_message = fields.Text("Warning Message")
    model_field_ids = fields.Many2many('ir.model.fields', string="Fields", domain="[('model_id', '=', model_id)]")
    compare_with = fields.Many2one(
        'ir.model.fields',
        string="Compare With",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['datetime', 'date'])]")

                    
    @api.constrains('model_id', 'company_id')
    def _check_duplicate_model(self):
        """
        Prevents duplicate lock date configurations for the same model and company.

        """
        for record in self:
            duplicate = self.search([
                ('model_id', '=', record.model_id.id),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    "The model is already selected for the company."
                )
