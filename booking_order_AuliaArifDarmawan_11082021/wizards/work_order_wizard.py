from odoo import api, fields, models


class WorkOrderWizard(models.TransientModel):
    _name = 'wizard.work.order.cancel'

    reason = fields.Text(string="Reason")

    @api.multi
    def work_order_cancel(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['work.order'].browse(active_ids):
            record.notes = self.reason
            record.state = 'cancel'
        return {'type': 'ir.actions.act_window_close'}