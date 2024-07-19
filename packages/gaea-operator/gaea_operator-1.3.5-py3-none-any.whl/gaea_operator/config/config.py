#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2024/2/26
# @Author  : yanxiaodong
# @File    : config.py
"""
from typing import Dict
import copy
import os
from abc import ABCMeta
import bcelogger

from gaea_tracker import ExperimentTracker
from windmillclient.client.windmill_client import WindmillClient
from windmillmodelv1.client.model_api_model import ModelMetadata, InputSize

from gaea_operator.utils import DEFAULT_TRANSFORM_CONFIG_FILE_NAME, Accelerator
from .generate_transform_config import generate_transform_config, KEY_CONTAIN_PREPROCESS
from .modify_package_files import ModifyPackageFiles
from .generate_transform_config import KEY_EVAL_SIZE, \
    KEY_EVAL_WIDTH, \
    KEY_EVAL_HEIGHT, \
    KEY_MAX_BATCH_SIZE, \
    KEY_MAX_BOX_NUM

KEY_NETWORK_ARCHITECTURE = 'networkArchitecture'


class Config(metaclass=ABCMeta):
    """
    Config write for train, transform and package.
    """
    accelerator2model_format = {Accelerator.T4: "TensorRT",
                                Accelerator.A100: "TensorRT",
                                Accelerator.V100: "TensorRT",
                                Accelerator.A10: "TensorRT",
                                Accelerator.A800: "TensorRT",
                                Accelerator.R200: "PaddleLite"}

    def __init__(self, windmill_client: WindmillClient, tracker_client: ExperimentTracker, metadata: Dict = {}):
        self.windmill_client = windmill_client
        self.tracker_client = tracker_client
        self._metadata = metadata

    @property
    def metadata(self):
        """
        Get metadata.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict):
        """
        Set metadata.
        """
        self._metadata = ModelMetadata(**value).dict()

    def write_train_config(self,
                           dataset_uri: str,
                           model_uri: str,
                           advanced_parameters: dict,
                           pretrain_model_uri: str):
        """
        Config write for train.
        """
        pass

    def write_eval_config(self, dataset_uri: str, model_uri: str, ):
        """
        Config write for eval.
        """
        pass

    def write_transform_config(self, model_uri: str, advanced_parameters: dict):
        """
        Config write for transform.
        """
        cfg_path = os.path.join(model_uri, DEFAULT_TRANSFORM_CONFIG_FILE_NAME)
        self._update_transform_metadata(advanced_parameters)

        generate_transform_config(advanced_parameters, cfg_path, self.metadata)

    def write_model_config(self, transform_model_uri: str, advanced_parameters: dict):
        """
        Config write for transform model.
        """
        network_architecture = self.metadata["algorithmParameters"].get(KEY_NETWORK_ARCHITECTURE, "")
        bcelogger.info('network architecture: {}'.format(network_architecture))
        contain_preprocess = advanced_parameters.get(KEY_CONTAIN_PREPROCESS, "true")
        cfg = ModifyPackageFiles(metadata=self.metadata, transform_model_uri=transform_model_uri)
        cfg.modify_model_config(network_architecture=network_architecture, contain_preprocess=contain_preprocess)

    def write_relate_config(self,
                            model_repo: str,
                            model_display_name: str,
                            template_ensemble_name: str,
                            template_ensemble_version: str,
                            ensemble_name: str,
                            sub_models: dict,
                            model_name: str,
                            template_model_name: str,
                            is_new_ensemble_model: bool = True,
                            extra_models: dict = None,
                            is_update_labels: bool = True):
        """
        Config write for connect model.
        """
        network_architecture = self.metadata["algorithmParameters"].get(KEY_NETWORK_ARCHITECTURE, "")
        bcelogger.info('network architecture: {}'.format(network_architecture))
        cfg = ModifyPackageFiles(sub_models=sub_models,
                                 extra_models=extra_models,
                                 metadata=self.metadata,
                                 model_repo=model_repo,
                                 template_ensemble_name=template_ensemble_name,
                                 template_ensemble_version=template_ensemble_version)
        modify_sub_models, modify_extra_models = cfg.write_relate_config(model_name=model_name,
                                                                         ensemble_name=ensemble_name,
                                                                         template_model_name=template_model_name,
                                                                         model_display_name=model_display_name,
                                                                         network_architecture=network_architecture,
                                                                         is_update_labels=is_update_labels)

        new_sub_models = copy.deepcopy(sub_models)
        new_extra_models = copy.deepcopy(extra_models)
        if is_new_ensemble_model:
            new_sub_models.update(new_extra_models)
            for name, version in new_sub_models.items():
                if name == template_model_name:
                    continue
                if name in sub_models:
                    modify_sub_models[name] = version
                if name in extra_models:
                    modify_extra_models[name] = version

        return modify_sub_models, modify_extra_models

    def write_ensemble_config(self,
                              model_repo: str,
                              sub_models: dict,
                              model_name_pairs: dict,
                              ensemble_name: str,
                              ensemble_version: str,
                              extra_models: dict = None):
        """
        Config write for ensemble.
        """
        cfg = ModifyPackageFiles(sub_models=sub_models,
                                 extra_models=extra_models,
                                 metadata=self.metadata,
                                 model_repo=model_repo,
                                 template_ensemble_name=ensemble_name,
                                 template_ensemble_version=ensemble_version)
        return cfg.modify_ensemble_config(model_name_pairs=model_name_pairs)

    def _update_train_metadata(self, advanced_parameters: Dict):
        meta_data = ModelMetadata(experimentName=self.tracker_client.experiment_name,
                                  jobName=self.tracker_client.job_name,
                                  algorithmParameters={KEY_NETWORK_ARCHITECTURE:
                                                           str(advanced_parameters[KEY_NETWORK_ARCHITECTURE])},
                                  experimentRunID=self.tracker_client.run_id)
        self._metadata = meta_data.dict()

    def _update_transform_metadata(self, advanced_parameters: Dict):
        if KEY_EVAL_SIZE in advanced_parameters:
            width, height = advanced_parameters.pop(KEY_EVAL_SIZE).split('*')
            advanced_parameters[KEY_EVAL_WIDTH] = width
            advanced_parameters[KEY_EVAL_HEIGHT] = height

        input_size = InputSize(width=int(advanced_parameters[KEY_EVAL_WIDTH]),
                               height=int(advanced_parameters[KEY_EVAL_HEIGHT]))

        meta_data = ModelMetadata(**self._metadata)
        meta_data.inputSize = input_size
        meta_data.experimentName = self.tracker_client.experiment_name
        meta_data.jobName = self.tracker_client.job_name
        meta_data.experimentRunID = self.tracker_client.run_id
        maxBoxNum = int(advanced_parameters[KEY_MAX_BOX_NUM]) \
            if KEY_MAX_BOX_NUM in advanced_parameters else 1
        meta_data.maxBoxNum = maxBoxNum
        advanced_parameters = {
            'inferenceMaxBatchSize': str(advanced_parameters[KEY_MAX_BATCH_SIZE]),
            KEY_NETWORK_ARCHITECTURE: str(advanced_parameters[KEY_NETWORK_ARCHITECTURE]),
            'maxBoxNum': str(maxBoxNum)}

        if meta_data.algorithmParameters is None:
            meta_data.algorithmParameters = advanced_parameters
        else:
            meta_data.algorithmParameters.update(advanced_parameters)

        self._metadata = meta_data.dict()
