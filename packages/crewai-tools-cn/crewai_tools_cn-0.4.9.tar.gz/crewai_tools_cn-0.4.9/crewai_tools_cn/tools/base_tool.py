from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Type

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, ConfigDict, Field, validator
from pydantic.v1 import BaseModel as V1BaseModel


class BaseTool(BaseModel, ABC):
    class _ArgsSchemaPlaceholder(V1BaseModel):
        pass

    model_config = ConfigDict()

    name: str
    """工具的唯一名称，清楚地表明其用途。"""
    description: str
    """用于告诉模型如何/何时/为什么使用该工具。"""
    args_schema: Type[V1BaseModel] = Field(default_factory=_ArgsSchemaPlaceholder)
    """工具接受的参数的架构。"""
    description_updated: bool = False
    """用于检查描述是否已更新的标志。"""
    cache_function: Optional[Callable] = lambda _args, _result: True
    """用于确定是否应该缓存工具的函数，应返回一个布尔值。如果为 None，则将缓存该工具。"""
    result_as_answer: bool = False
    """用于检查该工具是否应该是最终代理答案的标志。"""

    @validator("args_schema", always=True, pre=True)
    def _default_args_schema(cls, v: Type[V1BaseModel]) -> Type[V1BaseModel]:
        if not isinstance(v, cls._ArgsSchemaPlaceholder):
            return v

        return type(
            f"{cls.__name__}Schema",
            (V1BaseModel,),
            {
                "__annotations__": {
                    k: v for k, v in cls._run.__annotations__.items() if k != "return"
                },
            },
        )

    def model_post_init(self, __context: Any) -> None:
        self._generate_description()

        super().model_post_init(__context)

    def run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        print(f"正在使用工具：{self.name}")
        return self._run(*args, **kwargs)

    @abstractmethod
    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """工具的实际实现。"""

    def to_langchain(self) -> StructuredTool:
        self._set_args_schema()
        return StructuredTool(
            name=self.name,
            description=self.description,
            args_schema=self.args_schema,
            func=self._run,
        )

    def _set_args_schema(self):
        if self.args_schema is None:
            class_name = f"{self.__class__.__name__}Schema"
            self.args_schema = type(
                class_name,
                (V1BaseModel,),
                {
                    "__annotations__": {
                        k: v
                        for k, v in self._run.__annotations__.items()
                        if k != "return"
                    },
                },
            )

    def _generate_description(self):
        args = []
        args_description = []
        for arg, attribute in self.args_schema.schema()["properties"].items():
            if "type" in attribute:
                args.append(f"{arg}: '{attribute['type']}'")
            if "description" in attribute:
                args_description.append(f"{arg}: '{attribute['description']}'")

        description = self.description.replace("\n", " ")
        self.description = f"{self.name}({', '.join(args)}) - {description} {', '.join(args_description)}"


class Tool(BaseTool):
    func: Callable
    """调用工具时将执行的函数。"""

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


def to_langchain(
    tools: list[BaseTool | StructuredTool],
) -> list[StructuredTool]:
    return [t.to_langchain() if isinstance(t, BaseTool) else t for t in tools]


def tool(*args):
    """
    用于从函数创建工具的装饰器。
    """

    def _make_with_name(tool_name: str) -> Callable:
        def _make_tool(f: Callable) -> BaseTool:
            if f.__doc__ is None:
                raise ValueError("函数必须有一个文档字符串")
            if f.__annotations__ is None:
                raise ValueError("函数必须有类型注释")

            class_name = "".join(tool_name.split()).title()
            args_schema = type(
                class_name,
                (V1BaseModel,),
                {
                    "__annotations__": {
                        k: v for k, v in f.__annotations__.items() if k != "return"
                    },
                },
            )

            return Tool(
                name=tool_name,
                description=f.__doc__,
                func=f,
                args_schema=args_schema,
            )

        return _make_tool

    if len(args) == 1 and callable(args[0]):
        return _make_with_name(args[0].__name__)(args[0])
    if len(args) == 1 and isinstance(args[0], str):
        return _make_with_name(args[0])
    raise ValueError("无效的参数")
