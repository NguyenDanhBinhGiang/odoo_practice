{
    'name': "bai3",
    'category': 'Administration',
    'depends': ['base', 'sale', 'hr'],
    'data': [
        'views/business_plan.xml',
        'views/sale_order_view_inherit.xml',
        'data/hr_department_default_data.xml',
        'data/plan_email_template.xml',
        'security/ir.model.access.csv',
        'security/group.xml',
    ],
}
