from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class ServiceTeam(models.Model):
    _name = 'service.team'
    _rec_name = 'team_name'

    team_name = fields.Char(string='Team Name', required=True)
    team_leader = fields.Many2one('res.users', string='Team Leader', required=True)
    team_member = fields.Many2many('res.users', 'service_team_res_user_rel', 'service_team_id', 'user_id', string='Team Member')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_booking_order = fields.Boolean(string='Is Booking Order')
    team = fields.Many2one('service.team', string='Team')
    team_leader = fields.Many2one('res.users', string='Team Leader')
    team_member = fields.Many2many('res.users', 'sale_order_res_user_rel', 'service_team_id', 'user_id', string='Team Member')
    booking_start = fields.Datetime(string='Booking Start')
    booking_end = fields.Datetime(string='Booking End')

    @api.onchange('team')
    def onchange_field_team(self):
        self.team_leader = self.team.team_leader.id
        self.team_member = [(6, 0, self.team.team_member.ids)]

    @api.multi
    def button_check_team(self):
        so_name = self.check_team_availablity()
        print so_name
        if so_name != []:
            raise ValidationError('Team already has work order during that period on %s' % (so_name))
        else:
            raise ValidationError('Team is available for booking')

    def check_team_availablity(self):
        work_order_in_progress = self.env['work.order'].sudo().search([
            ('team','=', self.team.id),
            ('state','not in',('cancel','done'))
        ])
        so_name = []
        for each in work_order_in_progress:
            print each.bo_ref
            print each.bo_ref.name
            if (self.booking_start >= each.planned_start and self.booking_start <= each.planned_end) or (self.booking_end >= each.planned_start and self.booking_end <= each.planned_end):
                so_name.append(str(each.bo_ref.name))
        print so_name
        return so_name

    @api.multi
    def action_confirm(self):
        for each in self:
            if each.is_booking_order:
                vals = {
                    'team': each.team.id,
                    'team_leader': each.team_leader.id,
                    'team_member': [(6, 0, each.team_member.ids)],
                    'state': 'pending',
                    'planned_start': each.booking_start,
                    'planned_end': each.booking_end,
                    'bo_ref': self.id
                }
                so_name = each.check_team_availablity()
                if so_name != []:
                    raise ValidationError('Team is not available during this period, already booked on %s. Please book on another date.' % (so_name))
                self.env['work.order'].sudo().create(vals)

    def open_work_order_ids(self):
        action = self.env.ref('booking_order_AuliaArifDarmawan_11082021.action_work_order').read()[0]
        action['domain'] = [('bo_ref', '=', self.id)]
        return action

class WorkOrder(models.Model):
    _name = 'work.order'
    _rec_name = 'wo_number'

    wo_number = fields.Char(string='WO number')
    bo_ref = fields.Many2one('sale.order', string='Booking Order Reference', readonly=True)
    team = fields.Many2one('service.team', string='Team', required=True)
    team_leader = fields.Many2one('res.users', string='Team Leader', required=True)
    team_member = fields.Many2many('res.users', 'work_order_res_user_rel', 'wo_id', 'user_id', string='Team Member')
    planned_start = fields.Datetime(string='Planned Start', required=True)
    planned_end = fields.Datetime(string='Planned End', required=True)
    date_start = fields.Datetime(string='Date Start', readonly=True)
    date_end = fields.Datetime(string='Date End', readonly=True)
    state = fields.Selection([('pending','Pending'),
                              ('in_progress','In Progress'),
                              ('done','Done'),
                              ('cancel','Cancelled')],
                             string="State")
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        work_order = super(WorkOrder, self).create(vals)
        work_order.wo_number = self.env['ir.sequence'].next_by_code('work.order.sequence')

    @api.multi
    def button_start_work(self):
        for each in self:
            each.state = 'in_progress'
            each.date_start = datetime.now()

    @api.multi
    def button_end_work(self):
        for each in self:
            each.state = 'done'
            each.date_end = datetime.now()

    @api.multi
    def button_reset(self):
        for each in self:
            each.state = 'pending'
            each.date_start = False