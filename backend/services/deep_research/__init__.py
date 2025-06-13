# Deep Research (LangGraph) package

"""LangGraph Agentic RAG 実装を提供するサービスレイヤ。

Modules:
    state.py            : エージェントの共有状態データクラス
    retrieve_node.py    : RetrieveNode 実装（Azure AI Search）
    decide_node.py      : DecideNode 実装（検索結果十分性判定）
    answer_node.py      : AnswerNode 実装（GPT-4o レポート生成）
    agent.py            : DeepResearchLangGraphAgent 本体
"""

from .agent import DeepResearchLangGraphAgent
from .state import AgentState

__all__ = ["DeepResearchLangGraphAgent", "AgentState"]
