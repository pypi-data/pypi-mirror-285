# coding: utf-8

"""
    Generated by: https://openapi-generator.tech
"""

import pprint
import re  # noqa: F401

import six

from regula.documentreader.webclient.gen.configuration import Configuration
# this line was added to enable pycharm type hinting
from regula.documentreader.webclient.gen.models import *


"""

"""
class Point(object):
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
    """
    openapi_types = {
        'x': 'int',
        'y': 'int'
    }

    attribute_map = {
        'x': 'x',
        'y': 'y'
    }

    def __init__(self, x=None, y=None, local_vars_configuration=None):  # noqa: E501
        """Point - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._x = None
        self._y = None
        self.discriminator = None

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

    @property
    def x(self):
        """Gets the x of this Point.  # noqa: E501


        :return: The x of this Point.  # noqa: E501
        :rtype: int
        """
        return self._x

    @x.setter
    def x(self, x):
        """Sets the x of this Point.


        :param x: The x of this Point.  # noqa: E501
        :type x: int
        """

        self._x = x

    @property
    def y(self):
        """Gets the y of this Point.  # noqa: E501


        :return: The y of this Point.  # noqa: E501
        :rtype: int
        """
        return self._y

    @y.setter
    def y(self, y):
        """Sets the y of this Point.


        :param y: The y of this Point.  # noqa: E501
        :type y: int
        """

        self._y = y

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Point):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Point):
            return True

        return self.to_dict() != other.to_dict()
