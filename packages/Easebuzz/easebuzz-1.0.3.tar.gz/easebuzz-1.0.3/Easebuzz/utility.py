"""
This module contains helper funtions.
"""
import re
from . import constant


def check_argument_validation(*arg):
    """
    _checkArgumentValidation method Check number of Arguments Validation. 
    Means how many arguments submitted from form and verify with API documentation.

    param  array *arg - holds the all request.POST data, merchant key, salt key and env.
    Returns:
        True : if number of arguments  matched
        Dict : with status = 0, if number of arguments not matched
    """
    if len(arg) != 4:
        return {
            'status': 0,
            'data': 'Invalid number of arguments.'
        }
    return True


def get_url_payment(env):
    """
    _getURL method set based on environment (env = 'test' or env = 'prod') and generate url link.

    Args:
        env (str): holds the environment

    Returns:
        str: return string url_link - holds the full url link.
    """
    return constant.PAYMENT_URL_PROD if env == 'prod' else constant.PAYMENT_URL_TEST


def get_url(env):
    """
    _getURL method set based on environment (env = 'test' or env = 'prod') and generate url link.

    Args:
        env (str): holds the environment

    Returns:
        str: return string url_link - holds the full url link.
    """
    return constant.URL_PROD if env == 'prod' else constant.URL_TEST


def remove_space_and_prepare_post_array(params):
    """
    _removeSpaceAndPreparePostArray method Remove white space, converts characters to 
     HTML entities and prepared the posted array.

    Args:
        params (dict): holds request.POST array, merchant key, transaction id, etc.

    Returns:
        dict : holds the all posted value after removing space.
    """
    temp_dictionary = {}
    for key in params:
        temp_dictionary[key] = str(params[key]).strip()

    return temp_dictionary


def email_validation(email):
    """
    _email_validation method check email formate validation

    Args:
        email (str): holds the email address.

    Returns:
        boolean: True - email format is correct.
        dict: email format is wrong
    """

    if not re.match(constant.EMAIL_REGEX, email):
        return {
            'status' : 0,
            'data' : 'Email invalid, Please enter valid email.'
        }
    return True

