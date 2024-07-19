# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""This module defines the EngineName and TaskType enums."""
from enum import Enum
from typing import Dict, List, Optional


class EngineName(str, Enum):
    """Enum representing the names of the engines."""

    HF = "hf"
    VLLM = "vllm"
    MII = "mii"
    MII_V1 = "mii-v1"

    def __str__(self):
        """Return the string representation of the engine name."""
        return self.value


class ExtraParameters:
    """Extra parameter options."""

    KEY = "extra-parameters"
    ERROR = "error"
    DROP = "drop"
    PASS_THROUGH = "pass-through"
    OPTIONS = [ERROR, DROP, PASS_THROUGH]


class CommonAPI:
    """Common api constants."""

    CHAT_COMPLETION_TAG = "chat-completion"

    MODELS_TAGGS_MAPPING = {
        "mistralai/Mistral-7B-Instruct-v0.2": CHAT_COMPLETION_TAG,
        "mistralai/Mixtral-8x7B-Instruct-v0.1": CHAT_COMPLETION_TAG,
        "mistralai/Mixtral-8x22B-Instruct-v0.1": CHAT_COMPLETION_TAG,
        "Llama-2-7b-chat": CHAT_COMPLETION_TAG,
        "Llama-2-13b-chat": CHAT_COMPLETION_TAG,
        "Llama-2-70b-chat": CHAT_COMPLETION_TAG,
        "Meta-Llama-3-8B-Instruct": CHAT_COMPLETION_TAG,
        "Meta-Llama-3-70B-Instruct": CHAT_COMPLETION_TAG,
        "Phi-3-mini-4k-instruct": CHAT_COMPLETION_TAG,
        "Phi-3-mini-128k-instruct": CHAT_COMPLETION_TAG,
        "Phi-3-medium-4k-instruct": CHAT_COMPLETION_TAG,
        "Phi-3-medium-128k-instruct": CHAT_COMPLETION_TAG,
        "Phi-3-small-8k-instruct": CHAT_COMPLETION_TAG,
        "Phi-3-small-128k-instruct": CHAT_COMPLETION_TAG,
        "Phi-3-vision-128k-instruct": CHAT_COMPLETION_TAG
    }


class MetaData:
    """metadata keys."""

    MODEL_NAME = "base_model_name"
    MODEL_PROVIDER = "model_provider_name"


class ModelInfo:
    """Model info."""

    MODEL_NAME = "model_name"
    MODEL_PROVIDER = "model_provider_name"
    MODEL_TYPE = "model_type"


class TaskType(str, Enum):
    """Enum representing the types of tasks."""

    TEXT_GENERATION = "text-generation"
    CONVERSATIONAL = "conversational"
    TEXT_TO_IMAGE = "text-to-image"
    TEXT_CLASSIFICATION = "text-classification"
    TEXT_CLASSIFICATION_MULTILABEL = "text-classification-multilabel"
    NER = "text-named-entity-recognition"
    SUMMARIZATION = "text-summarization"
    QnA = "question-answering"
    TRANSLATION = "text-translation"
    TEXT_GENERATION_CODE = "text-generation-code"
    FILL_MASK = "fill-mask"
    CHAT_COMPLETION = "chat-completion"
    TEXT_TO_IMAGE_INPAINTING = "text-to-image-inpainting"

    def __str__(self):
        """Return the string representation of the task type."""
        return self.value


class SupportedTask:
    """Supported tasks by text-generation-inference."""

    TEXT_GENERATION = "text-generation"
    CHAT_COMPLETION = "chat-completion"
    TEXT_TO_IMAGE = "text-to-image"
    TEXT_CLASSIFICATION = "text-classification"
    TEXT_CLASSIFICATION_MULTILABEL = "text-classification-multilabel"
    NER = "token-classification"
    SUMMARIZATION = "summarization"
    QnA = "question-answering"
    TRANSLATION = "translation"
    TEXT_GENERATION_CODE = "text-generation-code"
    FILL_MASK = "fill-mask"
    TEXT_TO_IMAGE_INPAINTING = "text-to-image-inpainting"


class ServerSetupParams:
    """Parameters for setting up the server."""

    WAIT_TIME_MIN = 15  # time to wait for the server to become healthy
    DEFAULT_WORKER_COUNT = 1


class VLLMSupportedModels:
    """VLLM Supported Models List."""

    Models = {
        "ArcticForCausalLM",
        "AquilaForCausalLM",
        "BaiChuanForCausalLM",
        "BloomForCausalLM",
        "ChatGLMModel",
        "DeciLMForCausalLM",
        "FalconForCausalLM",
        "GemmaForCausalLM",
        "GPT2LMHeadModel",
        "GPTBigCodeForCausalLM",
        "GPTJForCausalLM",
        "GPTNeoXForCausalLM",
        "InternLMForCausalLM",
        "InternLM2ForCausalLM",
        "LlamaForCausalLM",
        "MistralForCausalLM",
        "MixtralForCausalLM",
        "MPTForCausalLM",
        "OLMoForCausalLM",
        "OPTForCausalLM",
        "OrionForCausalLM",
        "QWenLMHeadModel",
        "Qwen2ForCausalLM",
        "RWForCausalLM",
        "StableLmForCausalLM",
        "DbrxForCausalLM",
        "PhiForCausalLM",
        "Phi3ForCausalLM",
        "Phi3VForCausalLM",
        "Phi3SmallForCausalLM",
        "Phi3VForCausalLM",
        "YakForCausalLM"
    }


class MIISupportedModels:
    """MII Supported Models."""

    # TODO: Add more models from different tasks

    Models = {
        "BloomForCausalLM",
        "GPT2LMHeadModel",
        "GPTBigCodeForCausalLM",
        "GPTJForCausalLM",
        "GPTNeoXForCausalLM",
        "LlamaForCausalLM",
        "OPTForCausalLM",
        "FalconForCausalLM",
        "MistralForCausalLM",
        "MixtralForCausalLM",
        "PhiForCausalLM",
        "QWenLMHeadModel"
    }


class VLLMSpecialModels:
    """Models Types that require additional parameters to work with vllm."""

    # TODO: Remove "RefinedWebModel" and "RefinedWeb" once falcon models are updated to latest huggingface commit

    ModelTypes = {
        "falcon": {"kwargs": {"gpu-memory-utilization": .95}, "args": ["trust-remote-code"]},
        "RefinedWebModel": {"kwargs": {"gpu-memory-utilization": .95}, "args": ["trust-remote-code"]},
        "RefinedWeb": {"kwargs": {"gpu-memory-utilization": .95}, "args": ["trust-remote-code"]},
        "dbrx": {"args": ["trust-remote-code"]},
        "deci_lm": {"args": ["trust-remote-code"]},
        "phi": {"args": ["trust-remote-code"]},
        "phi3": {"kwargs": {"tensor-parallel-size": 1}, "args": ["trust-remote-code"]},
        "phi3small": {"kwargs": {"tensor-parallel-size": 1}, "args": ["trust-remote-code"]},
        "phi3_v": {
            "kwargs": {"tensor-parallel-size": 2, "gpu-memory-utilization": .95,
                       "image-input-type": "pixel_values", "image-token-id": 32044,
                       "image-openai": "phi3v_single_image", "image-input-shape": "1,3,336,336",
                       "image-feature-size": 2509},
            "args": ["trust-remote-code"]
        },
        "yak": {"kwargs": {"quantization": "yq"}},
        "artic": {"kwargs": {"quantization": "deepspeedfp"}, "args": ["trust-remote-code"]}
    }

    Models = {
        "microsoft/phi-3-mini-4k-instruct": {"kwargs": {"tensor-parallel-size": 1}},
        "microsoft/phi-3-mini-128k-instruct": {"kwargs": {"tensor-parallel-size": 1}},
        "microsoft/phi-3-small-8k-instruct": {"kwargs": {"tensor-parallel-size": 1}},
        "microsoft/phi-3-small-128k-instruct": {"kwargs": {"tensor-parallel-size": 1}},
        "microsoft/phi-3-medium-4k-instruct": {"kwargs": {"tensor-parallel-size": 1}},
        "microsoft/phi-3-medium-128k-instruct": {"kwargs": {"tensor-parallel-size": 2}}
    }

    @classmethod
    def get_kwargs(cls, model_type: str, model_name: Optional[str]) -> Dict:
        """Get the kwargs the vllm server needs for the given model."""
        kwargs = cls.ModelTypes.get(model_type, {}).get("kwargs", {})
        model_specific_kwargs = cls.Models.get(model_name, {}).get("kwargs", {})
        kwargs.update(model_specific_kwargs)
        return kwargs

    @classmethod
    def get_args(cls, model_type: str, model_name: Optional[str]) -> List:
        """Get the args the vllm server needs for the given model."""
        args = cls.ModelTypes.get(model_type, {}).get("args", [])
        model_specific_args = cls.Models.get(model_name, {}).get("args", [])
        args.extend(model_specific_args)
        return args


class MIIGenerationParams:
    """MII Generation Parameters."""

    MIIGenerationParams = {
        "prompt_length": ("Length of the input prompt. Autopopulated when creating requests, any user-provided values"
                          " will be ignored."),
        "max_length": "Maximum length of `input_tokens` + `generated_tokens`.",
        "max_new_tokens": "Maximum number of new tokens generated. `max_length` takes precedent.",
        "min_new_tokens": "Minimum number of new tokens generated.",
        "stream": "Enable streaming output.",
        "ignore_eos": "Ignore EoS token and continue generating text until we reach `max_length` or`max_new_tokens`.",
        "return_full_text": "Prepends the input prompt to the generated text.",
        "do_sample": "When `False`, do greedy sampling.",
        "top_p": "Top P value.",
        "top_k": "Top K value.",
        "temperature": "Temperature value.",
        "stop": "List of strings to stop generation at."
    }


ALL_TASKS = [
    SupportedTask.TEXT_TO_IMAGE,
    SupportedTask.TEXT_CLASSIFICATION,
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL,
    SupportedTask.NER,
    SupportedTask.SUMMARIZATION,
    SupportedTask.QnA,
    SupportedTask.TRANSLATION,
    SupportedTask.FILL_MASK,
    SupportedTask.TEXT_GENERATION,
    SupportedTask.CHAT_COMPLETION,
]

VLLM_MII_TASKS = [
    SupportedTask.TEXT_GENERATION,
    SupportedTask.CHAT_COMPLETION,
    TaskType.CONVERSATIONAL
]

MULTILABEL_SET = [
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL,
]

CLASSIFICATION_SET = [
    SupportedTask.TEXT_CLASSIFICATION,
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL
]

MULTIPLE_OUTPUTS_SET = [
    SupportedTask.NER,
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL
]


class ModelTypes:
    """Model types."""

    PHI3_V = "phi3_v"
