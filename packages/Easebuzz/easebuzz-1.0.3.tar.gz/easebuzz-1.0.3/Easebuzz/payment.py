""" Module for payment initiate
"""
import json
import os
import re
import traceback
import logging
from hashlib import sha512
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


def initiate_payment(params, merchant_key, salt, env):
    """ 
    initiate_payment method initiate payment and call display the payment page.

    Args:
        params (dict):  A dictionary containing payment-related parameters.
        merchant_key (str): The merchant key for authentication.
        salt (str): The salt for securing the payment process.
        env (str):  The environment (e.g., 'test' or 'production').

    Returns:
        dict :  holds the payment link and status.
    """
    try:
        result = _payment(params, merchant_key, salt, env)
        return _payment_response(result)
    except Exception:
        traceback.print_exc()
        logger.error("#######Error on payment:initiate_payment#######")
        return ({"status": False, "reason": 'Exception occurred'})


def _payment(params, merchant_key, salt, env):
    """
    _payment method use for initiate payment.

    Args:
        params (dict):  A dictionary containing payment-related parameters.
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

    params._mutable = True
    # push merchant key into params dictionary.
    params['key'] = merchant_key   

    # remove white space, html-entities(converts characters to HTML entities), prepared posted_array
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
    initiate_payment_url = utility.get_url_payment(env)

    # process to start pay
    pay_result = _pay(posted_array, salt, initiate_payment_url)

    return pay_result


def _type_validation(params):
    """
    _typeValidation method check type validation for field.

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

    if not isinstance(params['amount'], float):
        type_value = "The amount should float up to two or one decimal."

    if not isinstance(params['productinfo'], str):
        type_value =  "Product Information should be string"

    if not isinstance(params['firstname'], str):
        type_value =  "First Name should be string"

    if not isinstance(params['phone'], str):
        type_value = "Phone Number should be number"

    if not isinstance(params['email'], str):
        type_value = "Email should be string"

    if not isinstance(params['surl'], str):
        type_value = "Success URL should be string"

    if not isinstance(params['furl'], str):
        type_value = "Failure URL should be string"

    if type_value is not False:
        return {
           'status' : 0,
            'data' : type_value
        }

    return True


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
        empty_value = 'Amount'

    if not params['firstname']:
        empty_value = 'First Name'

    if not params['email']:
        empty_value ='Email'

    if not params['phone']:
        empty_value = 'Phone'

    if not params['productinfo']:
        empty_value ='Product Information'

    if not params['surl']:
        empty_value ='Success URL'

    if not params['furl']:
        empty_value ='Failure URL'

    if not salt:
        empty_value = 'Merchant Salt Key'

    if empty_value is not False:
        return {
            'status' : 0,
            'data' : 'Mandatory Parameter '+ empty_value +' can not empty'
        }

    return True


def _pay(params_array, salt_key, url):
    """
    _pay method initiate payment will be start from here.

    Args:
        params_array (dict): holds all form data with merchant key, transaction id etc.
        salt_key (str): holds the merchant salt key.
        url (str): holds the url based in env( environment type env = 'test' or env = 'prod')

    Returns:
        dict: status and data - holds the details.
              status = 0 means error.
              status = 1 means success and go the url link.
    """
    hash_key = None

    # generate hash key and push into params array.
    hash_key = _get_hash_key(params_array, salt_key)

    params_array['hash'] = hash_key

    # requests call for initiate pay link
    request_result = requests.post(url + 'payment/initiateLink', params_array)

    result = json.loads(request_result.content)

    if result['status'] == 1:
        accesskey = result['data']
    else:
        accesskey = ""

    if not accesskey:
        return result
    else:
        return {
            'status' : 1,
            'data' : url + 'pay/' + accesskey
        }


def _get_hash_key(posted, salt_key):
    """
    _get_hash_key method generate Hash key based on the API call (initiatePayment API).
    hash format (hash sequence) :
    hash = key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10|salt

    Args:
        posted (dict): holds the passed array.
        salt_key (str): holds merchant salt key.

    Returns:
        str: holds the generated hash key
    """
    hash_string = ""
    hash_sequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
    hash_sequence_array = hash_sequence.split("|")

    for value in hash_sequence_array:
        if value in posted:
            hash_string += str(posted[value])
        else:
            hash_string += ""
        hash_string += "|"

    hash_string += salt_key

    return  sha512(hash_string.encode('utf-8')).hexdigest().lower()


def _payment_response(params_array):
    """
    _payment_response method show response after API call.

    Args:
        params_array (dict): holds the passed array.

    Returns:
        dict: result['status'] = 1 - means go to easebuzz page,
              result['status'] = 0 - means error
    """

    if params_array['status'] == 1:

        return {
            "status" : 1,
            "data" : params_array['data']
        }
    else:
        return params_array


def easebuzz_response(response_params, salt_key):
    """
    easebuzz_response method verify API response is acceptable or not and
      returns the response object.

    Args:
        response_params (dict): holds the response array.
        salt_key (str): holds the merchant salt key.

    Returns:
        dict: with status and data - holds the details.
    """
    if len(response_params) == 0:
        return {
            'status' : 0,
            'data' : 'Response params is empty.'
        }

    # remove white space, html-entities, prepared easebuzz_payment_rResponse.
    easebuzz_payment_response = _remove_space_and_prepare_api_response_array(response_params)

    # empty validation
    empty_validation = _empty_validation(easebuzz_payment_response, salt_key)
    if empty_validation is not True:
        return empty_validation

    # check response the correct or not
    response_result = _get_response(easebuzz_payment_response, salt_key)

    return response_result


def _remove_space_and_prepare_api_response_array(response_array):
    """
    _remove_space_and_prepare_api_response_array method Remove white space,
     converts characters to HTML entities and prepared the posted array.

    Args:
        response_array (array): holds the API response array.

    Returns:
        dict: holds the all posted value after removing space.
    """
    temp_dictionary = {}
    for key in response_array:
        temp_dictionary[key] = str(response_array[key]).strip()
    return temp_dictionary


def _get_response(response_array, s_key):
    """
    _get_response check response is correct or not.

    Args:
        response_array (array): holds the API response array.
        s_key (str): holds the merchant salt key

    Returns:
        dict:- return array with status and data - holds the details.
               return integer status = 0 means error.
               return integer status = 1 means success.
    """

    # reverse hash key for validation means response is correct or not.
    reverse_hash_key = _get_reverse_hash_key(response_array, s_key)

    if reverse_hash_key == response_array['hash']:

        if response_array['status'] == 'success':
            return {
                'status' : 1,
                'url' : response_array['surl'],
                'data' : response_array
            }
        elif response_array['status'] == 'failure':
            return {
                'status' : 1,
                'url' : response_array['furl'],
                'data' : response_array
            }
        else:
            return {
                'status' : 1,
                'data' : response_array
            }
    else:
        return {
            'status' : 0,
            'data' : 'Hash key Mismatch'
        }


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
    reverse_hash_string += s_key + '|' + response_array['status']

    for value in hash_sequence_array:
        reverse_hash_string += "|"
        if value in response_array:
            reverse_hash_string += str(response_array[value])
        else:
            reverse_hash_string += ""

    return  sha512(reverse_hash_string.encode('utf-8')).hexdigest().lower()
