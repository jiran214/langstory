#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from modules import
from itertools import cycle

from langchain_core.documents import Document
from langchain_core.messages import ChatMessage
from langchain_core.output_parsers import StrOutputParser

import states
from modules import models
from modules.prompts import CHAT_PROMPT


chat_chain = (
    CHAT_PROMPT
    | models.chat_model
    | StrOutputParser()
)

summary_chain = (None, )


class SessionSupervisor:
    def create(self, state: states.StoryState):
        for session_manager in [Character(), Human()]:
            character_state = states.CharacterState(settings=state.character, namespace=f"{state.settings.namespace}{state.character.name}")
            try:
                session_manager.create(character_state)
            except StopIteration:
                break
        # 总结对话
        summary = summary_chain.invoke(character_state.session.get_history())
        state.update_history(summary)
        # 添加角色记忆
        character_state.add_memory(Document(page_content=summary))


class Character:
    def create(self, state: states.CharacterState):
        state.update_memory(...)
        character_input = chat_chain.invoke(state.get_inputs())
        if 'stop' in character_input:
            raise StopIteration
        state.session.messages.append(ChatMessage(role=state.character.name, content=character_input))


class Human:
    def create(self, state: states.CharacterState):
        state.session.messages.append(ChatMessage(role='玩家', content=str(input('玩家: '))))
