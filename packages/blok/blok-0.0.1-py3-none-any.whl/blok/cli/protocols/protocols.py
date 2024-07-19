from pydantic import BaseModel
from typing import List
import typing as t
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
from pathlib import Path


@dataclass
class CLIOptions:
    subcommand: str
    show_default: t.Union[bool, str, None] = None
    prompt: t.Union[bool, str] = False
    confirmation_prompt: t.Union[bool, str] = False
    prompt_required: bool = True
    hide_input: bool = False
    is_flag: t.Optional[bool] = None
    flag_value: t.Optional[t.Any] = None
    multiple: bool = False
    count: bool = False
    allow_from_autoenv: bool = True
    help: t.Optional[str] = None
    hidden: bool = False
    show_choices: bool = True
    show_envvar: bool = False
    type: t.Optional[t.Union[t.Any, t.Any]] = None
    required: bool = False
    default: t.Optional[t.Union[t.Any, t.Callable[[], t.Any]]] = None
    callback: t.Optional[t.Callable[[t.Any, t.Any, t.Any], t.Any]] = None
    nargs: t.Optional[int] = None
    multiple: bool = False
    metavar: t.Optional[str] = None
    expose_value: bool = True
    is_eager: bool = False
    shell_complete: t.Optional[
        t.Callable[
            [t.Any, t.Any, str],
            t.Union[t.List[t.Any], t.List[str]],
        ]
    ] = None


@dataclass
class BuildContext:
    docker_compose: dict
    file_tree: dict
    env: dict

@dataclass
class InitContext:
    values: dict
    dependencies: dict
    


@runtime_checkable
class DockerService(Protocol):
    def get_identifier(self) -> str:
        raise NotImplementedError("This method must be implemented by the subclass")

    def get_dependencies(self) -> List[str]:
        raise NotImplementedError("This method must be implemented by the subclass")

    def build(self, context: ExecutionContext):
        raise NotImplementedError("This method must be implemented by the subclass")

    def init(self, kwargs: t.Dict[str, t.Any], deps: t.Dict[str, "DockerService"]):
        raise NotImplementedError("This method must be implemented by the subclass")

    def get_options(self, name: str) -> List[CLIOptions]:
        raise NotImplementedError("This method must be implemented by the subclass")



def protocol(name: str):

    def decorator(cls):
        cls.__service_identifier__ = name

    
        return cls

    return runtime_checkable(decorator)



def implementatoin(name: str, dependencies: List[str] = [], options: List[CLIOptions] = []):

    def decorator(cls):
        cls.__service_identifier__ = name

        if not hasattr(cls, "get_identifier"):
            cls.get_identifier = lambda self: name

        if not hasattr(cls, "get_dependencies"):
            cls.get_dependencies = lambda self: self.dependencies

        if not hasattr(cls, "get_options"):
            cls.get_options = lambda self: self.options

        if not hasattr(cls, "build"):
            raise NotImplementedError("The build method must be implemented to build the service")
        
        if not hasattr(cls, "init"):
            raise NotImplementedError("The init method must be implemented to initialize the service")
        

        return cls
    
    return decorator
    