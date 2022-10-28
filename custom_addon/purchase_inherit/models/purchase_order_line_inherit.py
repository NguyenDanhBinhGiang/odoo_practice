from odoo import models, fields, api
import random


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    recommend_vendor = fields.Many2one('product.supplierinfo',
                                       string='Nha cung cap de xuat',
                                       compute='_compute_recommend_vendor',
                                       store=True, readonly=False)

    @api.depends('product_id')
    def _compute_recommend_vendor(self):
        for rec in self:
            if rec.product_id:
                """Choose the cheapest vendor"""
                vendors = rec.product_id.seller_ids
                prices = [x.price for x in vendors]
                cheapest_vendors = [x for x in vendors if x.price == min(prices)]

                if len(cheapest_vendors) == 1:
                    rec.recommend_vendor = cheapest_vendors[0]
                elif len(cheapest_vendors) > 1:
                    """If there are multiple cheapest vendors, choose the fastest"""
                    delays = [x.delay for x in cheapest_vendors]
                    fastest_vendors = [x for x in cheapest_vendors if x.delay == min(delays)]

                    if len(fastest_vendors) < 2:
                        rec.recommend_vendor = fastest_vendors[0]
                    else:
                        """If there are still multiple fastest vendors, then choose by random"""
                        rec.recommend_vendor = random.choice(fastest_vendors)
                else:
                    rec.recommend_vendor = False
        pass
