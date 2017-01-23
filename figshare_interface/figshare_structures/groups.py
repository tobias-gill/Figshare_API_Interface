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


class Groups:
    """

    """

    def __init__(self, token):

        self.token = token  # OAuth token for access to figshare api.

    def get_list(self):
        """
        Use to get a list of dictionaries that contian information on the groups under the figshare institution
        implementation associated to the authentication token used.
        :return: list of dictionaries holding information on the groups.
        """
        # Issue request to figshare API to return a list of information on the groups.
        result = issue_request(method='GET', endpoint='account/institution/groups', token=self.token)
        # Return the list of dictionaries.
        return result
