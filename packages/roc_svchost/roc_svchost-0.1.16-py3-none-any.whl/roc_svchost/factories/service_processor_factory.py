"""
Service processor factory
"""
import importlib
import sys
from types import ModuleType
from typing import Optional, Tuple
import traceback
import inspect
import subprocess
from glob import glob
from os import path
from dataclasses import dataclass
from rococo.messaging import BaseServiceProcessor
import importlib.metadata
from roc_svchost.logger import Logger
from .config_factory import Config
from roc_svchost import utils


logger = Logger().get_logger()


@dataclass(kw_only=True)
class ProcessorInfo:
    type: str
    queue_name: str
    version: str


def get_service_processor(config: Config) -> Optional[Tuple[BaseServiceProcessor, ProcessorInfo]]:
    """
    Dynamically imports the service processor
    """
    result = subprocess.run("poetry version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout.strip().split(' ')
        processor_package = output[0]
        processor_version = output[1]
    else:
        processor_package = find_processor_package_name("/app/svc")
        processor_version = importlib.metadata.version(processor_package)

    processor_module = f"{processor_package}.processor" if processor_package is not None else config.processor_module
    logger.info(f"processor_module: {processor_module}")

    try:
        # Dynamically import the module
        module = importlib.import_module(processor_module)

        processor_type = find_processor_type(module)
        if processor_type is None:
            processor_type = config.processor_type
        logger.info(f"processor_type: {processor_type}")

        # Access the class from the imported module
        dynamic_class = getattr(module, processor_type)

        # Create an instance of the dynamic class with the specified parameters
        instance = dynamic_class(*config.service_constructor_params)

        return instance, ProcessorInfo(
            type=processor_type,
            queue_name=config.get_env_var("QUEUE_NAME_PREFIX") + config.get_env_var(f'{processor_type}_QUEUE_NAME'),
            version=processor_version)

    except ImportError as e:
        logger.error("Error: Module '%s' not found. Error: %s",processor_module,e)
        logger.error(traceback.format_exc())
        logger.error(traceback.format_stack())
    except AttributeError as e:
        logger.error("Error: Class '%s' not found in module '%s'. Error: %s",
                      processor_type, processor_module,e)
        logger.error(traceback.format_exc())
        logger.error(traceback.format_stack())
    return None


def find_processor_package_name(search_root_dir: str) -> str:
    search_pattern = path.join(search_root_dir, "**", "processor.py")
    processor_path = utils.first(glob(search_pattern, recursive=True))

    if processor_path is not None:
        parts: list = processor_path.removeprefix(search_root_dir).split(path.sep)
        parts.remove('')
        # return f"{parts[0]}.processor" if len(parts) > 0 else None
        return parts[0] if len(parts) > 0 else None


def find_processor_type(module: ModuleType):
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj is not BaseServiceProcessor and issubclass(obj, BaseServiceProcessor):
            return name
