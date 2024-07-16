# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fabric_cf.orchestrator.swagger_server.models.base_model_ import Model
from fabric_cf.orchestrator.swagger_server import util


class PoaPostDataVcpuCpuMap(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, vcpu: str=None, cpu: str=None):  # noqa: E501
        """PoaPostDataVcpuCpuMap - a model defined in Swagger

        :param vcpu: The vcpu of this PoaPostDataVcpuCpuMap.  # noqa: E501
        :type vcpu: str
        :param cpu: The cpu of this PoaPostDataVcpuCpuMap.  # noqa: E501
        :type cpu: str
        """
        self.swagger_types = {
            'vcpu': str,
            'cpu': str
        }

        self.attribute_map = {
            'vcpu': 'vcpu',
            'cpu': 'cpu'
        }
        self._vcpu = vcpu
        self._cpu = cpu

    @classmethod
    def from_dict(cls, dikt) -> 'PoaPostDataVcpuCpuMap':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The poa_post_data_vcpu_cpu_map of this PoaPostDataVcpuCpuMap.  # noqa: E501
        :rtype: PoaPostDataVcpuCpuMap
        """
        return util.deserialize_model(dikt, cls)

    @property
    def vcpu(self) -> str:
        """Gets the vcpu of this PoaPostDataVcpuCpuMap.


        :return: The vcpu of this PoaPostDataVcpuCpuMap.
        :rtype: str
        """
        return self._vcpu

    @vcpu.setter
    def vcpu(self, vcpu: str):
        """Sets the vcpu of this PoaPostDataVcpuCpuMap.


        :param vcpu: The vcpu of this PoaPostDataVcpuCpuMap.
        :type vcpu: str
        """
        if vcpu is None:
            raise ValueError("Invalid value for `vcpu`, must not be `None`")  # noqa: E501

        self._vcpu = vcpu

    @property
    def cpu(self) -> str:
        """Gets the cpu of this PoaPostDataVcpuCpuMap.


        :return: The cpu of this PoaPostDataVcpuCpuMap.
        :rtype: str
        """
        return self._cpu

    @cpu.setter
    def cpu(self, cpu: str):
        """Sets the cpu of this PoaPostDataVcpuCpuMap.


        :param cpu: The cpu of this PoaPostDataVcpuCpuMap.
        :type cpu: str
        """
        if cpu is None:
            raise ValueError("Invalid value for `cpu`, must not be `None`")  # noqa: E501

        self._cpu = cpu
