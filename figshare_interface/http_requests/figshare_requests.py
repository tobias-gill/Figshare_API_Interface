"""
Figshare API Requests.


"""

import hashlib
import json
import os
import requests
from requests.exceptions import HTTPError

from .. import config

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"

"""
HTTP Requests to Figshare API.
"""


def raw_issue_request(method, url, data=None, token=None):
    """
    Construct a HTTP request.
    :param method: API method, i.e. PUT or GET.
    :param url: url to API endpoiint.
    :param data: Additional data to be passed to the endpoint.
    :param token: OAuth token.
    :return: Response from API.
    """
    # Check to see if a token has been given.
    if token is None:
        raise ValueError('No authentication token has been provided.')

    # Format authentication header.
    headers = {'Authorization': 'token ' + token}

    # If there is data to be passed with the request convert it to json format, if it is not already bytes.
    if data is not None:
        if not type(data) == bytes:
            data = json.dumps(data)

    # Raise request to API.
    response = requests.request(method=method, url=url, headers=headers, data=data)
    try:
        # Raises stored HTTPError, if one occurred.
        response.raise_for_status()
        try:
            # The response of the request is in bytes. Therefore is decoded to a string before being decoded by JSON.
            str_response = response.content.decode('utf-8')
            data = json.loads(str_response)

        except ValueError:
            # If the response can not be decoded raise a value error, returning the response contents.
            data = response.content

    except HTTPError as error:
        # If HTTPError occurs raise and print details from contents.
        print('Caught an HTTPError: {}'.format(error))
        print('Body:\n', response.content)
        raise

    # Return the decoded data from a successful request.
    return data


def issue_request(method, endpoint, *args, **kwargs):
    """
    Used to contruct raw issue requests from a base url and target endpoint.
    :param method: API request method.
    :param endpoint: target of the API request.
    :param args: Additional un-named arguments.
    :param kwargs: Additional named arguments.
    :return: Decoded data from a successful request.
    """
    return raw_issue_request(method=method, url=config.base_url.format(endpoint=endpoint), *args, **kwargs)


def get_file_check_data(file_name, chunk_size=1048576):
    """
    Reads file and uses md5 to encode for upload.
    :param file_name: path to file to be read.
    :param chunk_size: length of characters to read per chunk of file.
    :return:
    """

    with open(file_name, 'rb') as fin:
        md5 = hashlib.md5()
        size = 0
        data = fin.read(chunk_size)
        while data:
            size += len(data)
            md5.update(data)
            data = fin.read(chunk_size)
        return md5.hexdigest(), size


def initiate_new_upload(article_id, file_name, token):
    """
    Use to begin a new file upload to figshare API.
    :param article_id: id number of figshare article file is to be uploaded to.
    :param file_name: name of file to be stored on figshare.
    :param token: figshare authentication token.
    :return:
    """

    endpoint = 'account/articles/{article_id}/files'  # Un-formatted endpoint for file upload.
    endpoint = endpoint.format(article_id=article_id)  # Formatted endpoint for file upload.

    md5, size = get_file_check_data(file_name)  # Get file md5 encoding and file size.

    # Define data for HTTP request.
    data = {'name': os.path.basename(file_name),  # Local file path.
            'md5': md5,  # File md5 encoding.
            'size': size}  # File size.

    # Issue HTTP request.
    result = issue_request(method='POST', endpoint=endpoint, data=data, token=token)
    print('Initiated file upload:', result['location'], '\n')

    # Use returned complete url to get the figshare file_info from API.
    result = raw_issue_request(method='GET', url=result['location'], token=token)

    # Return figshare file_info.
    return result


def upload_parts(file_name, file_info, token):
    """
    Use to upload the parts of the file to the endpoint from the file_info returned by initiate_new_upload().
    :param file_name: Local path to file to be uploaded.
    :param file_info: file_info returned from fighsare.
    :param token: Authentication token.
    :return:
    """
    # Get the complete figshare file url from the file_info.
    url = '{upload_url}'.format(**file_info)
    # Get the figshare file information from the url.
    result = raw_issue_request(method='GET', url=url, token=token)

    # Sequentially upload parts of the file.
    if config.verbose:
        print('Uploading parts:')
    with open(file_name, 'rb') as fin:
        for part in result['parts']:
            upload_part(file_info=file_info, stream=fin, part=part, token=token)
    if config.verbose:
        print()


def upload_part(file_info, stream, part, token):
    """
    Upload a single part of a file.
    :param file_info: figshare file_info.
    :param stream: file stream to be uploaded.
    :param part:
    :param token: Authentication token.
    :return:
    """
    # Copy file info.
    udata = file_info.copy()
    udata.update(part)
    url = '{upload_url}/{partNo}'.format(**udata)

    stream.seek(part['startOffset'])
    data = stream.read(part['endOffset'] - part['startOffset'] + 1)

    raw_issue_request(method='PUT', url=url, data=data, token=token)
    if config.verbose:
        print('Upload part {partNo} from {startOffset} to {endOffset}'.format(**part))


def complete_upload(article_id, file_id, token):
    """
    Complete upload by posting the relavent information.
    :param article_id: id number given to article, within project.
    :param file_id: id number of file, within article.
    :param token: Authentication token.
    :return:
    """
    endpoint = 'account/articles/{article_id}/files/{file_id}'
    endpoint = endpoint.format(article_id=article_id, file_id=file_id)
    issue_request(method='POST', endpoint=endpoint, token=token)
