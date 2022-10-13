# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseInherit(http.Controller):
#     @http.route('/purchase_inherit/purchase_inherit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_inherit/purchase_inherit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_inherit.listing', {
#             'root': '/purchase_inherit/purchase_inherit',
#             'objects': http.request.env['purchase_inherit.purchase_inherit'].search([]),
#         })

#     @http.route('/purchase_inherit/purchase_inherit/objects/<model("purchase_inherit.purchase_inherit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_inherit.object', {
#             'object': obj
#         })
