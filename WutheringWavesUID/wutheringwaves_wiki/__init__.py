import os
import re
import shutil
from pathlib import Path

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.download_resource.download_file import download
from gsuid_core.utils.image.convert import convert_img
from .main import Guide
from .wiki import draw_wiki_detail
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id, alias_to_weapon_name
from ..utils.resource.RESOURCE_PATH import (
    GUIDE_CONFIG_MAP,
)
from ..wutheringwaves_config import WutheringWavesConfig, PREFIX

sv_waves_guide = SV('鸣潮攻略')
sv_waves_wiki = SV('鸣潮wiki')


@sv_waves_wiki.on_prefix((
    f'{PREFIX}角色wiki',
    f'{PREFIX}角色介绍',
    f'{PREFIX}武器wiki',
    f'{PREFIX}武器介绍',
))
async def send_waves_wiki(bot: Bot, ev: Event):
    if "角色" in ev.command:
        char_name = ev.text.strip(' ')
        char_id = char_name_to_char_id(char_name)
        if not char_id:
            return f'[鸣潮] 角色名{char_name}无法找到, 可能暂未适配, 请先检查输入是否正确！'

        name = alias_to_char_name(char_name)
        if name == '漂泊者':
            name = '漂泊者-女-衍射'
        elif name == '漂泊者·湮灭':
            name = '漂泊者-女-湮灭'
        await bot.logger.info(f'[鸣潮] 开始获取{name}wiki')
        img = await draw_wiki_detail("共鸣者", name)
        await bot.send(img)
    elif "武器" in ev.command:
        weapon_name = ev.text.strip(' ')
        weapon_name = alias_to_weapon_name(weapon_name)
        if not weapon_name:
            return f'[鸣潮] 武器名{weapon_name}无法找到, 可能暂未适配, 请先检查输入是否正确！'
        await bot.logger.info(f'[鸣潮] 开始获取{weapon_name}wiki')
        img = await draw_wiki_detail("武器", weapon_name)
        await bot.send(img)


@sv_waves_guide.on_prefix((f'{PREFIX}角色攻略', f'{PREFIX}刷新角色攻略'))
async def send_role_guide_pic(bot: Bot, ev: Event):
    is_force = True if '刷新' in ev.command else False

    char_name = ev.text.strip(' ')
    char_id = char_name_to_char_id(char_name)
    if not char_id:
        return f'[鸣潮] 角色名{char_name}无法找到, 可能暂未适配, 请先检查输入是否正确！'

    name = alias_to_char_name(char_name)
    if name == '漂泊者':
        name = '漂泊者·衍射'
    await bot.logger.info(f'[鸣潮] 开始获取{name}图鉴')

    config = WutheringWavesConfig.get_config('WavesGuideProvide')
    zip_list = []
    if config.data == 'all':
        for i in config.options:
            if i == 'all':
                continue
            name_dir = GUIDE_CONFIG_MAP[i][0] / name
            auth_id = GUIDE_CONFIG_MAP[i][1]
            zip_list.append((i, name_dir, auth_id))
    else:
        if config.data in GUIDE_CONFIG_MAP:
            name_dir = GUIDE_CONFIG_MAP[config.data][0] / name
            auth_id = GUIDE_CONFIG_MAP[config.data][1]
            zip_list.append((config.data, name_dir, auth_id))

    if not zip_list:
        return f'[鸣潮] 角色名{char_name}无法找到角色攻略图提供方, 请检查配置！'

    imgs = []
    for auth_name, name_dir, auth_id in zip_list:
        if is_force or not name_dir.exists() or len(os.listdir(name_dir)) == 0:
            await download_guide_pic(auth_id, name, name_dir, is_force)

        imgs.extend(await process_images(auth_name, name_dir))

    await send_images_based_on_config(config, imgs, bot)


async def send_images_based_on_config(config, imgs: list, bot: Bot):
    if not imgs:
        return await bot.send('[鸣潮] 该角色攻略不存在, 请检查输入角色是否正确！')

    # 处理发送逻辑
    if config.data == 'all':
        await bot.send(imgs)
    elif len(imgs) == 2:
        await bot.send(imgs[1])
    else:
        await bot.send(imgs)


async def process_images(auth_name: str, _dir: Path):
    imgs = []
    if _dir.exists() and len(os.listdir(_dir)) > 0:
        path_list = sorted(os.listdir(_dir))
        for _path in path_list:
            try:
                img = await convert_img(_dir / _path)
                imgs.append(img)
            except Exception as e:
                logger.warning(f"攻略图片读取失败 {_path}: {e}")
    if len(imgs) > 0:
        imgs.insert(0, f'攻略作者：{auth_name}')
    return imgs


async def download_guide_pic(auth_id: int, name: str, _dir: Path, is_force: bool):
    all_bbs_data = await Guide().get_guide_data(auth_id)
    if not all_bbs_data:
        return

    post_id = None
    for i in all_bbs_data:
        post_title = i['postTitle']
        if '·' in name:
            name_split = name.split('·')
            if all(fragment in post_title for fragment in name_split):
                post_id = i['postId']
                break
        elif name in post_title and '一图流' in post_title:
            post_id = i['postId']
            break

    if not post_id:
        return

    res = await Guide().get_ann_detail(post_id)
    if not res:
        return
    if is_force:
        force_delete_dir(_dir)

    for index, _temp in enumerate(res['postContent']):
        if _temp['contentType'] != 2:
            continue
        _msg = re.search(r'(https://.*[png|jpg])', _temp['url'])
        url = _msg.group(0) if _msg else ''

        if _temp['imgWidth'] < 1910:
            # Moealkyne 的攻略 1910起步
            # XMu 的攻略 2500起步
            # TODO
            continue

        if url:
            _dir.mkdir(parents=True, exist_ok=True)
            await download(url, _dir, f'{name}_{index}.jpg', tag="[鸣潮]")


def force_delete_dir(_dir: Path):
    try:
        if _dir.exists() and _dir.is_dir():
            shutil.rmtree(_dir)
    except Exception as e:
        print(f"Error deleting directory {_dir}: {e}")
