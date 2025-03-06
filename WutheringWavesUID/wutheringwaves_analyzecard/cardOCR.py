
# 标准库
import re
import os
import ssl
import httpx
import base64
import aiohttp
import asyncio
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
from opencc import OpenCC

# 项目内部模块
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.download_resource.download_file import download

from ..wutheringwaves_config import WutheringWavesConfig
from ..wutheringwaves_analyzecard.userData import save_card_dict_to_json


SRC_PATH = Path(__file__).parent / "src"
CARD_PATH = Path(__file__).parent / "src/card.jpg"
CARD_NAME = "card.jpg"

# 原始dc卡片参考分辨率，from example_card_2.png
REF_WIDTH = 1072
REF_HEIGHT = 602
    
# 裁切区域比例（左、上、右、下），数字来自src/example_card_2.png
# 技能树扫描顺序：普攻、共鸣技能、共鸣解放、变奏技能、共鸣回路(json_skillList顺序)
crop_ratios = [
    (  0/REF_WIDTH,   0/REF_HEIGHT, 420/REF_WIDTH, 350/REF_HEIGHT), # 角色
    (583/REF_WIDTH,  30/REF_HEIGHT, 653/REF_WIDTH, 130/REF_HEIGHT), # 普攻
    (456/REF_WIDTH, 115/REF_HEIGHT, 526/REF_WIDTH, 215/REF_HEIGHT), # 共鸣技能
    (694/REF_WIDTH, 115/REF_HEIGHT, 764/REF_WIDTH, 215/REF_HEIGHT), # 共鸣解放
    (501/REF_WIDTH, 250/REF_HEIGHT, 571/REF_WIDTH, 350/REF_HEIGHT), # 变奏技能
    (650/REF_WIDTH, 250/REF_HEIGHT, 720/REF_WIDTH, 350/REF_HEIGHT), # 共鸣回路
    ( 10/REF_WIDTH, 360/REF_HEIGHT, 214/REF_WIDTH, 590/REF_HEIGHT), # 声骸1
    (221/REF_WIDTH, 360/REF_HEIGHT, 425/REF_WIDTH, 590/REF_HEIGHT), # 声骸2
    (430/REF_WIDTH, 360/REF_HEIGHT, 634/REF_WIDTH, 590/REF_HEIGHT), # 声骸3
    (639/REF_WIDTH, 360/REF_HEIGHT, 843/REF_WIDTH, 590/REF_HEIGHT), # 声骸4
    (848/REF_WIDTH, 360/REF_HEIGHT, 1052/REF_WIDTH, 590/REF_HEIGHT), # 声骸5
    (800/REF_WIDTH, 240/REF_HEIGHT, 1020/REF_WIDTH, 350/REF_HEIGHT), # 武器
]
# 共鸣链识别顺序（从右往左，从6到1）
chain_crop_ratios = [
    (321/REF_WIDTH, 316/REF_HEIGHT, 332/REF_WIDTH, 327/REF_HEIGHT), # 6
    (276/REF_WIDTH, 316/REF_HEIGHT, 287/REF_WIDTH, 327/REF_HEIGHT), # 5
    (231/REF_WIDTH, 316/REF_HEIGHT, 242/REF_WIDTH, 327/REF_HEIGHT), # 4
    (186/REF_WIDTH, 316/REF_HEIGHT, 197/REF_WIDTH, 327/REF_HEIGHT), # 3
    (141/REF_WIDTH, 316/REF_HEIGHT, 152/REF_WIDTH, 327/REF_HEIGHT), # 2
    (100/REF_WIDTH, 316/REF_HEIGHT, 111/REF_WIDTH, 327/REF_HEIGHT), # 1
]

# 原始角色裁切区域参考分辨率，from crop_ratios
CHAR_WIDTH = 420
CHAR_HEIGHT = 350
char_crop_ratios = [
    (37/CHAR_WIDTH,  0/CHAR_HEIGHT, 250/CHAR_WIDTH,  45/CHAR_HEIGHT), # 上面角色名称与等级
    ( 0/CHAR_WIDTH, 45/CHAR_HEIGHT, 155/CHAR_WIDTH, 80/CHAR_HEIGHT), # 下面用户昵称与id
]

# 原始声骸裁切区域参考分辨率，from crop_ratios
ECHO_WIDTH = 204
ECHO_HEIGHT = 230
echo_crop_ratios = [
    (110/ECHO_WIDTH,  40/ECHO_HEIGHT, 204/ECHO_WIDTH,  85/ECHO_HEIGHT), # 右上角主词条(忽略声骸cost，暂不处理)
    ( 26/ECHO_WIDTH, 105/ECHO_HEIGHT, 204/ECHO_WIDTH, 230/ECHO_HEIGHT), # 下部6条副词条
]

# 识别结果容器
final_result = {
    "用户信息": {},
    "角色信息": {},
    "技能等级": [],
    "装备数据": [],
    "武器信息": {}
}

async def async_ocr(bot: Bot, ev: Event):
    """
    异步OCR识别函数
    """
    API_KEY = WutheringWavesConfig.get_config("OCRspaceApiKey").data  # 从控制台获取OCR.space的API密钥
    if not API_KEY:
        logger.info(f"[鸣潮]OCRspace API密钥为空！请检查控制台获取API密钥。")
        await bot.send(f"[鸣潮]OCRspace API密钥为空！请检查控制台获取API密钥。")
        return False

    if not await upload_discord_bot_card(bot, ev):
        await bot.send(f"[鸣潮]卡片分析已停止。")
        return False

    # 获取dc卡片识别结果,使用API_KEY
    ocr_results = await cut_card_to_ocr(API_KEY)
    logger.info(f"[鸣潮][OCRspace]dc卡片识别数据:\n{ocr_results}")

    if ocr_results[0]['error']:
        logger.info(f"[鸣潮]OCRspace识别访问失败！请检查控制台API密钥是否正确，服务器网络是否正常。")
        await bot.send(f"[鸣潮]OCRspace识别访问失败！请检查控制台API密钥是否正确，服务器网络是否正常。")
        return False

    bool, final_result = await ocr_results_to_dict(ocr_results)

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

def cut_image(image, crop_ratios):
    # 获取实际分辨率
    img_width, img_height = image.size  
    # 裁切图片
    cropped_images = []
    for ratio in crop_ratios:
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

    return cropped_images

def cut_image_need_data(image_need, data_crop_ratios):
    """
    裁切声骸卡片拼接词条数据: 右上角主词条与余下6条副词条
    裁切角色卡片拼接用户数据: 上面角色数据，下面用户信息
    目的: 优化ocrspace 模型2识别
    """
    # 获取裁切后的子图列表
    cropped_images = cut_image(image_need, data_crop_ratios)

    # 计算拼接后图片的总高度和最大宽度
    total_height = sum(img.height for img in cropped_images)
    max_width = max(img.width for img in cropped_images) if cropped_images else 0

    # 创建新画布并逐个粘贴子图
    image_only_data = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for img in cropped_images:
        image_only_data.paste(img, (0, y_offset))
        y_offset += img.height  # 累加y轴偏移量

    return image_only_data

def analyze_chain_num(image):
    cropped_chain_images = cut_image(image, chain_crop_ratios)

    avg_colors = []

    # 遍历切割后的图像区域
    for i, region in enumerate(cropped_chain_images):
        # 确保图像为RGB模式
        region = region.convert('RGB')
        region_array = np.array(region)

        # 计算平均颜色
        avg_r = int(np.mean(region_array[:, :, 0]))
        avg_g = int(np.mean(region_array[:, :, 1]))
        avg_b = int(np.mean(region_array[:, :, 2]))
        avg_colors.append((avg_r, avg_g, avg_b))

    def is_chain_color(color):
        """
        参考 rgb值 -- 3链
        (143, 129, 79)
        (144, 129, 80)
        (142, 128, 79)
        (203, 185, 127)
        (205, 189, 132)
        (207, 191, 135)
        360 与 530 的中值为 445
        """
        r, g, b = color
        return (r + g + b) > 445

    chain_num = 0
    chain_bool = False # 共鸣链判断触发应连续
    for color in avg_colors:
        if not chain_bool and is_chain_color(color):
            chain_bool = True
            chain_num = 1
            continue
        if chain_bool and is_chain_color(color):
            chain_num += 1
            continue
        if chain_bool and not is_chain_color(color):
            logger.debug(f"[鸣潮]卡片分析 共鸣链识别出现断裂错误")
            return 0
        
    return chain_num

async def cut_card_to_ocr(api_key):
    """
    裁切卡片：角色，技能树*5，声骸*5，武器
        （按比例适配任意分辨率，1920*1080识别效果优良）
    """

    # 打开图片
    image = Image.open(CARD_PATH).convert('RGB')
    
    # 分析角色共鸣链数据
    chain_num = analyze_chain_num(image)
    if not final_result["角色信息"].get("共鸣链"):
        final_result["角色信息"]["共鸣链"] = chain_num

    # 裁切卡片，分割识别范围
    cropped_images = cut_image(image, crop_ratios)

    # 进一步裁切角色图
    image_char = cropped_images[0]
    cropped_images[0] = cut_image_need_data(image_char, char_crop_ratios)

    # 进一步裁剪拼接声骸图
    for i in range(6, 11):  # 替换索引6-10，即5张声骸图
        image_echo = cropped_images[i]
        cropped_images[i] = cut_image_need_data(image_echo, echo_crop_ratios) 

    # for i, cropped_image in enumerate(cropped_images):
    #     # 保存裁切后的图片
    #     cropped_image.save(f"{SRC_PATH}/_{i}.png")
    
    os.remove(CARD_PATH) # 删除原图片

    # 调用 images_ocrspace 函数并获取识别结果
    return await images_ocrspace(api_key, cropped_images)

async def images_ocrspace(api_key, cropped_images):
    """
    使用 OCR.space 免费API识别碎块图片
    """
    API_KEY = api_key
    API_URL = 'https://api.ocr.space/parse/image'

    async with aiohttp.ClientSession() as session:
        tasks = []
        for img in cropped_images:
            # 将PIL.Image转换为base64
            try:
                buffered = BytesIO()
                img.save(buffered, format='PNG')
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            except Exception as e:
                print(f"图像转换错误: {e}")
                continue
                
            # 构建请求参数
            payload = {
                'apikey': API_KEY,
                'language': 'cht',          # 仅繁体中文（正确参数值）
                'isOverlayRequired': 'True', # 需要坐标信息
                'base64Image': f'data:image/png;base64,{img_base64}',
                'OCREngine': 2,             # 使用引擎2, 识别效果更好，声骸识别差一些
                'isTable': 'True',    # 启用表格识别模式
                'detectOrientation': 'True', # 自动检测方向
                'scale': 'True'              # 图像缩放增强
            }

            tasks.append(fetch_ocr_result(session, API_URL, payload))

        # 限制并发数为5防止超过API限制
        semaphore = asyncio.Semaphore(5)
        # 修改返回结果处理
        results = await asyncio.gather(*(process_with_semaphore(task, semaphore) for task in tasks))
        
        # 扁平化处理（合并所有子列表）
        return [item for sublist in results for item in sublist]

async def process_with_semaphore(task, semaphore):
    async with semaphore:
        return await task

async def fetch_ocr_result(session, url, payload):
    """发送OCR请求并处理响应"""
    try:
        async with session.post(url, data=payload) as response:
            # 检查HTTP状态码
            if response.status != 200:
                # 修改错误返回格式为字典（与其他成功结果结构一致）
                return [{'error': f'HTTP Error {response.status}', 'text': None}]
                
            data = await response.json()
                
            # 检查API错误
            if data.get('IsErroredOnProcessing', False):
                return [{'error': data.get('ErrorMessage', '未知错误'), 'text': None}]
                
            # 解析结果
            if not data.get('ParsedResults'):
                return [{'error': 'No Results', 'text': None}]
                
            output = []
                
            # 提取识别结果
            for result in data.get('ParsedResults', []):
                # 补充完整文本
                if parsed_text := result.get('ParsedText'):
                    output.append({
                        'text': parsed_text,
                        'error': None  # 统一数据结构
                    })
                
            return output
                
    except aiohttp.ClientError as e:
        return [{'error': f'Network Error:{str(e)}', 'text': None}]
    except Exception as e:
        return [{'error': f'Processing Error:{str(e)}', 'text': None}]

async def ocr_results_to_dict(ocr_results):
    """
    适配OCR.space输出结构的增强版结果解析
    输入结构: [{'text': '...', 'error': ...}, ...]
    """
    # 增强正则模式（适配多行文本处理）
    patterns = {
        "name": re.compile(r'^([\u4e00-\u9fa5A-Za-z]+)'), # 支持英文名，为后续逻辑判断用
        "level": re.compile(r'(?i)(.V?\.?)\s*(\d+)'),
        "skill_level": re.compile(r'(\d+)/10'),
        "player_info": re.compile(r'玩家名稱[:：]\s*(\S+)'),
        "uid_info": re.compile(r'特.碼[:：]\s*(\d+)'),
        "echo_value": re.compile(r'([\u4e00-\u9fa5]+)\s*\D*([\d.]+%?)'), # 不支持英文词条(空格不好处理), 支持处理"暴擊傷害 器44%", "攻擊 ×18%"
        "weapon_info": re.compile(r'([\u4e00-\u9fa5]+)\s+LV\.(\d+)')
    }

    cc = OpenCC('t2s')  # 繁体转简体

    # 处理角色信息（第一个识别结果）
    if ocr_results:
        first_result = ocr_results[0]
        if first_result['error'] is None:
            lines = first_result['text'].split('\t') # 支持"◎\t洛可可\tLV.90\t"
            for line in lines:
                # 文本预处理：去除多余的空白符
                line_clean = re.sub(r'\s+', ' ', line).strip()  # 使用 \s+ 匹配所有空白符，并替换为单个空格
                # line = line.strip()
                
                # 角色名提取
                if not final_result["角色信息"].get("角色名"):
                    name_match = patterns["name"].search(line_clean)
                    if name_match:
                        name = name_match.group()
                        name = name.replace("吟槑", "吟霖")
                        if not re.match(r'^[\u4e00-\u9fa5]+$', name):
                            logger.debug(f" [鸣潮][dc卡片识别] 识别出英文角色名:{name}，退出识别！")
                            return False, final_result
                        final_result["角色信息"]["角色名"] = cc.convert(name)
                
                # 等级提取
                level_match = patterns["level"].search(line_clean)
                if level_match and not final_result["角色信息"].get("等级"):
                    final_result["角色信息"]["等级"] = int(level_match.group(2))
                
                # 玩家名称
                player_match = patterns["player_info"].search(line_clean)
                if player_match:
                    final_result["用户信息"]["玩家名称"] = player_match.group(1)
                
                # UID提取
                uid_match = patterns["uid_info"].search(line_clean)
                if uid_match:
                    final_result["用户信息"]["UID"] = uid_match.group(1)

    # 处理技能等级（第2-6个结果）
    for idx in range(1, 6):
        if idx >= len(ocr_results) or ocr_results[idx]['error'] is not None:
            final_result["技能等级"].append(1)
            continue
            
        text = ocr_results[idx]['text']
        matches = patterns["skill_level"].findall(text)
        if matches:
            try:
                level = int(matches[0])
                final_result["技能等级"].append(min(level, 10))  # 限制最大等级为10
            except:
                final_result["技能等级"].append(1)
        else:
            final_result["技能等级"].append(1)

    # 处理声骸装备（第7-11个结果）
    for idx in range(6, 11):
        if idx >= len(ocr_results) or ocr_results[idx]['error'] is not None:
            continue
            
        equipment = {"mainProps": [], "subProps": []}
        text = ocr_results[idx]['text']
        
        # 文本预处理：去除多余的空白符
        text_clean = re.sub(r'\s+', ' ', text).strip()  # 使用 \s+ 匹配所有空白符，并替换为单个空格

        # 提取属性对
        matches = patterns["echo_value"].findall(text_clean)
        valid_entries = []
        for attr, value in matches:
            # 属性清洗
            attr = attr.strip()
            # 自定义替换优先执行（在繁转简之前）
            attr = attr.replace("暴擎傷害", "暴擊傷害").replace("暴擎", "暴擊")
            clean_attr = cc.convert(attr) # 标准繁简转换
            # 验证属性名是否符合预期（至少两个中文字符，且不含数字）
            if len(clean_attr) >= 2 and not re.search(r'[0-9]', clean_attr):
                valid_entries.append((clean_attr, value))
        
        # 分配主副属性
        if valid_entries:
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
            
            final_result["装备数据"].append(equipment)

    # 处理武器信息（最后一个结果）
    if len(ocr_results) > 11 and ocr_results[11]['error'] is None:
        text = ocr_results[11]['text']
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 武器名称（取第一行有效文本）
        for line in lines:
            if patterns["name"].search(line):
                final_result["武器信息"]["武器名"] = cc.convert(line)
                break
                
        # 武器等级
        for line in lines:
            level_match = patterns["level"].search(line)
            if level_match:
                final_result["武器信息"]["等级"] = int(level_match.group(2))
                break

    logger.info(f" [鸣潮][dc卡片识别] 最终提取内容:\n{final_result}")
    return True, final_result
