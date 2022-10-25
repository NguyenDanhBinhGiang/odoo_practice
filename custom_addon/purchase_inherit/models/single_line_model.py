from odoo import models, fields


class SingleLine(models.Model):
    _name = 'single.line'
    _sql_constraints = [
        ('only_one_check_constraint', 'CHECK (only_one_record_lock)', 'Can not have more than 1 config'),
        ('only_one_unique_constraint', 'UNIQUE (only_one_record_lock)', 'Can not have more than 1 config'),
    ]

    only_one_record_lock = fields.Boolean('Invisible field to make this table only have 1 row',
                                          default=True, invisible=True)
