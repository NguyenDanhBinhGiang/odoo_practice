from odoo import models, fields


class FileExport(models.Model):
    _name = 'file.export'

    file_name = fields.Char('Ten file')
    file = fields.Binary()

    def show_pop_up(self):
        self.ensure_one()
        view_id = self.env.ref('crm_sale_inherit.excel_report_export').id

        # noinspection PyUnresolvedReferences
        return {
            'type': 'ir.actions.act_window',
            'name': 'Excel export',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'file.export',
            'res_id': self.id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }
