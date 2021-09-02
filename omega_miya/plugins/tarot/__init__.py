"""
@Author         : Ailitonia
@Date           : 2021/08/31 21:05
@FileName       : __init__.py.py
@Project        : nonebot2_miya 
@Description    : 塔罗插件
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

import random
import pathlib
from nonebot import MatcherGroup, logger
from nonebot.plugin.export import export
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.adapters.cqhttp.permission import GROUP
from nonebot.adapters.cqhttp.message import MessageSegment
from omega_miya.utils.omega_plugin_utils import init_export, init_permission_state
from .config import Config
from .utils import generate_tarot_card


# Custom plugin usage text
__plugin_custom_name__ = '塔罗牌'
__plugin_usage__ = r'''【塔罗牌插件】
塔罗牌插件

**Permission**
Command & Lv.10
or AuthNode

**AuthNode**
basic

**Usage**
/单张塔罗牌'''

# 声明本插件可配置的权限节点
__plugin_auth_node__ = [
    'basic'
]

# Init plugin export
init_export(export(), __plugin_custom_name__, __plugin_usage__, __plugin_auth_node__)


Tarot = MatcherGroup(
    type='message',
    # 使用run_preprocessor拦截权限管理, 在default_state初始化所需权限
    state=init_permission_state(
        name='tarot',
        command=True,
        level=10,
        auth_node='basic'),
    permission=GROUP,
    priority=10,
    block=True)

single_tarot = Tarot.on_command('单张塔罗牌')


@single_tarot.handle()
async def handle_single_tarot(bot: Bot, event: GroupMessageEvent, state: T_State):
    group_resources = Config().get_group_resources(group_id=event.group_id)
    # 随机一张出来
    card = random.choice(group_resources.pack.cards)
    # 再随机正逆
    direction = random.choice([-1, 1])
    if direction == 1:
        need_positive = True
        need_negative = False
    else:
        need_positive = False
        need_negative = True
    # 绘制卡图
    card_result = await generate_tarot_card(
        id_=card.id,
        resources=group_resources,
        direction=direction,
        need_desc=False,
        need_positive=need_positive,
        need_negative=need_negative)

    if card_result.error:
        logger.error(f'{event.group_id}/{event.user_id} 生成塔罗牌图片失败, {card_result.info}')
        await single_tarot.finish('生成塔罗牌图片失败了QAQ, 请稍后再试或联系管理员处理')
    else:
        msg = MessageSegment.image(pathlib.Path(card_result.result).as_uri())
        logger.info(f'{event.group_id}/{event.user_id} 获取生成塔罗牌图片成功')
        await single_tarot.finish(msg)