"""
Only used to clear out the sandbox to run app data transfer again
"""

from infusionsoft.library import Infusionsoft

from constants import TE361_APIKEY
from infusionsoft_actions import delete_table

DESTINATION_APPNAME = 'te361'
DESTINATION_API_KEY = TE361_APIKEY

infusionsoft = Infusionsoft(DESTINATION_APPNAME, DESTINATION_API_KEY)

delete_table(infusionsoft, 'Contact')
delete_table(infusionsoft, 'ContactGroup')
delete_table(infusionsoft, 'ContactGroupCategory')
delete_table(infusionsoft, 'ContactAction')
