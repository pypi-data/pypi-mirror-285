#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/27
# @Author  : yanxiaodong
# @File    : accelerator.py
"""
from typing import Dict
from abc import ABCMeta, abstractmethod


class Accelerator(metaclass=ABCMeta):
    """
    Accelerator
    """
    T4 = "T4"
    V100 = "V100"
    A100 = "A100"
    A10 = "A10"
    A800 = "A800"
    R200 = "R200"

    NVIDIA = "Nvidia"
    KUNLUN = "Kunlun"

    def __init__(self, kind: str = None, name: str = "T4"):
        self.name = name
        self.image = ""
        self.args = None
        self.env = None

        self._kind = kind

    @property
    def get_name(self):
        """
        Name
        """
        if self.name is None:
            return self.T4
        return self.name

    @property
    def get_names(self):
        """
        Name
        """
        return [self.T4, self.V100, self.A100, self.A10, self.A800, self.R200]

    @property
    def get_kind(self):
        """
        Kind
        """
        if self._kind is None:
            name_list = self.name.split("/", maxsplit=1)
            if len(name_list) > 1:
                self._kind = name_list[0]
            elif len(name_list) == 1:
                if self.name in [self.T4, self.V100, self.A100, self.A10, self.A800]:
                    self._kind = self.NVIDIA
                else:
                    self._kind = self.KUNLUN
            else:
                self._kind = self.KUNLUN
        return self._kind

    def set_image(self, name_to_image: Dict = None):
        """
        Set image
        """
        if name_to_image is not None:
            self.image = name_to_image.get(self.name, self.image)

    def suggest_image(self):
        """
        Suggest image
        """
        return self.image

    def suggest_env(self):
        """
        Suggest env
        """
        return self.env

    def suggest_args(self):
        """
        Suggest args
        """
        return self.args

    @abstractmethod
    def suggest_flavours(self):
        """
        Suggest flavours
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_flavour_tips(self):
        """
        Suggest flavours
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        raise NotImplementedError()

    @abstractmethod
    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        raise NotImplementedError()


class NvidiaAccelerator(Accelerator):
    """
    Nvidia Accelerator
    """
    def __init__(self, kind: str = None, name: str = "T4"):
        super().__init__(kind=kind, name=name)
        self.image = \
            "iregistry.baidu-int.com/acg_aiqp_algo/triton-inference-server/triton_r22_12_nvidia_infer_trt86:1.4.6"
        self.args = {"backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"}
        self.env = \
            {
                "LD_LIBRARY_PATH":
                    "/usr/local/cuda/compat/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/opt/tritonserver/lib",
                "PATH": "/opt/tritonserver/bin:/usr/local/mpi/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:"
                        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/ucx/bin"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = [{"name": "c4m16gpu1", "display_name": "CPU: 4核 内存: 16Gi GPU: 1卡"},
                        {"name": "c8m32gpu1", "display_name": "CPU: 8核 内存: 32Gi GPU: 1卡"},
                        {"name": "c8m32gpu2", "display_name": "CPU: 8核 内存: 32Gi GPU: 2卡"},
                        {"name": "c16m64gpu2", "display_name": "CPU: 16核 内存: 64Gi GPU: 2卡"},
                        {"name": "c16m32gpu4", "display_name": "CPU: 16核 内存: 32Gi GPU: 4卡"},
                        {"name": "c16m64gpu4", "display_name": "CPU: 16核 内存: 64Gi GPU: 4卡"},
                        {"name": "c32m96gpu4", "display_name": "CPU: 32核 内存: 96Gi GPU: 4卡"}]

        return flavour_list

    def suggest_flavour_tips(self):
        """
        Suggest flavour tips
        """
        return "gpu"

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """
        resource = {"accelerator": self.name,
                    "gpu": "75",
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}
        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "args": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        return ["config.maxResources.scalarResources.nvidia.com/gpu>1"]


class KunlunAccelerator(Accelerator):
    """
    Kunlun Accelerator
    """
    def __init__(self, kind: str = None, name: str = "R200"):
        super().__init__(kind=kind, name=name)
        self.image = "iregistry.baidu-int.com/acg_aiqp_algo/triton-inference-server/triton_r22_12_kunlun_infer:2.2.4"
        self.args = {"backend-config": "tensorrt,plugins=/opt/tritonserver/lib/libmmdeploy_tensorrt_ops.so"}
        self.env = \
            {
                "LD_LIBRARY_PATH": "/opt/tritonserver/lib",
                "XTCL_L3_SIZE": "16776192"
            }

    def suggest_flavours(self):
        """
        Suggest flavours
        """
        flavour_list = [{"name": "c4m16xpu1", "display_name": "CPU: 4核 内存: 16Gi XPU: 1卡"}]
        return flavour_list

    def suggest_flavour_tips(self):
        """
        Suggest flavour tips
        """
        return "xpu"

    def suggest_model_server_parameters(self):
        """
        Suggest model server parameters
        """

        resource = {"accelerator": self.name,
                    "gpu": "7500",
                    "limits": {"cpu": "10", "mem": "10Gi"},
                    "requests": {"cpu": "100m", "mem": "50Mi"}}
        model_server_parameters = {
            "image": self.image,
            "env": self.env,
            "backend": self.args,
            "resource": resource}

        return model_server_parameters

    def suggest_resource_tips(self):
        """
        Suggest resource tips
        """
        return ["config.maxResources.scalarResources.baidu.com/xpu-mem>1"]


def get_accelerator(name: str = Accelerator.T4, kind: str = None) -> Accelerator:
    """
    Get accelerator.
    """
    if kind == Accelerator.NVIDIA:
        return NvidiaAccelerator(kind=kind, name=name)
    if kind == Accelerator.KUNLUN:
        return KunlunAccelerator(kind=kind, name=name)

    if name in (Accelerator.T4, Accelerator.V100, Accelerator.A100, Accelerator.A10, Accelerator.A800):
        return NvidiaAccelerator(name=name)
    elif name in (Accelerator.R200,):
        return KunlunAccelerator(name=name)
    else:
        raise Exception("Unsupported accelerator: {}".format(name))