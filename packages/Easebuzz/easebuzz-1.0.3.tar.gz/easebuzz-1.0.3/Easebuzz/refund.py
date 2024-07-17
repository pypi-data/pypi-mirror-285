"""Module for raising refund againt a transaction
"""

from hashlib import sha512
import json
import re
import os
import traceback
import logging
import requests
from . import constant, utility

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


def initiate_refund(params, merchant_key, salt, env):
    """
    initiate_refund method refund amount and call display the refund page.

    Args:
        params (dict):  A dictionary containing refund-related parameters.
        merchant_key (str): The merchant key for authentication.
        salt (str): The salt for securing the payment process.
        env (str):  The environment (e.g., 'test' or 'production').

    Returns:
        dict : holds the holds the refund array.
    """
    try:
        result = _refund(params, merchant_key, salt, env)
        return result

    except Exception as _:
        traceback.print_exc()
        logger.error("#######Error on refund:initiate_refund#######")
        return ({"status": False, "reason": 'Exception occured'})
    

def _refund(params, merchant_key, salt, env):
    """
    _refund method use for initiate refund.

    Args:
        params (dict):  A dictionary containing refund-related parameters.
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
    if isinstance(argument_validation,dict) and argument_validation['status'] == 0:
        return argument_validation

    # push merchant key into params dictionary.
    params._mutable = True
    params['key'] = merchant_key

    # remove white space, htmlentities(converts characters to HTML entities), prepared posted_array
    posted_array = utility.remove_space_and_prepare_post_array(params)

    # empty validation
    empty_validation = _empty_validation(posted_array, salt)
    if empty_validation is not True:
        return empty_validation

    # check refund amount should be in floating formate
    if re.match(constant.AMOUNT_REGEX, posted_array['refund_amount']):
        posted_array['refund_amount'] = float(posted_array['refund_amount'])

    # check amount should be in floating formate
    if re.match(constant.AMOUNT_REGEX, posted_array['amount']):
        posted_array['amount'] = float(posted_array['amount'])

    # type validation
    type_validation = _type_validation(posted_array)
    if type_validation is not True:
        return type_validation

    # email validation
    email_validation = utility.email_validation(posted_array['email'])
    if email_validation is not True:
        return email_validation

    # get URL based on environment like (env = 'test' or env = 'prod')
    refund_url = utility.get_url(env)

    # process to start refund
    refund_result = _refund_payment(posted_array, salt, refund_url)

    return refund_result


def _empty_validation(params, salt):
    """
    _empty_validation method check empty validation for Mandatory Parameters.

    Args:
        params (dict): holds the all request.POST data
        salt (str): holds the merchant salt key.

    Returns:
        Boolean: True - all params Mandatory parameters is not empty.
        Dict : with status and data - params parameters or salt are empty.
    """
    empty_value = False

    if not params['key']:
        empty_value = 'Merchant Key'

    if not params['txnid']:
        empty_value = 'Transaction ID'

    if not params['refund_amount']:
        empty_value = 'Refund Amount'

    if not params['amount']:
        empty_value = 'Paid Amount'

    if not params['email']:
        empty_value ='Email ID'

    if not params['phone']:
        empty_value = 'Phone'

    if not salt:
        empty_value = 'Merchant Salt Key'

    if empty_value is not False:
        return {
            'status' : 0,
            'data' : 'Mandatory Parameter '+ empty_value +' can not empty'
        }

    return True


def _type_validation(params):
    """
    _type_validation method check type validation for field.

    Args:
        params (dict):  holds the all request.POST data.
        salt (str): holds the merchant salt key.
        env (str): holds the environment.

    Returns:
        boolean True: - all params parameters type are correct.
        dict : with status = 0 and data - params parameters type mismatch.
    """
    type_value = False

    if not isinstance(params['key'], str):
        type_value = "Merchant Key should be string"

    if not isinstance(params['txnid'], str):
        type_value = "Transaction ID should be string"

    if not isinstance(params['phone'], str):
        type_value = "Phone Number should be number"

    if not isinstance(params['refund_amount'], float):
        type_value = "The refund amount should float up to two or one decimal."

    if not isinstance(params['amount'], float):
        type_value = "The paid amount should float up to two or one decimal."

    if not isinstance(params['email'], str):
        type_value = "Email ID should be string"

    if type_value is not False:
        return {
           'status' : 0,
            'data' : type_value
        }

    return True


def _refund_payment(params_array, salt_key, url):
    """
    _refund_payment method initiate refund payment.

    Args:
        params_array (dict): holds all form data with merchant key, transaction id etc.
        salt_key (str): holds the merchant salt key.
        url (str): holds the url based in env( environment type env = 'test' or env = 'prod')

    Returns:
        dict: status and data - holds the details.
              status = 0 means error.
              status = 1 means success.
    """
    hash_key = None

    # generate hash key and push into params array.
    hash_key = _get_hash_key(params_array, salt_key)
    params_array['hash'] = hash_key

    # requests call for retrive transaction
    request_result = requests.post(url + 'transaction/v1/refund', params_array)

    return json.loads(request_result.content)


def _get_hash_key(posted, salt_key):
    """
    _get_hash_key method generate Hash key based on the API call (initiatePayment API).
    hash format (hash sequence) :
        hash = key|txnid|amount|refund_amount|email|phone|salt

    Args:
        posted (dict): holds the passed array.
        salt_key (str): holds merchant salt key.

    Returns:
        str: holds the generated hash key
    """
    hash_string = ""
    hash_sequence = "key|txnid|amount|refund_amount|email|phone"

    hash_sequence_array = hash_sequence.split("|")

    for value in hash_sequence_array:
        if value in posted:
            hash_string += str(posted[value])
        else:
            hash_string += ""
        hash_string += "|"

    hash_string += salt_key

    return  sha512(hash_string.encode('utf-8')).hexdigest().lower()
