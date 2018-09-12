KEY = 'nndwt7ass8w95kqfgh2utw9h'
SECRET = 'fWew3CY7zp'
FTP_PASS = 'Furinkazan6'

CF_FORM_ID = {
  'Contact': -1,
  'Affiliate': -3,
  'Lead': -4,
  'ContactAction': -5,
  'Company': -6,
  'Job': -9,
  'Subscription': -10
}

DATATYPES = {
  1: 'Phone',
  2: 'SSN',
  3: 'Currency',
  4: 'Percent',
  5: 'State',
  6: 'YesNo',
  7: 'Year',
  8: 'Month',
  9: 'DayOfWeek',
  10: 'Name',
  11: 'NumberDecimal',
  12: 'Number',
  13: 'Date',
  14: 'DateTime',
  15: 'Text',
  16: 'TextArea',
  17: 'MultiSelect',
  18: 'Website',
  19: 'Email',
  20: 'Radio',
  21: 'Select',
  22: 'User',
  23: 'Drilldown'
}

FIELDS = {
    'ActionSequence': ['Id',
                       'TemplateName',
                       'VisibleToTheseUsers'],
    'AffResource': ['Id',
                    'Notes',
                    'ProgramIds',
                    'ResourceHREF',
                    'ResourceHTML',
                    'ResourceOrder',
                    'ResourceType',
                    'Title'],
    'Affiliate': ['AffCode',
                  'AffName',
                  'ContactId',
                  'DefCommissionType',
                  'Id',
                  'LeadAmt',
                  'LeadCookieFor',
                  'LeadPercent',
                  'NotifyLead',
                  'NotifySale',
                  'ParentId',
                  'Password',
                  'PayoutType',
                  'SaleAmt',
                  'SalePercent',
                  'Status'],
    'CCharge': ['Amt',
                'ApprCode',
                'CCId',
                'Id',
                'MerchantId',
                'OrderNum',
                'PaymentGatewayId',
                'PaymentId',
                'RefNum'],
    'CProgram': ['Active',
                 'BillingType',
                 'DefaultCycle',
                 'DefaultFrequency',
                 'DefaultPrice',
                 'Description',
                 'Family',
                 'HideInStore',
                 'Id',
                 'LargeImage',
                 'ProductId',
                 'ProgramName',
                 'ShortDescription',
                 'Sku',
                 'Status',
                 'Taxable'],
    'Campaign': ['Id',
                 'Name',
                 'Status'],
    'CampaignStep': ['CampaignId',
                     'Id',
                     'StepStatus',
                     'StepTitle',
                     'TemplateId'],
    'Campaignee': ['Campaign',
                   'CampaignId',
                   'ContactId',
                   'Id',
                   'Status'],
    'Company': ['AccountId',
                'Address1Type',
                'Address2Street1',
                'Address2Street2',
                'Address2Type',
                'Address3Street1',
                'Address3Street2',
                'Address3Type',
                'Anniversary',
                'AssistantName',
                'AssistantPhone',
                'BillingInformation',
                'Birthday',
                'City',
                'City2',
                'City3',
                'Company',
                'CompanyID',
                'ContactNotes',
                'ContactType',
                'Country',
                'Country2',
                'Country3',
                'CreatedBy',
                'DateCreated',
                'Email',
                'EmailAddress2',
                'EmailAddress3',
                'Fax1',
                'Fax1Type',
                'Fax2',
                'Fax2Type',
                'FirstName',
                'Groups',
                'Id',
                'JobTitle',
                'LastName',
                'LastUpdated',
                'LastUpdatedBy',
                'MiddleName',
                'Nickname',
                'OwnerID',
                'Password',
                'Phone1',
                'Phone1Ext',
                'Phone1Type',
                'Phone2',
                'Phone2Ext',
                'Phone2Type',
                'Phone3',
                'Phone3Ext',
                'Phone3Type',
                'Phone4',
                'Phone4Ext',
                'Phone4Type',
                'Phone5',
                'Phone5Ext',
                'Phone5Type',
                'PostalCode',
                'PostalCode2',
                'PostalCode3',
                'ReferralCode',
                'SpouseName',
                'State',
                'State2',
                'State3',
                'StreetAddress1',
                'StreetAddress2',
                'Suffix',
                'Title',
                'Username',
                'Validated',
                'Website',
                'ZipFour1',
                'ZipFour2',
                'ZipFour3'],
    'Contact': ['AccountId',
                'Address1Type',
                'Address2Street1',
                'Address2Street2',
                'Address2Type',
                'Address3Street1',
                'Address3Street2',
                'Address3Type',
                'Anniversary',
                'AssistantName',
                'AssistantPhone',
                'BillingInformation',
                'Birthday',
                'City',
                'City2',
                'City3',
                'Company',
                'CompanyID',
                'ContactNotes',
                'ContactType',
                'Country',
                'Country2',
                'Country3',
                'CreatedBy',
                'DateCreated',
                'Email',
                'EmailAddress2',
                'EmailAddress3',
                'Fax1',
                'Fax1Type',
                'Fax2',
                'Fax2Type',
                'FirstName',
                'Groups',
                'Id',
                'JobTitle',
                'LastName',
                'LastUpdated',
                'LastUpdatedBy',
                'LeadSourceId',
                'Leadsource',
                'MiddleName',
                'Nickname',
                'OwnerID',
                'Password',
                'Phone1',
                'Phone1Ext',
                'Phone1Type',
                'Phone2',
                'Phone2Ext',
                'Phone2Type',
                'Phone3',
                'Phone3Ext',
                'Phone3Type',
                'Phone4',
                'Phone4Ext',
                'Phone4Type',
                'Phone5',
                'Phone5Ext',
                'Phone5Type',
                'PostalCode',
                'PostalCode2',
                'PostalCode3',
                'ReferralCode',
                'SpouseName',
                'State',
                'State2',
                'State3',
                'StreetAddress1',
                'StreetAddress2',
                'Suffix',
                'Title',
                'Username',
                'Validated',
                'Website',
                'ZipFour1',
                'ZipFour2',
                'ZipFour3'],
    'ContactAction': ['Accepted',
                      'ActionDate',
                      'ActionDescription',
                      'ActionType',
                      'CompletionDate',
                      'ContactId',
                      'CreatedBy',
                      'CreationDate',
                      'CreationNotes',
                      'EndDate',
                      'Id',
                      'IsAppointment',
                      'LastUpdated',
                      'LastUpdatedBy',
                      'ObjectType',
                      'OpportunityId',
                      'PopupDate',
                      'Priority',
                      'UserID'],
    'ContactGroup': ['GroupCategoryId',
                     'GroupDescription',
                     'GroupName',
                     'Id'],
    'ContactGroupAssign': ['Contact.Address1Type',
                           'Contact.Address2Street1',
                           'Contact.Address2Street2',
                           'Contact.Address2Type',
                           'Contact.Address3Street1',
                           'Contact.Address3Street2',
                           'Contact.Address3Type',
                           'Contact.Anniversary',
                           'Contact.AssistantName',
                           'Contact.AssistantPhone',
                           'Contact.BillingInformation',
                           'Contact.Birthday',
                           'Contact.City',
                           'Contact.City2',
                           'Contact.City3',
                           'Contact.Company',
                           'Contact.CompanyID',
                           'Contact.ContactNotes',
                           'Contact.ContactType',
                           'Contact.Country',
                           'Contact.Country2',
                           'Contact.Country3',
                           'Contact.CreatedBy',
                           'Contact.DateCreated',
                           'Contact.Email',
                           'Contact.EmailAddress2',
                           'Contact.EmailAddress3',
                           'Contact.Fax1',
                           'Contact.Fax1Type',
                           'Contact.Fax2',
                           'Contact.Fax2Type',
                           'Contact.FirstName',
                           'Contact.Groups',
                           'Contact.Id',
                           'Contact.JobTitle',
                           'Contact.LastName',
                           'Contact.LastUpdated',
                           'Contact.LastUpdatedBy',
                           'Contact.Leadsource',
                           'Contact.MiddleName',
                           'Contact.Nickname',
                           'Contact.OwnerID',
                           'Contact.Phone1',
                           'Contact.Phone1Ext',
                           'Contact.Phone1Type',
                           'Contact.Phone2',
                           'Contact.Phone2Ext',
                           'Contact.Phone2Type',
                           'Contact.Phone3',
                           'Contact.Phone3Ext',
                           'Contact.Phone3Type',
                           'Contact.Phone4',
                           'Contact.Phone4Ext',
                           'Contact.Phone4Type',
                           'Contact.Phone5',
                           'Contact.Phone5Ext',
                           'Contact.Phone5Type',
                           'Contact.PostalCode',
                           'Contact.PostalCode2',
                           'Contact.PostalCode3',
                           'Contact.ReferralCode',
                           'Contact.SpouseName',
                           'Contact.State',
                           'Contact.State2',
                           'Contact.State3',
                           'Contact.StreetAddress1',
                           'Contact.StreetAddress2',
                           'Contact.Suffix',
                           'Contact.Title',
                           'Contact.Website',
                           'Contact.ZipFour1',
                           'Contact.ZipFour2',
                           'Contact.ZipFour3',
                           'ContactGroup',
                           'ContactId',
                           'DateCreated',
                           'GroupId'],
    'ContactGroupCategory': ['CategoryDescription',
                             'CategoryName',
                             'Id'],
    'CreditCard': ['BillAddress1',
                   'BillAddress2',
                   'BillCity',
                   'BillCountry',
                   'BillName',
                   'BillState',
                   'BillZip',
                   'CardType',
                   'ContactId',
                   'Email',
                   'ExpirationMonth',
                   'ExpirationYear',
                   'FirstName',
                   'Id',
                   'Last4',
                   'LastName',
                   'MaestroIssueNumber',
                   'NameOnCard',
                   'PhoneNumber',
                   'ShipAddress1',
                   'ShipAddress2',
                   'ShipCity',
                   'ShipCompanyName',
                   'ShipCountry',
                   'ShipFirstName',
                   'ShipLastName',
                   'ShipMiddleName',
                   'ShipName',
                   'ShipPhoneNumber',
                   'ShipState',
                   'ShipZip',
                   'StartDateMonth',
                   'StartDateYear',
                   'Status'],
    'DataFormField': ['DataType',
                      'DefaultValue',
                      'FormId',
                      'GroupId',
                      'Id',
                      'Label',
                      'ListRows',
                      'Name',
                      'Values'],
    'DataFormGroup': ['Id',
                      'Name',
                      'TabId'],
    'DataFormTab': ['FormId',
                    'Id',
                    'TabName'],
    'EmailAddStatus': ['DateCreated',
                       'Email',
                       'Id',
                       'LastClickDate',
                       'LastOpenDate',
                       'LastSentDate',
                       'Type'],
    'Expense': ['ContactId',
                'DateIncurred',
                'ExpenseAmt',
                'ExpenseType',
                'Id',
                'TypeId'],
    'FileBox': ['ContactId',
                'Extension',
                'FileName',
                'FileSize',
                'Id',
                'Public'],
    'GroupAssign': ['Admin',
                    'GroupId',
                    'Id',
                    'UserId'],
    'Invoice': ['AffiliateId',
                'ContactId',
                'CreditStatus',
                'DateCreated',
                'Description',
                'Id',
                'InvoiceTotal',
                'InvoiceType',
                'JobId',
                'LastUpdated',
                'LeadAffiliateId',
                'PayPlanStatus',
                'PayStatus',
                'ProductSold',
                'PromoCode',
                'RefundStatus',
                'Synced',
                'TotalDue',
                'TotalPaid'],
    'InvoiceItem': ['CommissionStatus',
                    'DateCreated',
                    'Description',
                    'Discount',
                    'Id',
                    'InvoiceAmt',
                    'InvoiceId',
                    'LastUpdated',
                    'OrderItemId'],
    'InvoicePayment': ['Amt',
                       'Id',
                       'InvoiceId',
                       'LastUpdated',
                       'PayDate',
                       'PayStatus',
                       'PaymentId',
                       'SkipCommission'],
    'Job': ['ContactId',
            'DateCreated',
            'DueDate',
            'Id',
            'JobNotes',
            'JobRecurringId',
            'JobStatus',
            'JobTitle',
            'OrderStatus',
            'OrderType',
            'ProductId',
            'ShipCity',
            'ShipCompany',
            'ShipCountry',
            'ShipFirstName',
            'ShipLastName',
            'ShipMiddleName',
            'ShipPhone',
            'ShipState',
            'ShipStreet1',
            'ShipStreet2',
            'ShipZip',
            'StartDate'],
    'JobRecurringInstance': ['AutoCharge',
                             'DateCreated',
                             'Description',
                             'EndDate',
                             'Id',
                             'InvoiceItemId',
                             'RecurringId',
                             'StartDate',
                             'Status'],
    'Lead': ['AffiliateId',
             'ContactID',
             'CreatedBy',
             'DateCreated',
             'DateInStage',
             'EstimatedCloseDate',
             'Id',
             'IncludeInForecast',
             'LastUpdated',
             'LastUpdatedBy',
             'Leadsource',
             'MonthlyRevenue',
             'NextActionDate',
             'NextActionNotes',
             'Objection',
             'OpportunityNotes',
             'OpportunityTitle',
             'OrderRevenue',
             'ProjectedRevenueHigh',
             'ProjectedRevenueLow',
             'StageID',
             'StatusID',
             'UserID'],
    'LeadSource': ['CostPerLead',
                   'Description',
                   'EndDate',
                   'Id',
                   'LeadSourceCategoryId',
                   'Medium',
                   'Message',
                   'Name',
                   'StartDate',
                   'Status',
                   'Vendor'],
    'LeadSourceCategory': ['Description',
                           'Id',
                           'Name'],
    'LeadSourceExpense': ['Amount',
                          'DateIncurred',
                          'Id',
                          'LeadSourceId',
                          'LeadSourceRecurringExpenseId',
                          'Notes',
                          'Title'],
    'LeadSourceRecurringExpense': ['Amount',
                                   'EndDate',
                                   'Id',
                                   'LeadSourceId',
                                   'NextExpenseDate',
                                   'Notes',
                                   'StartDate',
                                   'Title'],
    'LinkedContactType': ['Id',
                          'MaxLinked',
                          'TypeName'],
    'MtgLead': ['ActualCloseDate',
                'ApplicationDate',
                'CreditReportDate',
                'DateAppraisalDone',
                'DateAppraisalOrdered',
                'DateAppraisalReceived',
                'DateRateLockExpires',
                'DateRateLocked',
                'DateTitleOrdered',
                'DateTitleReceived',
                'FundingDate',
                'Id'],
    'OrderItem': ['CPU',
                  'Id',
                  'ItemDescription',
                  'ItemName',
                  'ItemType',
                  'Notes',
                  'OrderId',
                  'PPU',
                  'ProductId',
                  'Qty',
                  'SubscriptionPlanId'],
    'PayPlan': ['AmtDue',
                'DateDue',
                'FirstPayAmt',
                'Id',
                'InitDate',
                'InvoiceId',
                'StartDate',
                'Type'],
    'PayPlanItem': ['AmtDue',
                    'AmtPaid',
                    'DateDue',
                    'Id',
                    'PayPlanId',
                    'Status'],
    'Payment': ['ChargeId',
                'Commission',
                'ContactId',
                'Id',
                'InvoiceId',
                'PayAmt',
                'PayDate',
                'PayNote',
                'PayType',
                'RefundId',
                'Synced',
                'UserId'],
    'Product': ['BottomHTML',
                'CityTaxable',
                'CountryTaxable',
                'DateCreated',
                'Description',
                'HideInStore',
                'Id',
                'InventoryLimit',
                'InventoryNotifiee',
                'IsPackage',
                'LargeImage',
                'LastUpdated',
                'NeedsDigitalDelivery',
                'ProductName',
                'ProductPrice',
                'Shippable',
                'ShippingTime',
                'ShortDescription',
                'Sku',
                'StateTaxable',
                'Status',
                'Taxable',
                'TopHTML',
                'Weight'],
    'ProductCategory': ['CategoryDisplayName',
                        'CategoryImage',
                        'CategoryOrder',
                        'Id',
                        'ParentId'],
    'ProductCategoryAssign': ['Id',
                              'ProductCategoryId',
                              'ProductId'],
    'ProductInterest': ['DiscountPercent',
                        'Id',
                        'ObjType',
                        'ObjectId',
                        'ProductId',
                        'ProductType',
                        'Qty',
                        'SubscriptionPlanId'],
    'ProductInterestBundle': ['BundleName',
                              'Description',
                              'Id'],
    'ProductOptValue': ['Id',
                        'IsDefault',
                        'Label',
                        'Name',
                        'OptionIndex',
                        'PriceAdjustment',
                        'ProductOptionId',
                        'Sku'],
    'ProductOption': ['AllowSpaces',
                      'CanContain',
                      'CanEndWith',
                      'CanStartWith',
                      'Id',
                      'IsRequired',
                      'Label',
                      'MaxChars',
                      'MinChars',
                      'Name',
                      'OptionType',
                      'Order',
                      'ProductId',
                      'TextMessage'],
    'RecurringOrder': ['AffiliateId',
                       'AutoCharge',
                       'BillingAmt',
                       'BillingCycle',
                       'CC1',
                       'CC2',
                       'ContactId',
                       'EndDate',
                       'Frequency',
                       'Id',
                       'LastBillDate',
                       'LeadAffiliateId',
                       'MaxRetry',
                       'MerchantAccountId',
                       'NextBillDate',
                       'NumDaysBetweenRetry',
                       'OriginatingOrderId',
                       'PaidThruDate',
                       'PaymentGatewayId',
                       'ProductId',
                       'ProgramId',
                       'PromoCode',
                       'Qty',
                       'ReasonStopped',
                       'ShippingOptionId',
                       'StartDate',
                       'Status',
                       'SubscriptionPlanId'],
    'RecurringOrderWithContact': ['AffiliateId',
                                  'AutoCharge',
                                  'BillingAmt',
                                  'BillingCycle',
                                  'CC1',
                                  'CC2',
                                  'City',
                                  'ContactId',
                                  'Country',
                                  'Email',
                                  'EmailAddress2',
                                  'EmailAddress3',
                                  'EndDate',
                                  'FirstName',
                                  'Frequency',
                                  'Id',
                                  'LastBillDate',
                                  'LastName',
                                  'LeadAffiliateId',
                                  'MaxRetry',
                                  'MerchantAccountId',
                                  'MiddleName',
                                  'NextBillDate',
                                  'Nickname',
                                  'NumDaysBetweenRetry',
                                  'OriginatingOrderId',
                                  'PaidThruDate',
                                  'PaymentGatewayId',
                                  'Phone1',
                                  'Phone1Ext',
                                  'Phone1Type',
                                  'Phone2',
                                  'Phone2Ext',
                                  'Phone2Type',
                                  'PostalCode',
                                  'ProductId',
                                  'ProgramId',
                                  'PromoCode',
                                  'Qty',
                                  'ReasonStopped',
                                  'RecurringOrderId',
                                  'ShippingOptionId',
                                  'SpouseName',
                                  'StartDate',
                                  'State',
                                  'Status',
                                  'StreetAddress1',
                                  'StreetAddress2',
                                  'SubscriptionPlanId',
                                  'Suffix',
                                  'Title',
                                  'ZipFour1'],
    'Referral': ['AffiliateId',
                 'ContactId',
                 'DateExpires',
                 'DateSet',
                 'IPAddress',
                 'Id',
                 'Info',
                 'Source',
                 'Type'],
    'SavedFilter': ['FilterName',
                    'Id',
                    'ReportStoredName',
                    'UserId'],
    'SocialAccount': ['AccountName',
                      'AccountType',
                      'ContactId',
                      'DateCreated',
                      'Id',
                      'LastUpdated'],
    'Stage': ['Id',
              'StageName',
              'StageOrder',
              'TargetNumDays'],
    'StageMove': ['CreatedBy',
                  'DateCreated',
                  'Id',
                  'MoveDate',
                  'MoveFromStage',
                  'MoveToStage',
                  'OpportunityId',
                  'PrevStageMoveDate',
                  'UserId'],
    'Status': ['Id',
               'StatusName',
               'StatusOrder',
               'TargetNumDays'],
    'SubscriptionPlan': ['Active',
                         'Cycle',
                         'Frequency',
                         'Id',
                         'NumberOfCycles',
                         'PlanPrice',
                         'PreAuthorizeAmount',
                         'ProductId',
                         'Prorate'],
    'Template': ['Categories',
                 'Id',
                 'PieceTitle',
                 'PieceType'],
    'Ticket': ['CloseDate',
               'ContactId',
               'CreatedBy',
               'DateCreated',
               'DateInStage',
               'DevId',
               'FolowUpDate',
               'HasCustomerCalled',
               'Id',
               'IssueId',
               'LastUpdated',
               'LastUpdatedBy',
               'Ordering',
               'Priority',
               'Stage',
               'Summary',
               'TargetCompletionDate',
               'TicketApplication',
               'TicketCategory',
               'TicketTitle',
               'TicketTypeId',
               'TimeSpent',
               'UserId'],
    'TicketStage': ['Id',
                    'StageName'],
    'TicketType': ['CategoryId',
                   'Id',
                   'Label'],
    'User': ['City',
             'Email',
             'EmailAddress2',
             'EmailAddress3',
             'FirstName',
             'GlobalUserId',
             'HTMLSignature',
             'Id',
             'LastName',
             'MiddleName',
             'Nickname',
             'Partner',
             'Phone1',
             'Phone1Ext',
             'Phone1Type',
             'Phone2',
             'Phone2Ext',
             'Phone2Type',
             'PostalCode',
             'Signature',
             'SpouseName',
             'State',
             'StreetAddress1',
             'StreetAddress2',
             'Suffix',
             'Title',
             'ZipFour1'],
    'UserGroup': ['Id',
                  'Name',
                  'OwnerId']
}
