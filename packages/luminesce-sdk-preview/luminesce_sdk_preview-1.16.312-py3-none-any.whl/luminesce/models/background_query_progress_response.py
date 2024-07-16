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


class BackgroundQueryProgressResponse(object):
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
        'has_data': 'bool',
        'row_count': 'int',
        'status': 'TaskStatus',
        'state': 'BackgroundQueryState',
        'progress': 'str',
        'feedback': 'list[FeedbackEventArgs]',
        'query': 'str',
        'query_name': 'str',
        'columns_available': 'list[Column]'
    }

    attribute_map = {
        'has_data': 'hasData',
        'row_count': 'rowCount',
        'status': 'status',
        'state': 'state',
        'progress': 'progress',
        'feedback': 'feedback',
        'query': 'query',
        'query_name': 'queryName',
        'columns_available': 'columnsAvailable'
    }

    required_map = {
        'has_data': 'optional',
        'row_count': 'optional',
        'status': 'optional',
        'state': 'optional',
        'progress': 'optional',
        'feedback': 'optional',
        'query': 'optional',
        'query_name': 'optional',
        'columns_available': 'optional'
    }

    def __init__(self, has_data=None, row_count=None, status=None, state=None, progress=None, feedback=None, query=None, query_name=None, columns_available=None, local_vars_configuration=None):  # noqa: E501
        """BackgroundQueryProgressResponse - a model defined in OpenAPI"
        
        :param has_data:  Is there currently data for this Query?
        :type has_data: bool
        :param row_count:  Number of rows of data held. -1 if none as yet.
        :type row_count: int
        :param status: 
        :type status: luminesce.TaskStatus
        :param state: 
        :type state: luminesce.BackgroundQueryState
        :param progress:  The full progress log (up to this point at least)
        :type progress: str
        :param feedback:  Individual Feedback Messages (to replace Progress).  A given message will be returned from only one call.
        :type feedback: list[luminesce.FeedbackEventArgs]
        :param query:  The LuminesceSql of the original request
        :type query: str
        :param query_name:  The QueryName given in the original request
        :type query_name: str
        :param columns_available:  When HasData is true this is the schema of columns that will be returned if the data is requested
        :type columns_available: list[luminesce.Column]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._has_data = None
        self._row_count = None
        self._status = None
        self._state = None
        self._progress = None
        self._feedback = None
        self._query = None
        self._query_name = None
        self._columns_available = None
        self.discriminator = None

        if has_data is not None:
            self.has_data = has_data
        if row_count is not None:
            self.row_count = row_count
        if status is not None:
            self.status = status
        if state is not None:
            self.state = state
        self.progress = progress
        self.feedback = feedback
        self.query = query
        self.query_name = query_name
        self.columns_available = columns_available

    @property
    def has_data(self):
        """Gets the has_data of this BackgroundQueryProgressResponse.  # noqa: E501

        Is there currently data for this Query?  # noqa: E501

        :return: The has_data of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: bool
        """
        return self._has_data

    @has_data.setter
    def has_data(self, has_data):
        """Sets the has_data of this BackgroundQueryProgressResponse.

        Is there currently data for this Query?  # noqa: E501

        :param has_data: The has_data of this BackgroundQueryProgressResponse.  # noqa: E501
        :type has_data: bool
        """

        self._has_data = has_data

    @property
    def row_count(self):
        """Gets the row_count of this BackgroundQueryProgressResponse.  # noqa: E501

        Number of rows of data held. -1 if none as yet.  # noqa: E501

        :return: The row_count of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: int
        """
        return self._row_count

    @row_count.setter
    def row_count(self, row_count):
        """Sets the row_count of this BackgroundQueryProgressResponse.

        Number of rows of data held. -1 if none as yet.  # noqa: E501

        :param row_count: The row_count of this BackgroundQueryProgressResponse.  # noqa: E501
        :type row_count: int
        """

        self._row_count = row_count

    @property
    def status(self):
        """Gets the status of this BackgroundQueryProgressResponse.  # noqa: E501


        :return: The status of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: luminesce.TaskStatus
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this BackgroundQueryProgressResponse.


        :param status: The status of this BackgroundQueryProgressResponse.  # noqa: E501
        :type status: luminesce.TaskStatus
        """

        self._status = status

    @property
    def state(self):
        """Gets the state of this BackgroundQueryProgressResponse.  # noqa: E501


        :return: The state of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: luminesce.BackgroundQueryState
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this BackgroundQueryProgressResponse.


        :param state: The state of this BackgroundQueryProgressResponse.  # noqa: E501
        :type state: luminesce.BackgroundQueryState
        """

        self._state = state

    @property
    def progress(self):
        """Gets the progress of this BackgroundQueryProgressResponse.  # noqa: E501

        The full progress log (up to this point at least)  # noqa: E501

        :return: The progress of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: str
        """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """Sets the progress of this BackgroundQueryProgressResponse.

        The full progress log (up to this point at least)  # noqa: E501

        :param progress: The progress of this BackgroundQueryProgressResponse.  # noqa: E501
        :type progress: str
        """

        self._progress = progress

    @property
    def feedback(self):
        """Gets the feedback of this BackgroundQueryProgressResponse.  # noqa: E501

        Individual Feedback Messages (to replace Progress).  A given message will be returned from only one call.  # noqa: E501

        :return: The feedback of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: list[luminesce.FeedbackEventArgs]
        """
        return self._feedback

    @feedback.setter
    def feedback(self, feedback):
        """Sets the feedback of this BackgroundQueryProgressResponse.

        Individual Feedback Messages (to replace Progress).  A given message will be returned from only one call.  # noqa: E501

        :param feedback: The feedback of this BackgroundQueryProgressResponse.  # noqa: E501
        :type feedback: list[luminesce.FeedbackEventArgs]
        """

        self._feedback = feedback

    @property
    def query(self):
        """Gets the query of this BackgroundQueryProgressResponse.  # noqa: E501

        The LuminesceSql of the original request  # noqa: E501

        :return: The query of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: str
        """
        return self._query

    @query.setter
    def query(self, query):
        """Sets the query of this BackgroundQueryProgressResponse.

        The LuminesceSql of the original request  # noqa: E501

        :param query: The query of this BackgroundQueryProgressResponse.  # noqa: E501
        :type query: str
        """

        self._query = query

    @property
    def query_name(self):
        """Gets the query_name of this BackgroundQueryProgressResponse.  # noqa: E501

        The QueryName given in the original request  # noqa: E501

        :return: The query_name of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: str
        """
        return self._query_name

    @query_name.setter
    def query_name(self, query_name):
        """Sets the query_name of this BackgroundQueryProgressResponse.

        The QueryName given in the original request  # noqa: E501

        :param query_name: The query_name of this BackgroundQueryProgressResponse.  # noqa: E501
        :type query_name: str
        """

        self._query_name = query_name

    @property
    def columns_available(self):
        """Gets the columns_available of this BackgroundQueryProgressResponse.  # noqa: E501

        When HasData is true this is the schema of columns that will be returned if the data is requested  # noqa: E501

        :return: The columns_available of this BackgroundQueryProgressResponse.  # noqa: E501
        :rtype: list[luminesce.Column]
        """
        return self._columns_available

    @columns_available.setter
    def columns_available(self, columns_available):
        """Sets the columns_available of this BackgroundQueryProgressResponse.

        When HasData is true this is the schema of columns that will be returned if the data is requested  # noqa: E501

        :param columns_available: The columns_available of this BackgroundQueryProgressResponse.  # noqa: E501
        :type columns_available: list[luminesce.Column]
        """

        self._columns_available = columns_available

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
        if not isinstance(other, BackgroundQueryProgressResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BackgroundQueryProgressResponse):
            return True

        return self.to_dict() != other.to_dict()
