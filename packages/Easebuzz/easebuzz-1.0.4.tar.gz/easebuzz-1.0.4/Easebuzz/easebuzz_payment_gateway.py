'''
* Easebuzz class si wrapper to payment apis of easebuzz Payment Gateway
'''
import json
from . import payment, transaction, transaction_v2, transaction_date, refund, refund_v2, payout, refund_status


class EasebuzzAPIs:
    """Main class to help calling library function"""
    MERCHANT_KEY = ''
    SALT = ''
    ENV = ''

    '''
    *
    * initialized private variable for setup easebuzz payment gateway.
    *
    * @param  string key - holds the merchant key.
    * @param  string salt - holds the merchant salt key.
    * @param  string env - holds the env(environment). 
    *
    '''
    def __init__(self, key, salt, env):
        self.MERCHANT_KEY = key
        self.SALT = salt
        self.ENV = env

    def initiate_payment_api(self, params):
        """

        initiatePaymentAPI function used to integrate easebuzz for payment using http method - POST
    
        Args:
            params (_dict_): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = payment.initiate_payment(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def transaction_api(self, params):
        """

        transactionAPI function to query for single transaction using http method - POST
    
        Args:
            params (_dict_): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = transaction.get_transaction_details(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def transaction_api_v2(self, params):
        """

        transactionAPI function to query for single transaction using http method - POST
    
        Args:
            params (_dict_): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = transaction_v2.get_transaction_details(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def transaction_date_api(self, params):
        """
        transactionDateAPI function to transaction based on date using http method - POST
    
        Args:
            params (dict): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = transaction_date.get_transactions_by_date(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def refund_api(self, params):
        """
        refund_api function to refund for the transaction using http method - POST
    
        Args:
            params (dict): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = refund.initiate_refund(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def refund_api_v2(self, params):
        """
        refund_api function to refund for the transaction using http method - POST
    
        Args:
            params (dict): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = refund_v2.initiate_refund(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def refund_status_api(self, params):
        """
        refund_status_api function to check refund_status for the transaction using http method - POST
    
        Args:
            params (dict): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = refund_status.refund_status(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def payout_api(self, params):
        """
        payout_api function to payout for particular date using http method - POST
    
        Args:
            params (dict): holds the request.POST data which is pass from the html form.

        Returns:
            dict: ApiResponse['status']== 1 successful and ApiResponse['status']== 0 error.
        """

        result = payout.get_payout_details_by_date(params, self.MERCHANT_KEY, self.SALT, self.ENV)
        return json.dumps(result)

    def easebuzz_response(self, params):
        """easebuzz_response method to verify easebuzz API response is acceptable or not
            using http method - POST

        Args:
            params (dict): holds the API response array.

        Returns:
            dict: olds the API response array after verification of response.
        """

        result = payment.easebuzz_response(params, self.SALT)
        return json.dumps(result)
