from odoo import fields, models,api
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta


class ProjectChecklist(models.Model):
    _name = "project.checklist"
    _description = "Project Checklist"
    
    name = fields.Char(string = "Name")
    stage_ids = fields.Many2many('project.task.type', string = "Stages")
    project_ids = fields.Many2many('project.project', string="Projects")
    assigned_user_ids = fields.Many2many('res.users', string="Assigned Users")
    deadline = fields.Date(string="Checklist Deadline")
    
    
    @api.constrains('deadline')
    def _check_deadline(self):
        for record in self:
            if record.deadline and fields.Date.from_string(record.deadline) < datetime.today().date():
                raise ValidationError("The deadline cannot be set to a past date.")

class Projecttask(models.Model):
    _inherit = 'project.task'

    checklist_ids = fields.Many2many('project.checklist',domain="[('project_ids', '=', project_id),('stage_ids', '=', stage_id),('assigned_user_ids', 'in', user_ids)]")
    
    progress = fields.Float(compute="_compute_progress",default = 0.0 , store = True)
    
    progress_visible = fields.Boolean(
        string="Show Progress",
        compute="_compute_progress_visible",
        store=False
    )
    user_ids = fields.Many2many('res.users', string="Assigned Users")
    
    
    @api.depends('stage_id', 'project_id')
    def _compute_progress_visible(self):
        for task in self:
            checklists = self.env['project.checklist'].search([
                ('project_ids', 'in', task.project_id.id),
                ('stage_ids', 'in', task.stage_id.id),
                ('assigned_user_ids', 'in', task.user_ids.ids)
            ])
            task.progress_visible = bool(checklists) 

    @api.depends('checklist_ids', 'user_ids', 'project_id', 'stage_id')
    def _compute_progress(self):
        """
        Computes whether the progress should be visible based on the project, stage, and assigned users.
        The progress is visible if there are checklists assigned to the task for the given project and stage.
        """
        for task in self:
            checklists = self.env['project.checklist'].search([
                ('project_ids', '=', task.project_id.id),
                ('stage_ids', '=', task.stage_id.id),
                ('assigned_user_ids', 'in', task.user_ids.ids)
            ])

            total_checklists = len(checklists)

            assigned_checklist_ids = []
            for checklist in checklists:
                assigned_checklist_ids.append(checklist.id)

            completed_checklist_ids = []
            for checklist in task.checklist_ids:
                if checklist.id in assigned_checklist_ids:
                    completed_checklist_ids.append(checklist.id)

            completed_checklists = len(completed_checklist_ids)

            if total_checklists > 0:
                task.progress = (completed_checklists / total_checklists) * 100
            else:
                task.progress = 0.0

    def write(self, vals):
        """
        Overrides the write method to add validation when modifying a task.
        Ensures that checklists are completed before moving to another stage and that users
        can only modify checklists assigned to them.
        """
        for task in self:
            if 'stage_id' in vals:
                new_stage = self.env['project.task.type'].browse(vals['stage_id'])
                checklists = self.env['project.checklist'].search([
                    ('project_ids', 'in', task.project_id.id),
                    ('stage_ids', 'in', task.stage_id.id),
                    ('assigned_user_ids', 'in', task.user_ids.ids)
                ])

                if checklists and task.progress < 100:
                    raise ValidationError("Complete all checklist items before moving to another stage.")
                
                vals['checklist_ids'] = [(5, 0, 0)]
                vals['progress'] = 0.0

            current_user = self.env.user
            project_manager = task.project_id.user_id

            if 'checklist_ids' in vals:
                new_checklist_ids = []
                for command in vals['checklist_ids']:
                    if command[0] == 4:  
                        new_checklist_ids.append(command[1])
                    elif command[0] == 6:  
                        new_checklist_ids = command[2]  

                assigned_checklists = self.env['project.checklist'].search([
                    ('assigned_user_ids', '=', current_user.id)
                ])
                assigned_checklist_ids = assigned_checklists.ids

                if current_user != project_manager:
                    for checklist_id in new_checklist_ids:
                        if checklist_id not in assigned_checklist_ids:
                            raise ValidationError("You can only tick checklists assigned to you.")

        return super(Projecttask, self).write(vals)
    
                   
                    
    def send_checklist_reminder(self):
        """
        Sends a reminder email for tasks that have checklists with a deadline of the next day.
        The email is sent to the assigned users of the checklist.
        """
        template = self.env.ref('project_checklist_scs.send_reminder_for_task_checklist')
        today = fields.Date.today()
        reminder_date = today + timedelta(days=1)        
        checklists = self.env['project.checklist'].search([('deadline', '=', reminder_date)])
        
        for checklist in checklists:
            assigned_users = checklist.assigned_user_ids
            email_recipients = ','.join(assigned_users.mapped('email'))

            if email_recipients:
                tasks = self.env['project.task'].search([
                    ('checklist_ids', 'not in', checklist.id),
                    ('project_id', 'in', checklist.project_ids.ids),
                    ('stage_id', 'in', checklist.stage_ids.ids),
                    ('user_ids', 'in', assigned_users.ids)
                ])
               
                for task in tasks:
                    if template:
                        template.update({"email_to": email_recipients})
                        template.send_mail(task.id, force_send=True)
                    
     