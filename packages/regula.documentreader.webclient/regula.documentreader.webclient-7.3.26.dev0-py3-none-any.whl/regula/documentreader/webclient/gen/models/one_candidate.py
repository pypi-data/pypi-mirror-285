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
Contains information about one document type candidate
"""
class OneCandidate(object):
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
        'document_name': 'str',
        'id': 'int',
        'p': 'float',
        'rfid_presence': 'RfidLocation',
        'fdsid_list': 'FDSIDList',
        'necessary_lights': 'int',
        'check_authenticity': 'int',
        'uv_exp': 'int',
        'authenticity_necessary_lights': 'int'
    }

    attribute_map = {
        'document_name': 'DocumentName',
        'id': 'ID',
        'p': 'P',
        'rfid_presence': 'RFID_Presence',
        'fdsid_list': 'FDSIDList',
        'necessary_lights': 'NecessaryLights',
        'check_authenticity': 'CheckAuthenticity',
        'uv_exp': 'UVExp',
        'authenticity_necessary_lights': 'AuthenticityNecessaryLights'
    }

    def __init__(self, document_name=None, id=None, p=None, rfid_presence=None, fdsid_list=None, necessary_lights=None, check_authenticity=None, uv_exp=None, authenticity_necessary_lights=None, local_vars_configuration=None):  # noqa: E501
        """OneCandidate - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._document_name = None
        self._id = None
        self._p = None
        self._rfid_presence = None
        self._fdsid_list = None
        self._necessary_lights = None
        self._check_authenticity = None
        self._uv_exp = None
        self._authenticity_necessary_lights = None
        self.discriminator = None

        if document_name is not None:
            self.document_name = document_name
        if id is not None:
            self.id = id
        if p is not None:
            self.p = p
        if rfid_presence is not None:
            self.rfid_presence = rfid_presence
        if fdsid_list is not None:
            self.fdsid_list = fdsid_list
        if necessary_lights is not None:
            self.necessary_lights = necessary_lights
        if check_authenticity is not None:
            self.check_authenticity = check_authenticity
        if uv_exp is not None:
            self.uv_exp = uv_exp
        if authenticity_necessary_lights is not None:
            self.authenticity_necessary_lights = authenticity_necessary_lights

    @property
    def document_name(self):
        """Gets the document_name of this OneCandidate.  # noqa: E501

        Document name  # noqa: E501

        :return: The document_name of this OneCandidate.  # noqa: E501
        :rtype: str
        """
        return self._document_name

    @document_name.setter
    def document_name(self, document_name):
        """Sets the document_name of this OneCandidate.

        Document name  # noqa: E501

        :param document_name: The document_name of this OneCandidate.  # noqa: E501
        :type document_name: str
        """

        self._document_name = document_name

    @property
    def id(self):
        """Gets the id of this OneCandidate.  # noqa: E501

        Unique document type template identifier (Regula's internal numeric code)  # noqa: E501

        :return: The id of this OneCandidate.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OneCandidate.

        Unique document type template identifier (Regula's internal numeric code)  # noqa: E501

        :param id: The id of this OneCandidate.  # noqa: E501
        :type id: int
        """

        self._id = id

    @property
    def p(self):
        """Gets the p of this OneCandidate.  # noqa: E501

        A measure of the likelihood of correct recognition in the analysis of this type of document  # noqa: E501

        :return: The p of this OneCandidate.  # noqa: E501
        :rtype: float
        """
        return self._p

    @p.setter
    def p(self, p):
        """Sets the p of this OneCandidate.

        A measure of the likelihood of correct recognition in the analysis of this type of document  # noqa: E501

        :param p: The p of this OneCandidate.  # noqa: E501
        :type p: float
        """
        if (self.local_vars_configuration.client_side_validation and
                p is not None and p > 1):  # noqa: E501
            raise ValueError("Invalid value for `p`, must be a value less than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                p is not None and p < 0):  # noqa: E501
            raise ValueError("Invalid value for `p`, must be a value greater than or equal to `0`")  # noqa: E501

        self._p = p

    @property
    def rfid_presence(self):
        """Gets the rfid_presence of this OneCandidate.  # noqa: E501


        :return: The rfid_presence of this OneCandidate.  # noqa: E501
        :rtype: RfidLocation
        """
        return self._rfid_presence

    @rfid_presence.setter
    def rfid_presence(self, rfid_presence):
        """Sets the rfid_presence of this OneCandidate.


        :param rfid_presence: The rfid_presence of this OneCandidate.  # noqa: E501
        :type rfid_presence: RfidLocation
        """

        self._rfid_presence = rfid_presence

    @property
    def fdsid_list(self):
        """Gets the fdsid_list of this OneCandidate.  # noqa: E501


        :return: The fdsid_list of this OneCandidate.  # noqa: E501
        :rtype: FDSIDList
        """
        return self._fdsid_list

    @fdsid_list.setter
    def fdsid_list(self, fdsid_list):
        """Sets the fdsid_list of this OneCandidate.


        :param fdsid_list: The fdsid_list of this OneCandidate.  # noqa: E501
        :type fdsid_list: FDSIDList
        """

        self._fdsid_list = fdsid_list

    @property
    def necessary_lights(self):
        """Gets the necessary_lights of this OneCandidate.  # noqa: E501

        Combination of lighting scheme identifiers (Light enum) required to conduct OCR for this type of document  # noqa: E501

        :return: The necessary_lights of this OneCandidate.  # noqa: E501
        :rtype: int
        """
        return self._necessary_lights

    @necessary_lights.setter
    def necessary_lights(self, necessary_lights):
        """Sets the necessary_lights of this OneCandidate.

        Combination of lighting scheme identifiers (Light enum) required to conduct OCR for this type of document  # noqa: E501

        :param necessary_lights: The necessary_lights of this OneCandidate.  # noqa: E501
        :type necessary_lights: int
        """

        self._necessary_lights = necessary_lights

    @property
    def check_authenticity(self):
        """Gets the check_authenticity of this OneCandidate.  # noqa: E501

        Set of authentication options provided for this type of document (combination of Authenticity enum)  # noqa: E501

        :return: The check_authenticity of this OneCandidate.  # noqa: E501
        :rtype: int
        """
        return self._check_authenticity

    @check_authenticity.setter
    def check_authenticity(self, check_authenticity):
        """Sets the check_authenticity of this OneCandidate.

        Set of authentication options provided for this type of document (combination of Authenticity enum)  # noqa: E501

        :param check_authenticity: The check_authenticity of this OneCandidate.  # noqa: E501
        :type check_authenticity: int
        """

        self._check_authenticity = check_authenticity

    @property
    def uv_exp(self):
        """Gets the uv_exp of this OneCandidate.  # noqa: E501

        The required exposure value of the camera when receiving images of a document of this type for a UV lighting scheme  # noqa: E501

        :return: The uv_exp of this OneCandidate.  # noqa: E501
        :rtype: int
        """
        return self._uv_exp

    @uv_exp.setter
    def uv_exp(self, uv_exp):
        """Sets the uv_exp of this OneCandidate.

        The required exposure value of the camera when receiving images of a document of this type for a UV lighting scheme  # noqa: E501

        :param uv_exp: The uv_exp of this OneCandidate.  # noqa: E501
        :type uv_exp: int
        """

        self._uv_exp = uv_exp

    @property
    def authenticity_necessary_lights(self):
        """Gets the authenticity_necessary_lights of this OneCandidate.  # noqa: E501

        Combination of lighting scheme identifiers (combination of Light enum) needed to perform all authenticity checks specified in CheckAuthenticity  # noqa: E501

        :return: The authenticity_necessary_lights of this OneCandidate.  # noqa: E501
        :rtype: int
        """
        return self._authenticity_necessary_lights

    @authenticity_necessary_lights.setter
    def authenticity_necessary_lights(self, authenticity_necessary_lights):
        """Sets the authenticity_necessary_lights of this OneCandidate.

        Combination of lighting scheme identifiers (combination of Light enum) needed to perform all authenticity checks specified in CheckAuthenticity  # noqa: E501

        :param authenticity_necessary_lights: The authenticity_necessary_lights of this OneCandidate.  # noqa: E501
        :type authenticity_necessary_lights: int
        """

        self._authenticity_necessary_lights = authenticity_necessary_lights

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
        if not isinstance(other, OneCandidate):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, OneCandidate):
            return True

        return self.to_dict() != other.to_dict()
