from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date

class BaseModel(models.AbstractModel):
    _inherit = "base"

    def _check_lock_date(self,vals=None):
        """
        Ensures records cannot be modified if locked, except for editable fields.

        """
        company = self.env.company  
        lock_date_models = company.closing_date_model_ids.filtered(
            lambda l: l.model_id.model == self._name  
        )
        for lock in lock_date_models:
            compare_field = lock.compare_with.name 
            lock_date = lock.lock_date  

            editable_fields = lock_date_models.model_field_ids.mapped('name')
            for record in self:
                if compare_field and lock_date:
                    compare_value = getattr(record, compare_field, None)
                    
                    if isinstance(compare_value, datetime):
                        compare_value = compare_value.date()
                    
                    if vals:
                        non_editable_fields = [
                            field for field in vals.keys() if field not in editable_fields
                        ]
                        if compare_value and compare_value <  lock_date and non_editable_fields:
                            raise UserError(_(
                                lock.warning_message or 
                                "You cannot create or update this record due to lock date restrictions."
                            ))

                    if not vals and compare_value and compare_value <  lock_date:
                        raise UserError(_(
                            lock.warning_message or 
                            "You cannot create or update this record due to lock date restrictions."
                        ))
    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides create to validate lock date restrictions.
        """
        for vals in vals_list:
            dummy_record = self.new(vals)
            dummy_record._check_lock_date(vals)
        records = super().create(vals_list)
        return records

    def write(self, vals):
        """
        Overrides write to validate lock date restrictions.
        """
        self = self.with_context(updated_fields=vals.keys())
        result = super().write(vals)
        self._check_lock_date()  
        return result

