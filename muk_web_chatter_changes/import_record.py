from idlelib.iomenu import encoding

from odoo import api, fields, models, _
import pandas as pd
import mimetypes
from io import BytesIO
import pandas as pd
from odoo import models, fields, api
from odoo.exceptions import UserError
import openpyxl
from io import BytesIO
import os
from io import BytesIO
import pandas as pd
from odoo.exceptions import UserError
from odoo import fields, models
import base64


class ImportRecords(models.Model):
    _name = 'import.record.master'

    # Using Many2many relation to ir.attachment for storing the attachment
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string='Attachment', required=True)
    model = fields.Selection(string='Class', selection=[('mis.main', 'MIS'),
                                                        ('esbtr.mtr', 'ESBTR'),
                                                        ('dd.deposition', 'DD Deposition'),
                                                        ('bt.property.collection', 'BT/Property Collection'),
                                                        ('share.certificate', 'Share Certificate'),
                                                        ('courier.details', 'Courier Details'),
                                                        ('vendor.payment.confirmation', 'Vendor Payment Confirmation'),
                                                        ('rac.remarks', 'RAC Remarks'),
                                                        ('vendor.remarks', 'Vendor Remarks'),
                                                        ('reconcile.records', 'Reconcile Records')
                                                        ], required=1)

    def mis_button_action_view(self):
        for record in self:
            # Assuming there's at least one attachment; loop through all if needed
            for attachment in record.attachment_ids:
                # Get the file content (base64 encoded) and decode it
                file_data = base64.b64decode(attachment.datas)

                # Convert the binary data into a file-like object
                excel_file = BytesIO(file_data)

                # Read the Excel file using pandas
                try:
                    # Read all sheets or specify a sheet if needed
                    df = pd.read_excel(excel_file, dtype={"App ID": str})
                    date_columns = ['Clearance Date', 'EM Creation Date', 'NOI Receipt Received Date',
                                    'Submitted To IGR', ]
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID'))
                        # app_id = row.get('App ID')
                        loan_amnt = row.get('Loan Amount')
                        print('.........', rec_id, loan_amnt)
                        # print('App id  ', app_id)
                        vendor_payment_id = self.env['vendor.payment.confirmation'].search(
                            [('name', '=', row.get('Vendor Payment'))], limit=1
                        ).id
                        rac_remarks_id = self.env['rac.remarks'].search(
                            [('name', '=', row.get('RAC Remarks'))], limit=1
                        ).id
                        vendor_remarks_id = self.env['vendor.remarks'].search(
                            [('name', '=', row.get('Vendor Remarks'))], limit=1
                        ).id
                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['mis.main'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'cpc': cpc_id,
                                    'customer_name': row.get('Customer Name'),
                                    'lan_no': row.get('LAN No'),
                                    'product': row.get('Product - HL/LAP/ HL BT/ LAP BT'),
                                    'sales_manager_name': row.get('Sales Manager Name'),
                                    'sales_manager_mob_no': row.get('Sales Manager Mobile No'),
                                    'customer_contact_no': row.get('Customer Contact No'),
                                    'customer_email': row.get('Customer Email'),
                                    'loan_amount': loan_amnt,
                                    'mode': row.get('Mode - Chq/DD/Online'),
                                    'cheq_dd': row.get('Cheque/DD Number'),
                                    'cheq_dd_amount': row.get('Cheque/DD Amount'),
                                    'clearance_date': row.get('Clearance Date'),
                                    'cheq_dd_bank_name': row.get('Chq/DD Bank Name'),
                                    'payment_details': row.get('Payment Details'),
                                    'vendor_payment_id': vendor_payment_id,
                                    'fsd_received': row.get('FSD Received (Y/N)'),
                                    'document_sharing_status': row.get('Document Sharing Status'),
                                    'rac_remarks': rac_remarks_id,
                                    'vendor_remarks': vendor_remarks_id,
                                    'all_data_shared_with_anulom': row.get('All Data Shared With Anulom'),
                                    'em_creation_date': row.get('EM Creation Date'),
                                    'noi_receipt_received_date': row.get('NOI Receipt Received Date'),

                                    # 'submitted_to_igr': row.get('Submitted To IGR'),
                                    # 'token_number': row.get('Token Number'),
                                    # 'sro': row.get('SRO'),
                                    # 'amount_receivable': row.get('Amount Receivable'),
                                    # 'amount_received': row.get('Amount Received'),
                                    # 'diff': row.get('Diff'),
                                    # 'rf_paid': int(row.get('RF Paid') or 0),
                                    # 'DHC': row.get('DHC'),
                                    # 'stamp_duty': row.get('Stamp Duty'),
                                    # 'comments': row.get('Comments'),
                                    # 'freeze_all': row.get('Freeze All')
                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['mis.main'].create({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id,
                                    'cpc': cpc_id,
                                    'customer_name': row.get('Customer Name'),
                                    'lan_no': row.get('LAN No'),
                                    'product': row.get('Product - HL/LAP/ HL BT/ LAP BT'),
                                    'sales_manager_name': row.get('Sales Manager Name'),
                                    'sales_manager_mob_no': row.get('Sales Manager Mobile No'),
                                    'customer_contact_no': row.get('Customer Contact No'),
                                    'customer_email': row.get('Customer Email'),
                                    'loan_amount': loan_amnt,
                                    'mode': row.get('Mode - Chq/DD/Online'),
                                    'cheq_dd': row.get('Cheque/DD Number'),
                                    'cheq_dd_amount': row.get('Cheque/DD Amount'),
                                    'clearance_date': row.get('Clearance Date'),
                                    'cheq_dd_bank_name': row.get('Chq/DD Bank Name'),
                                    'payment_details': row.get('Payment Details'),
                                    'vendor_payment_id': vendor_payment_id,
                                    'fsd_received': row.get('FSD Received (Y/N)'),
                                    'document_sharing_status': row.get('Document Sharing Status'),
                                    'rac_remarks': rac_remarks_id,
                                    'vendor_remarks': vendor_remarks_id,
                                    'all_data_shared_with_anulom': row.get('All Data Shared With Anulom'),
                                    'em_creation_date': row.get('EM Creation Date'),
                                    'noi_receipt_received_date': row.get('NOI Receipt Received Date'),
                                    # 'submitted_to_igr': row.get('Submitted To IGR'),
                                    # 'token_number': row.get('Token Number'),
                                    # 'sro': row.get('SRO'),
                                    # 'amount_receivable': row.get('Amount Receivable'),
                                    # 'amount_received': row.get('Amount Received'),
                                    # 'diff': row.get('Diff'),
                                    # 'rf_paid': int(row.get('RF Paid') or 0),
                                    # 'DHC': row.get('DHC'),
                                    # 'stamp_duty': row.get('Stamp Duty'),
                                    # 'comments': row.get('Comments'),
                                    # 'freeze_all': row.get('Freeze All')
                                })
                                print('Performed Create On Record')
                        # for column_name, value in row.items():
                        #     print(f"  {column_name}: {value}")
                        # print("---")
                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")

    def esbtr_button_action_view(self):
        for record in self:
            # Assuming there's at least one attachment; loop through all if needed
            for attachment in record.attachment_ids:
                # Get the file content (base64 encoded) and decode it
                file_data = base64.b64decode(attachment.datas)

                # Convert the binary data into a file-like object
                excel_file = BytesIO(file_data)

                # Read the Excel file using pandas
                try:
                    # Read all sheets or specify a sheet if needed
                    df = pd.read_excel(excel_file, dtype={"App ID": str})
                    date_columns = ['Data Date', 'Processing Date', 'Funds Receive Date',
                                    'Submission Date', ]
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID'))
                        product_id = self.env['product.product'].search(
                            [('name', '=', row.get('Product'))], limit=1
                        ).id

                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['esbtr.mtr'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'customer_name': row.get('Customer Name'),
                                    'em_amount': row.get('EM Amount'),
                                    'loan_amount': row.get('Loan Amount'),
                                    'cpc': cpc_id,
                                    'product_id': product_id,
                                    'grn_no': row.get('GRN No'),
                                    'tran_id': row.get('Tran ID'),
                                    'data_date': row.get('Data Date'),
                                    'precessing_date': row.get('Processing Date'),
                                    'funds_receive_date': row.get('Funds Receive Date'),
                                    'submission_date': row.get('Submission Date'),
                                    'comments': row.get('Comments'),

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['esbtr.mtr'].create({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'customer_name': row.get('Customer Name'),
                                    'em_amount': row.get('EM Amount'),
                                    'loan_amount': row.get('Loan Amount'),
                                    'cpc': cpc_id,
                                    'product_id': product_id,
                                    'grn_no': row.get('GRN No'),
                                    'tran_id': row.get('Tran ID'),
                                    'data_date': row.get('Data Date'),
                                    'precessing_date': row.get('Processing Date'),
                                    'funds_receive_date': row.get('Funds Receive Date'),
                                    'submission_date': row.get('Submission Date'),
                                    'comments': row.get('Comments'),
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")

    def share_button_action_view(self):
        for record in self:
            # Assuming there's at least one attachment; loop through all if needed
            for attachment in record.attachment_ids:
                # Get the file content (base64 encoded) and decode it
                file_data = base64.b64decode(attachment.datas)

                # Convert the binary data into a file-like object
                excel_file = BytesIO(file_data)

                # Read the Excel file using pandas
                try:
                    # Read all sheets or specify a sheet if needed
                    df = pd.read_excel(excel_file, dtype={"App ID": str})
                    date_columns = ['Date - Data Shared with Agency', 'Next Followup Date',
                                    'Share Certificate Receive Date',
                                    'Share Certificate Submission Date', 'Share Certificate Society Submission Date']
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID'))

                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['share.certificate'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'cpc': cpc_id,
                                    'customer_name': row.get('Customer Name'),

                                    'customer_contact_no': row.get('Customer Contact No'),
                                    'secretary_name': row.get('Secretary Name'),
                                    'secretary_contact_no': row.get('Secretary contact No'),
                                    'property_address': row.get('Property Address'),
                                    'data_shared_with_agency': row.get('Date - Data Shared with Agency'),
                                    'calling_remarks': row.get('Calling Remarks'),
                                    'next_followup_date': row.get('Next Followup Date'),
                                    'document_status': row.get('Document Status'),
                                    'share_certificate_receive_date': row.get('Share Certificate Receive Date'),
                                    'share_certificate_submission_date': row.get('Share Certificate Submission Date'),
                                    'remarks': row.get('Remarks'),
                                    'share_certificate_society_sub_date': row.get(
                                        'Share Certificate Society Submission Date'),

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['share.certificate'].create({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'cpc': cpc_id,
                                    'customer_name': row.get('Customer Name'),
                                    'customer_contact_no': row.get('Customer Contact No'),
                                    'secretary_name': row.get('Secretary Name'),
                                    'secretary_contact_no': row.get('Secretary contact No'),
                                    'property_address': row.get('Property Address'),
                                    'data_shared_with_agency': row.get('Date - Data Shared with Agency'),
                                    'calling_remarks': row.get('Calling Remarks'),
                                    'next_followup_date': row.get('Next Followup Date'),
                                    'document_status': row.get('Document Status'),
                                    'share_certificate_receive_date': row.get('Share Certificate Receive Date'),
                                    'share_certificate_submission_date': row.get('Share Certificate Submission Date'),
                                    'remarks': row.get('Remarks'),
                                    'share_certificate_society_sub_date': row.get(
                                        'Share Certificate Society Submission Date'),

                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")

    def dd_deposition_button_action_view(self):
        pass

    def bt_property_button_action_view(self):
        pass

    def courier_button_action_view(self):
        pass

    def vendor_payment_button_action_view(self):
        pass

    def rac_remarks_button_action_view(self):
        pass

    def vendor_remarks_button_action_view(self):
        pass

    def reconcile_records_button_action_view(self):
        pass
