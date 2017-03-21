"""

"""

from ..http_requests.figshare_requests import *
from ..metadata_structures.stm_metadata_structures.stm_topo_metadata import *
from ..metadata_structures.stm_metadata_structures.stm_spec_metadata import *
from .. import config

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class Projects:

    def __init__(self, token):

        self.token = token  # OAuth token for access to figshare API.

    def get_list(self):
        """
        Used to get a list of private projects
        :return: list of projects.
        """
        result = issue_request(method='GET', endpoint='account/projects', token=self.token)
        return result

    def get_info(self, project_id):
        """
        Returns information from a given figshare project id.
        :param project_id: Integer figshare project id number.
        :return: Dictionary of project information.
        """
        endpoint = 'account/projects/{id}'.format(id=project_id)  # Construct HTTP endpoint
        # Issue HTTP request and return the project information.
        result = issue_request(method='GET', endpoint=endpoint, token=self.token)
        return result

    def search(self, search, limit=100):
        """
        Use to return the results of a search query at the projects endpoint.
        :param search: String containing the figshare query. See 'https://docs.figshare.com/Search/search/'.
        :param limit: Sets the maximum number of results to add to the return.
        :return: List of dictionaries.
        """
        # Construct the figshare search query. See 'https://docs.figshare.com/Search/search/' for more info.
        data = {"search_for": search}
        endpoint = 'account/projects/search?limit={limit}'.format(limit=limit)

        # Issue HTTP request. Will return a list dictionaries each with information on an existing project that has met
        # the search parameters.
        result = issue_request(method='POST', endpoint=endpoint, data=data, token=self.token)

        return result

    def check_if_exists(self, search):
        """
        Use to search your figshare projects for existing projects with the exact same title as input.
        :param search: string containing the title name to search for. See 'https://docs.figshare.com/Search/search/'.
        :return: True, if title already exists. False, if it does not.
        """

        # Ideally this will either be a single project if the title is already in use.
        result = self.search(search)

        # Check to see that returned result has the same title as that searched for.
        for project in range(len(result)):
            # If project title already exists return True
            if result[project]['title'] == search:
                return True
            # If no project exists with the same title return False.
            else:
                return False

    def create(self, title, description, funding, group_id):
        """
        Create a figshare project.

        :param title: String containing the desired title of the project.
                        - String length should be between 3 and 500 characters.
        :param description: String containing a detailed description of the project.
                              - No limit to string length.
        :param funding: String containing acknowledgements to funding.
                          - String length should be no more than 2000 characters.
        :param group_id: Integer of figshare group id.
        :return: Dictionary containing the newly created figshare project information.
        """

        # Check to see if a project already exists with the same title.
        if self.check_if_exists(title):
            raise ValueError('Project already exists with title: {title}'.format(title=title))

        # Check the structure of input parameters to see if they meet requirements for figshare inputs.
        # Title Checks.
        if not type(title) == str:  # Checks to see if title is a string.
            raise TypeError('title is not a string')
        if not len(title) > 3 & len(title) < 501:  # Checks to see if the length of title is between 3 and 500 chars.
            raise ValueError('Title is not between 3 and 500 characters long.')

        if not type(description) == str:  # Checks to see if description is a string.
            raise TypeError('description is not a string.')

        if not type(funding) == str:  # Checks to see if funding is a string.
            raise TypeError('funding is not a string')
        if not len(funding) < 2001:  # Checks to see if the funding string is under 2000 characters long.
            raise ValueError('funding string is longer than 2000 characters.')

        if not type(group_id) == int:  # Checks to see id group_id is an integer.
            raise TypeError('group_id is not an integer.')

        # Construct data dictionary to pass to HTTP request.
        data = {
            'title': title,
            'description': description,
            'funding': funding,
            'group_id': group_id
        }

        # Issue HTTP request. Returns dictionary of newly created project information.
        result = issue_request(method='POST', endpoint='account/projects', data=data, token=self.token)
        if config.verbose:
            print('Created project: ', result['location'], '\n')

        # Use the returned location url to check that information can be collected from figshare.
        project_info = raw_issue_request(method='GET', url=result['location'], token=self.token)

        # Return new project information.
        return project_info

    def update(self, project_id, title=None, description=None, funding=None, group_id=None):
        """
        Update project information of an existing figshare project.

        Arguments
        :param project_id: Integer value of figshare project id to be updated

        Optional Arguments
        :param title: String containing updated project title.
                        - String length should be between 3 and 500 characters.
        :param description: String containing updated project description.
                              - No limit to string length.
        :param funding: String containing updated project funding.
                          - String length should be no more than 2000 characters long.
        :param group_id: Integer of updated fighsare group id.
        :return: Dictionary of updated figshare project information.
        """

        # Construct data dictionary to pass to HTTP request.
        data = {}  # Empty dictionary to add updated information.

        # Check the structure of input parameters to see if they meet requirements for figshare inputs.
        # Title Checks.
        if title is not None:  # If an updated title is provided
            if not type(title) == str:  # Checks to see if title is a string.
                raise TypeError('title is not a string')
            # Checks to see if the length of title is between 3 and 500 chars.
            elif not len(title) > 3 & len(title) < 501:
                raise ValueError('Title is not between 3 and 500 characters long.')
            # Check to see if project title already exists.
            if self.check_if_exists(title):
                raise ValueError('Project already exists with title: {title}'.format(title=title))
            # If all ok then add updated title to data dictionary.
            else:
                data['title'] = title

        if description is not None:
            if not type(description) == str:  # Checks to see if description is a string.
                raise TypeError('description is not a string.')
            else:
                data['description'] = description

        if funding is not None:
            if not type(funding) == str:  # Checks to see if funding is a string.
                raise TypeError('funding is not a string')
            elif not len(funding) < 2001:  # Checks to see if the funding string is under 2000 characters long.
                raise ValueError('funding string is longer than 2000 characters.')
            else:
                data['funding'] = funding
        if group_id is not None:
            if not type(group_id) == int:  # Checks to see id group_id is an integer.
                raise TypeError('group_id is not an integer.')
            else:
                data['group_id'] = group_id

        # Construct an endpoint from the project_id given.
        endpoint = 'account/projects/{project_id}'.format(project_id=project_id)

        issue_request(method='PUT', endpoint=endpoint, data=data, token=self.token)
        if config.verbose:
            print('Project: {project_id} updated'.format(project_id=project_id))

        project_info = self.get_info(project_id=project_id)

        return project_info

    def delete(self, project_id, safe=True):
        """
        Use to delete a Figshare project given a project id. A confirmation is required.

        Arguments
        :param project_id: Integer of a Figshare project id.

        Optional Arguments
        :param safe: Boolean that can be used to override the project deletion confirmation.
        :return:
        """

        # Get the information of the given project.
        project_info = self.get_info(project_id)

        # Format a string for input confirmation.
        confirmation_str = 'Are you sure you want to delete project: {id}.\n{title}'.format(id=project_id,
                                                                                            title=project_info['title'])
        confirmation_resp = ''
        if safe:
            # If in default safe mode ask for confirmation.
            # Ask use to confirm that they want to delete the project found.
            confirmation_resp = input(confirmation_str)
        elif not safe:
            # If set to unsafe automatically set confirmation to yes.
            confirmation_resp = 'y'

        # Lists for valid responses to input.
        confirmation_yes = ['y', 'Y', 'yes', 'Yes', 'YES']
        confirmation_no = ['n', 'N', 'no', 'No', 'NO']

        if confirmation_resp in confirmation_yes:
            # If the delete is confirmed then proceed.
            # Construct an endpoint from the given project_id.
            endpoint = 'account/projects/{id}'.format(id=project_id)

            # Issue deletion request.
            issue_request(method='DELETE', endpoint=endpoint, token=self.token)
            if config.verbose:
                print('Deleted Project: ', project_id, '.')
        elif confirmation_resp in confirmation_no:
            # If deletion is canceled.
            print('Project: {id}. deletion canceled.')
        else:
            # If input response is unknown.
            print('Unknown response: {resp}. Project not deleted.'.format(resp=confirmation_resp))

    def list_articles(self, project_id, page_size=100, page=1):

        # Construct an endpoint from the given project_id.
        endpoint = 'account/projects/{id}/articles'.format(id=project_id)
        data = {"page_size": page_size,
                "page": page}
        # Get a list of figshare_articles under project.
        result = issue_request(method='GET', endpoint=endpoint, data=data, token=self.token)

        # Return result list.
        return result

    def search_articles(self, search, limit=100, offset=1):

        data = {"search_for": search,
                "page_size": limit,
                "page": offset}
        endpoint = 'account/articles/search'.format(limit=limit)
        result = issue_request(method='POST', endpoint=endpoint, data=data, token=self.token)

        return result

    def get_article(self, project_id, article_id):

        # Construct an endpoint from the given project and article id's.
        endpoint = 'account/projects/{project_id}/articles/{article_id}'.format(project_id=project_id,
                                                                                article_id=article_id)
        # Get article info
        result = issue_request(method='GET', endpoint=endpoint, token=self.token)

        # Return result
        return result

    def create_article(self, project_id, article_data):

        # Remove references key if no entry.
        if article_data['references'][0] == '':
            del article_data['references']

        """
        FIXME: This is really specific to STM files. May need to generalise this either using file endings or new param.
        """
        if article_data['type'] == 'topo':
            article_data = stm_topo_metadata(article_data).get_data()
        elif article_data['type'] == 'ivcurve':
            article_data = stm_spec_metadata(article_data).get_data()
        elif article_data['type'] == 'ivmap':
            raise ValueError('File type: {type} is not yet supported'.format(type=article_data['type']))
        elif article_data['type'] == 'izcurve':
            raise ValueError('File type: {type} is not yet supported'.format(type=article_data['type']))

        # Check to see if article already exists in project.
        article_list = self.list_articles(project_id)  # Get list of figshare_articles associated with project.
        article_list_titles = []
        for article in article_list:
            article_list_titles.append(article['title'])
        if article_data['title'] in article_list_titles:  # Is new article title in the project already?
            raise FileExistsError('Article with title: {title} already exists in project: {project_id}'.format(
                title=article_data['title'], project_id=project_id))
        else:

            endpoint = 'account/projects/{project_id}/articles'.format(project_id=project_id)  # construct endpoint.
            # Issue HTTP request to create article. get back the new figshare article info.
            result = issue_request(method='POST', endpoint=endpoint, data=article_data, token=self.token)
            if config.verbose:  # If not in quite mode.
                print('Article created: ', result['location'], '\n')  # Notify article has been created.

            # get the new article information from the returned url.
            result = raw_issue_request(method='GET', url=result['location'], token=self.token)

            return result['id']

    @staticmethod
    def update_article(token, article_id, article_data):

        # Check the structure of input parameters to see if they meet requirements for figshare inputs.
        # Title Checks.
        if 'title' in article_data:  # If an updated title is provided
            if not type(article_data['title']) == str:  # Checks to see if title is a string.
                raise TypeError('title is not a string')
            # Checks to see if the length of title is between 3 and 500 chars.
            elif not len(article_data['title']) > 3 & len(article_data['title']) < 501:
                raise ValueError('Title is not between 3 and 500 characters long.')

        if 'funding' in article_data:
            if not type(article_data['funding']) == str:  # Checks to see if funding is a string.
                raise TypeError('funding is not a string')
            elif not len(article_data['funding']) < 2001:  # Checks to see if the funding string is under 2000 characters long.
                raise ValueError('funding string is longer than 2000 characters.')

        if 'references' in article_data:
            if article_data['references'] == '':
                del article_data['references']
            elif article_data['references'] == ['[]']:
                del article_data['references']
            elif article_data['references'] is []:
                del article_data['references']

        endpoint = 'account/articles/{id}'.format(id=article_id)

        issue_request(method='PUT', endpoint=endpoint, data=article_data, token=token)

    def list_files(self, article_id):

        # Construct an endpoint from the given project_id.
        endpoint = 'account/articles/{article_id}/files'.format(article_id=article_id)

        # Get a list of figshare_articles under project.
        result = issue_request(method='GET', endpoint=endpoint, token=self.token)

        # Return result list.
        return result

    def upload_file(self, article_id, file_name):

        files_list = self.list_files(article_id)
        for file in files_list:
            if file['name'] == file_name.split('/')[-1]:
                raise FileExistsError('File already exists in article: {article_id}, with name: {name}'.format(
                    article_id=article_id, name=file['name']))

        file_info = initiate_new_upload(article_id=article_id, file_name=file_name, token=self.token)
        upload_parts(file_name=file_name, file_info=file_info, token=self.token)
        complete_upload(article_id=article_id, file_id=file_info['id'], token=self.token)

    def article_delete(self, project_id, article_id):

        # Construct an endpoint from the given project_id.
        endpoint = 'account/projects/{project_id}/articles/{article_id}'.format(project_id=project_id,
                                                                                article_id=article_id)

        issue_request(method='DELETE', endpoint=endpoint, token=self.token)
        print('Deleted Article: {article_id} in Project: {project_id}.'.format(article_id=article_id,
                                                                               project_id=project_id))
