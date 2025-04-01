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



    def esbtr_button_action_view(self):
        for record in self:
            for attachment in record.attachment_ids:
                file_data = base64.b64decode(attachment.datas)
                excel_file = BytesIO(file_data)

                try:
                    df = pd.read_excel(excel_file, dtype={"App ID": str})
                    date_columns = ['Data Date', 'Processing Date', 'Funds Receive Date',
                                    'Submission Date', ]
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")
                    df = df.fillna(False)

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
                                sr_no = row.get('SR.NO')
                                if not pd.isna(sr_no):
                                    if not str(sr_no).isdigit():
                                        raise ValidationError("Srno cannot be String")

                                if not pd.isna(cpc_id):
                                    cpc_name = self.env['res.partner'].search(
                                        [('name', '=', cpc_id)]
                                    ).id
                                    if not cpc_id:
                                        raise ValidationError(f"{row.get('CPC')} not found")

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
                                    'name_of_sales_manager': row.get('Sales Manager'),
                                    'bt_bank_name': row.get('BT Bank Name'),
                                    'dd_deposit_name': row.get('DD Deposit Name'),
                                    'user_id': row.get('User') or False,

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
                                    'name_of_sales_manager': row.get('Sales Manager'),
                                    'bt_bank_name': row.get('BT Bank Name'),
                                    'dd_deposit_name': row.get('DD Deposit Name'),
                                    'user_id': row.get('User') or False,
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

                    # Iterate through each row and print
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
