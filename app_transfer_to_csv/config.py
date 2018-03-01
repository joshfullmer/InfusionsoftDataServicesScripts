from constants import QJ154_APIKEY, TE361_APIKEY

SOURCE_APPNAME = 'qj154'
SOURCE_API_KEY = QJ154_APIKEY
DESTINATION_APPNAME = 'te361'
DESTINATION_API_KEY = TE361_APIKEY

CONTACTS = True
CONTACTS_WITH_TAG_IDS = []
COMPANIES = True
# Set to False if you are going to create custom fields yourself.  This is
# used when the customer doesn't want all custom fields moved.
#
# This applies to company custom fields as well
CREATE_CUSTOM_FIELDS = True
TAGS = True
# Set to True if you want a Tag CSV to import instead of automatically creating
# tags through API
TAGS_CSV = False
PRODUCTS = True
# Feed the app a list of Product IDs to skip transferring, in case the customer
# doesn't want all of the products transferred.
# Comma-separated list of IDs.
PRODUCTS_TO_SKIP = []
CONTACT_ACTIONS = True
OPPORTUNITIES = True
ORDERS = True
SUBSCRIPTIONS = True
SUBSCRIPTION_CUT_OFF_DATE = "2018/01/01"
