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
from odoo.exceptions import UserError, ValidationError
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
                    df = df.fillna(False)

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)
                        # app_id = row.get('App ID')
                        loan_amnt = row.get('Loan Amount')
                        print('.........', rec_id, loan_amnt)
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

                        data = {
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
                            'all_data_shared_with_anulom': row.get('All Data Shared With Anulom(Date)'),
                            'em_creation_date': row.get('EM Creation Date'),
                            'noi_receipt_received_date': row.get('NOI Receipt Received Date'),

                        }
                        # validations----------------------------------------
                        vendor_rem = row.get('Vendor Remarks')
                        vendor_payment = row.get('Vendor Payment')
                        rac_rem = row.get('RAC Remarks')
                        sr_no = row.get('SR.NO')
                        cpc_name = row.get('CPC')

                        if not pd.isna(sr_no):
                            if not str(sr_no).isdigit():
                                raise ValidationError(f"Srno cannot be String in row{index+1}")

                        if cpc_name:
                            cpc_record = self.env['res.partner'].search([('name', '=', cpc_name)])
                            if not cpc_record:
                                raise ValidationError(f"CPC '{row.get('CPC')}' not found in res.partner in row {index+1}")
                            cpc_id = cpc_record.id
                        else:
                            cpc_id = False

                        if vendor_payment:
                            vendor_pay_record = self.env['vendor.payment.confirmation'].search(
                                [('name', '=', vendor_payment)])
                            if not vendor_pay_record:
                                raise ValidationError(
                                    f"vendor '{row.get('Vendor Payment')}' not found in vendor.payment.confirmation in row {index+1}")
                            vendor_payment_id = vendor_pay_record.id
                        else:
                            vendor_payment_id = False

                        if vendor_rem:
                            vendor_rem_record = self.env['vendor.remarks'].search([('name', '=', vendor_rem)])
                            if not vendor_rem_record:
                                raise ValidationError(
                                    f"vendor '{row.get('Vendor Remarks')}' not found in vendor.remarks in row {index+1}")
                            vendor_remarks_id = vendor_rem_record.id
                        else:
                            vendor_remarks_id = False

                        if rac_rem:
                            rac_rem_record = self.env['rac.remarks'].search([('name', '=', rac_rem)])
                            if not rac_rem_record:
                                raise ValidationError(
                                    f"'{row.get('RAC Remarks')}' not found in rac.remarks in row {index+1}")
                            rac_remarks_id = rac_rem_record.id
                        else:
                            rac_remarks_id = False

                        # validations----------------------------------------

                        if rec_id:
                            obj = self.env['mis.main'].search([('app_id', '=', rec_id)])
                            if obj:

                                obj.write(data)
                            else:
                                self.env['mis.main'].create(data)
                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

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
                    df = df.fillna(False)

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)
                        product_id = self.env['product.product'].search(
                            [('name', '=', row.get('Product'))], limit=1
                        ).id

                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        sr_no = row.get('SR.NO')
                        cpc_name = row.get('CPC')
                        product_name = row.get('Product')

                        # validations---------------------------------------------
                        if not pd.isna(sr_no):
                            if not str(sr_no).isdigit():
                                raise ValidationError(f"Srno cannot be String in row{index+1}")

                        if cpc_name:
                            cpc_record = self.env['res.partner'].search([('name', '=', cpc_name)])
                            if not cpc_record:
                                raise ValidationError(f"CPC '{row.get('CPC')}' not found in res.partner in row {index+1}")
                            cpc_id = cpc_record.id
                        else:
                            cpc_id = False

                        if product_name:
                            product_record = self.env['product.product'].search([('name', '=', product_name)])
                            if not product_record:
                                raise ValidationError(f"CPC '{row.get('Product')}' not found in res.partner.")
                            product_id = product_record.id
                        else:
                            product_id = False

                        # validations---------------------------------------------

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['esbtr.mtr'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                sr_no = row.get('SR.NO')
                                if not pd.isna(sr_no):
                                    if not str(sr_no).isdigit():
                                        raise ValidationError(f"Srno cannot be String in row{index+1}")

                                # if not pd.isna(cpc_id):
                                #     cpc_name = self.env['res.partner'].search(
                                #         [('name', '=', cpc_id)]
                                #     )
                                #     if not cpc_name:
                                #         raise ValidationError(f"{cpc_name} not found")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'customer_name': row.get('Customer Name') or '',
                                    'em_amount': row.get('EM Amount'),
                                    'loan_amount': row.get('Loan Amount'),
                                    'cpc': cpc_id,
                                    'product_id': product_id,
                                    'grn_no': row.get('GRN No'),
                                    'tran_id': row.get('Tran ID'),
                                    'data_date': row.get('Data Date') or False,
                                    'precessing_date': row.get('Processing Date') or False,
                                    'funds_receive_date': row.get('Funds Receive Date') or False,
                                    'submission_date': row.get('Submission Date') or False,
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
                                    'data_date': row.get('Data Date') or False,
                                    'precessing_date': row.get('Processing Date') or False,
                                    'funds_receive_date': row.get('Funds Receive Date') or False,
                                    'submission_date': row.get('Submission Date') or False,
                                    'comments': row.get('Comments'),
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

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
                    df = df.fillna(False)

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        sr_no = row.get('SR.NO')
                        cpc_name = row.get('CPC')

                        # validations---------------------------------------------
                        if not pd.isna(sr_no):
                            if not str(sr_no).isdigit():
                                raise ValidationError(f"Srno cannot be String in row{index+1}")

                        if cpc_name:
                            cpc_record = self.env['res.partner'].search([('name', '=', cpc_name)])
                            if not cpc_record:
                                raise ValidationError(f"CPC '{row.get('CPC')}' not found in res.partner in row {index+1}")
                            cpc_id = cpc_record.id
                        else:
                            cpc_id = False

                        # validations---------------------------------------------

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['share.certificate'].search([('app_id', '=', rec_id)])
                            print(obj)
                            data = {
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

                            }
                            if obj:

                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write(data)
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['share.certificate'].create(data)
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def dd_deposition_button_action_view(self):
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
                    date_columns = ['Loan Disb Date']
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")
                    df = df.fillna(False)
                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        user_id = self.env['hr.employee'].search(
                            [('name', '=', row.get('User'))]
                        ).id

                        sr_no = row.get('SR.NO')
                        cpc_name = row.get('CPC')
                        user_name = row.get('User')

                        # validations---------------------------------------------
                        if not pd.isna(sr_no):
                            if not str(sr_no).isdigit():
                                raise ValidationError(f"Srno cannot be String in row{index+1}")

                        if cpc_name:
                            cpc_record = self.env['res.partner'].search([('name', '=', cpc_name)])
                            if not cpc_record:
                                raise ValidationError(f"CPC '{row.get('CPC')}' not found in res.partner in row {index+1}")
                            cpc_id = cpc_record.id
                        else:
                            cpc_id = False


                        if user_name:
                            user_record = self.env['hr.employee'].search([('name', '=', user_name)])
                            if not user_record:
                                raise ValidationError(f"User '{row.get('User')}' not found in hr.employee.")
                            user_id = user_record.id
                        else:
                            user_id = False

                        # validations---------------------------------------------

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['dd.deposition'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id,
                                    'cpc': cpc_id or False,
                                    'loan_disb_date': row.get('Loan Disb Date') if pd.notna(
                                        row.get('Loan Disb Date')) else False,
                                    'lan_no': row.get('LAN No'),
                                    'customer_name': row.get('Customer Name'),
                                    'loan_amount': row.get('Loan Amount') if pd.notna(
                                        row.get('Loan Amount')) else False,
                                    'dd_no': row.get('DD No'),
                                    'type_of_transaction': row.get('Type of Transaction'),
                                    'name_of_sales_manager': row.get('Name of Sales Manager'),
                                    'bt_bank_name': row.get('BT Bank Name'),
                                    'dd_deposit_name': row.get('DD Deposit Name'),
                                    'user_id': user_id or False,

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['dd.deposition'].create({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id,
                                    'cpc': cpc_id or False,
                                    'loan_disb_date': row.get('Loan Disb Date') if pd.notna(
                                        row.get('Loan Disb Date')) else False,
                                    'lan_no': row.get('LAN No'),
                                    'customer_name': row.get('Customer Name'),
                                    'loan_amount': row.get('Loan Amount') if pd.notna(
                                        row.get('Loan Amount')) else False,
                                    'dd_no': row.get('DD No'),
                                    'type_of_transaction': row.get('Type of Transaction'),
                                    'name_of_sales_manager': row.get('Name of Sales Manager'),
                                    'bt_bank_name': row.get('BT Bank Name'),
                                    'dd_deposit_name': row.get('DD Deposit Name'),
                                    'user_id': user_id or False,
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def bt_property_button_action_view(self):
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
                    date_columns = [
                        'Document Receive date', 'Date - Data Shared with Agency',
                        'Next Followup Date', 'Document Submission Date'
                    ]
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")
                    df = df.fillna(False)
                    # for col in date_columns:
                    #     if col in df.columns:
                    #         if df[col].isnull():
                    #             df[col] = None
                    #         print("jjjjjjjjjjjjjjjjj")
                    #         df[col] = pd.to_datetime(df[col], errors='coerce')
                    #         # Replace NaT with None (suitable for SQL insertions)
                    #         df[col] = df[col].where(pd.notnull(df[col]), None)
                    #     else:
                    #         df[col] = None
                    #         print(":::::::::::::::")

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        cpc_id = self.env['res.partner'].search(
                            [('name', '=', row.get('CPC'))], limit=1
                        ).id

                        sr_no = row.get('SR.NO')
                        cpc_name = row.get('CPC')

                        # validations---------------------------------------------
                        if not pd.isna(sr_no):
                            if not str(sr_no).isdigit():
                                raise ValidationError(f"Srno cannot be String in row{index+1}")

                        if cpc_name:
                            cpc_record = self.env['res.partner'].search([('name', '=', cpc_name)])
                            if not cpc_record:
                                raise ValidationError(f"CPC '{row.get('CPC')}' not found in res.partner in row {index+1}")
                            cpc_id = cpc_record.id
                        else:
                            cpc_id = False

                        # validations---------------------------------------------

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['bt.property.collection'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'cpc': cpc_id,
                                    'customer_name': row.get('Customer Name'),
                                    'description': row.get('Description'),
                                    'document_receive_date': row.get('Document Receive date'),
                                    'transaction_type': row.get('Transaction Type'),
                                    'previous_finance_name': row.get('Previous Finance Name & Branch'),
                                    'property_address': row.get('Property Address'),
                                    'communication_address': row.get('Communication Address'),
                                    'contact_no_1': row.get('Contact 1'),
                                    'contact_no_2': row.get('Contact 2'),
                                    'sm_name': row.get('SM Name'),
                                    'data_shared_with_agency': row.get('Date - Data Shared with Agency') or False,
                                    'calling_remarks': row.get('Calling Remarks'),
                                    'next_followup_date': row.get('Next Followup Date') or False,
                                    'document_status': row.get('Document Status'),
                                    'document_submission_date': row.get('Document Submission Date') or False,
                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['bt.property.collection'].create({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'lan_no': row.get('LAN No'),
                                    'cpc': cpc_id,
                                    'customer_name': row.get('Customer Name'),
                                    'description': row.get('Description'),
                                    'document_receive_date': row.get('Document Receive date'),
                                    'transaction_type': row.get('Transaction Type'),
                                    'previous_finance_name': row.get('Previous Finance Name & Branch'),
                                    'property_address': row.get('Property Address'),
                                    'communication_address': row.get('Communication Address'),
                                    'contact_no_1': row.get('Contact 1'),
                                    'contact_no_2': row.get('Contact 2'),
                                    'sm_name': row.get('SM Name'),
                                    'data_shared_with_agency': row.get('Date - Data Shared with Agency', None) or False,
                                    'calling_remarks': row.get('Calling Remarks', None),
                                    'next_followup_date': row.get('Next Followup Date') or False,
                                    'document_status': row.get('Document Status'),
                                    'document_submission_date': row.get('Document Submission Date', None) or False,
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def courier_button_action_view(self):
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

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        # rec_id = str(row.get('App ID'))
                        rec_id = str(row.get('App ID')).zfill(6)

                        courier_company_id = self.env['res.partner'].search(
                            [('name', '=', row.get('Courier Company Name'))], limit=1
                        ).id

                        sr_no = row.get('SR.NO')
                        cpc_name = row.get('CPC')

                        # validations---------------------------------------------
                        if not pd.isna(sr_no):
                            if not str(sr_no).isdigit():
                                raise ValidationError(f"Srno cannot be String in row{index+1}")

                        if cpc_name:
                            cpc_record = self.env['res.partner'].search([('name', '=', cpc_name)])
                            if not cpc_record:
                                raise ValidationError(f"CPC '{row.get('CPC')}' not found in res.partner in row {index+1}")
                            cpc_id = cpc_record.id
                        else:
                            cpc_id = False

                        # validations---------------------------------------------

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['courier.details'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'courier_company_name': courier_company_id,
                                    'courier_to': row.get('Courier To'),
                                    'name_of_person': row.get('Name of Person'),
                                    'address': row.get('Address'),
                                    'mob_no': row.get('Mob No'),
                                    'docket_details': row.get('Docket Details'),
                                    'particulars': row.get('Particulars'),
                                    'remarks': row.get('Remarks'),

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['courier.details'].create({
                                    'sr_no': row.get('SR.NO'),
                                    'app_id': rec_id or obj.app_id,
                                    'courier_company_name': courier_company_id,
                                    'courier_to': row.get('Courier To'),
                                    'name_of_person': row.get('Name of Person'),
                                    'address': row.get('Address'),
                                    'mob_no': row.get('Mob No'),
                                    'docket_details': row.get('Docket Details'),
                                    'particulars': row.get('Particulars'),
                                    'remarks': row.get('Remarks'),

                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def vendor_payment_button_action_view(self):
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

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['vendor.payment.confirmation'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'name': row.get('Name'),
                                    'app_id': rec_id or obj.app_id,

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['vendor.payment.confirmation'].create({
                                    'name': row.get('Name'),
                                    'app_id': rec_id or obj.app_id,
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def rac_remarks_button_action_view(self):
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

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['rac.remarks'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'name': row.get('Name'),
                                    'app_id': rec_id or obj.app_id,

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['rac.remarks'].create({
                                    'name': row.get('Name'),
                                    'app_id': rec_id or obj.app_id,
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def vendor_remarks_button_action_view(self):
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

                    # Iterate through each row and print
                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['vendor.remarks'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'name': row.get('Name'),
                                    'app_id': rec_id or obj.app_id,

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['vendor.remarks'].create({
                                    'name': row.get('Name'),
                                    'app_id': rec_id or obj.app_id,
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))

    def reconcile_records_button_action_view(self):
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
                    date_columns = ['Actual Date', 'Value Date',
                                    ]
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")
                    df = df.fillna(False)

                    for index, row in df.iterrows():
                        print(f"Row {index + 1}:")
                        # print(row)
                        rec_id = str(row.get('App ID')).zfill(6)

                        if rec_id:
                            # Search for the record by ID
                            obj = self.env['reconcile.records'].search([('app_id', '=', rec_id)])
                            print(obj)
                            if obj:
                                print(f"Existing record found for App ID: {rec_id}")
                                obj.write({
                                    'name': row.get('Label'),
                                    'app_id': rec_id or obj.app_id,
                                    'actual_date': row.get('Actual Date'),
                                    'value_date': row.get('Value Date'),
                                    'bank_id': row.get('Bank'),
                                    'debit': row.get('Debit'),
                                    'credit': row.get('Credit'),
                                    'balance': row.get('Balance'),

                                })
                                print('Performed Write On Record')
                            else:
                                print(f"New App ID found, creating record: {rec_id}")
                                self.env['reconcile.records'].create({
                                    'name': row.get('Label'),
                                    'app_id': rec_id or obj.app_id,
                                    'actual_date': row.get('Actual Date'),
                                    'value_date': row.get('Value Date'),
                                    'bank_id': row.get('Bank'),
                                    'debit': row.get('Debit'),
                                    'credit': row.get('Credit'),
                                    'balance': row.get('Balance'),
                                })
                                print('Performed Create On Record')

                except Exception as e:
                    print(f"Error reading Excel file: {str(e)}")
                    raise ValidationError(str(e))
