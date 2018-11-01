"""
This contains all of the choices and settings for the
entire app_transfer_to_csv application

"""

from constants import QJ154_APIKEY, TE361_APIKEY

SOURCE_APPNAME = 'bb253'
SOURCE_API_KEY = '87903b26fc2aaeeb6dbf33c3d2384cb6'
DESTINATION_APPNAME = 'vq581'
DESTINATION_API_KEY = '00607cf3ef86f1941fb97d46f09e915e'

# Step 1
CONTACTS = True
COMPANIES = False
TAGS = True
PRODUCTS = True

# Step 2
NOTES = True
TASKS_APPOINTMENTS = True
OPPORTUNITIES = False
ORDERS = True
SUBSCRIPTIONS = False

# Step 3
# ORDER ITEMS
# ORDER PAYMENTS

# ADDITIONAL SETTINGS
# ===================

# This setting allows you to provide a list of tag IDs. The app will only
# add contacts with that tag ID to the CSV for importing
CONTACTS_WITH_TAG_IDS = [734,721,719,717,715,713,707,699,697,622,612,610,608,598,594,590,577,575,573,571,569,541,245,243,241,205,187,185,183,179,167]

# Set to False if you are going to create custom fields yourself.  This is
# used when the customer doesn't want all custom fields moved.
# NOTE: This applies to company custom fields as well
CREATE_CUSTOM_FIELDS = True

# Set to True if you want a Tag CSV to import instead of automatically creating
# tags through API
TAGS_CSV = False

# Feed the app a list of Product IDs to skip transferring, in case the customer
# doesn't want all of the products transferred.
# Comma-separated list of IDs.
PRODUCTS_TO_SKIP = []

# This will shift the next bill dates of subscriptions if the customer
# needs time in their old app to cancel subscriptions.  No subscriptions will
# bill before the cutoff date you specify below
# Format: "YYYY/MM/DD"
SUBSCRIPTION_CUT_OFF_DATE = ''
