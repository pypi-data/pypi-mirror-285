#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/12
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from typing import List

from ..base_node import BaseNode
from ..types import Properties
from gaea_operator.artifacts import Variable
from gaea_operator.utils import Accelerator, get_accelerator


class Train(BaseNode):
    """
    Train
    """
    NAME = "train"
    DISPLAY_NAME = "模型训练"

    def __init__(self, train_skip: int = -1):
        accelerator = get_accelerator(kind=Accelerator.NVIDIA)
        compute_tips = {Accelerator.NVIDIA: ["training", "tags.usage=train"] + accelerator.suggest_resource_tips()}
        flavour_tips = {Accelerator.NVIDIA: accelerator.suggest_flavour_tips()}

        properties = Properties(accelerator=accelerator.get_name,
                                computeTips=compute_tips,
                                flavourTips=flavour_tips,
                                modelFormats={
                                    Accelerator.NVIDIA: {f"{self.name()}.model_name": ["PaddlePaddle", "PyTorch"]}
                                })

        outputs: List[Variable] = \
            [
                Variable(type="model",
                         name="output_model_uri",
                         displayName="模型训练后的模型",
                         key=f"{self.name()}.model_name",
                         value="train.output_model_uri")
            ]

        super().__init__(outputs=outputs, properties=properties)
        self.train_skip = train_skip

    def suggest_compute_tips(self):
        """
        suggest compute tips
        """
        return self.properties.computeTips[get_accelerator(self.properties.accelerator).get_kind]

    def __call__(self, *args, **kwargs):
        pass