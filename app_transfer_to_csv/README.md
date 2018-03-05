INSTRUCTIONS
============

1. Fill in the source and destination appnames and API keys found in config.py
2. Indicate which of the items need to be transferred by setting the individual settings in config.py to True or False accordingly (must be capitalized)
3. Check the Additional settings in config.py for things that may aid you in importing the CSVs
4. If you are transferring any of the below, create a custom field tab in the destination app, so the API can create custom fields
  1. Contacts
  2. Companies
  3. Contact Actions
  4. Opportunities
  5. Orders
5. Run step1 in the terminal
  1. Change directory into 'app_transfer_to_csv/'
  2. Run 'python step1.py'
6. Grab the ZIP file that's created in app_transfer_to_csv/output' for step1 and import all things for step1
7. Run step2 in the terminal (same as #5)
8. Import step2 (same as #6)
9. Run step3 in the terminal (same as #5)
10. Import step3 (same as #6)

NOTE: You can tell which things are transferred by step in the config.py file.  
If the customer doesn't need anything from step 3 or step 2, you can skip running those steps.