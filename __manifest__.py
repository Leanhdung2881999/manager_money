{
    'name': "Manager Money",
	'name_vi_VN': "Quản lý tiền cá nhân",
    'version': '0.1.0',
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v15demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v15demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'summary': " Module hỗ trợ quản lý thu chi cá nhân ",
    'summary_vi_VN': " Module hỗ trợ quản lý thu chi cá nhân ",
    'category': 'Finance',
    'description': """
        Một module hỗ trợ quản lý chi tiêu đầu vào đầu ra cho cá nhân
        Key Features
        1. Wallet 
           * View wallet
           * CRUD wallet 
        2. Transaction 
           * View Transaction 
           * CRUD Transaction 
        Editions Supported
        1. Community Edition
        2. Enterprise Edition
    """,
    'description_vi_VN': """
        Một module hỗ trợ quản lý chi tiêu đầu vào đầu ra cho cá nhân
        Key Features
        1. Wallet 
           * View wallet
           * CRUD wallet 
        2. Transaction 
           * View Transaction 
           * CRUD Transaction 
        Editions Supported
        1. Community Edition
        2. Enterprise Edition
    """,
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': '99.9',
    'currency': 'EUR',
    'license': 'OPL-1',
    'depends': ['base','website','web'],
    # always loaded
    'data': [
        'security/manager_money_security.xml',
        'security/ir.model.access.csv',
        'views/wallet_views.xml',
        'views/transaction_oneday_views.xml',
        'views/transaction_views.xml',
        'views/category_views.xml',
        'views/menu_views.xml',
        'data/category_data.xml',
        'wizard/transaction_wizard_views.xml',
        'wizard/transaction_oneday_wizard_views.xml',
        'reports/manager_transactions_report.xml',
        'reports/manager_transactions_templates.xml',
        'data/service_cron.xml',
        'views/templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'images' : [
        # 'static/description/main_screenshot.png'
        ],
    
}
