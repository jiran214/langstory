#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
from collections import deque
from typing import List, Optional, Dict, Any

from langchain_core.documents import Document
from langchain_core.messages import ChatMessage
from pydantic import BaseModel, Field
import langstory
from modules.context import Retriever


class Character(BaseModel):
    name: str
    description: str


class StorySettings(BaseModel):
    version: str = Field(default=langstory.__version__, description='版本')
    namespace: str = Field(description="命名空间")
    title: str = Field(description="故事标题")
    description: str = Field(description="故事摘要")
    characters: Dict[str, Character] = Field(description="人物角色")
    goal: str = Field(description="玩家目标")
    total_epoch: int = Field(default=10, description="故事时长")
    language: str = Field(default='中文')


class SessionState(BaseModel):
    messages: List[ChatMessage]

    def get_history(self):
        history_list = []
        for msg in self.messages:
            history_list.append(f"{msg.role}: {msg.content}")
        return '\n'.join(history_list)


class CharacterState(BaseModel):
    settings: Character
    session: SessionState = Field(default_factory=SessionState)
    memory: List[Document] = []
    namespace: str

    def update_memory(self, query: str):
        retriever: Retriever = Retriever.get_instance(self.namespace)
        self.memory = retriever.search_context(query)

    def add_memory(self, docs: Document):
        retriever: Retriever = Retriever.get_instance(self.namespace)
        retriever.add_context(docs)

    def get_inputs(self):
        _inputs = {
            'history': self.session.get_history(),
            'character': self.settings.name,
            'memory': ''.join((doc.page_content for doc in self.memory))
        }
        return _inputs


class StoryState(BaseModel):
    settings: StorySettings
    current_epoch: int = Field(default=0, description="当前进度")
    scene: Optional[str] = Field(default=None, description="场景")
    character: Character = Field(description='出场人物')
    history: deque[str] = Field(default_factory=functools.partial(deque, maxlen=10), description="剧情历史")

    def update_history(self, story):
        self.history.append(story)

    def get_inputs(self):
        _inputs = self.model_dump()
        _inputs.update(_inputs.pop('settings'))
        return _inputs
