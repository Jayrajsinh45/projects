from odoo import fields, models,api
from odoo.exceptions import ValidationError
from datetime import datetime



class LockDateModel(models.Model):
    _name = "lock.date.model"
    _description = "Lock Date Models"

    company_id = fields.Many2one('res.company',string="Company",)
    model_id = fields.Many2one('ir.model',string="Model",required=True,ondelete='cascade')
    lock_date = fields.Date()
    warning_message = fields.Text("Warning Message")
    model_field_ids = fields.Many2many('ir.model.fields', string="Fields", domain="[('model_id', '=', model_id)]")


    def validate_lock_date(self, model_name, record_date):
        lock_date_record = self.search([
            ('model_id.model', '=', model_name),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if lock_date_record and lock_date_record.lock_date:
            if record_date < lock_date_record.lock_date:
                raise ValidationError(lock_date_record.warning_message or 
                                    f"Records for the model '{model_name}' cannot have a date earlier than {lock_date_record.lock_date}.")

                    