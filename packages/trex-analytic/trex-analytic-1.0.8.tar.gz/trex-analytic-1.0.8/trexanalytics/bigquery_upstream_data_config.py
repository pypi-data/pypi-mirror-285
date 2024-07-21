'''
Created on 26 Jan 2021

@author: jacklok
'''
from trexanalytics.conf import UPSTREAM_UPDATED_DATETIME_FIELD_NAME, MERCHANT_DATASET, SYSTEM_DATASET
import uuid, logging  
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexanalytics.bigquery_table_template_config import REGISTERED_CUSTOMER_TEMPLATE, REGISTERED_MERCHANT_TEMPLATE, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE,\
    CUSTOMER_TRANSACTION_TEMPLATE, MERCHANT_CUSTOMER_REWARD_TEMPLATE,\
    MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE, MERCHANT_CUSTOMER_PREPAID_TEMPLATE 
from trexlib.utils.google.bigquery_util import default_serializable
from datetime import datetime, timedelta
from trexmodel.models.datastore.transaction_models import CustomerTransactionWithRewardDetails,\
    CustomerTransactionWithPrepaidDetails
from trexanalytics import conf
from trexmodel.models.datastore.ndb_models import convert_to_serializable_value
from trexmodel import program_conf 
from trexmodel.models.datastore.redeem_models import CustomerRedeemedItemUpstream

__REGISTERED_MERCHANT_TEMPLATE_UPSTREAM_SCHEMA = { 
                                                'MerchantKey'           : 'key_in_str',
                                                'CompanyName'           : 'company_name',
                                                'RegisteredDateTime'    : 'registered_datetime',
                                            }

__REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA = {
                                                'UserKey'           : 'registered_user_acct_key',
                                                'CustomerKey'       : 'key_in_str',
                                                'MerchantKey'       : 'registered_merchant_acct_key',
                                                'DOB'               : 'birth_date',
                                                'Gender'            : 'gender',
                                                'MobilePhone'       : 'mobile_phone',
                                                'Email'             : 'email',
                                                'MobileAppInstall'  : 'mobile_app_installed',
                                                'RegisteredDateTime': 'registered_datetime',
                                                'RegisteredOutlet'  : 'registered_outlet_key',
                                                }

__MERCHANT_REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA = {
                                                        'UserKey'           : 'registered_user_acct_key',
                                                        'CustomerKey'       : 'key_in_str',
                                                        'DOB'               : 'birth_date',
                                                        'Gender'            : 'gender',
                                                        'MobilePhone'       : 'mobile_phone',
                                                        'Email'             : 'email',
                                                        'MobileAppInstall'  : 'mobile_app_installed',
                                                        'RegisteredDateTime': 'registered_datetime',
                                                        'RegisteredOutlet'  : 'registered_outlet_key',
                                                        }


__CUSTOMER_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'transact_user_acct_key',
                                            "CustomerKey"           : 'transact_customer_key',
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "InvoiceId"             : 'invoice_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "IsSalesTransaction"    : 'is_sales_transaction',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__CUSTOMER_REWARD_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "CustomerKey"           : 'transact_customer_key',
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "RewardFormat"          : 'reward_format',
                                            "RewardAmount"          : 'reward_amount',
                                            "ExpiryDate"            : 'expiry_date',
                                            "RewardFormatKey"       : 'reward_format_key',
                                            "RewardedDateTime"      : 'rewarded_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__CUSTOMER_PREPAID_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "CustomerKey"           : 'transact_customer_key',
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "TopupAmount"           : 'topup_amount',
                                            "PrepaidAmount"         : 'prepaid_amount',
                                            "TopupDateTime"         : 'topup_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__CUSTOMER_REDEMPTION_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "CustomerKey"           : 'customer_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "RedeemedOutlet"        : 'redeemed_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "RedeemedAmount"        : 'redeemed_amount',
                                            "RewardFormat"          : 'reward_format',
                                            "VoucherKey"            : 'voucher_key',
                                            "RedeemedDateTime"      : 'redeemed_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }


upstream_schema_config = {
                            REGISTERED_MERCHANT_TEMPLATE            : __REGISTERED_MERCHANT_TEMPLATE_UPSTREAM_SCHEMA,
                            REGISTERED_CUSTOMER_TEMPLATE            : __REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_REGISTERED_CUSTOMER_TEMPLATE   : __MERCHANT_REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA,
                            CUSTOMER_TRANSACTION_TEMPLATE           : __CUSTOMER_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_CUSTOMER_REWARD_TEMPLATE       : __CUSTOMER_REWARD_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_CUSTOMER_PREPAID_TEMPLATE      : __CUSTOMER_PREPAID_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE   : __CUSTOMER_REDEMPTION_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            }

logger = logging.getLogger('upstream')

def __create_upstream(upstream_entity, merchant_acct, upstream_template, dataset_name, table_name, streamed_datetime=None, **kwargs):
    upstream_json = {}
    if upstream_entity:
        schema = upstream_schema_config.get(upstream_template)
        for upstrem_field_name, attr_name in schema.items():
            upstream_json[upstrem_field_name] = default_serializable(getattr(upstream_entity, attr_name))
        
        logger.debug('upstream_entity classname=%s', upstream_entity.__class__.__name__)
    
    if streamed_datetime is None:
        streamed_datetime = datetime.utcnow()
            
    upstream_json['Key'] = uuid.uuid1().hex
    
    if (UPSTREAM_UPDATED_DATETIME_FIELD_NAME in upstream_json) == False:
        upstream_json[UPSTREAM_UPDATED_DATETIME_FIELD_NAME] = default_serializable(streamed_datetime)
    
    #year = update_datetime.yeaar
    
    #dataset_with_year_prefix = '{year}_{dataset}'.format(year=year, dataset=dataset_name)
    
    for key, value in kwargs.items():
        upstream_json[key] = convert_to_serializable_value(value, datetime_format='%Y-%m-%d %H:%M:%S', date_format='%Y-%m-%d', time_format='%H:%M:%S')
    
    logger.debug('-------------------------------------------------')
    logger.debug('dataset_name=%s', dataset_name)
    logger.debug('table_name=%s', table_name)
    logger.debug('upstream_template=%s', upstream_template)
    logger.debug('upstream_json=%s', upstream_json)
    logger.debug('-------------------------------------------------')
    UpstreamData.create(merchant_acct, dataset_name, table_name, upstream_template, [upstream_json])
    

def create_registered_customer_upstream_for_system(customer):
    streamed_datetime = datetime.utcnow()
    
    table_name          = REGISTERED_CUSTOMER_TEMPLATE
    final_table_name    = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    merchant_acct       = customer.registered_merchant_acct
    __create_upstream(customer, merchant_acct, REGISTERED_CUSTOMER_TEMPLATE, SYSTEM_DATASET, final_table_name, streamed_datetime=streamed_datetime)

def create_merchant_registered_customer_upstream_for_merchant(customer):
    streamed_datetime = datetime.utcnow()
    
    table_name          = MERCHANT_REGISTERED_CUSTOMER_TEMPLATE
    merchant_acct       = customer.registered_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    
    __create_upstream(customer, merchant_acct, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE, MERCHANT_DATASET, final_table_name, streamed_datetime=streamed_datetime)    
    
def create_merchant_sales_transaction_upstream_for_merchant(transaction_details, streamed_datetime=None):
    return create_merchant_customer_transaction_upstream_for_merchant(transaction_details, streamed_datetime=streamed_datetime)

def create_merchant_customer_transaction_upstream_for_merchant(transaction_details, streamed_datetime=None):
    if streamed_datetime is None:
        streamed_datetime     = transaction_details.transact_datetime
        
    table_name          = CUSTOMER_TRANSACTION_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    
    __create_upstream(transaction_details, merchant_acct, CUSTOMER_TRANSACTION_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=streamed_datetime, Reverted=False, RevertedDateTime=None)
    
def create_merchant_customer_transaction_reverted_upstream_for_merchant(transaction_details, reverted_datetime):
    partition_datetime = transaction_details.transact_datetime
        
    table_name          = CUSTOMER_TRANSACTION_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, partition_datetime.strftime('%Y%m%d'))
    
    __create_upstream(transaction_details, merchant_acct, CUSTOMER_TRANSACTION_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=reverted_datetime, Reverted=True, RevertedDateTime=reverted_datetime)    

def create_merchant_customer_reward_upstream_for_merchant(transaction_details, reward_details, streamed_datetime=None):
    if streamed_datetime is None:
        streamed_datetime = datetime.utcnow()
    
    table_name          = MERCHANT_CUSTOMER_REWARD_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    
    transaction_details_with_reward_details = CustomerTransactionWithRewardDetails(transaction_details, reward_details)
    
    updated_datetime = transaction_details.transact_datetime
    
    __create_upstream(transaction_details_with_reward_details, merchant_acct, MERCHANT_CUSTOMER_REWARD_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=streamed_datetime, Reverted=False, RevertedDateTime=None,
                      UpdatedDateTime=updated_datetime,
                      )
    
def create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, prepaid_details, streamed_datetime=None):
    if streamed_datetime is None:
        streamed_datetime = datetime.utcnow()
    
    table_name          = MERCHANT_CUSTOMER_PREPAID_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    
    transaction_details_with_prepaid_details = CustomerTransactionWithPrepaidDetails(transaction_details, prepaid_details)
    
    __create_upstream(transaction_details_with_prepaid_details, merchant_acct, MERCHANT_CUSTOMER_PREPAID_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=streamed_datetime, Reverted=False, RevertedDateTime=None)    
    
def create_merchant_customer_reward_reverted_upstream_for_merchant(transaction_details, reward_details, reverted_datetime):
    partition_datetime = transaction_details.transact_datetime
    
    
    table_name          = MERCHANT_CUSTOMER_REWARD_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, partition_datetime.strftime('%Y%m%d'))
    
    transaction_details_with_reward_details = CustomerTransactionWithRewardDetails(transaction_details, reward_details)
    
    updated_datetime = transaction_details.reverted_datetime

    __create_upstream(transaction_details_with_reward_details, merchant_acct, MERCHANT_CUSTOMER_REWARD_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=reverted_datetime, Reverted=True, RevertedDateTime=reverted_datetime,
                      UpdatedDateTime=updated_datetime,
                      )    


def create_merchant_customer_prepaid_reverted_upstream_for_merchant(transaction_details, prepaid_details, reverted_datetime):
    partition_datetime = transaction_details.transact_datetime
    
    
    table_name          = MERCHANT_CUSTOMER_PREPAID_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, partition_datetime.strftime('%Y%m%d'))
    
    transaction_details_with_prepaid_details = CustomerTransactionWithPrepaidDetails(transaction_details, prepaid_details)
    
    __create_upstream(transaction_details_with_prepaid_details, merchant_acct, MERCHANT_CUSTOMER_PREPAID_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=reverted_datetime, Reverted=True, RevertedDateTime=reverted_datetime) 

def create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, streamed_datetime=None, reverted=False, reverted_datetime=None):
    if streamed_datetime is None:
        streamed_datetime = datetime.utcnow()
    
    logger.debug('customer_redemption.merchant_acct=%s', customer_redemption.merchant_acct)
    
    table_name          = MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE
    merchant_acct       = customer_redemption.redeemed_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    
    upstream_data_list = []
    
    if customer_redemption.reward_format in (program_conf.REWARD_FORMAT_POINT, program_conf.REWARD_FORMAT_STAMP, program_conf.REWARD_FORMAT_PREPAID):
        upstream_data_list.append(customer_redemption.to_upstream_info())
    
    elif customer_redemption.reward_format == program_conf.REWARD_FORMAT_VOUCHER:
        upstream_data_list.extend(customer_redemption.to_voucher_upstream_info_list())
            
    for upstream_data in upstream_data_list:
        updated_datetime = customer_redemption.redeemed_datetime
        if reverted:
            updated_datetime = customer_redemption.reverted_datetime
            
        __create_upstream(upstream_data, merchant_acct, MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE, MERCHANT_DATASET, final_table_name, 
                      streamed_datetime=streamed_datetime, Reverted=reverted, RevertedDateTime=reverted_datetime, 
                      UpdatedDateTime=updated_datetime
                      )
    
def create_merchant_customer_redemption_reverted_upstream_for_merchant(redemption_details):
    create_merchant_customer_redemption_upstream_for_merchant(redemption_details, 
                                                              streamed_datetime=redemption_details.redeemed_datetime, 
                                                              reverted=True, 
                                                              reverted_datetime=redemption_details.reverted_datetime)     
