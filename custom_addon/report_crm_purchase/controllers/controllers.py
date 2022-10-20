# -*- coding: utf-8 -*-
# from odoo import http


# class ReportCrmPurchase(http.Controller):
#     @http.route('/report_crm_purchase/report_crm_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_crm_purchase/report_crm_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_crm_purchase.listing', {
#             'root': '/report_crm_purchase/report_crm_purchase',
#             'objects': http.request.env['report_crm_purchase.report_crm_purchase'].search([]),
#         })

#     @http.route('/report_crm_purchase/report_crm_purchase/objects/<model("report_crm_purchase.report_crm_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_crm_purchase.object', {
#             'object': obj
#         })
