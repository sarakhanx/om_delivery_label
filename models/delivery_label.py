from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Operation Type',
        required=True,
        readonly=False,
        index=True
    )
    hide_picking_type = fields.Boolean(
        string='Hide Picking Type',
        compute='_compute_hide_picking_type',
        store=True
    )

    @api.depends('state')
    def _compute_hide_picking_type(self):
        for record in self:
            # Logic to determine if picking type should be hidden
            # For now, we'll keep it always visible
            record.hide_picking_type = False

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

    # Computed field for amount residual
    amount_residual_display = fields.Monetary(
        string='Amount Residual',
        compute='_compute_amount_residual',
        store=True,
        help='Shows the remaining amount to be paid'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )

    @api.depends('sale_id.invoice_ids.amount_residual_signed')
    def _compute_amount_residual(self):
        for record in self:
            if record.sale_id and record.sale_id.invoice_ids:
                # Sum all residual amounts from related invoices
                record.amount_residual_display = sum(record.sale_id.invoice_ids.mapped('amount_residual_signed'))
            else:
                record.amount_residual_display = 0.0

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