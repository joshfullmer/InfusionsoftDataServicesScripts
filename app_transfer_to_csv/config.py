"""
This contains all of the choices and settings for the
entire app_transfer_to_csv application

"""

from constants import QJ154_APIKEY, TE361_APIKEY

SOURCE_APPNAME = 'qj154'
SOURCE_API_KEY = QJ154_APIKEY
DESTINATION_APPNAME = 'te361'
DESTINATION_API_KEY = TE361_APIKEY

# Step 1
CONTACTS = True
COMPANIES = True
TAGS = True
PRODUCTS = True

# Step 2
NOTES = True
TASKS_APPOINTMENTS = True
OPPORTUNITIES = True
ORDERS = True
SUBSCRIPTIONS = True

# Step 3
# ORDER ITEMS
# ORDER PAYMENTS

# ADDITIONAL SETTINGS
# ===================

# This setting allows you to provide a list of tag IDs. The app will only
# add contacts with that tag ID to the CSV for importing
CONTACTS_WITH_TAG_IDS = []

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
