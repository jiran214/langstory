#!/usr/bin/env python
# -*- coding: utf-8 -*-

STORY_PROMPT = """# 故事设定
{story_settings}

# 进度
{current_epoch}/{total_epoch}

# 剧情回顾
{history}"""


CHAT_PROMPT = STORY_PROMPT + """
## 判断对话终止条件
1. 玩家想结束对话
2. 对话偏离剧情
3. 对话轮数超过10轮

## 对话终止标识
当对话结束，在末尾加上标识符 STOP，注意未结束时不能加该标识

## {character}的记忆
{memory}

## Current conversation
The following is a friendly conversation between 玩家 and {character}. 
{history}
{character}: """
