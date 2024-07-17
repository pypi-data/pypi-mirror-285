from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Optional
from textwrap import dedent
import datetime

import re

from toolshop.core.logging import logger


class Parameter(BaseModel):
    model_config = dict(extra="forbid") # No extra fields allowed

    name: str
    type: str 
    description: Optional[str] = None
    required: bool = True


class Documentation(BaseModel):
    model_config = dict(extra="forbid") # No extra fields allowed

    description: str
    parameters: Optional[list[Parameter]] = None
    usage: Optional[str] = None

    def __post_init__(self):
        MAX_OPENAI_DESCRIPTION_LENGTH = 1024

        if len(self.description) > MAX_OPENAI_DESCRIPTION_LENGTH:
            raise ValueError(f"Description is too long.  Max length is {MAX_OPENAI_DESCRIPTION_LENGTH}.")

    def __str__(self):
        parameter_string = "Args:\n"
        for p in self.parameters:
            if not p.required:
                type_string = f"{p.type}, optional"
            else:
                type_string = p.type
            
            parameter_string += f"    {p.name} ({type_string}): {p.description}\n"

        doc = dedent(self.description)
        doc += "\n\n" + dedent(parameter_string)

        if self.usage:
            doc += "\n\n" + dedent(self.usage)

        return doc


class Tool(ABC):
    def __init__(self, state = None, require_confirmation: bool = None):
        self.__name__ = self._camel_to_snake(self.__class__.__name__)
        self._state = state
        
        if hasattr(self, "_require_confirmation"):
            self.require_confirmation = getattr(self, "_require_confirmation")
        
        if require_confirmation is not None:
            self.require_confirmation = require_confirmation
        
        if self.call.__doc__:
            self.__doc__ = self.call.__doc__  
        

        MAX_OPENAI_DESCRIPTION_LENGTH = 1024

        if len(self.__doc__) > MAX_OPENAI_DESCRIPTION_LENGTH:
            raise ValueError(
              f"Description is too long "
              f"for tool {self.__name__}. Max length is "
              f"{MAX_OPENAI_DESCRIPTION_LENGTH} but current."
              f"description length is {len(self.__doc__)}."
            )


    @abstractmethod
    def call(self, *args, **kwargs):
        pass

    @staticmethod
    def _camel_to_snake(name):
        "Convert camel-case to snake-case."
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @property
    def state(self):
        if self._state:
            return self._state
        else:
            class NoOp:
                def __getattr__(self, name):
                    logger.info(f"No shared state provided for the tool. Ignoring call to self.state.{name} by returning a no-op function.")
                    return lambda *args, **kwargs: None

            return NoOp()

    def return_result_to_agent(self):
        if hasattr(self, "_return_result_to_agent"):
            return self._return_result_to_agent
        else:
            return True
    
    def log_header(self):
        logger.info(f"=== {self.__name__}() ===")

    def log_params(self, *args, **kwargs):
        if args:
            logger.info(f"args: {args}")

        if kwargs:
            kwarg_items = sorted(kwargs.items(), key=lambda x: len(str(x[1])))

            for k, v in kwarg_items:
                if isinstance(v, str) and "\n" in v:
                    logger.info(f"{k}:\n{v}")
                else:
                    logger.info(f"{k}: {v}")

    def log_result(self, result):
        logger.info(f"\nresult:\n{result}")

    def log_footer(self, result):
        logger.info("=" * len(f"=== {self.__name__}() ==="))

    def post_call_hook(self):
        pass

    def __call__(self, *args, **kwargs):
        self.log_header()
        self.log_params(*args, **kwargs)

        if hasattr(self, 'require_confirmation') and self.require_confirmation:
            confirmation = input(f"Do you want to allow agent to run {self.__name__}?  Type 'yes' to allow: ")
            if confirmation != "yes":
                raise Exception(f"Request to run {self.__name__} was denied by the user.")

        result = self.call(*args, **kwargs)
        self.log_result(result)
        self.log_footer(result)
    
        if self.state.get_result_to_file():
            with open(self.state.get_result_to_file(), 'w') as f:
                f.write(str(result))
            
            self.state.disable_result_to_file()
        
        self.post_call_hook()

        if self.return_result_to_agent():
            return result

    def get_partial(self):
        import inspect

        # Create a new function that wraps 'self.__call__' following the exact signature of 'call'
        def partial_func(*args, **kwargs):
            return self.__call__(*args, **kwargs)

        partial_func.__signature__ = inspect.signature(self.call)
        partial_func.__doc__ = self.call.__doc__
        partial_func.__annotations__ = self.call.__annotations__
        partial_func.__name__ = self.__name__

        return partial_func

    def to_marvin(self):
        return self.get_partial()


class State:
    def __init__(self):
        self.file_read_at = {}
        self.file_updated_at = {}
        self.coder_confirms = 0
    
    def record_file_read(self, file_path: str):
        self.file_read_at[file_path] = datetime.datetime.now()
    
    def record_file_update(self, file_path: str):
        self.file_updated_at[file_path] = datetime.datetime.now()
    
    def record_confirm(self):
        self.coder_confirms += 1
    
    def raise_error_if_this_file_has_not_been_read_since_it_was_last_updated(self, file_path):
        if file_path not in self.file_read_at:
            raise ValueError("You must read the file before writing to it.")
        
        if file_path in self.file_updated_at and self.file_updated_at[file_path] > self.file_read_at[file_path]:
            raise ValueError(f"File {file_path} must be re-read first.")

    def enable_result_to_file(self, path):
        self._result_to_file = path

    def get_result_to_file(self):
        if hasattr(self, "_result_to_file"):
            return self._result_to_file
        else:
            return None

    def disable_result_to_file(self):
        self._result_to_file = None