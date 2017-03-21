"""

"""

from ..http_requests.figshare_requests import *
from .. import config

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class Collections:
    """

    """

    def __init__(self, token):

        self.token = token

    def get_list(self):
        """
        Used to get a list of private collections
        :return: list of collections.
        """
        result = issue_request(method='GET', endpoint='account/collections', token=self.token)
        return result

    def get_info(self, collection_id):
        """
        Returns information from a given figshare collection id.
        :param collection_id: Integer figshare collection id number.
        :return: Dictionary of collection information.
        """
        endpoint = 'account/collections/{id}'.format(id=collection_id)  # Construct HTTP endpoint
        # Issue HTTP request and return the project information.
        result = issue_request(method='GET', endpoint=endpoint, token=self.token)
        return result

    def get_articles(self, collection_id, limit=100):
        """
        Returns a list of figshare_articles in the given article.

        :param collection_id: Integer of figshare collection id number.
        :param limit: Defines the maximum number of figshare_articles to be returned.
        :return: List of collection figshare_articles.
        """
        endpoint = 'account/collections/{id}/figshare_articles?limit={limit}'.format(id=collection_id, limit=limit)
        result = issue_request(method='GET', endpoint=endpoint, token=self.token)
        return result

    def check_if_exists(self, search):
        """
        Use to search your figshare collections for existing collection with the exact same title as input.
        :param search: string containing the title name to search for.
        :return: True, if title already exists. False, if it does not.
        """

        # Construct the figshare search query. See 'https://docs.figshare.com/Search/search/' for more info.
        data = {
            "search_for": "'{search}'".format(search=search)
        }
        # Issue HTTP request. Will return a list dictionaries each with information on an existing collection that has
        # met the search parameters.
        # Ideally this will either be a single project if the title is already in use.
        result = issue_request(method='POST', endpoint='account/collections/search', data=data, token=self.token)

        # Check to see that returned result has the same title as that searched for.
        for collection in range(len(result)):
            # If project title already exists return True
            if result[collection]['title'] == search:
                return True
            # If no collection exists with the same title return False.
            else:
                return False

    @staticmethod
    def check_arg(argument, structure):
        """
        Check the structure of a given argument.
        :param argument: input argument.
        :param structure: intended structures.
        :return:
        """
        if type(structure) != list:
            if type(argument) != structure:
                raise TypeError('{arg} is not {struc}'.format(arg=argument, struc=structure))
        elif type(structure) == list:
            for element in argument:
                if type(element) != structure[0]:
                    raise TypeError(
                        '{arg} contains element that is not {struc}.'.format(arg=argument, struc=structure[0]))

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def create(self, title, description, articles=None, authors=None, categories=None, tags=None, references=None,
               custom_fields=None):
        """
        Create a new figshare collection.
        :param title: String containing the desired title for the collection.
                        - String length should be between 2 and 500 characters.
        :param description: String containing detailed description of the collection.
                        - No limit to string length.
        :param articles: Array of Integers containing the article id's to be associated to the collection.
        :param authors: Array of Dictionaries containing either {"id": int} or {"name": 'first second'}.
        :param categories: Array of Integers for the figshare categories to be associated to the collection.
        :param tags: Array of Strings for the tags to be associated to the collection.
        :param references: Array of Strings containing references to be associated with the collection.
        :param custom_fields: Dictionary object where key, value pairs contain other metadata names and values.
        :return:  Dictionary containing the newly created figshare collection information.
        """

        # Check to see if a project already exists with the same title.
        if self.check_if_exists(title):
            raise ValueError('Collection already exists with title: {title}'.format(title=title))

        args_name = []
        args = []

        # Check the structure of input parameters to see if they meet requirements for figshare inputs.
        # Title Checks.
        self.check_arg(title, str)
        if not len(title) > 3 & len(title) < 501:  # Checks to see if the length of title is between 3 and 500 chars.
            raise ValueError('Title is not between 3 and 500 characters long.')

        args_name.append('title')
        args.append(title)

        # Check description
        self.check_arg(description, str)
        args_name.append('description')
        args.append(description)

        update_required = False
        update_articles = False
        update_authors = False
        update_categories = False
        update_references = False

        # Check figshare_articles.
        if articles is not None:
            self.check_arg(articles, [int])
            if len(articles) <= 10:
                args_name.append('figshare_articles')
                args.append(articles)
            else:
                update_required = True
                update_articles = True

        # Check authors.
        if authors is not None:
            self.check_arg(authors, [dict])
            if len(authors) <= 10:
                args_name.append('authors')
                args.append(authors)
            else:
                update_required = True
                update_authors = True

        # Check categories
        if categories is not None:
            self.check_arg(categories, [int])
            if len(categories) <= 10:
                args_name.append('categories')
                args.append(categories)
            else:
                update_required = True
                update_categories = True

        # Check Tags if given.
        if tags is not None:
            self.check_arg(tags, [str])
            args_name.append('tags')
            args.append(tags)

        # Check references is given.
        if references is not None:
            self.check_arg(references, [str])
            if len(references) <= 10:
                args_name.append('references')
                args.append(references)
            else:
                update_required = True
                update_references = True

        # Do not know what the structure of custom_fields will be therefore will have to check before calling.
        if custom_fields is not None:
            args_name.append('custom_fields')
            args.append(custom_fields)

        # Construct data dictionary to pass to HTTP request.
        data = {}
        for arg in range(len(args)):
            data[args_name[arg]] = args[arg]

        # Issue HTTP request. Returns dictionary of newly created collection information.
        result = issue_request(method='POST', endpoint='account/collections', data=data, token=self.token)
        if config.verbose:
            print('Created collection: ', result['location'], '\n')

        # Use the returned location url to check that information can be collected from figshare.
        collection_info = raw_issue_request(method='GET', url=result['location'], token=self.token)

        collection_id = collection_info['id']

        if update_required:
            if update_articles:
                for subsec in list(self.chunks(articles, 10)):
                    data = {'figshare_articles': subsec}
                    endpoint = 'account/collections/{collection_id}/figshare_articles'.format(collection_id=collection_id)
                    issue_request(method='POST', endpoint=endpoint, data=data, token=self.token)
                if config.verbose:
                    print('Articles added to collection: {id}'.format(id=collection_id))

            if update_authors:
                for subsec in list(self.chunks(authors, 10)):
                    data = {'authors': subsec}
                    endpoint = 'account/collections/{collection_id}/authors'.format(collection_id=collection_id)
                    issue_request(method='POST', endpoint=endpoint, data=data, token=self.token)
                if config.verbose:
                    print('Authors added to collection: {id}'.format(id=collection_id))

            if update_categories:
                for subsec in list(self.chunks(categories, 10)):
                    data = {'categories': subsec}
                    endpoint = 'account/collections/{collection_id}/categories'.format(collection_id=collection_id)
                    issue_request(method='POST', endpoint=endpoint, data=data, token=self.token)
                if config.verbose:
                    print('Categories added to collection: {id}'.format(id=collection_id))

            if update_references:
                for subsec in list(self.chunks(references, 10)):
                    data = {'references': subsec}
                    endpoint = 'account/collections/{collection_id}/references'.format(collection_id=collection_id)
                    issue_request(method='POST', endpoint=endpoint, data=data, token=self.token)
                if config.verbose:
                    print('References added to collection: {id}'.format(id=collection_id))

        collection_info = raw_issue_request(method='GET', url=result['location'], token=self.token)

        # Return new project information.
        return collection_info

    def publish(self, collection_id):

        endpoint = 'account/collections/{collection_id}/publish'.format(collection_id=collection_id)
        result = issue_request(method='POST', endpoint=endpoint, token=self.token)

        if config.verbose:
            print('Published collection: {id}.'.format(id=collection_id))

        return result

    def publish_article(self, article_id):

        endpoint = 'account/figshare_articles/{article_id}/publish'.format(article_id=article_id)
        result = issue_request(method='POST', endpoint=endpoint, token=self.token)

        if config.verbose:
            print('Published article: {id}.'.format(id=article_id))

        return result
