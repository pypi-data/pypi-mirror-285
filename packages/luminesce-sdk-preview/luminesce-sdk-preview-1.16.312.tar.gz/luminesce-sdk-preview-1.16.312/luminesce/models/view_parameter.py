# coding: utf-8

"""
    FINBOURNE Luminesce Web API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 1.16.312
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from luminesce.configuration import Configuration


class ViewParameter(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'name': 'str',
        'data_type': 'DataType',
        'value': 'str',
        'is_table_data_mandatory': 'bool',
        'description': 'str'
    }

    attribute_map = {
        'name': 'name',
        'data_type': 'dataType',
        'value': 'value',
        'is_table_data_mandatory': 'isTableDataMandatory',
        'description': 'description'
    }

    required_map = {
        'name': 'required',
        'data_type': 'required',
        'value': 'required',
        'is_table_data_mandatory': 'optional',
        'description': 'optional'
    }

    def __init__(self, name=None, data_type=None, value=None, is_table_data_mandatory=None, description=None, local_vars_configuration=None):  # noqa: E501
        """ViewParameter - a model defined in OpenAPI"
        
        :param name:  Name of the provider (required)
        :type name: str
        :param data_type:  (required)
        :type data_type: luminesce.DataType
        :param value:  Value of the provider (required)
        :type value: str
        :param is_table_data_mandatory:  Should this be selected? False would imply it is only being filtered on.  Ignored when Aggregations are present
        :type is_table_data_mandatory: bool
        :param description:  Description of the parameter
        :type description: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._data_type = None
        self._value = None
        self._is_table_data_mandatory = None
        self._description = None
        self.discriminator = None

        self.name = name
        self.data_type = data_type
        self.value = value
        if is_table_data_mandatory is not None:
            self.is_table_data_mandatory = is_table_data_mandatory
        self.description = description

    @property
    def name(self):
        """Gets the name of this ViewParameter.  # noqa: E501

        Name of the provider  # noqa: E501

        :return: The name of this ViewParameter.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ViewParameter.

        Name of the provider  # noqa: E501

        :param name: The name of this ViewParameter.  # noqa: E501
        :type name: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 256):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) < 0):
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `0`")  # noqa: E501

        self._name = name

    @property
    def data_type(self):
        """Gets the data_type of this ViewParameter.  # noqa: E501


        :return: The data_type of this ViewParameter.  # noqa: E501
        :rtype: luminesce.DataType
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Sets the data_type of this ViewParameter.


        :param data_type: The data_type of this ViewParameter.  # noqa: E501
        :type data_type: luminesce.DataType
        """
        if self.local_vars_configuration.client_side_validation and data_type is None:  # noqa: E501
            raise ValueError("Invalid value for `data_type`, must not be `None`")  # noqa: E501

        self._data_type = data_type

    @property
    def value(self):
        """Gets the value of this ViewParameter.  # noqa: E501

        Value of the provider  # noqa: E501

        :return: The value of this ViewParameter.  # noqa: E501
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this ViewParameter.

        Value of the provider  # noqa: E501

        :param value: The value of this ViewParameter.  # noqa: E501
        :type value: str
        """
        if self.local_vars_configuration.client_side_validation and value is None:  # noqa: E501
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                value is not None and len(value) > 256):
            raise ValueError("Invalid value for `value`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                value is not None and len(value) < 0):
            raise ValueError("Invalid value for `value`, length must be greater than or equal to `0`")  # noqa: E501

        self._value = value

    @property
    def is_table_data_mandatory(self):
        """Gets the is_table_data_mandatory of this ViewParameter.  # noqa: E501

        Should this be selected? False would imply it is only being filtered on.  Ignored when Aggregations are present  # noqa: E501

        :return: The is_table_data_mandatory of this ViewParameter.  # noqa: E501
        :rtype: bool
        """
        return self._is_table_data_mandatory

    @is_table_data_mandatory.setter
    def is_table_data_mandatory(self, is_table_data_mandatory):
        """Sets the is_table_data_mandatory of this ViewParameter.

        Should this be selected? False would imply it is only being filtered on.  Ignored when Aggregations are present  # noqa: E501

        :param is_table_data_mandatory: The is_table_data_mandatory of this ViewParameter.  # noqa: E501
        :type is_table_data_mandatory: bool
        """

        self._is_table_data_mandatory = is_table_data_mandatory

    @property
    def description(self):
        """Gets the description of this ViewParameter.  # noqa: E501

        Description of the parameter  # noqa: E501

        :return: The description of this ViewParameter.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ViewParameter.

        Description of the parameter  # noqa: E501

        :param description: The description of this ViewParameter.  # noqa: E501
        :type description: str
        """
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) > 256):
            raise ValueError("Invalid value for `description`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 0):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `0`")  # noqa: E501

        self._description = description

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ViewParameter):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ViewParameter):
            return True

        return self.to_dict() != other.to_dict()
