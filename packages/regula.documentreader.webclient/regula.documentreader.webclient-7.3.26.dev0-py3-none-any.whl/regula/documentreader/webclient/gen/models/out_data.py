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
class OutData(object):
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
        'url': 'str',
        'images': 'list[OutDataTransactionImagesFieldValue]'
    }

    attribute_map = {
        'url': 'url',
        'images': 'images'
    }

    def __init__(self, url=None, images=None, local_vars_configuration=None):  # noqa: E501
        """OutData - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._url = None
        self._images = None
        self.discriminator = None

        if url is not None:
            self.url = url
        if images is not None:
            self.images = images

    @property
    def url(self):
        """Gets the url of this OutData.  # noqa: E501

        Response url  # noqa: E501

        :return: The url of this OutData.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this OutData.

        Response url  # noqa: E501

        :param url: The url of this OutData.  # noqa: E501
        :type url: str
        """

        self._url = url

    @property
    def images(self):
        """Gets the images of this OutData.  # noqa: E501


        :return: The images of this OutData.  # noqa: E501
        :rtype: list[OutDataTransactionImagesFieldValue]
        """
        return self._images

    @images.setter
    def images(self, images):
        """Sets the images of this OutData.


        :param images: The images of this OutData.  # noqa: E501
        :type images: list[OutDataTransactionImagesFieldValue]
        """

        self._images = images

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
        if not isinstance(other, OutData):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OutData):
            return True

        return self.to_dict() != other.to_dict()
