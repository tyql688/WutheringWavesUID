from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.message import send_diff_msg
from .deal import add_cookie, delete_cookie, get_cookie
from ..utils.database.models import WavesBind
from ..utils.waves_prefix import PREFIX

waves_bind_uid = SV('waves绑定uid')
waves_add_ck = SV('waves添加ck')
waves_del_ck = SV('waves删除ck')
waves_get_ck = SV('waves获取ck', area='DIRECT')


@waves_add_ck.on_prefix((
    f'{PREFIX}添加CK', f'{PREFIX}添加ck',
    f'{PREFIX}添加Token', f'{PREFIX}添加token', f'{PREFIX}添加TOKEN'
))
async def send_waves_add_ck_msg(bot: Bot, ev: Event):
    ck = ev.text.strip()
    await bot.send(await add_cookie(ev, ck))


@waves_del_ck.on_prefix((
    f'{PREFIX}删除ck', f'{PREFIX}删除CK',
    f'{PREFIX}删除Token', f'{PREFIX}删除token', f'{PREFIX}删除TOKEN'
))
async def send_waves_del_ck_msg(bot: Bot, ev: Event):
    uid = ev.text.strip()
    if not uid or len(uid) != 9:
        return await bot.send(f'末尾需要跟正确的UID, 例如 {PREFIX}删除CK1234567')
    await bot.send(await delete_cookie(uid))


@waves_get_ck.on_fullmatch((
    f'{PREFIX}获取ck', f'{PREFIX}获取CK',
    f'{PREFIX}获取Token', f'{PREFIX}获取token', f'{PREFIX}获取TOKEN'
))
async def send_waves_del_ck_msg(bot: Bot, ev: Event):
    await bot.send(await get_cookie(bot, ev))


@waves_bind_uid.on_command(
    (
        f'{PREFIX}绑定uid',
        f'{PREFIX}绑定UID',
        f'{PREFIX}切换uid',
        f'{PREFIX}切换UID',
        f'{PREFIX}删除uid',
        f'{PREFIX}删除UID',
        f'{PREFIX}删除全部uid',
        f'{PREFIX}删除全部UID',
        f'{PREFIX}查看uid',
        f'{PREFIX}查看UID',
    ),
    block=True,
)
async def send_waves_bind_uid_msg(bot: Bot, ev: Event):
    uid = ev.text.strip()

    await bot.logger.info('[鸣潮] 开始执行[绑定/解绑用户信息]')
    qid = ev.user_id
    await bot.logger.info('[鸣潮] [绑定/解绑]UserID: {}'.format(qid))

    if '绑定' in ev.command:
        if not uid:
            return await bot.send('该命令需要带上正确的uid!\n')
        data = await WavesBind.insert_waves_uid(qid, ev.bot_id, uid, ev.group_id, lenth_limit=9)
        if data == 0 or data == -2:
            retcode = await WavesBind.switch_uid_by_game(qid, ev.bot_id, uid)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f'[鸣潮] 绑定UID{uid}成功！',
                -1: f'[鸣潮] UID{uid}的位数不正确！',
                -2: f'[鸣潮] UID{uid}已经绑定过了！',
                -3: '[鸣潮] 你输入了错误的格式!',
            },
        )
    elif '切换' in ev.command:
        retcode = await WavesBind.switch_uid_by_game(qid, ev.bot_id, uid)
        if retcode == 0:
            uid_list = await WavesBind.get_uid_list_by_game(qid, ev.bot_id)
            return await bot.send(f'[鸣潮] 切换UID【{uid_list[0]}】成功！')
        else:
            return await bot.send(f'[鸣潮] 尚未绑定该UID{uid}')
    elif '查看' in ev.command:
        uid_list = await WavesBind.get_uid_list_by_game(qid, ev.bot_id)
        if uid_list:
            uids = '\n'.join(uid_list)
            return await bot.send(f'[鸣潮] 绑定的UID列表为：\n{uids}')
        else:
            return await bot.send(f'[鸣潮] 尚未绑定任何UID')
    elif '删除全部' in ev.command:
        retcode = await WavesBind.update_data(
            user_id=qid,
            bot_id=ev.bot_id,
            **{WavesBind.get_gameid_name(None): None},
        )
        if retcode == 0:
            return await bot.send(f'[鸣潮] 删除全部UID成功！')
        else:
            return await bot.send(f'[鸣潮] 尚未绑定任何UID')
    else:
        data = await WavesBind.delete_uid(qid, ev.bot_id, uid)
        return await send_diff_msg(
            bot,
            data,
            {
                0: f'[鸣潮] 删除UID{uid}成功！',
                -1: f'[鸣潮] 该UID{uid}不在已绑定列表中！',
            },
        )
