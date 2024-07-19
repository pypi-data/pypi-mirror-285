#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/3/12
# @Author  : yanxiaodong
# @File    : __init__.py.py
"""
from typing import List, Dict
from paddleflow.pipeline import ContainerStep

from ..base_node import BaseNode
from ..types import Properties
from gaea_operator.artifacts import Variable
from gaea_operator.utils import Accelerator, get_accelerator


class Eval(BaseNode):
    """
    Train
    """
    NAME = "eval"
    DISPLAY_NAME = "模型评估"

    def __init__(self, eval_skip: int = -1, pre_nodes: Dict[str, ContainerStep] = None):
        accelerator = get_accelerator(kind=Accelerator.NVIDIA)
        compute_tips = {Accelerator.NVIDIA: ["training", "tags.usage=train"] + accelerator.suggest_resource_tips()}
        flavour_tips = {Accelerator.NVIDIA: accelerator.suggest_flavour_tips()}

        properties = Properties(accelerator=accelerator.get_name,
                                computeTips=compute_tips,
                                flavourTips=flavour_tips,
                                modelFormats={
                                    Accelerator.NVIDIA: {f"{self.name()}.model_name": ["PaddlePaddle", "PyTorch"]}
                                })

        inputs: List[Variable] = \
            [
                Variable(type="model", name="input_model_uri", value="train.output_model_uri")
            ]
        outputs: List[Variable] = \
            [
                Variable(type="dataset",
                         name="output_dataset_uri",
                         displayName="模型评估的数据集",
                         value="eval.output_dataset_uri"),
                Variable(type="model",
                         name="output_model_uri",
                         displayName="模型评估后的模型",
                         key=f"{self.name()}.model_name",
                         value="eval.output_model_uri")
            ]

        super().__init__(inputs=inputs, outputs=outputs, properties=properties)
        self.eval_skip = eval_skip
        self.pre_nodes = pre_nodes

    def suggest_compute_tips(self):
        """
        suggest compute tips
        """
        return self.properties.computeTips[get_accelerator(self.properties.accelerator).get_kind]

    def __call__(self, *args, **kwargs):
        pass