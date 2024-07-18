import inspect
import logging
from types import AsyncGeneratorType, GeneratorType
from typing import Any, Callable

from pydantic import BaseModel

from ._depends import SchedulingDepends


class TaskSignature:
    def __init__(self, identifier: str, name: str, func: Callable):
        self.__identifier = identifier
        self.__name = name
        self.__func = func

    def get_arguments(
        self,
        parameters: BaseModel,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        specs = {}
        generators = {}
        signature = inspect.signature(self.__func)

        for name, param in signature.parameters.items():
            match param.default:
                case SchedulingDepends():
                    value = param.default.dependency()

                    if isinstance(value, (GeneratorType, AsyncGeneratorType)):
                        generators[name] = value
                    else:
                        specs[name] = value

                    continue

            match param.annotation:
                case logging.Logger:
                    specs[name] = logging.getLogger(f'scheduling.{self.__identifier}')
                case parameters.__class__:
                    specs[name] = parameters.model_copy(deep=True)

        return specs, generators
