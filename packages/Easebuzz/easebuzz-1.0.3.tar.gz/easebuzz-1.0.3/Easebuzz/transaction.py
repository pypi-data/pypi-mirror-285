""" Module for trasanction info
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


def get_transaction_details(params, merchant_key, salt, env):
    """Get transaction details.

    Args:
        params (dict):  A dictionary containing transaction-related parameters.
        merchant_key (str): The merchant key for authentication.
        salt (str): The salt for securing the payment process.
        env (str):  The environment (e.g., 'test' or 'production').

    Returns:
        dict: holds the single transaction details.
    """
    
    try:
        result = _transaction(params, merchant_key, salt, env)
        easebuzz_transaction_response =  _validate_transaction_response(result, salt)
        return easebuzz_transaction_response
    except Exception as _:
        traceback.print_exc()
        logger.error("#######Error on transaction:get_transaction_details#######")
        return ({"status": False, "reason": 'Exception occured'})


def _transaction(params, merchant_key, salt, env):
    """
    _transaction method use for get single transaction details.

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
    params['key'] = merchant_key

    # remove white space, htmlentities(converts characters to HTML entities), prepared posted_array
    posted_array = utility.remove_space_and_prepare_post_array(params)

    # empty validation
    empty_validation = _empty_validation(posted_array, salt)
    if empty_validation is not True:
        return empty_validation

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
    transaction_url = utility.get_url(env)

    # process to start get transaction details
    transaction_result = _get_transaction(posted_array, salt, transaction_url)

    return transaction_result


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

    if not params['amount']:
        empty_value = 'Transaction Amount'

    if not params['email']:
        empty_value ='Email'

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
        type_value =  "Merchant Transaction ID should be string"

    if not isinstance(params['amount'], float):
        type_value = "The amount should float up to two or one decimal."

    if not isinstance(params['phone'], str):
        type_value = "Phone Number should be number"

    if not isinstance(params['email'], str):
        type_value = "Email should be string"

    if type_value is not False:
        return {
           'status' : 0,
            'data' : type_value
        }

    return True


def _get_transaction(params_array, salt_key, url):
    """
    _get_transaction method get all details of a single transaction.

    Args:
        params_array (dict): holds all form data with merchant key, transaction id etc.
        salt_key (str): holds the merchant salt key.
        url (str): holds the url based in env( environment type env = 'test' or env = 'prod')

    Returns:
        dict: status and data - holds the details of a particular transaction.
              status = 0 means error.
              status = 1 means success.
    """
    hash_key = None

    # generate hash key and push into params array.
    hash_key = _get_hash_key(params_array, salt_key)

    params_array['hash'] = hash_key

    # requests call for retrive transaction
    request_result = requests.post(url + 'transaction/v1/retrieve', params_array)

    return json.loads(request_result.content)


def _get_hash_key(posted, salt_key):
    """
    _get_hash_key method generate Hash key based on the API call (initiatePayment API).
    hash format (hash sequence) :
        hash = key|txnid|amount|email|phone|salt
    Args:
        posted (dict): holds the passed array.
        salt_key (str): holds merchant salt key.

    Returns:
        str: holds the generated hash key
    """
    hash_string = ""
    hash_sequence = "key|txnid|amount|email|phone"

    hash_sequence_array = hash_sequence.split("|")

    for value in hash_sequence_array:
        if value in posted:
            hash_string += str(posted[value])
        else:
            hash_string += ""
        hash_string += "|"

    hash_string += salt_key

    return  sha512(hash_string.encode('utf-8')).hexdigest().lower()


def _validate_transaction_response(response_array, salt_key):
    """
    _validate_transaction_response method call response method for verify the response

    Args:
        response_array (dict): holds the passed array.
        salt_key (str): hold merchant salt key

    Returns:
        dict: result['status'] = 1 - means transaction response is valid as it matched the hash,
              result['status'] = 0 - means error
    """

    if response_array['status'] is  True:

        # reverse hash key for validation means response is correct or not.
        reverse_hash_key = _get_reverse_hash_key(response_array['msg'], salt_key)

        if reverse_hash_key == response_array['msg']['hash']:
            return response_array

        else:
            return {
                'status' : 0,
                'data' : 'Hash key Mismatch'
            }

    return response_array


def _get_reverse_hash_key(response_array, s_key):
    """
    _get_reverse_hash_key to generate Reverse hash key for validation.
    reverse hash formate (hash sequence) :
    reverse_hash = salt|response_array['status']|udf10|udf9|udf8|udf7|udf6|udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key


    Args:
        response_array (dict):  holds the response array.
        s_key (str):  holds the merchant salt key.

    Returns:
        str: reverse_hash - holds the generated reverse hash key.
    """
    reverse_hash_string_sequence = "udf10|udf9|udf8|udf7|udf6|udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key"

    # make an array or split into array base on pipe sign.
    reverse_hash_string = ""

    hash_sequence_array = reverse_hash_string_sequence.split("|")
    reverse_hash_string += s_key + '|' + str(response_array['status'])

    for value in hash_sequence_array:
        reverse_hash_string += "|"
        if value in response_array:
            reverse_hash_string += str(response_array[value])
        else:
            reverse_hash_string += ""

    return  sha512(reverse_hash_string.encode('utf-8')).hexdigest().lower()
