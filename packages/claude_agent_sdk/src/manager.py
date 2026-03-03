"""
AI Studio Agent 实例管理器

统一管理 AIStudioAgent 实例的创建、获取、销毁，
以及聊天业务逻辑处理。
"""
from typing import Dict, Optional, AsyncIterator
from pathlib import Path

from .agent import AIStudioAgent
from .bo import (
    ChatStreamChunk,
    ChatStreamChunkType,
    CHUNK_TYPE_MAP,
)

class AgentManager:
    """AI Studio Agent 实例管理器（单例模式）"""

    _instance: Optional["AgentManager"] = None

    # 存储已初始化的 agent 实例 {workspace_name: agent_instance}
    _agents: Dict[str, AIStudioAgent] = {}

    def __new__(cls) -> "AgentManager":
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ==================== 实例管理 ====================

    def has_workspace(self, workspace_name: str) -> bool:
        """检查工作空间是否已初始化"""
        return workspace_name in self._agents

    def get_agent(self, workspace_name: str) -> Optional[AIStudioAgent]:
        """获取指定工作空间的 Agent 实例"""
        return self._agents.get(workspace_name)

    def get_workspace_dir(self, workspace_name: str) -> Optional[Path]:
        """获取工作空间目录路径"""
        agent = self.get_agent(workspace_name)
        return agent.workspace_dir if agent else None

    def init_workspace(self, workspace_name: str) -> tuple[AIStudioAgent, str]:
        """
        初始化工作空间

        Args:
            workspace_name: 工作空间名称

        Returns:
            tuple: (agent实例, 状态字符串)
                - 如果是新创建: (agent, "initialized")
                - 如果已存在: (agent, "already_initialized")

        Raises:
            ValueError: 工作空间名称无效
        """
        if not workspace_name:
            raise ValueError("工作空间名称不能为空")

        if workspace_name in self._agents:
            return self._agents[workspace_name], "already_initialized"

        agent = AIStudioAgent(workspace_name=workspace_name)
        self._agents[workspace_name] = agent
        return agent, "initialized"

    def get_or_create_agent(self, workspace_name: str) -> AIStudioAgent:
        """
        获取或创建 Agent 实例

        Args:
            workspace_name: 工作空间名称

        Returns:
            AIStudioAgent: Agent 实例
        """
        agent, _ = self.init_workspace(workspace_name)
        return agent

    def destroy_workspace(self, workspace_name: str) -> bool:
        """
        销毁工作空间

        Args:
            workspace_name: 工作空间名称

        Returns:
            bool: 是否成功销毁
        """
        if workspace_name in self._agents:
            del self._agents[workspace_name]
            return True
        return False

    def list_workspaces(self) -> list[str]:
        """
        列出所有已初始化的工作空间

        Returns:
            list: 工作空间名称列表
        """
        return list(self._agents.keys())

    # ==================== 聊天业务逻辑 ====================

    async def send_message(self, workspace_name: str, message: str) -> None:
        """
        向指定工作空间发送消息

        Args:
            workspace_name: 工作空间名称
            message: 用户消息

        Raises:
            ValueError: 工作空间未初始化
        """
        agent = self.get_agent(workspace_name)
        if not agent:
            raise ValueError(f"工作空间 '{workspace_name}' 未初始化")
        await agent.send_message(message)

    async def process_response(
        self, workspace_name: str
    ) -> AsyncIterator[ChatStreamChunk]:
        """
        处理 Agent 响应流

        Args:
            workspace_name: 工作空间名称

        Yields:
            ChatStreamChunk: 流式响应块

        Raises:
            ValueError: 工作空间未初始化
        """
        agent = self.get_agent(workspace_name)
        if not agent:
            raise ValueError(f"工作空间 '{workspace_name}' 未初始化")

        async for chunk in agent.process_response():
            chunk_type = CHUNK_TYPE_MAP.get(chunk.type, ChatStreamChunkType.TEXT)
            yield ChatStreamChunk(
                type=chunk_type,
                content=chunk.content,
                metadata=chunk.metadata
            )

    async def chat(
        self, workspace_name: str, message: str
    ) -> AsyncIterator[ChatStreamChunk]:
        """
        完整的聊天流程：发送消息并返回响应流

        Args:
            workspace_name: 工作空间名称
            message: 用户消息

        Yields:
            ChatStreamChunk: 流式响应块
        """
        await self.send_message(workspace_name, message)
        async for chunk in self.process_response(workspace_name):
            yield chunk

    async def interrupt(self, workspace_name: str) -> None:
        """
        中断指定工作空间的对话

        Args:
            workspace_name: 工作空间名称

        Raises:
            ValueError: 工作空间未初始化
        """
        agent = self.get_agent(workspace_name)
        if not agent:
            raise ValueError(f"工作空间 '{workspace_name}' 未初始化")
        await agent.interrupt()

    # ==================== 工具方法 ====================

    @staticmethod
    def create_error_chunk(error_msg: str) -> ChatStreamChunk:
        """创建错误响应块"""
        return ChatStreamChunk(
            type=ChatStreamChunkType.ERROR,
            content=error_msg,
            metadata=None
        )

    @staticmethod
    def create_system_chunk(content: str, metadata: dict = None) -> ChatStreamChunk:
        """创建系统消息响应块"""
        return ChatStreamChunk(
            type=ChatStreamChunkType.SYSTEM,
            content=content,
            metadata=metadata
        )


# 全局单例实例
agent_manager = AgentManager()
