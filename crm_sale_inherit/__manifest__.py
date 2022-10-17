{
    'name': "crm_sale_inherit",
    'category': 'Administration',
    'depends': ['base', 'crm', 'sale_management', 'sale_crm'],
    'data': [
        'security/group.xml',
        'security/security_rules.xml',
        'views/crm_team_inherit.xml',
        'views/crm_lead_inherit.xml',
    ],
}
