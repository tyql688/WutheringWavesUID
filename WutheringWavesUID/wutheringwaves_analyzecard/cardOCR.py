
# 标准库
from pathlib import Path
import asyncio
import ssl
import re
import os

# 第三方库
import httpx
import easyocr
import numpy as np
from PIL import Image
from opencc import OpenCC

# 项目内部模块
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.download_resource.download_file import download

from ..wutheringwaves_analyzecard.userData import save_card_dict_to_json


SRC_PATH = Path(__file__).parent / "src"
CARD_PATH = Path(__file__).parent / "src/card.jpg"
CARD_NAME = "card.jpg"

# 原始参考分辨率
REF_WIDTH = 1072
REF_HEIGHT = 602
    
# 裁切区域比例（左、上、右、下），数字来自src/example_card_2.png
# 技能树扫描顺序：普攻、共鸣技能、共鸣解放、变奏技能、共鸣回路(json_skillList顺序)
crop_ratios = [
    (  0/REF_WIDTH,   0/REF_HEIGHT, 420/REF_WIDTH, 350/REF_HEIGHT), # 角色
    (583/REF_WIDTH,  30/REF_HEIGHT, 653/REF_WIDTH, 130/REF_HEIGHT), # 普攻
    (456/REF_WIDTH, 115/REF_HEIGHT, 526/REF_WIDTH, 215/REF_HEIGHT), # 共鸣技能
    (694/REF_WIDTH, 115/REF_HEIGHT, 764/REF_WIDTH, 215/REF_HEIGHT), # 共鸣解放
    (650/REF_WIDTH, 250/REF_HEIGHT, 720/REF_WIDTH, 350/REF_HEIGHT), # 变奏技能
    (501/REF_WIDTH, 250/REF_HEIGHT, 571/REF_WIDTH, 350/REF_HEIGHT), # 共鸣回路
    ( 10/REF_WIDTH, 360/REF_HEIGHT, 214/REF_WIDTH, 590/REF_HEIGHT), # 声骸1
    (221/REF_WIDTH, 360/REF_HEIGHT, 425/REF_WIDTH, 590/REF_HEIGHT), # 声骸2
    (430/REF_WIDTH, 360/REF_HEIGHT, 634/REF_WIDTH, 590/REF_HEIGHT), # 声骸3
    (639/REF_WIDTH, 360/REF_HEIGHT, 843/REF_WIDTH, 590/REF_HEIGHT), # 声骸4
    (848/REF_WIDTH, 360/REF_HEIGHT, 1052/REF_WIDTH, 590/REF_HEIGHT), # 声骸5
    (800/REF_WIDTH, 240/REF_HEIGHT, 1020/REF_WIDTH, 350/REF_HEIGHT), # 武器
]

async def async_ocr(bot: Bot, ev: Event):
    """
    异步OCR识别函数
    """
    if not await upload_discord_bot_card(bot, ev):
        await bot.send(f"[鸣潮]卡片分析已停止。")
        return False
    # 获取dc卡片识别结果
    bool, final_result = await cut_card_ocr()
    if bool:
        await save_card_dict_to_json(bot, ev, final_result)
    else:
        await bot.send(f"[鸣潮]Please use chinese card！")
    

async def get_image(ev: Event):
    """
    获取图片链接
    change from .upload_card.get_image
    """
    res = []
    for content in ev.content:
        if content.type == "img" and content.data and isinstance(content.data, str) and content.data.startswith("http"):
            res.append(content.data)
        elif content.type == "image" and content.data and isinstance(content.data, str) and content.data.startswith("http"):
            res.append(content.data)

    if not res and ev.image:
        res.append(ev.image)

    return res

async def upload_discord_bot_card(bot: Bot, ev: Event):
    """
    上传Discord机器人的卡片
    change from .upload_card.upload_custom_card
    """
    at_sender = True if ev.group_id else False

    upload_images = await get_image(ev)
    if not upload_images:
        await bot.send(f"[鸣潮]获取卡片图失败！\n", at_sender)
        return False

    logger.info(f"[鸣潮]卡片分析上传链接{upload_images}")
    success = True
    for upload_image in upload_images:
        # name = f"card_{int(time.time() * 1000)}.jpg"
        name = CARD_NAME
        if not CARD_PATH.exists():
            try:
                if httpx.__version__ >= "0.28.0":
                    ssl_context = ssl.create_default_context()
                    # ssl_context.set_ciphers("AES128-GCM-SHA256")
                    ssl_context.set_ciphers("DEFAULT")
                    sess = httpx.AsyncClient(verify=ssl_context)
                else:
                    sess = httpx.AsyncClient()
            except Exception as e:
                logger.exception(f"{httpx.__version__} - {e}")
                sess = None
            code = await download(upload_image, SRC_PATH, name, tag="[鸣潮]", sess=sess)
            if not isinstance(code, int) or code != 200:
                # 成功
                success = False
                break

    if success:
        await bot.send(f"[鸣潮]上传卡片图成功！进行数据提取中...\n", at_sender)
        return True
    else:
        await bot.send(f"[鸣潮]上传卡片图失败！\n", at_sender)
        return False

async def cut_card_ocr():
    """
    裁切卡片：角色，技能树*5，声骸*5，武器
        （按比例适配任意分辨率，1920*1080识别效果优良）
    """

    # 打开图片
    image = Image.open(CARD_PATH).convert('RGB')
    img_width, img_height = image.size  # 获取实际分辨率
    
    # 裁切图片
    cropped_images = []
    for i, ratio in enumerate(crop_ratios):
        # 根据相对比例计算实际裁切坐标
        left = ratio[0] * img_width
        top = ratio[1] * img_height
        right = ratio[2] * img_width
        bottom = ratio[3] * img_height
        
        # 四舍五入取整并确保不越界
        left = max(0, int(round(left)))
        top = max(0, int(round(top)))
        right = min(img_width, int(round(right)))
        bottom = min(img_height, int(round(bottom)))
        
        # 执行裁切
        cropped_image = image.crop((left, top, right, bottom))
        cropped_images.append(cropped_image)
        
        # 保存裁切后的图片
        cropped_image.save(f"{SRC_PATH}/_{i}.png")
    
    os.remove(CARD_PATH) # 删除原图片

    async def card_part_ocr():
        """
        识别碎块图片
        """
        reader = easyocr.Reader(['ch_tra', 'en'])  # 选择语言，繁体中文和英语
        results = []
        for cropped_image in cropped_images:
            image_np = np.array(cropped_image) # 将PIL.Image转为numpy数组
            result = reader.readtext(image_np) # 结果为：[位置, '文字', 置信度]
            results.append(result)
        return results


    # 调用 card_part_ocr 函数并获取识别结果
    ocr_results = await card_part_ocr()

    return await ocr_results_to_dict(ocr_results)
   
async def is_valid_prop(entry):
    """验证属性是否有效"""
    name, value = entry
    # 过滤无效属性名（根据实际需求调整）
    if not name or len(name) < 2:
        return False
    # 过滤纯数值属性名
    if re.match(r'^\d+%?$', name):
        return False
    return True

async def ocr_results_to_dict(ocr_results):
    # 将识别结果转换为字典
    final_result = {
        "用户信息": {},
        "角色信息": {},
        "技能等级": [],
        "装备数据": [],
        "武器信息": {}
    }

    # 增强版正则模式, 正则与置信度限制
    patterns = {
        "name": (re.compile(r'^[\u4e00-\u9fa5A-Za-z]+$'), 0.9),
        "level": (re.compile(r'(?i)[lv]+[.\s]*(\d+)'), 0.01),  # 支持L.90格式
        "skill_level": (re.compile(r'L\.?V?[./|]?(\d+).*?10'), 0.3),  # 更宽松的匹配
        "player_id_en": (re.compile(r'PlayerID'), 0.7), # 未使用
        "player_id_cn": (re.compile(r'玩家名稱'), 0.7),
        "uid_en": (re.compile(r'U[|]?D'), 0.7), # 未使用
        "uid_cn": (re.compile(r'特徵碼'), 0.7),
        "echo_value": (re.compile(r'(\d+\.?\d*%?)'), 0.01),  # 更宽松的声骸装备处理逻辑
        "weapon_name": (re.compile(r'^[\u4e00-\u9fa5A-Za-z]+$'), 0.8),
        "weapon_level": (re.compile(r'LV\.(\d+)'), 0.5)
    }
    

    # 创建转换器
    cc = OpenCC('t2s')  # t2s 表示繁体转简体

    # 正则表达式：提取属性名称
    # prop_pattern = re.compile(r'(?P<attr>[a-zA-Z\u4e00-\u9fa5]+)')
    prop_pattern = re.compile(
        r'^[^a-zA-Z\u4e00-\u9fa5]*'  # 去除前缀符号/空格
        r'(?P<attr>[a-zA-Z\u4e00-\u9fa5]+)'  # 匹配至少2个中文字符
    )

    # 增强属性处理逻辑
    # attribute_aliases = {
    #     "文攻擊": "攻击",
    #     "女攻擊": "攻击",
    #     "弋攻擊": "攻击",
    #     "C攻擊": "攻击",
    #     "X攻擊": "攻击",
    #     "暴擊": "暴击",
    #     "暴擊傷害": "暴击伤害",
    #     "共鳴效率": "共鸣效率",
    #     # ...补充更多映射...
    # }
    # 用字符数量判断了，出现三个字符只能是错误识别，不确定，先这样保留

    def validate_value(text):
        """通用数值格式校验"""
        return re.match(r'^[\w-]+$', text)  # 允许字母、数字、常见符号

    # 处理角色信息 (image_0)
    if ocr_results:
        data = ocr_results[0]
        i = 0
        while i < len(data):
            text, conf = data[i][1], data[i][2]
            logger.info(f" [鸣潮][dc卡片识别] ocr基础信息内容:{text}，置信度:{conf}")

            
            # 角色名提取
            if patterns["name"][0].fullmatch(text) and conf >= patterns["name"][1]:
                if '角色名' not in final_result["角色信息"]:
                    # text为英文，则退出
                    if not re.match(r'^[\u4e00-\u9fa5]+$', text):
                        logger.debug(f" [鸣潮][dc卡片识别] 识别出英文角色名:{text}，退出识别！")
                        return False, final_result
                    final_result["角色信息"]["角色名"] = cc.convert(text)
            
            # 角色等级提取
            level_match = patterns["level"][0].search(text)
            if level_match and conf >= patterns["level"][1]:
                if '等级' not in final_result["角色信息"]:
                    final_result["角色信息"]["等级"] = int(level_match.group(1))
            
            # 处理用户昵称
            if (patterns["player_id_cn"][0].search(text) and conf >= patterns["player_id_cn"][1]):
                if i+1 < len(data) and data[i+1][1].isdigit():
                    next_text, next_conf = data[i+1][1], data[i+1][2]
                    if validate_value(next_text) and next_conf >= 0.5:  # 置信度阈值
                        final_result["用户信息"]["玩家名称"] = next_text
                        i += 1  # 跳过已处理的数字
            
            # 处理UID
            if (patterns["uid_cn"][0].search(text) and conf >= patterns["uid_cn"][1]):
                if i+1 < len(data) and data[i+1][1].isdigit():
                    next_text, next_conf = data[i+1][1], data[i+1][2]
                    if next_text.isdigit() and next_conf >= 0.7:  # UID严格限定为数字
                        final_result["用户信息"]["UID"] = next_text
                        i += 1  # 跳过已处理的数字
            
            i += 1

        # 处理技能等级的逻辑优化
        for idx in range(1, 6):
            if idx >= len(ocr_results):
                final_result["技能等级"].append(None)
                continue
                
            max_level = 0
            for data in ocr_results[idx]:
                text = data[1].replace(" ", "").upper()  # 预处理文本
                logger.info(f" [鸣潮][dc卡片识别] ocr技能数据:{text}")
                match = patterns["skill_level"][0].search(text)
                if match:
                    try:
                        level = int(match.group(1))
                        if 1 <= level <= 10:  # 添加合理范围验证
                            max_level = max(max_level, level)
                    except: pass
            final_result["技能等级"].append(max_level if max_level else None)
        
        # 处理声骸装备数据 (image_6-10)
        for idx in range(6, 11):
            if idx >= len(ocr_results):
                continue
                
            equipment = {
                "mainProps": [],
                "subProps": []
            }
            buffer = []
            current_attr = None
            
            for data in sorted(ocr_results[idx], key=lambda x: x[0][0][1]):  # 按Y坐标排序
                text, conf = data[1], data[2]
                logger.info(f" [鸣潮][dc卡片识别] ocr声骸信息内容:{text}，置信度:{conf}")

                # 数值提取和关联
                value_match = patterns["echo_value"][0].search(text)
                if value_match and conf > patterns["echo_value"][1]:
                    value = value_match.group(1)
                    if current_attr:
                        buffer.append((current_attr, value))
                    current_attr = None
                else:
                    # 标准化属性名称
                    # cleaned_text = attribute_aliases.get(text, text)
                    cleaned_text = text if len(text) != 3 else text[1:]  # 取后两个字符, 避免出现“弋攻擊”
                    clean_attr = prop_pattern.search(cleaned_text)
                    pat_attr = None
                    if clean_attr:
                        pat_attr = cc.convert(clean_attr.group(1))  # 'attr' 是分组名称
                    current_attr = pat_attr if len(pat_attr) > 1 else None

            # 智能分配词条
            valid_entries = [entry for entry in buffer if await is_valid_prop(entry)]
            logger.info(f" [鸣潮][dc卡片识别] 声骸信息提取内容:{valid_entries}")
            
            # 主词条逻辑（取前两个有效词条）
            for entry in valid_entries[:2]:
                equipment["mainProps"].append({
                    "attributeName": entry[0],
                    "attributeValue": entry[1],
                    "iconUrl": "" 
                })
            
            # 副词条逻辑（取接下来5个有效词条）
            for entry in valid_entries[2:7]:
                equipment["subProps"].append({
                    "attributeName": entry[0],
                    "attributeValue": entry[1]
                })

            # 有效性验证
            if len(equipment["mainProps"]) >= 1:
                final_result["装备数据"].append(equipment)

        # 武器名称提取逻辑优化
        if len(ocr_results) > 11:
            for data in ocr_results[11]:
                text, conf = data[1], data[2]
                logger.info(f" [鸣潮][dc卡片识别] ocr武器信息内容:{text}，置信度:{conf}")

                # 匹配武器名
                if patterns["weapon_name"][0].fullmatch(text) and conf >= patterns["weapon_name"][1]:
                    if '武器名' not in final_result["武器信息"]:
                        final_result["武器信息"]["武器名"] = cc.convert(text)
            
                # 匹配武器等级
                level_match = patterns["weapon_level"][0].search(text)
                if level_match and conf >= patterns["weapon_level"][1]:
                    if '等级' not in final_result["武器信息"]:
                        final_result["武器信息"]["等级"] = int(level_match.group(1))

    logger.info(f" [鸣潮][dc卡片识别] 提取内容:{final_result}")
    return True, final_result
