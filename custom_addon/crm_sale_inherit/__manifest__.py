{
    'name': "crm_sale_inherit",
    'category': 'Administration',
    'depends': ['base', 'crm', 'sale_management', 'sale_crm', 'bai3', 'tree_button'],
    'data': [
        'security/group.xml',
        'security/security_rules.xml',
        'security/ir.model.access.csv',
        'views/crm_team_inherit.xml',
        'views/crm_lead_inherit.xml',
        'wizard/crm_report_wizard.xml',
        'wizard/crm_team_report_wizard.xml',
        'wizard/file_export.xml',
    ],
}
