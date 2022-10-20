# -*- coding: utf-8 -*-
{
    'name': "purchase_inherit",
    'category': 'Administration',
    'depends': ['base', 'hr', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'data/data.xml',
        'views/department_view_inherit.xml',
        'views/purchase_order_view_inherit.xml',
        'views/spending_limit_view.xml',
        'views/spending_report.xml',
    ],
}
