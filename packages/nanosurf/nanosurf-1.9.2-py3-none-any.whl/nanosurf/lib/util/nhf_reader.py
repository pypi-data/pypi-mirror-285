"""Nanosurf nhf-file reader implementation for studio data
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT"""

import typing
import enum
import pathlib 
import re
import json
import numpy as np
import h5py
from nanosurf.lib.datatypes import sci_val

class NHFMeasurementType(enum.Enum):
    Undefined = enum.auto()
    Unknown = enum.auto()
    Image = enum.auto()
    Spectroscopy = enum.auto()
    WaveModeNMA = enum.auto()
    Calibration = enum.auto()

def _default_verbose_output_handler(msg:str):
    print(msg)

def extract_unit(text_with_unit:str) -> str:
    """ Extracts the unit from a text string containing the unit in parentheses (e.g 'Meter (m)' return 'm')
        if no parentheses are found the returned string is empty.
    """
    si_unit = ""
    matches  = re.findall(r'\(([^\)]+)\)',text_with_unit)
    try:
        si_unit = matches[0]
    except IndexError:
        pass
    return si_unit   

def get_attributes(instance: typing.Union[h5py.File,h5py.Group,h5py.Dataset]) -> dict[str]:
    """ Iterates over the attributes of the given instance and puts them to a dictionary.
    If the attribute for the data type is available, data type specific information is stored.

    Parameters
    ----------

        instance: h5py.File | h5py.Group | h5py.Dataset
            Instance within the .nhf file to be read.

    Return
    ------
        attributes_dict: dict
            Contains the attributes of the analyzed instance.

    """
    if not isinstance(instance, (h5py.File, h5py.Group, h5py.Dataset)):
        raise TypeError("Not supported type of instance provided")
    
    attributes_dict: dict = {}
    for attributes_key, attributes_val in instance.attrs.items():
        attributes_dict[attributes_key] = attributes_val
    return attributes_dict

def _get_sub_items_by_name(instance: typing.Union[h5py.File,h5py.Group], identifiers: list[str]) -> dict[str, str]:
    """ Reads the names of the sub items of the given instance and puts them to a dict, where key - segment id, value- segment name

    Parameters
    ----------

        instance: h5py.File | h5py.Group | h5py.Dataset
            Instance within the .nhf file to be read.
        identifiers: list of strings
            The attribute which identifies the items by its name

    Return
    ------
        item_names: dict
            Contains the names to the given instance.
            key - segment id, value- segment name

    """
    if isinstance(instance, h5py.File) or isinstance(instance, h5py.Group):
        item_names: dict[str, str] = {}
        for seg_key in instance.keys():
            for id_name in identifiers:
                try:
                    item_names[seg_key] = instance[seg_key].attrs[id_name]
                    break
                except KeyError:
                    pass # try next name
        return item_names
    else:
        return None

def _get_unidentified_sub_groups(instance: typing.Union[h5py.File,h5py.Group], known_names: dict[str, str]) -> dict[str, h5py.Group]:
    """ Reads the names of the sub items of the given instance which are not already identified by the known_name dict and puts them into a dict
    """
    if isinstance(instance, h5py.File) or isinstance(instance, h5py.Group):
        if known_names is None:
            known_names = {}
        item_names: dict[str, h5py.Group] = {}
        for seg_key in instance.keys():
            seg_key:str
            if seg_key not in known_names: 
                if isinstance(instance[seg_key],h5py.Group):
                    item_names[seg_key] = instance[seg_key]
                    sub_groups = _get_unidentified_sub_groups(item_names[seg_key],{})
                    if sub_groups is not None:
                        item_names[seg_key].groups = sub_groups
                    sub_dataset = _get_unidentified_sub_dataset(item_names[seg_key],{})
                    if sub_dataset is not None:
                        item_names[seg_key].datasets = sub_dataset
        return item_names
    else:
        return None 
            
def _get_unidentified_sub_dataset(instance: typing.Union[h5py.File,h5py.Group], known_names: dict[str, str]) -> dict[str, h5py.Group]:
    """ Reads the names of the datasets of the given instance which are not already identified by the known_name dict and puts them into a dict
    """
    if isinstance(instance, h5py.File) or isinstance(instance, h5py.Group):
        if known_names is None:
            known_names = {}
        item_names: dict[str, h5py.Group] = {}
        for seg_key in instance.keys():
            seg_key:str
            if seg_key not in known_names: 
                if isinstance(instance[seg_key],h5py.Dataset):
                    item_names[seg_key] = instance[seg_key]
        return item_names
    else:
        return None 
            

class NHFDataset():
    def __init__(self, dataset:h5py.Dataset) -> None:
        # type hint is only correct after scale_dataset_to_physical_units() is called at data read time
        self.dataset:np.ndarray = dataset
        self.attribute = get_attributes(dataset)
        self._inject_data_conversion_attributes()

    def scale_dataset_to_physical_units(self) -> None:
        """ If scaling information are provided in the Dataset, apply them.
        Converts the bit pattern of the saved raw data to the value of the given datatype saved in the attributes
        and scales it with the given calibration values.

        Attention: 
            'dataset' is read from file in this process, which can last long depending on array size.
            Also dataset is converted from h5py dataset into numpy.ndarray
        """
        try:
            signal_min = self.attribute['signal_calibration_min']
            signal_max = self.attribute['signal_calibration_max']
            type_min = self.attribute['type_min']
            type_max = self.attribute['type_max']
        except KeyError:
            signal_min = 0.0
            signal_max = 1.0
            type_min = 0.0
            type_max = 1.0
        
        try:
            calibration_factor = (signal_max - signal_min) / (type_max-type_min)
        except ZeroDivisionError:
            calibration_factor = 1.0
            signal_min = 0.0
            type_min = 0.0
            
        self.dataset = (self.dataset[:] - type_min) * calibration_factor + signal_min

    @property
    def unit(self) -> str:
        si_unit = ""
        try:
            unit_text = self.attribute["signal_calibration_unit"]
            si_unit = extract_unit(unit_text)
            if si_unit == "":
                si_unit = unit_text
        except KeyError:
            pass
        return si_unit   

    @property
    def name(self) -> str:
        my_name = ""
        try:
            my_name = self.attribute['signal_name']
        except KeyError:
            pass
        return my_name


    def _inject_data_conversion_attributes(self):
        """ Search for attributes defining information about data value scaling 

        Parameters
        ----------
            attr_dict: dict
                dictionary to be analyzed and populate with conversion information.
        """
        if 'dataset_element_type' in self.attribute:
            element_type = self.attribute['dataset_element_type']
            if isinstance(element_type, str): # file version 2.x
                    try:
                        self.attribute['type_min'] = NHFFileReader.dataset_element_type_defined_as_str[element_type][0]
                        self.attribute['type_max'] = NHFFileReader.dataset_element_type_defined_as_str[element_type][1]
                        self.attribute['type']     = NHFFileReader.dataset_element_type_defined_as_str[element_type][2]
                    except  IndexError:
                        raise IOError(f"Unknown dataset_element_type '{element_type}'. ")
                    
                    if 'signal_name' in self.attribute:
                        if 'signal_calibration_unit' not in self.attribute:
                            self.attribute['signal_calibration_unit'] = ""
                        if 'signal_calibration_max' not in self.attribute:
                            self.attribute['signal_calibration_max'] = 1.0
                        if 'signal_calibration_min' not in self.attribute:
                            self.attribute['signal_calibration_min'] = 0.0
            else: # file version 1.x
                try:
                    self.attribute['type_min'] = NHFFileReader.dataset_element_type_defined_as_int[element_type][0]
                    self.attribute['type_max'] = NHFFileReader.dataset_element_type_defined_as_int[element_type][1]
                    self.attribute['type']     = NHFFileReader.dataset_element_type_defined_as_int[element_type][2]
                except IndexError:
                    raise IOError(f"Unknown dataset_element_type number {element_type}. ")
                
                try:
                    if 'base_calibration_unit' in self.attribute:
                        self.attribute['signal_name'] = self.attribute['name']
                        self.attribute['signal_calibration_unit'] = self.attribute['base_calibration_unit']
                        self.attribute['signal_calibration_max'] = self.attribute['base_calibration_max']
                        self.attribute['signal_calibration_min'] = self.attribute['base_calibration_min']
                except KeyError:
                    raise IOError(f"Missing complete signal calibration information for {self.attribute['name']}")
        
class NHFProperties():
    def __init__(self) -> None:
        pass

class NHFSegment():
    def __init__(self, name: str, file_hdl: 'NHFFileReader', hdf_group:h5py.Group) -> None:
        self._name = name
        self._file_hdl = file_hdl
        self._hdf_group = hdf_group
        self.channel: dict[str, NHFDataset] = {}
        self.group: dict[str, h5py.Group] = {}
        self.datasets: dict[str, h5py.Dataset] = {}
        self.property:NHFProperties = NHFProperties()
        self.attribute = get_attributes(self._hdf_group) 
        self._dataset_size = (0,0)
        self._dataset_range = (0.0,0.0)
        self._inject_segment_configuration_properties(known_identifiers=['segment_configuration', 'scan_configuration'])

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def dataset_size_x(self) -> int:
        return self._dataset_size[0]

    @property
    def dataset_size_y(self) -> int:
        return self._dataset_size[1]

    @property
    def dataset_range_x(self) -> float:
        return self._dataset_range[0]

    @property
    def dataset_range_y(self) -> float:
        return self._dataset_range[1]

    def read_channel(self, ch:typing.Union[str, int], as_matrix:bool = False) -> NHFDataset:
        nhf_dataset = None
        if isinstance(ch, str):
            nhf_dataset = self.channel[ch]
        elif isinstance(ch, int):
            nhf_dataset = list(self.channel.values())[ch]
        else:
            raise TypeError(f"Parameter 'ch' has not supported data type of '{type(ch)}'")
        
        assert isinstance(nhf_dataset, NHFDataset), ""
        self._file_hdl.print_verbose(f"Reading channel '{ch}'")
        nhf_dataset.scale_dataset_to_physical_units()
        if as_matrix:
            if self._dataset_size == (0,0):
                raise ValueError("No size information stored in segment. Dataset cannot be converted to matrix.")
            nhf_dataset.dataset = np.flipud(np.reshape(np.array(nhf_dataset.dataset), (self.dataset_size_x, self.dataset_size_y)))
        return nhf_dataset
    
    def channel_name(self, key: int) -> str:
        return list(self.channel.keys())[key]
    
    def channel_count(self) -> int:
        return len(self.channel)
    
    def group_count(self) -> int:
        return len(self.group)        

    def group_name(self, key: int) -> str:
        return list(self.group.keys())[key]

    def dataset_count(self) -> int:
        return len(self.datasets)
        
    def dataset_name(self, key: int) -> str:
        return list(self.datasets.keys())[key]

    def find_dataset_by_attribute_value(self, attr_name:str, attr_value:typing.Any) -> h5py.Dataset:
        for dataset in self.datasets.values():
            if attr_name in dataset.attrs:
                if dataset.attrs[attr_name] == attr_value:
                    return dataset
        return None
    
    def find_group_by_attribute_value(self, attr_name:str, attr_value:typing.Any) -> h5py.Group:
        for gr in self.group.values():
            if attr_name in gr.attrs:
                if gr.attrs[attr_name] == attr_value:
                    return gr
        return None
    
    def read_dataset_size(self) -> typing.Tuple[int, int]:
        rect_axis_size = (0,0)
        try:
            points_per_line = self.attribute['image_points_per_line']
            number_of_lines = self.attribute['image_number_of_lines']
            rect_axis_size = (points_per_line, number_of_lines)
        except KeyError:
            pass
        try:
            points_per_line = self.attribute["grid_number_of_columns"]
            number_of_lines = self.attribute["grid_number_of_rows"]
            rect_axis_size = (points_per_line, number_of_lines)   
        except KeyError:
            pass         
        try:
            points_per_line = self.attribute["rect_axis_size"][1]
            number_of_lines = self.attribute["rect_axis_size"][0]
            rect_axis_size = (points_per_line, number_of_lines)   
        except KeyError:
            pass         
        return rect_axis_size
    
    def read_dataset_range(self) -> typing.Tuple[float, float]:
        rect_axis_range = (0,0)
        try:
            range_x = self.attribute['image_size_x']
            range_y = self.attribute['image_size_y']
            rect_axis_range = (range_x, range_y)
        except KeyError:
            pass
        try:
            range_x = self.attribute["rect_axis_range"][1]
            range_y = self.attribute["rect_axis_range"][0]
            rect_axis_range = (range_x, range_y)   
        except KeyError:
            pass         
        try:
            range_x = self.attribute["grid_width"]
            range_y = self.attribute["grid_height"]
            rect_axis_range = (range_x, range_y)   
        except KeyError:
            pass         
        return rect_axis_range

    def _read_segment_structure(self):
        # read known dataset as 'channels'
        channel_identifier = 'signal_name' if self._file_hdl.version() >= (2,0) else 'name'        
        dataset_names = _get_sub_items_by_name(self._hdf_group, identifiers=[channel_identifier])
        if dataset_names:
            for dataset_id, dataset_name in dataset_names.items():
                dataset_data = self._hdf_group[dataset_id]
                self.channel[dataset_name] = NHFDataset(dataset_data)
        
        # read unknown dataset as 'group'
        self.group = _get_unidentified_sub_groups(self._hdf_group, dataset_names)
        self.datasets = _get_unidentified_sub_dataset(self._hdf_group, dataset_names)
        self._dataset_size = self.read_dataset_size()
        self._dataset_range = self.read_dataset_range()
                
    def _inject_segment_configuration_properties(self, known_identifiers: list[str]):
        for identifier in known_identifiers:
            if identifier in  self.attribute:
                segment_config = json.loads(self.attribute[identifier])
                if 'property' in segment_config:
                    for prop_name, prop_value in segment_config['property'].items():
                            if isinstance(prop_value, dict) and 'value' in prop_value:
                                try: # to create a SciVal access to property
                                    # prepare value and unit
                                    prop_value['value'] = float(prop_value['value'])
                                    if 'unit' not in prop_value:
                                        prop_value['unit'] = ""

                                    # create attribute access to properties
                                    if prop_name not in self.attribute:
                                        self.attribute[prop_name] = prop_value
                                    else:
                                        self._file_hdl.print_verbose(f"Warning: Cannot create property '{prop_name}'. Attribute already exists")
    
                                    setattr(self.property,prop_name,sci_val.SciVal(value=prop_value['value'], unit_str=prop_value['unit']))
                                except Exception:
                                    # properties seems not to be a number 
                                    if prop_name not in self.attribute:
                                        self.attribute[prop_name] = prop_value['value']
                                    else:
                                        self._file_hdl.print_verbose(f"Warning: Cannot create property '{prop_name}'. Attribute already exists")
                            else:
                                self._file_hdl.print_verbose(f"Warning: Unexpected property format of type '{type(prop_value)}' found")

class NHFMeasurement(NHFSegment):
    def __init__(self, name: str, file_hdl: 'NHFFileReader', hdf_group:h5py.Group) -> None:
        super().__init__(name, file_hdl, hdf_group)
        self.segment: dict[str, NHFSegment] = {}
        self._measurement_type = NHFMeasurementType.Undefined

    def segment_name(self, key: int) -> str:
        return list(self.segment.keys())[key]
    
    def segment_count(self) -> int:
        return len(self.segment)
    
    @property
    def measurement_type(self) -> NHFMeasurementType:
        return self._detect_group_type()
    
    def read_dataset_size(self) -> typing.Tuple[int, int]:
        size = super().read_dataset_size()
        if (0,0) == size:
            for seg in self.segment.values():
                size = seg.read_dataset_size()
                if size != (0,0):
                    break
        return size
    
    def _detect_group_type(self) -> NHFMeasurementType:
        if self._measurement_type == NHFMeasurementType.Undefined:
            if self._file_hdl.version() == (2,0):
                if 'group_type' in self.attribute:
                    current_group_type = self.attribute['group_type']
                    if current_group_type == 'image_line_based':
                        self._measurement_type = NHFMeasurementType.Image
                    elif current_group_type == 'spectroscopy':
                        self._measurement_type = NHFMeasurementType.Spectroscopy
                    elif current_group_type == 'wavemode_nma':
                        self._measurement_type = NHFMeasurementType.WaveModeNMA
                    elif current_group_type == 'calibration':
                        self._measurement_type = NHFMeasurementType.Calibration
                    else:
                        self._measurement_type = NHFMeasurementType.Unknown
            elif self._file_hdl.version() == (1,1):
                if 'measurement_type' in self.attribute:
                    current_group_type = self.attribute['measurement_type']
                    if current_group_type == 'image_line_based':
                        self._measurement_type = NHFMeasurementType.Image
                    elif current_group_type == 'spectroscopy_grid':
                        self._measurement_type = NHFMeasurementType.Spectroscopy
                    elif current_group_type == 'wavemode_nma':
                        self._measurement_type = NHFMeasurementType.WaveModeNMA
                    else:
                        self._measurement_type = NHFMeasurementType.Unknown

        if self._measurement_type == NHFMeasurementType.Unknown:
                self._file_hdl.print_verbose(f"Warning: Detecting group type for unknown file version: {self._file_hdl.version()}")
        if self._measurement_type == NHFMeasurementType.Undefined:
            self._file_hdl.print_verbose(f"Warning: measurement '{self.name}' has unknown 'group_type' = '{current_group_type}'")
        return self._measurement_type

    def _read_measurement_structure(self):
        segment_names = _get_sub_items_by_name(self._hdf_group, identifiers=['segment_name', 'name'])
        if segment_names:
            for segment_id, segment_name in segment_names.items():
                segment_data = self._hdf_group[segment_id]

                if isinstance(segment_data, h5py.Group):
                    self.segment[segment_name] = NHFSegment(segment_name, self._file_hdl, segment_data)
                    self.segment[segment_name]._read_segment_structure()
                elif isinstance(segment_data, h5py.Dataset):
                    self.channel[segment_name] = NHFDataset(segment_data)

        self.group = _get_unidentified_sub_groups(self._hdf_group, segment_names)
        self.datasets = _get_unidentified_sub_dataset(self._hdf_group, segment_names)

        self._dataset_size = self.read_dataset_size()
        self._dataset_range = self.read_dataset_range()    
        for seg in self.segment.values():
            seg._dataset_range = self._dataset_range
            seg._dataset_size = self._dataset_size

class NHFFileReader():
    """ Main class to access nhf-files """

    dataset_element_type_defined_as_int: dict = {
        0: [-(2.0**31), 2.0**31, 'dt_int32' ],
        1: [-(2.0**8) , 2.0**8 , 'dt_uint8' ],
        2: [-(2.0**16), 2.0**16, 'dt_uint16'],
        3: [-(2.0**32), 2.0**32, 'dt_uint32'],
        4: [-(2.0**64), 2.0**64, 'dt_uint64'],
        5: [-(2.0**15), 2.0**15, 'dt_int16' ],
        6: [-(2.0**64), 2.0**64, 'dt_int64' ],
        7: [       0.0, 0.0    , 'dt_double']
    }
    dataset_element_type_defined_as_str: dict = {
        'int32' : [-(2.0**31), 2.0**31, 'dt_int32' ],
        'uint8' : [-(2.0**8) , 2.0**8 , 'dt_uint8' ],
        'uint16': [-(2.0**16), 2.0**16, 'dt_uint16'],
        'uint32': [-(2.0**32), 2.0**32, 'dt_uint32'],
        'uint64': [-(2.0**64), 2.0**64, 'dt_uint64'],
        'int16' : [-(2.0**15), 2.0**15, 'dt_int16' ],
        'int64' : [-(2.0**64), 2.0**64, 'dt_int64' ],
        'double': [       0.0, 0.0    , 'dt_double']
    }
    
    def __init__(self, filename: pathlib.Path=None, verbose=False, verbose_handler=None):
        """ Provide a nhf-file path directly at creating of the class or call later read() with filename
         
        Parameters
        ----------
            verbose: bool
                Set this to True if messages during reading or accessing is desired
            
            verbose_handler: func(msg:str)
                Define an own message handler functions to redirect the messages 
                A None is provided the default message handler print the message to console
        """
        self.group: dict[str, h5py.Group] = {}        
        self.datasets: dict[str, h5py.Dataset] = {}        
        self.measurement: dict[str, NHFMeasurement] = {}
        self.attribute: dict[str, typing.Any] = {}
        self._filename = filename
        self._file_id = None
        self._last_file_version = (0,0)
        self._verbose = verbose
        self._verbose_output_handler = verbose_handler if verbose_handler else _default_verbose_output_handler
        self._last_print_verbose_message = ""
        if self._filename:
            if not self.read():
                raise IOError(self._last_print_verbose_message)
            
    def version(self) -> typing.Tuple[int, int]:
        """ returns file version information in form of (major, minor) version number. If not accessible it returns (0,0)"""
        try: 
            return self._last_file_version
        except IndexError:
            return (0,0)
        
    def read(self, filename: pathlib.Path=None) -> bool:
        """ Open the nid-file with given path for read access. """
        self._clear_data()
        if filename is not None:
            self._filename = filename
        self._filename = pathlib.Path(self._filename)
        if self._filename.is_file():
            try:
                self._file_id = h5py.File(self._filename, 'r')
                self.attribute = get_attributes(self._file_id)
                self._read_version()
                if self.version() == (1,1) or self.version() == (2,0):
                    self._read_file_structure()
                    return True
                else:
                    self.print_verbose(f"File version {self.version()} is not supported.")
                    return False
                    
            except Exception as e:
                if self._file_id is not None: 
                    self._file_id.close()
                self._file_id = None
                self._clear_data()
                self.print_verbose(f"Could not read structure of file.'\nReason: {e}")
                return False
        else:
           self.print_verbose(f"File does not exist: {self._filename}")
           return False
        
    def measurement_name(self, key: int) -> str:
        return list(self.measurement.keys())[key]
    
    def measurement_count(self) -> int:
        return len(self.measurement)
    
    def group_count(self) -> int:
        return len(self.group)        

    def group_name(self, key: int) -> str:
        return list(self.group.keys())[key]

    def dataset_count(self) -> int:
        return len(self.datasets)
        
    def dataset_name(self, key: int) -> str:
        return list(self.datasets.keys())[key]

    def print_verbose(self, msg:str):
        self._last_print_verbose_message = msg
        if self._verbose:
            self._verbose_output_handler(msg)

    def last_message(self) -> str:
        return self._last_print_verbose_message
    
    def pretty_print_structure(self):
        print(self)

    # internal functions, not for user access
    
    def _read_version(self):
        major = int(self.attribute['nsf_file_version_major'])
        minor = int(self.attribute['nsf_file_version_minor'])
        self._last_file_version = (major, minor)        

    def _read_file_structure(self):        
        measurement_identifier = 'measurement_name' if self.version() >= (2,0) else 'name'
        measurement_names = _get_sub_items_by_name(self._file_id, identifiers=[measurement_identifier])
        if measurement_names:
            for measurement_id, measurement_name in measurement_names.items():
                measurement_data = self._file_id[measurement_id]
                self.measurement[measurement_name] = NHFMeasurement(measurement_name, self, measurement_data)
                self.measurement[measurement_name]._read_measurement_structure()

        self.group = _get_unidentified_sub_groups(self._file_id, measurement_names)
        self.datasets = _get_unidentified_sub_dataset(self._file_id, measurement_names)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._clear_data()
        if self._file_id:
            self._file_id.close()
        self._file_id = None

    def __str__(self) -> str:
        structure = ""
        if self.measurement_count() > 0:
            for m_name, m_class in self.measurement.items():
                structure += f"Measurement '{m_name}' of type '{m_class.measurement_type.name}':\n"
                if m_class.segment_count() > 0:
                    for s_name, s_class in m_class.segment.items():
                        structure += f"    Segment '{s_name}':\n"
                        if s_class.channel_count() > 0:
                            for g_name in s_class.channel.keys():
                                structure += f"        Channel '{g_name}':\n"
                        if s_class.group_count() > 0:
                            for g_name in s_class.group.keys():
                                structure += f"        Group '{g_name}':\n"
                        if s_class.dataset_count() > 0:
                            for d_name in s_class.datasets.keys():
                                structure += f"        Dataset '{d_name}':\n"
                if m_class.channel_count() > 0:
                    for g_name in m_class.channel.keys():
                        structure += f"    Channel '{g_name}':\n"
                if m_class.group_count() > 0:
                    for g_name in m_class.group.keys():
                        structure += f"    Group '{g_name}':\n"
                if m_class.dataset_count() > 0:
                    for d_name in m_class.datasets.keys():
                        structure += f"    Dataset '{d_name}':\n"
        if self.group_count() > 0:
            for g_name in self.group.keys():
                structure += f"Group '{g_name}':\n"
        if self.dataset_count() > 0:
            for d_name in self.datasets.keys():
                structure += f"Dataset '{d_name}':\n"
        return structure

    def __del__(self):
        if self._file_id:
            self._file_id.close()
        self._file_id = None

    def _clear_data(self):
        self.group: dict[str, h5py.Group] = {}
        self.measurement: dict[str, NHFMeasurement] = {}
        self.attribute: dict[str, typing.Any] = {}
