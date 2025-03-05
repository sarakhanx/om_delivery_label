{
    'name': 'Delivery Label Print',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Delivery',
    'summary': 'ปริ๊นใบปะหน้าที่กล่องสินค้าเพื่อทำการจัดส่ง',
    'description': """
        This module adds a custom delivery label printing functionality:
        * Print delivery labels in A4 landscape format
        * Add "ใบปะหน้า" button in delivery operations
        * Custom layout with company and delivery information
    """,
    'author': 'Need Shopping',
    'website': 'https://www.needshopping.co',
    'depends': ['stock', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_label_view.xml',
        'views/print_confirm_wizard_view.xml',
        'reports/delivery_label_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
} 