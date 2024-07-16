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


class FileReaderBuilderResponse(object):
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
        'query': 'str',
        'error': 'str',
        'columns': 'list[ColumnInfo]',
        'data': 'object'
    }

    attribute_map = {
        'query': 'query',
        'error': 'error',
        'columns': 'columns',
        'data': 'data'
    }

    required_map = {
        'query': 'optional',
        'error': 'optional',
        'columns': 'optional',
        'data': 'optional'
    }

    def __init__(self, query=None, error=None, columns=None, data=None, local_vars_configuration=None):  # noqa: E501
        """FileReaderBuilderResponse - a model defined in OpenAPI"
        
        :param query:  The generated SQL
        :type query: str
        :param error:  The error from running generated SQL Query, if any
        :type error: str
        :param columns:  Column information for the results
        :type columns: list[luminesce.ColumnInfo]
        :param data:  The resulting data from running the Query
        :type data: object

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._query = None
        self._error = None
        self._columns = None
        self._data = None
        self.discriminator = None

        self.query = query
        self.error = error
        self.columns = columns
        self.data = data

    @property
    def query(self):
        """Gets the query of this FileReaderBuilderResponse.  # noqa: E501

        The generated SQL  # noqa: E501

        :return: The query of this FileReaderBuilderResponse.  # noqa: E501
        :rtype: str
        """
        return self._query

    @query.setter
    def query(self, query):
        """Sets the query of this FileReaderBuilderResponse.

        The generated SQL  # noqa: E501

        :param query: The query of this FileReaderBuilderResponse.  # noqa: E501
        :type query: str
        """

        self._query = query

    @property
    def error(self):
        """Gets the error of this FileReaderBuilderResponse.  # noqa: E501

        The error from running generated SQL Query, if any  # noqa: E501

        :return: The error of this FileReaderBuilderResponse.  # noqa: E501
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error):
        """Sets the error of this FileReaderBuilderResponse.

        The error from running generated SQL Query, if any  # noqa: E501

        :param error: The error of this FileReaderBuilderResponse.  # noqa: E501
        :type error: str
        """

        self._error = error

    @property
    def columns(self):
        """Gets the columns of this FileReaderBuilderResponse.  # noqa: E501

        Column information for the results  # noqa: E501

        :return: The columns of this FileReaderBuilderResponse.  # noqa: E501
        :rtype: list[luminesce.ColumnInfo]
        """
        return self._columns

    @columns.setter
    def columns(self, columns):
        """Sets the columns of this FileReaderBuilderResponse.

        Column information for the results  # noqa: E501

        :param columns: The columns of this FileReaderBuilderResponse.  # noqa: E501
        :type columns: list[luminesce.ColumnInfo]
        """

        self._columns = columns

    @property
    def data(self):
        """Gets the data of this FileReaderBuilderResponse.  # noqa: E501

        The resulting data from running the Query  # noqa: E501

        :return: The data of this FileReaderBuilderResponse.  # noqa: E501
        :rtype: object
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this FileReaderBuilderResponse.

        The resulting data from running the Query  # noqa: E501

        :param data: The data of this FileReaderBuilderResponse.  # noqa: E501
        :type data: object
        """

        self._data = data

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
        if not isinstance(other, FileReaderBuilderResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FileReaderBuilderResponse):
            return True

        return self.to_dict() != other.to_dict()
