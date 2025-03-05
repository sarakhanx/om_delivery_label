from odoo import models, fields, api

class PrintConfirmWizard(models.TransientModel):
    _name = 'print.confirm.wizard'
    _description = 'Print Confirmation Wizard'

    picking_id = fields.Many2one('stock.picking', string='Picking')
    picking_ids = fields.Many2many('stock.picking', string='Pickings')
    print_type = fields.Selection([
        ('delivery_label', 'ใบปะหน้า'),
        ('pack_delivery', 'แพ็คขนส่ง')
    ], string='Print Type')
    last_print_date = fields.Datetime(string='Last Print Date', related='picking_id.last_print_date')
    message = fields.Text(string='Message', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self._context.get('multiple_records'):
            picking_ids = self._context.get('default_picking_ids', [])
            pickings = self.env['stock.picking'].browse(picking_ids)
            res['picking_ids'] = [(6, 0, pickings.ids)]
            printed_count = len(pickings.filtered(lambda p: p.delivery_label_printed if self._context.get('default_print_type') == 'delivery_label' else p.pack_delivery_printed))
            total_count = len(pickings)
            
            doc_type = 'ใบปะหน้า' if self._context.get('default_print_type') == 'delivery_label' else 'เอกสารแพ็คขนส่ง'
            res['message'] = f'⚠️ แจ้งเตือน: มี {printed_count} จาก {total_count} {doc_type} ที่ถูกพิมพ์ไปแล้ว\n\nคุณต้องการพิมพ์ซ้ำหรือไม่?'
        else:
            if self._context.get('active_id'):
                picking = self.env['stock.picking'].browse(self._context.get('active_id'))
                res['picking_id'] = picking.id
                res['print_type'] = self._context.get('default_print_type')
                if res['print_type'] == 'delivery_label':
                    res['message'] = f'⚠️ แจ้งเตือน: ใบปะหน้านี้ถูกพิมพ์ไปแล้วเมื่อ {picking.last_print_date.strftime("%d/%m/%Y %H:%M:%S")}\n\nคุณต้องการพิมพ์ซ้ำหรือไม่?'
                else:
                    res['message'] = f'⚠️ แจ้งเตือน: เอกสารแพ็คขนส่งนี้ถูกพิมพ์ไปแล้วเมื่อ {picking.last_print_date.strftime("%d/%m/%Y %H:%M:%S")}\n\nคุณต้องการพิมพ์ซ้ำหรือไม่?'
        return res

    def action_confirm(self):
        self.ensure_one()
        if self._context.get('multiple_records'):
            pickings = self.picking_ids
        else:
            pickings = self.picking_id

        if self.print_type == 'delivery_label':
            return pickings.action_print_delivery_label_confirmed()
        else:
            return pickings.action_print_pack_delivery_confirmed() 