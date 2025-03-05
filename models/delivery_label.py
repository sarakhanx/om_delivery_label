from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_label_printed = fields.Boolean(string='Delivery Label Printed', default=False, copy=False)
    pack_delivery_printed = fields.Boolean(string='Pack Delivery Printed', default=False, copy=False)
    last_print_date = fields.Datetime(string='Last Print Date', copy=False)

    # Computed fields for status icons
    delivery_label_status = fields.Boolean(
        string='Delivery Label Status',
        compute='_compute_print_status',
        store=True,
        help='Shows if delivery label has been printed'
    )
    pack_delivery_status = fields.Boolean(
        string='Pack Delivery Status',
        compute='_compute_print_status',
        store=True,
        help='Shows if pack delivery has been printed'
    )

    @api.depends('delivery_label_printed', 'pack_delivery_printed')
    def _compute_print_status(self):
        for record in self:
            record.delivery_label_status = record.delivery_label_printed
            record.pack_delivery_status = record.pack_delivery_printed

    def action_print_delivery_label(self):
        if len(self) > 1:
            # Check if any selected record has been printed before
            printed_pickings = self.filtered('delivery_label_printed')
            if printed_pickings:
                return {
                    'name': 'ยืนยันการพิมพ์ซ้ำ',
                    'type': 'ir.actions.act_window',
                    'res_model': 'print.confirm.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_picking_ids': self.ids,
                        'default_print_type': 'delivery_label',
                        'multiple_records': True
                    }
                }
            return self.action_print_delivery_label_confirmed()
        else:
            self.ensure_one()
            if self.delivery_label_printed:
                return {
                    'name': 'ยืนยันการพิมพ์ซ้ำ',
                    'type': 'ir.actions.act_window',
                    'res_model': 'print.confirm.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_picking_id': self.id,
                        'default_print_type': 'delivery_label'
                    }
                }
            return self.action_print_delivery_label_confirmed()

    def action_print_delivery_label_confirmed(self):
        self.write({
            'delivery_label_printed': True,
            'last_print_date': fields.Datetime.now()
        })
        return self.env.ref('om_delivery_label.action_report_delivery_label').report_action(self)

    def action_print_pack_delivery(self):
        if len(self) > 1:
            # Check if any selected record has been printed before
            printed_pickings = self.filtered('pack_delivery_printed')
            if printed_pickings:
                return {
                    'name': 'ยืนยันการพิมพ์ซ้ำ',
                    'type': 'ir.actions.act_window',
                    'res_model': 'print.confirm.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_picking_ids': self.ids,
                        'default_print_type': 'pack_delivery',
                        'multiple_records': True
                    }
                }
            return self.action_print_pack_delivery_confirmed()
        else:
            self.ensure_one()
            if self.pack_delivery_printed:
                return {
                    'name': 'ยืนยันการพิมพ์ซ้ำ',
                    'type': 'ir.actions.act_window',
                    'res_model': 'print.confirm.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_picking_id': self.id,
                        'default_print_type': 'pack_delivery'
                    }
                }
            return self.action_print_pack_delivery_confirmed()

    def action_print_pack_delivery_confirmed(self):
        self.write({
            'pack_delivery_printed': True,
            'last_print_date': fields.Datetime.now()
        })
        return self.env.ref('om_delivery_label.action_report_pack_delivery').report_action(self) 