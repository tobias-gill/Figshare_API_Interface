"""

"""

import os
import configparser

__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"

"""
Set-up From Config File.
"""

# Read Config File and Extract Information
config_file = os.path.abspath(__file__ + '/../' + 'figshare_interface.config')

if os.path.isfile(config_file):
    config_file_exist = True
else:
    pass

config = configparser.ConfigParser()
config.read(config_file)

# Determine in in staging.
# Fall back value is true to prevent unintentional editing of live site.
staging = config.getboolean('DEFAULT', 'Staging')

# Get Base URL to use.
assert type(staging) is bool  # Check staging is a boolean.
if staging:
    config_url = config.get('base_urls', 'Staging_url')
    base_url = ''
    for char in config_url:
        if char != '\'':
            base_url += char

    base_url += '/{endpoint}'
else:
    config_url = config.get('base_urls', 'Live_url')
    base_url = ''
    for char in config_url:
        if char != '\'':
            base_url += char

    base_url += '/{endpoint}'

# Determine if in quite mode.
verbose = config.getboolean('DEFAULT', 'verbose', fallback=True)
assert type(verbose) is bool  # Check that verbose is a boolean
