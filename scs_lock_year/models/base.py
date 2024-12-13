from odoo import fields, models,api
from odoo.exceptions import ValidationError


class BaseModelExtension(models.AbstractModel):
    _inherit = "base"


    @api.model_create_multi
    def create(self, vals):
        model_name = self._name
        lock_date_model = self.env['lock.date.model'].search([
            ('model_id.model', '=', model_name),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if model_name in ['mail.followers', 'ir.cron.progress']:
            return super(BaseModelExtension, self).create(vals)

        res = super(BaseModelExtension, self).create(vals)
        if res and hasattr(res, 'create_date'):
            record_date = res.create_date
            create_date = fields.Date.to_date(record_date)

            if lock_date_model and lock_date_model.lock_date:
                lock_date = lock_date_model.lock_date

                if record_date and create_date < lock_date:
                        raise ValidationError(lock_date_model.warning_message)
        return res


    def write(self, vals):
        model_name = self._name

        lock_date_model = self.env['lock.date.model'].search([
            ('model_id.model', '=', model_name),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if lock_date_model and lock_date_model.lock_date:
            lock_date = lock_date_model.lock_date
            warning_message = f"You are not allowed to update fields after lock date"

            editable_fields = lock_date_model.model_field_ids.mapped('name')

            for record in self:
                record_date = fields.Date.from_string(record.create_date or record.date or None) 
                if record_date and record_date < lock_date:
                    restricted_fields = [field for field in vals if field not in editable_fields]
                    if restricted_fields:
                        raise ValidationError(warning_message)

        return super(BaseModelExtension, self).write(vals)