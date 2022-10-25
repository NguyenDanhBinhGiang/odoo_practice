{
    'name': "CRM and Purchase Report",
    'category': 'Administration',
    'depends': ['crm_sale_inherit', 'purchase_inherit'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'data/cron_email_template.xml',
        'views/monthly_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'report_crm_purchase/static/src/mail_template.css',
        ],
    },

}
