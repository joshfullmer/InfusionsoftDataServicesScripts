# SUMMARY

This application will transfer all data from a free trial app to a paid app.
It will automatically transfer Contacts, Tags, and Actions(Tasks, Notes, Appts)

# INSTRUCTIONS

1. Create Custom Field tabs for Contact and ContactAction
    1. This is crucial.  This app won't run if this step is skipped.
2. Add the source appname and apikey, and destination appname and apikey in 'free_app_data_transfer.py'
3. If we are transferring only contacts with a certain ID, include that in the CONTACTS_WITH_TAG_IDS variable, comma separated
4. Run the application in the terminal.