{
    'name': 'MIS Modification',
    'version': '1.0',
    'category': 'MIS Modification',
    'summary': 'MIS Modification',
    'description': 'MIS Modification',
    'author': 'Krishna Dubey',
    'website': "",
    'depends': ['base', 'mail', 'hr', 'product', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/inherit_res_partner_view.xml',
        'views/root_menu_view.xml',
        'views/mis_main_view.xml',
        'views/vendor_payment_master_view.xml',
        'views/rac_master_view.xml',
        'views/vendor_remarks_view.xml',
        'views/esbtr_view.xml',
        'views/import_record.xml',
        'views/dd_deposition_view.xml',
        'views/bt_property_collection.xml',
        'views/share_certificate_view.xml',
        'views/courier_details_view.xml',
        'views/reconcile_records_view.xml',
        'views/wizard.xml',
        'wizard/mail_template_wizard_view.xml',
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
