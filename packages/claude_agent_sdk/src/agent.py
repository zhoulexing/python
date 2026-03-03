"""
Claude Agent SDK Core Session Management

This module provides the core functionality for managing chat sessions with Claude AI.
It handles message processing, conversation history, and persistence.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncIterator

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
    create_sdk_mcp_server
)

from .mcps.factory import define_mcp_servers
from .bo import ResponseChunk, ResponseChunkType
from app.utils.env_utils import get_env

env = {
    "ANTHROPIC_API_KEY": get_env("LITELLM_API_KEY"),
    "ANTHROPIC_BASE_URL": get_env("LITELLM_BASE_URL"),
}


class AIStudioAgent:
    """AI Studio Agent"""

    def __init__(self, workspace_name: str):
        """
        Initialize a chat session.

        Args:
            client: ClaudeSDKClient instance
            history_dir: Directory to store conversation history (defaults to ~/.claude_chat)
        """

        if not workspace_name:
            raise ValueError("Workspace name is required")

        # 创建工作空间
        self.root_workspace_dir = Path.cwd()
        self.workspace_dir = self.root_workspace_dir / \
            "ai-studio-workspace" / workspace_name
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # 加载 skills
        self._load_skills()

        # 创建client客户端
        self.client = self._create_agent_client()

        # 初始化对话历史
        self.conversation_history: List[Dict[str, str]] = []
        self._connected = False

    def _load_skills(self):
        """
        Load skills from the skills directory.
        将整个 skills 目录（包含目录本身）复制到工作空间的 .claude 目录下。
        """
        # 定义源目录和目标目录
        skills_dir = Path(__file__).parent / "skills"
        target_dir = self.workspace_dir / ".claude"
        target_skills_dir = target_dir / "skills"

        # 如果 skills 目录不存在，直接返回
        if not skills_dir.exists():
            print(f"[警告] Skills 目录不存在: {skills_dir}")
            return

        # 如果目标目录中已存在 skills 目录，先删除它
        if target_skills_dir.exists():
            shutil.rmtree(target_skills_dir)
            print(f"[信息] 已删除旧的 skills 目录: {target_skills_dir}")

        # 创建目标目录（如果不存在）
        target_dir.mkdir(parents=True, exist_ok=True)

        # 复制整个 skills 目录到目标目录
        shutil.copytree(skills_dir, target_skills_dir)
        print(f"[成功] Skills 目录已复制到: {target_skills_dir}")

    def _read_mcp_servers(self):
        """
        读取 MCP 服务器配置并组装参数。

        Returns:
            tuple: (mcp_servers字典, allowed_tools列表)
                - mcp_servers: 字典，键为服务器名称，值为服务器实例（工具列表）
                - allowed_tools: 列表，包含允许使用的工具标识符，格式为 mcp__{server_name}__{tool_name}
        """
        server_definitions = define_mcp_servers()
        mcp_servers = {}
        allowed_tools = []

        for server_def in server_definitions:
            server_name = server_def["name"]
            tools = server_def["tools"]

            # 组装 mcp_servers
            mcp_servers[server_name] = create_sdk_mcp_server(
                name=server_name,
                tools=tools
            )

            # 从工具中提取工具名称并构建 allowed_tools
            for tool_func in tools:
                tool_name = tool_func.name

                tool_identifier = f"mcp__{server_name}__{tool_name}"
                allowed_tools.append(tool_identifier)

        return mcp_servers, allowed_tools

    # 初始化Agent
    def _create_agent_client(self):
        """
        Initialize the Claude agent.
        """
        mcp_servers, allowed_tools = self._read_mcp_servers()
        options = ClaudeAgentOptions(
            setting_sources=["project"],
            env=env,
            cwd=self.workspace_dir,
            include_partial_messages=True,
            permission_mode="bypassPermissions",
        )
        if mcp_servers and allowed_tools:
            options.mcp_servers = mcp_servers
            options.allowed_tools = allowed_tools

        return ClaudeSDKClient(options=options)

    async def _ensure_connected(self):
        """
        Ensure the client is connected. Connects lazily on first use.
        """
        if not self._connected:
            await self.client.connect()
            self._connected = True

    async def process_response(self) -> AsyncIterator[ResponseChunk]:
        """
        Process and collect Claude's response as an async iterator.

        Yields:
            ResponseChunk: Response chunks with type and content
        """
        async for message in self.client.receive_messages():
            if isinstance(message, AssistantMessage):
                # 处理助手消息中的内容块
                for content_block in message.content:
                    if isinstance(content_block, TextBlock):
                        yield ResponseChunk(
                            type=ResponseChunkType.TEXT,
                            content=content_block.text,
                            metadata={"model": message.model}
                        )
                    elif isinstance(content_block, ThinkingBlock):
                        yield ResponseChunk(
                            type=ResponseChunkType.THINKING,
                            content=content_block.thinking,
                            metadata={"model": message.model}
                        )
                    elif isinstance(content_block, ToolUseBlock):
                        yield ResponseChunk(
                            type=ResponseChunkType.TOOL_USE,
                            content={
                                "id": content_block.id,
                                "name": content_block.name,
                                "input": content_block.input
                            },
                            metadata={"model": message.model}
                        )
                    elif isinstance(content_block, ToolResultBlock):
                        yield ResponseChunk(
                            type=ResponseChunkType.TOOL_RESULT,
                            content={
                                "tool_use_id": content_block.tool_use_id,
                                "content": content_block.content,
                                "is_error": getattr(content_block, 'is_error', False)
                            },
                            metadata={"model": message.model}
                        )

            elif isinstance(message, SystemMessage):
                # 处理系统消息
                yield ResponseChunk(
                    type=ResponseChunkType.SYSTEM,
                    content=message.data,
                    metadata={"subtype": message.subtype}
                )

            elif isinstance(message, ResultMessage):
                # 处理结果消息
                yield ResponseChunk(
                    type=ResponseChunkType.RESULT,
                    content={
                        "result": message.result,
                        "is_error": message.is_error,
                        "num_turns": message.num_turns,
                        "session_id": message.session_id,
                    },
                    metadata={
                        "subtype": message.subtype,
                        "duration_ms": message.duration_ms,
                        "duration_api_ms": message.duration_api_ms,
                        "total_cost_usd": message.total_cost_usd,
                        "usage": message.usage
                    }
                )

    async def send_message(self, user_input: str) -> str:
        """
        Send message to Claude and get response.

        Args:
            user_input: The user's message

        Returns:
            Claude's response text

        Raises:
            Exception: If there's an error communicating with Claude
        """
        # Ensure connection is established before sending message
        await self._ensure_connected()
        await self.client.query(user_input)

    async def interrupt(self) -> None:
        """
        Interrupt the current conversation.
        """
        await self.client.interrupt()

    def save_conversation(self, filename: Optional[str] = None) -> Path:
        """
        Save conversation history to JSON file.

        Args:
            filename: Custom filename (defaults to timestamped filename)

        Returns:
            Path to the saved file

        Raises:
            ValueError: If there's no conversation to save
            Exception: If file writing fails
        """
        if not self.conversation_history:
            raise ValueError("No conversation to save")

        if filename is None:
            filename = f"conversation_{datetime.now().strftime('%Y%m%d')}.json"

        filepath = self.workspace_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f,
                      ensure_ascii=False, indent=2)

        return filepath

    def load_conversation(self, filename: str) -> int:
        """
        Load conversation history from JSON file.

        Args:
            filename: Name of the file to load

        Returns:
            Number of messages loaded

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If file reading or parsing fails
        """
        filepath = self.workspace_dir / filename

        with open(filepath, 'r', encoding='utf-8') as f:
            self.conversation_history = json.load(f)

        return len(self.conversation_history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.

        Returns:
            List of conversation entries with timestamp, user message, and assistant response
        """
        return self.conversation_history.copy()

    def get_history_summary(self) -> List[Dict[str, str]]:
        """
        Get a summarized view of conversation history.

        Returns:
            List of entries with truncated messages for display
        """
        summary = []
        for entry in self.conversation_history:
            summary.append({
                "timestamp": entry.get("timestamp", "Unknown"),
                "user": entry["user"][:100] + ("..." if len(entry["user"]) > 100 else ""),
                "assistant": entry["assistant"][:100] + ("..." if len(entry["assistant"]) > 100 else ""),
            })
        return summary
