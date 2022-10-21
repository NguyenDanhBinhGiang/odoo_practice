{
    'name': "CRM and Purchase Report",
    'category': 'Administration',
    'depends': ['crm_sale_inherit', 'purchase_inherit'],
    'data': [
        'data/cron.xml',
        'data/cron_email_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'report_crm_purchase/static/src/mail_template.css',
        ],
    },

}
