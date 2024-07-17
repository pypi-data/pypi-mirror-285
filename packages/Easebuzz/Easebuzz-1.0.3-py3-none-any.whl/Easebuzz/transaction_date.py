"""Module for transaction details 
"""
from hashlib import sha512
import json
import os
import traceback
import logging
import requests
from . import utility

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
formate = logging.Formatter("%(asctime)s -- %(name)s -- %(message)s")
log_file = os.environ.get('EASEBUZZ_LOG_FILE', '/var/log/easebuzz_log.txt')
if os.path.exists(log_file):
    fh = logging.FileHandler(log_file)
else:
    fh = logging.FileHandler("logss.txt")
fh.setFormatter(formate)
logger.addHandler(fh)


def get_transactions_by_date(params, merchant_key, salt, env):
    """
    get_transactions_by_date method use for transaction based on date

    Args:
        params (dict):  A dictionary containing transaction-related parameters.
        merchant_key (str): The merchant key for authentication.
        salt (str): The salt for securing the payment process.
        env (str):  The environment (e.g., 'test' or 'production').

    Returns:
        dict : holds the all transaction details based on date.
    """
    try:
        result = _date_transaction(params, merchant_key, salt, env)
        return result

    except Exception as _:
        traceback.print_exc()
        logging.error("#######Error on transaction_date:get_transactions_by_date#######")
        return ({"status": False, "reason": 'Exception occurred'})


def _date_transaction(params, merchant_key, salt, env):
    """
    _date_transaction method use for get all transaction details based on date.

    Args:
        params (dict):  A dictionary containing transaction-related parameters.
        merchant_key (str): The merchant key for authentication.
        salt (str): The salt for securing the payment process.
        env (str):  The environment (e.g., 'test' or 'production').

    Returns:
        dict: pay_result - holds the response with status and data.
                           return integer status = 1 successful.
                           return integer status = 0 error.
    """
    posted_array = {}

    # argument validation
    argument_validation = utility.check_argument_validation(params, merchant_key, salt, env)
    if isinstance(argument_validation, dict) and argument_validation['status'] == 0:
        return argument_validation

    # push merchant key into params dictionary.
    params._mutable = True
    params['merchant_key'] = merchant_key

    # remove white space, htmlentities(converts characters to HTML entities), prepared posted_array
    posted_array = utility.remove_space_and_prepare_post_array(params)

    # empty validation
    empty_validation = _empty_validation(posted_array)
    if empty_validation is not True:
        return empty_validation

    # email validation
    email_validation = utility.email_validation(posted_array['merchant_email'])
    if email_validation is not True:
        return email_validation

    # get URL based on environment like (env = 'test' or env = 'prod')
    transaction_url = utility.get_url(env)

    # process to start get transaction details
    date_transaction_result = _get_date_transaction(posted_array, salt, transaction_url)

    return date_transaction_result


def _empty_validation(params):
    """
    _empty_validation method check empty validation for Mandatory Parameters.

    Args:
        params (dict): holds the all request.POST data
        salt (_type_): holds the merchant salt key.

    Returns:
        Boolean: True - all params Mandatory parameters is not empty.
        Dict : with status and data - params parameters or salt are empty.
    """

    empty_value = False

    if not params['merchant_key']:
        empty_value = "Merchant Key can not empty"

    if not params['merchant_email']:
        empty_value = "Merchant Email can not empty"

    if not params['transaction_date']:
        empty_value = "Transaction date can not empty"

    if empty_value is not False:
        return {
            'status' : 0,
            'data' : empty_value
        }

    return True


def _get_date_transaction(params_array, salt_key, url):
    """
    _get_date_transaction method get all transaction details based on date.

    Args:
        params_array (dict): holds all form data with merchant key, transaction id etc.
        salt_key (str): holds the merchant salt key.
        url (str): holds the url based in environment type env = 'test' or env = 'prod'

    Returns:
        dict: status and data - holds the details of all transaction on a date.
              status = 0 means error.
              status = 1 means success.
    """
    hash_key = None

    # generate hash key and push into params array.
    hash_key = _get_hash_key(params_array, salt_key)
    params_array['hash'] = hash_key

    # requests call for retrive transaction based on date
    request_result = requests.post(url + 'transaction/v1/retrieve/date', params_array)
    temp_result = json.loads(request_result.content)

    return temp_result


def _get_hash_key(posted, salt_key):
    """
    _get_hash_key method generate Hash key based on the API call (initiatePayment API).
    hash format (hash sequence) :
        hash = merchant_key|merchant_email|transaction_date|salt
    Args:
        posted (dict): holds the passed array.
        salt_key (str): holds merchant salt key.

    Returns:
        str: holds the generated hash key
    """
    hash_string = ""
    hash_sequence = "merchant_key|merchant_email|transaction_date"

    hash_sequence_array = hash_sequence.split("|")

    for value in hash_sequence_array:
        if value in posted:
            hash_string += str(posted[value])
        else:
            hash_string += ""
        hash_string += "|"

    hash_string += salt_key

    return  sha512(hash_string.encode('utf-8')).hexdigest().lower()
