#!/usr/bin/env python
# -*- coding: utf-8 -*-
from modules import models, prompts
import states
from pydantic import v1, Field

from modules.utils import PydanticParser

PROMPT = prompts.STORY_PROMPT + """
# 指令
根据剧情发展和故事进度，请为下一章故事生成一个开头Character。"""


class OpeningFragment(v1.BaseModel):
    scene: str = v1.Field(description='下一幕的场景')
    story: str = v1.Field(description='剧情发展开端')
    character: str = v1.Field(description='出场人物')


opening_chain = (
    PROMPT
    | models.chat_model
    | PydanticParser(pydantic_object=OpeningFragment)
)


class StoryOpening:
    def create(self, state: states.StoryState):
        _inputs = state.get_inputs()
        opening: OpeningFragment = opening_chain.invoke(_inputs)
        state.scene = opening.scene
        state.character = state.settings.character.get(opening.character)
        state.update_history(state.story)
        