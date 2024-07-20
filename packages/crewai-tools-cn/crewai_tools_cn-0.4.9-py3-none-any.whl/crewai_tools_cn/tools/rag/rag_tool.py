from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field, model_validator

from crewai_tools_cn.tools.base_tool import BaseTool


class Adapter(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def query(self, question: str) -> str:
        """使用问题查询知识库并返回答案。"""

    @abstractmethod
    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """向知识库添加内容。"""


class RagTool(BaseTool):
    class _AdapterPlaceholder(Adapter):
        def query(self, question: str) -> str:
            raise NotImplementedError

        def add(self, *args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

    name: str = "知识库"
    description: str = "可用于回答问题的知识库。"
    summarize: bool = False
    adapter: Adapter = Field(default_factory=_AdapterPlaceholder)
    config: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from embedchain import App

            from crewai_tools_cn.adapters.embedchain_adapter import EmbedchainAdapter

            app = App.from_config(config=self.config) if self.config else App()
            self.adapter = EmbedchainAdapter(
                embedchain_app=app, summarize=self.summarize
            )

        return self

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.adapter.add(*args, **kwargs)

    def _run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        self._before_run(query, **kwargs)

        return f"相关内容：\n{self.adapter.query(query)}"

    def _before_run(self, query, **kwargs):
        pass
