"""
Script to parse the zyvex SoftScope CSV files into a format useful for creating figshare articles.
"""

import pandas as pd
import numpy as np


class SoftScopeFile:

    def __init__(self, filename):

        if self.is_softscope(filename):
            self.file_info = {}
            self.scan_info = []
            self.data = []

            self.get_file_info(filename)
            self.get_file_data(filename)

    def get_file_info(self, filename):
        """Return the file info from the SoftScope File"""
        file_info = pd.read_csv(filename, nrows=5)

        for row in range(1, 5):
            self.file_info[file_info['SoftScope CSV'][row]] = file_info['1.0'][row]

    def get_file_data(self, filename):
        """Return the file and scan data."""

        file_data = pd.read_csv(filename, header=6)

        for column in file_data.columns:
            self.scan_info.append(column)

        for column in self.scan_info:
            self.data.append(np.array(file_data[column]))

    def is_softscope(self, filename):
        """Check to see that the given .csv file is a softscope file."""
        file_head = pd.read_csv(filename, nrows=1).columns[0]

        if file_head != 'SoftScope CSV':
            raise Exception('File is not SoftScope CSV File.\nGiven CSV file has header: {head}.')
        else:
            return True
