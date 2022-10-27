# -*- coding: utf-8 -*-
{
    'name': "purchase_inherit",
    'category': 'Administration',
    'depends': ['base', 'hr', 'purchase', 'tree_button'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/department_view_inherit.xml',
        'views/purchase_order_view_inherit.xml',
        'views/spending_limit_view.xml',
        'views/spending_report.xml',
    ],
    #
    # "qweb": ['static/src/xml/*.xml'],
    #
    # 'assets': {
    #     'web.assets_backend': [
    #         'purchase_inherit/static/src/js/list_controller.js',
    #     ],
    # },
}
