from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cod_amount = fields.Monetary(
        string='COD Amount / ยอดเรียกเก็บปลายทาง',
        currency_field='currency_id',
        tracking=True,
        help='Amount to be collected on delivery'
    )

    show_cod_field = fields.Boolean(
        string='Show COD Field',
        compute='_compute_show_cod_field',
        store=True
    )

    @api.depends('sale_order_template_id')
    def _compute_show_cod_field(self):
        """Compute whether to show COD field based on template"""
        for record in self:
            # Default to True if no template or template not in [2, 3]
            record.show_cod_field = not (record.sale_order_template_id.id in [2, 3])

    @api.onchange('cod_amount')
    def _onchange_cod_amount(self):
        """Update invoice payment terms when COD amount changes"""
        for order in self:
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    invoice.amount_residual = order.cod_amount
                    invoice.amount_residual_signed = order.cod_amount

    @api.onchange('sale_order_template_id', 'amount_total')
    def _onchange_template_for_cod(self):
        """Handle COD amount based on template and total amount"""
        for order in self:
            if order.sale_order_template_id.id in [2, 3]:
                order.cod_amount = 0.0
            else:
                # Set COD amount equal to total amount if template allows COD
                order.cod_amount = order.amount_total

    @api.onchange('order_line')
    def _onchange_order_line_for_cod(self):
        """Update COD amount when order lines change"""
        for order in self:
            if not order.sale_order_template_id.id in [2, 3]:
                order.cod_amount = order.amount_total 