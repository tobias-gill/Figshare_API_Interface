"""
=========================================
Base Figshare Article Metadata Structure.
=========================================



"""


__author__ = "Tobias Gill"
__credits__ = ["Tobias Gill", "Adrian-Tudor Panescu", "Miriam Keshani"]
__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "Tobias Gill"
__email__ = "toby.gill.09@ucl.ac.uk"
__status__ = "Development"


class article_metadata(object):
    """
    Base class for creating the metadata structures in figshare.

    The key, value pairs in model_structure are the default fields on figshare.
    """
    def __init__(self, input_dict):
        """

        :param input_dict: A dictionary object containing at least the mandatory metadata for a fighare article.
        :return: input_dict after checking its' structure.
        """

        self.input_dict = input_dict

        self._mandatory_structure()
        self._model_structure()

        if not self._check_structure(self.input_dict, self.mandatory_structure, self.model_structure):
            raise ValueError('Error found in structure of input dictionary.')

    def _model_structure(self):
        """
        creates a dict object that has the model data types for each metadata field.
        :return:
        """
        self.model_structure = {
            'title': str,
            'description': str,
            'tags': [str],
            'references': [str],
            'categories': [int],
            'authors': [dict],
            'defined_type': str,
            'funding': str,
            'license': str
        }

    def _mandatory_structure(self):
        """
        Creates a dict object with the mandatory fields metadata types.
        :return:
        """
        self.mandatory_structure = {
            'title': str,
            'description': str,
            'authors': [dict],
            'defined_type': str,
        }

    @staticmethod
    def _check_structure(input_dict, mandatory, model):
        """
        Used to check that the values of the input dictionary are the right type.

        :param input_dict: python dictionary to be checked.
        :return:
        """

        # Check to see if the input dictionary has the keys for the mandatory metadata structure.
        for key, value in mandatory.items():
            if 'custom_fields' in input_dict:
                if key not in input_dict and key not in input_dict['custom_fields']:
                    raise ValueError('input dictionary does not have mandatory key: {key}'.format(key=key))
            else:
                if key not in input_dict:
                    raise ValueError('input dictionary does not have mandatory key: {key}'.format(key=key))
        # Check to see if the input dictionary has keys that are wrong.
        for key, value in input_dict.items():
            # Checks to see if keys of input dictionary are in the model dictionary.
            if key != 'custom_fields':
                if key not in model:
                    raise ValueError('Unknown input dictionary key: {key}.'.format(key=key))

                # If the model dictionary key value is a list check to see if value in list are correct type.
                if type(value) is list:
                    if type(value[0]) is not model[key][0]:
                        err_message = 'input dictionary key: {ky} list type: {ty} is not {ref}'
                        err_message = err_message.format(ky=key, ty=value[0], ref=model[key][0])
                        raise ValueError(err_message)

                else:
                    # Checks to see if the type of the value for key is correct, in comparison to the model dictionary.
                    if type(value) is not model[key]:
                        err_message = 'input dictionary key: {ky} type: {ty} is not {ref}'
                        err_message = err_message.format(ky=key, ty=type(value), ref=model[key])
                        raise ValueError(err_message)
        return True

    def get_data(self, input_dict):

        return input_dict
