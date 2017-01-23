"""
============================================================
Figshare Article Metadata Structure for STM Topography data.
============================================================



"""

from ..base_figshare_metadata import *


class stm_topo_metadata(article_metadata):
    """
    Child of the base figshare article_metadata class.

    This class adds additional meta_data specific to STM topography articles.
    """
    def __init__(self, input_dict):
        """

        :param input_dict: A dictionary object constructed from a flatfile.info dictionary and additional info required
                           for a figshare article. See article_metadata for more information.
        :return: A reformatted dictionary in a format ready for use in creating/updating a figshare article.
        """
        self.input_dict = input_dict

        # Reformat the structure of information from the flatfile dictionary.
        self.reformatted_dict = self._reformat_flatfile_dict(self.input_dict)

        # Create the mandatory figshare dictionary structure.
        self._mandatory_structure()
        # Create the model figshare dictionary structure.
        self._model_structure()

        # Create the mandatory topography dictionary structure.
        self._mandatory_stm_topo_structure()
        # Create the model topography dictionary structure.
        self._model_stm_topo_structure()

        # Check the input dictionary against the mandatory and model dictionary structures.
        if not self._check_structure(self.reformatted_dict, {**self.mandatory_structure,
                                                             **self.mandatory_stm_topo_structure},
                                     {**self.model_structure, **self.model_stm_topo_structure}):
            # If the check does not return True raise an error.
            raise ValueError('Error found in structure of input dictionary.')

    def _reformat_flatfile_dict(self, input_dict):
        """
        Removes unused information from the flatfile dictionary and reformats the name of some keys.
        :return:
        """

        # Delete currently unused parameters from flatfile info.
        if 'offset' in input_dict:
            del input_dict['offset']
        if 'runcycle' in input_dict:
            del input_dict['runcycle']

        # Convert some information from the flatfile to the format required for figshare.
        input_dict['title'] = input_dict['filename'].split('\\')[-1]  # Extracts the filename as a title.

        # If a description is already provided add the flatfile comment to the description.
        if 'description' in input_dict:
            input_dict['description'] += input_dict['comment']

        # If no description exists create one from the flatfile comment.
        else:
            input_dict['description'] = input_dict['comment']

        # Delete now redundant information from the flatfile.
        if 'comment' in input_dict:
            del input_dict['comment']
        if 'filename' in input_dict:
            del input_dict['filename']

        return input_dict

    def _mandatory_stm_topo_structure(self):
        """
        Creates a dictionary that contains the mandatory keys for an STM topography file.
        Key values are types that the input data is required to be.
        :return:
        """

        self.mandatory_stm_topo_structure = {
            'type': str,
            'vgap': float,
            'current': float,
            'xres': int,
            'yres': int,
            'xinc': float,
            'yinc': float,
            'xreal': float,
            'yreal': float,
            'unit': str,
            'unitxy': str,
            'date': str,
            'direction': [str]
        }

    def _model_stm_topo_structure(self):
        """
        Creates a dictionary that contains additional 'ideal' or 'model' information for a STM topography file.
        Key values are types that the input data is required to be.
        :return:
        """

        self.model_stm_topo_structure = {
            'sample': str,
            'users': str,
            'substrate': str,
            'adsorbate': str,
            'prep': str,
            'notebook': str,
            'notes': str
        }

        # Creates a new dictionary from combining the mandatory structure and model structure.
        self.model_stm_topo_structure = {**self.mandatory_stm_topo_structure, **self.model_stm_topo_structure}

    def get_data(self):
        """
        Takes the input dictionary are deconstructs it into the default fields of Figshare and adds the additional
        fields to a new dictionary contained within the 'custom_fields' key.
        :return: dictionary object that can be used to create a figshare article.
        """

        # Create a new dictionary that has a single key, who's value is an empty dictionary.
        output_dir = {'custom_fields': {}}

        # iterate over the key, value pairs of the input dictionary.
        for key, value in self.reformatted_dict.items():
            # If the key, value pair belongs to the standard figshare metadata structure add directly to output_dir.
            if key in self.model_structure:
                output_dir[key] = value
            # If the key, value pair belongs to the STM topography metadata add it to the figshare custom_fields dict.
            elif key in self.model_stm_topo_structure:
                output_dir['custom_fields'][key] = value

        # Return the figshare ready dictionary.
        return output_dir
