import json
from odoo import http
from odoo.http import request, Response


class CrmPurchaseReport(http.Controller):
    def get_report_data(self, month):
        pass

    @http.route('/report', type='http', auth='none', methods=['POST'], csrf=False)
    def user_partner(self, token=None, month=None, year=None):
        if not all([token, month, year]):
            Response.status = '400 Bad Request'
            return json.dumps({'err': 'Request body must have token, month and year'})
        if token != 'odooneverdie':
            Response.status = '401 Unauthorized'
            return json.dumps({'err': 'Wrong token'})
        if month not in range(0, 13):
            Response.status = '400 Bad Request'
            return json.dumps({'err': f'Bad month value: {month}'})

        domain = [
            ('month', '=', month),
            ('year', '=', year)
        ]
        result = request.env['monthly.report'].sudo().search(domain)
        if len(result) < 1:
            request.env['monthly.report'].sudo().create_report(month, year)
        result = request.env['monthly.report'].sudo().search(domain)[0]
        data = {
            'sales': [{
                'sale_team_name': x.sale_team_id.name,
                'real_revenue': x.total_revenue,
                'diff': x.revenue_diff
            } for x in result.sale_report_ids]
            ,
            'purchase': [{
                'department_name': x.department_id.name,
                'real_cost': x.total_spending,
                'diff': x.spending_diff
            } for x in result.purchase_report_ids]
        }
        data = json.dumps(data)
        return request.make_response(data, headers=[('Content-Type', 'application/json')])
