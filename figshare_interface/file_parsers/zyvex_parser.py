"""
Script to parse the XML format .ZAD files from the Zyvex STM Lithography hardware.
"""
# Author: Udi Fuchs
# Copyright: (c) 2010-2014 Zyvex Labs LCC

import xml.dom.minidom as dom
import zlib
import base64
import numpy


class ZyvexFile:

    def __init__(self, filename):

        if self.is_zad_file(filename):

            self.exp_info = {}
            self.file_info = {}
            self.scan_info = []
            self.data = []

            self.load(filename)

    @staticmethod
    def detect_by_name(filename):
        """Identified ZAD files by their ending."""
        if filename.endswith(".zad"):
            return 100
        else:
            return 0

    @staticmethod
    def detect_by_content(head):
        """Identified ZAD files by their XML header."""
        if head == '<?xml version="1.0" ?><SCANZ_DATA version="5">':
            return 100
        if head == '<?xml version="1.0" ?><SCANZ_DATA version="6">':
            return 100
        if head == '<?xml version="1.0" ?>\r\n<SCANZ_DATA version="6">':
            return 100
        if head == '<?xml version="1.0" ?>\r\n<SCANZ_DATA version="7">':
            return 100
        if head == '<?xml version="1.0" ?>\n<SCANZ_DATA version="7">':
            return 100
        else:
            return 0

    @staticmethod
    def unpack_string(string):
        """Unpack a comma separated string into 2 parts."""
        return string[1:-1].split(', ')

    def is_zad_file(self, filename):
        """Read the first 100 Bytes of a file and check it is a ZAD file"""
        f = open(filename)
        fd = f.read(100)
        f.close()

        # Get XML Header
        start = 0
        for i in range(2):
            ind = fd.index('>', start)
            start = ind + 1
        head = fd[0:ind+1]

        if self.detect_by_content(head) == 0:
            raise Exception('File Header does not match known format. Check that this is a .ZAD file.')
        else:
            return True

    def load(self, filename):
        """Load scan data from a ZAD file."""

        doc = dom.parse(filename)
        scanz_data = doc.getElementsByTagName('SCANZ_DATA')[0]
        version = scanz_data.getAttribute('version')
        assert version == '5' or version == '6' or version == '7'

        system_data = doc.getElementsByTagName('SystemData')[0]
        calib_xyz = self.unpack_string(system_data.getAttribute('CalibXYZ'))
        calib_z = float(calib_xyz[2])
        max_piezo_voltage = system_data.getAttribute('MaxPiezoVoltage')
        if max_piezo_voltage == '':
            max_piezo_voltage = 150.0
        else:
            max_piezo_voltage = float(max_piezo_voltage)
        # creator = system_data.getAttribute('Creator')
        # dsp_filer_params = system_data.getAttribute('DSPFilterParams')
        # dsp_version = system_data.getAttribute('DSPVersion')
        preamp_max_curr = system_data.getAttribute('PreampMaxCurr')
        if preamp_max_curr == '':
            preamp_gain = system_data.getAttribute('PreampGain')
            preamp_max_curr = 10.0 ** (10 - int(preamp_gain))
        else:
            preamp_max_curr = float(preamp_max_curr)
        # system_id = system_data.getAttribute('SystemID')
        if version == '5':
            vernier_z = float(system_data.getAttribute('VernierZ'))

        file_data = doc.getElementsByTagName('FileData')[0]
        self.file_info['file_name'] = file_data.getAttribute('FileName')
        # nb_name = file_data.getAttribute('NBName')
        # scanz_ver = file_data.getAttribute('SCANZver')
        self.file_info['sample_name'] = file_data.getAttribute('SampleName')
        self.file_info['tip_name'] = file_data.getAttribute('TipName')
        self.file_info['user_id'] = file_data.getAttribute('UserID')

        scan_data = doc.getElementsByTagName('ScanData')[0]
        if version != '5':
            vernier_z = float(scan_data.getAttribute('VernierZ'))
        # center = scan_data.getAttribute('Center')
        self.file_info['comments'] = scan_data.getAttribute('Comments')
        # drift_auto = scan_data.getAttribute('DriftAuto')
        # drift_corr = scan_data.getAttribute('DriftCorr')
        # extra_dict = scan_data.getAttribute('ExtraDict')
        self.file_info['image_size'] = scan_data.getAttribute('ImageSize')
        self.file_info['sample_bias'] = scan_data.getAttribute('SampleBias')
        self.file_info['scan_rotation'] = scan_data.getAttribute('ScanRotation')
        self.file_info['scan_size'] = self.unpack_string(scan_data.getAttribute('ScanSize'))
        self.file_info['scan_speed'] = scan_data.getAttribute('ScanSpeed')
        self.file_info['set_point'] = scan_data.getAttribute('Setpoint')
        self.file_info['time_created'] = scan_data.getAttribute('TimeCreated')
        self.file_info['time_scan_done'] = scan_data.getAttribute('TimeScanDone')
        scan_bufs = scan_data.getElementsByTagName('ScanBuf')

        self.file_info['xyunit'] = 'm'
        self.file_info['iunit'] = 'A'
        self.file_info['vunit'] = 'V'
        self.file_info['zunit'] = 'm'

        for index, sb in enumerate(scan_bufs):
            scan_dict = {}
            dim_str = self.unpack_string(sb.getAttribute('Dims'))
            chan_name = sb.getAttribute('ChanName')
            scan_dict['type'] = chan_name
            max_value = sb.getAttribute('MaxValue')
            if max_value == '':
                max_value = 0x7fff
            else:
                max_value = int(max_value)
            # crc_data = int(sb.getAttribute('CRCA'))  # Checksum of data
            # crc_comp = int(sb.getAttribute('CRCC'))  # Checksum of compressed data
            b64_data = sb.getAttribute('DataZ64')
            comp_data = base64.b64decode(b64_data)

            # There has been a change in zlib.deompress from Python2 to 3 that seems to result in a different crc32
            # check sum. However, on a few test cases with the script run in Python 2 and 3 there appears to be no
            # difference in the output data.

            # crc_check = zlib.crc32(comp_data)
            # if crc_comp != crc_check:
            #    raise Exception('CRC error in compressed data %s != %s' %
            #                    (crc_comp, crc_check))

            data = zlib.decompress(comp_data)

            # crc_check = zlib.crc32(data)
            # if crc_data != crc_check:
            #     raise Exception('CRC error in data %s != %s' %
            #                     (crc_data, crc_check))

            # Remember that numpy dims swap X & Y
            dim = (int(dim_str[1]), int(dim_str[0]))
            if max_value < 0x8000:
                raw_data = numpy.fromstring(data, dtype=numpy.int16).reshape(dim)
            else:
                raw_data = numpy.fromstring(data, dtype=numpy.int32).reshape(dim)

            a = numpy.asarray(raw_data, dtype='float')
            scan_dict['xres'] = int(dim_str[0])
            scan_dict['yres'] = int(dim_str[1])
            scan_dict['xreal'] = float(self.file_info['scan_size'][0]) * 1e-9
            scan_dict['yreal'] = float(self.file_info['scan_size'][1]) * 1e-9

            self.scan_info.append(scan_dict)

            if chan_name[0:4] == 'Topo':
                a *= (calib_z * max_piezo_voltage * vernier_z / 10.0 * 1e-9 /
                      max_value)
            else:
                a *= preamp_max_curr * 1e-9 / max_value

            self.data.append(a)
