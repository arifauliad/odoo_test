# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Booking Order',
    'version': '1.0',
    'summary': 'Booking Order Module By Aulia Arif Darmawan',
    'sequence': 30,
    'description': """ Booking Order Module By Aulia Arif Darmawan """,
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'data/sequence.xml',
        'data/template_print_work_order.xml',
        'wizards/work_order_wizard.xml',
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
