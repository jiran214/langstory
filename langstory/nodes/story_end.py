#!/usr/bin/env python
# -*- coding: utf-8 -*-
import states
from modules import models, prompts
from pydantic import v1

from modules.utils import PydanticParser

PROMPT = prompts.STORY_PROMPT + """
## 指令
根据剧情发展和故事进度，请为该故事生成一个结局，如果进度还没到最后，则生成一个阶段性的结局。"""


class EndingFragment(v1.BaseModel):
    story: str = v1.Field(description='小说后续的剧情发展故事')


end_chain = (
    PROMPT
    | models.chat_model
    | PydanticParser(pydantic_object=EndingFragment)
)


class StoryEnding:
    def create(self, state: states.StoryState):
        _inputs = state.get_inputs()
        end: EndingFragment = end_chain.invoke(_inputs)
        state.update_history(end)