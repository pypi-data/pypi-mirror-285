from trimble.id._constants import PACKAGE_NAME
from .analytics_http_client import AnalyticsHttpClient
import pkg_resources  

class FixedTokenProvider:
    """
    A token provider that returns a fixed token
    """
    def __init__(self, token, product_name = None):
        """
        Initialize FixedTokenProvider class

        :param token: Sets access token to FixedTokenProvider
        :param productName: Product name of the consuming application
        """
        self._token = token
        self._consumerKey = None
        self._version = pkg_resources.require(PACKAGE_NAME)[0].version

        AnalyticsHttpClient.send_init_event(
            name=self.__class__.__name__, 
            client_name=PACKAGE_NAME, 
            client_version=self._version)
    
    def with_token(self, token):
        """
        Sets consumer key to FixedTokenProvider

        :param consumer_key: Sets consumer key to FixedTokenProvider
        """
        self._token = token
        return self

    async def retrieve_token(self):
        """
        Retrieves fixed token
        """
        AnalyticsHttpClient.send_method_event(
            name=f"{self.__class__.__name__}_retrieve_token", 
            client_name=PACKAGE_NAME, 
            client_version=self._version)

        return self._token
    