"""
Step 3 generates 2 CSVs:
- order_items.csv
- payments.csv

"""
import csv
import glob
import json
import os
import zipfile

from infusionsoft.library import Infusionsoft

import config
from infusionsoft_actions import create_custom_field, get_table
from tools import convert_dict_dates_to_string


dir_path = "output/{} -- {}/".format(config.SOURCE_APPNAME,
                                     config.DESTINATION_APPNAME)
os.makedirs(dir_path, exist_ok=True)

src_infusionsoft = Infusionsoft(config.SOURCE_APPNAME, config.SOURCE_API_KEY)
dest_infusionsoft = Infusionsoft(config.DESTINATION_APPNAME,
                                 config.DESTINATION_API_KEY)


# RELATIONSHIPS
# =============================================================================

product_relationship = {}
if os.path.isfile("{}product_relationship.json".format(dir_path)):
    with open("{}product_relationship.json".format(dir_path), 'r') as fp:
        product_relationship = json.load(fp)
product_relationship = {int(k): int(v) for k, v in
                        product_relationship.items()}


# ORDER ITEMS
# =============================================================================

if config.ORDERS:
    src_order_id = create_custom_field(dest_infusionsoft,
                                       'Source App Order ID',
                                       'Job')['Name']

    order_relationship = {}
    for order in get_table(
            dest_infusionsoft,
            'Job',
            {src_order_id: "_%"},
            ['Id', src_order_id]):
        if isinstance(order, str):
            break
        order_relationship[int(order[src_order_id])] = order['Id']

    order_items = get_table(src_infusionsoft, 'OrderItem')
    invoice_items = get_table(src_infusionsoft, 'InvoiceItem')
    invoice_amounts = {}
    for ii in invoice_items:
        invoice_amounts[ii['OrderItemId']] = ii['InvoiceAmt']

    with open("{}order_items.csv".format(dir_path),
              'w',
              newline='') as csvfile:
        fieldnames = ['OrderId',
                      'ProductId',
                      'ItemType',
                      'ItemName',
                      'ItemDescription',
                      'Qty',
                      'PricePerUnit',
                      'Notes']
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()

        for item in order_items:
            if not order_relationship.get(item['OrderId']):
                continue
            item['OrderId'] = order_relationship[item['OrderId']]
            if not product_relationship.get(item.get('ProductId')):
                continue
            item['ProductId'] = product_relationship[item['ProductId']]
            item['PricePerUnit'] = invoice_amounts[item['Id']] / item['Qty']
            writer.writerow(item)


# PAYMENTS
# =============================================================================
    payments = get_table(src_infusionsoft, 'Payment')
    src_invoices = get_table(src_infusionsoft, 'Invoice')
    src_inv_rel = {}
    for invoice in src_invoices:
        src_inv_rel[invoice['JobId']] = invoice['Id']

    dest_invoices = get_table(dest_infusionsoft, 'Invoice')
    dest_inv_rel = {}
    for invoice in dest_invoices:
        dest_inv_rel[invoice['JobId']] = invoice['Id']

    invoice_relationship = {}
    for key, value in src_inv_rel.items():
        if order_relationship.get(key):
            if dest_inv_rel.get(order_relationship.get(key)):
                invoice_relationship[value] = dest_inv_rel.get(
                    order_relationship.get(key))

    with open("{}order_payments.csv".format(dir_path),
              'w',
              newline='') as csvfile:
        fieldnames = ['InvoiceId',
                      'PayDate',
                      'PayType',
                      'PayAmt',
                      'PayNote']
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()

        for payment in payments:
            try:
                payment['InvoiceId'] = int(payment['InvoiceId'])
            except ValueError:
                continue
            if not invoice_relationship.get(payment['InvoiceId']):
                continue
            payment['InvoiceId'] = invoice_relationship[payment['InvoiceId']]
            payment = convert_dict_dates_to_string(payment)
            writer.writerow(payment)


# ZIPFILE
# =============================================================================

    # Generate ZIP file for all csvs created, then delete the CSVs
    zipf = zipfile.ZipFile("{}{}_to_{}_step3.zip".format(
        dir_path,
        config.SOURCE_APPNAME,
        config.DESTINATION_APPNAME), 'w')

    for name in glob.glob("{}*.csv".format(dir_path)):
        zipf.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
        try:
            os.remove(name)
        except OSError:
            pass
else:
    print("Orders weren't selected in config.py")
