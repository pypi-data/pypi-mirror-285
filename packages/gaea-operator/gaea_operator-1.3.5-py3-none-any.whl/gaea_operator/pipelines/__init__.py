#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py
"""
from gaea_operator.pipelines.ocrnet_pipeline.pipeline import pipeline as ocrnet_pipeline
from gaea_operator.pipelines.ppyoloe_plus_pipeline.pipeline import pipeline as ppyoloe_plus_pipeline
from gaea_operator.pipelines.resnet_pipeline.pipeline import pipeline as resnet_pipeline
from gaea_operator.pipelines.change_ppyoloe_plus_pipeline.pipeline import pipeline as change_ppyoloe_plus_pipeline
from gaea_operator.pipelines.change_ocrnet_pipeline.pipeline import pipeline as change_ocrnet_pipeline
from gaea_operator.pipelines.codetr_pipeline.pipeline import pipeline as codetr_pipeline

category_to_ppls = {
    "Image/SemanticSegmentation": [ocrnet_pipeline],
    "Image/ObjectDetection": [ppyoloe_plus_pipeline, codetr_pipeline],
    "Image/ImageClassification/MultiClass": [resnet_pipeline],
    "Image/ChangeDetection/ObjectDetection": [change_ppyoloe_plus_pipeline],
    "Image/ChangeDetection/SemanticSegmentation": [change_ocrnet_pipeline]
}

name_to_display_name = {
    "ocrnet": "通用语义分割模型",
    "ppyoloe_plus": "通用目标检测模型",
    "resnet": "轻量级分类模型",
    "change_ppyoloe_plus": "通用变化检测模型",
    "change_ocrnet": "通用变化分割模型",
    "codetr": "高精度目标检测模型"
}

name_to_local_name = {
    "ocrnet": "SemanticSegmentation",
    "ppyoloe_plus": "ObjectDetection",
    "resnet": "LightClassification",
    "change_ppyoloe_plus": "ChangeObjectDetection",
    "change_ocrnet": "ChangeSemanticSegmentation",
    "codetr": "HighPrecisionObjectDetection"
}
