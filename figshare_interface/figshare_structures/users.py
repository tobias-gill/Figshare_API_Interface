"""

"""

from ..http_requests.figshare_requests import *

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class User:
    """

    """

    def __init__(self, token):

        self.token = token

    def get_info(self):

        result = issue_request(method='GET', endpoint='account', token=self.token)

        return result
