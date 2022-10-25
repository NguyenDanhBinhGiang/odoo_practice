import base64

from odoo import models, fields, api


class CrmTeamInherit(models.Model):
    _inherit = 'crm.team'
    _sql_constraints = [(f'doanh_so_thang{i}_check', f'CHECK("chi_tieu_doanh_so_thang_{i}">0)',
                         f'chi tieu doanh so thang {i} phai > 0')
                        for i in range(1, 13)]

    for i in range(1, 13):
        exec(f"chi_tieu_doanh_so_thang_{i} = fields.Float('Thang {i}')")

    def stop_btn(self):
        pass

