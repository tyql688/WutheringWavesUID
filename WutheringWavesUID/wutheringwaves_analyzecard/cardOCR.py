
# 标准库
import re
import ssl
import httpx
import base64
import aiohttp
import asyncio
import numpy as np
from PIL import Image
from io import BytesIO
from opencc import OpenCC
from aiohttp import ClientTimeout
from async_timeout import timeout

# 项目内部模块
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger

from .detail_json import DETAIL
from ..wutheringwaves_config import WutheringWavesConfig
from ..wutheringwaves_analyzecard.userData import save_card_dict_to_json


# 原始dc卡片参考分辨率，from example_card_2.png
REF_WIDTH = 1072
REF_HEIGHT = 602
    
# 裁切区域比例（左、上、右、下），数字来自src/example_card_2.png
# 技能树扫描顺序：普攻、共鸣技能、共鸣解放、变奏技能、共鸣回路(json_skillList顺序)
# 有可能出现空声骸，故放最后
crop_ratios = [
    (  0/REF_WIDTH,   0/REF_HEIGHT, 420/REF_WIDTH, 350/REF_HEIGHT), # 角色
    (890/REF_WIDTH, 240/REF_HEIGHT, 1020/REF_WIDTH,310/REF_HEIGHT), # 武器
    (583/REF_WIDTH,  30/REF_HEIGHT, 653/REF_WIDTH, 130/REF_HEIGHT), # 普攻
    (456/REF_WIDTH, 115/REF_HEIGHT, 526/REF_WIDTH, 215/REF_HEIGHT), # 共鸣技能
    (694/REF_WIDTH, 115/REF_HEIGHT, 764/REF_WIDTH, 215/REF_HEIGHT), # 共鸣解放
    (501/REF_WIDTH, 250/REF_HEIGHT, 571/REF_WIDTH, 350/REF_HEIGHT), # 变奏技能
    (650/REF_WIDTH, 250/REF_HEIGHT, 720/REF_WIDTH, 350/REF_HEIGHT), # 共鸣回路
    ( 10/REF_WIDTH, 360/REF_HEIGHT, 214/REF_WIDTH, 590/REF_HEIGHT), # 声骸1
    (221/REF_WIDTH, 360/REF_HEIGHT, 425/REF_WIDTH, 590/REF_HEIGHT), # 声骸2
    (430/REF_WIDTH, 360/REF_HEIGHT, 634/REF_WIDTH, 590/REF_HEIGHT), # 声骸3
    (639/REF_WIDTH, 360/REF_HEIGHT, 843/REF_WIDTH, 590/REF_HEIGHT), # 声骸4
    (848/REF_WIDTH, 360/REF_HEIGHT, 1052/REF_WIDTH,590/REF_HEIGHT), # 声骸5
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

# 全局配置
OCR_TIMEOUT = ClientTimeout(total=10)  # 总超时 10 秒
OCR_SESSION = None  # 全局会话实例

async def get_global_session():
    global OCR_SESSION
    if OCR_SESSION is None or OCR_SESSION.closed:
        # 设置连接池参数：最多 10 个连接，空闲 60 秒自动关闭
        connector = aiohttp.TCPConnector(
            limit=10,
            keepalive_timeout=60  # 空闲连接保留 60 秒
        )
        OCR_SESSION = aiohttp.ClientSession(
            connector=connector,
            timeout=ClientTimeout(total=10)
        )
        logger.info("[鸣潮]已创建新的全局 OCR 会话")
    return OCR_SESSION

async def check_ocr_link_accessible(key="helloworld") -> bool:
    """
    检查OCR.space示例链接是否能正常访问，返回布尔值。
    """
    url = "https://api.ocr.space/parse/imageurl"
    payload = {
        'url': 'https://dl.a9t9.com/ocr/solarcell.jpg',
        'apikey': f'{key}',
    }
    try:
        session = await get_global_session()  # 复用全局会话
        async with session.get(url, data=payload, timeout=10) as response:
            data = await response.json()
            logger.debug(f"[鸣潮]OCR.space示例链接访问成功，状态码为 {response.status}\n内容：{data}")
            return response.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError):
        logger.warning("[鸣潮]OCR.space 访问示例链接失败，请检查网络或服务状态。")
        return False

async def check_ocr_engine_accessible() -> int:
    """
    检查OcrEngine_2状态（通过解析HTML表格）
    返回1表示UP，0表示DOWN或其他错误
    """
    from bs4 import BeautifulSoup
    url = "https://status.ocr.space"
    try:
        session = await get_global_session()
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 定位目标表格
            target_table = soup.find('h4', string='API Access Points').find_next('table')
            
            # 查找包含"Free OCR API"的行
            for row in target_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >=4 and "Free OCR API" in cells[0].text:
                    status_1 = cells[2].text.strip().upper()
                    status_2 = cells[3].text.strip().upper()
                    logger.info(f"[鸣潮] OcrEngine_1:{status_1}, OcrEngine_2:{status_2}")
                    if status_2 == "UP":
                        return 2
                    elif status_1 == "UP":
                        return 1
                    else:
                        return 0
                    
            logger.warning("[鸣潮] 未找到状态行")
            return 1
            
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.warning(f"[鸣潮] 网络错误: {e}")
        return -1
    except Exception as e:
        logger.warning(f"[鸣潮] 解析异常: {e}")
        return -1
async def async_ocr(bot: Bot, ev: Event):
    """
    异步OCR识别函数
    """
    api_key_list = WutheringWavesConfig.get_config("OCRspaceApiKeyList").data  # 从控制台获取OCR.space的API密钥
    if api_key_list == []:
        logger.warning("[鸣潮] OCRspace API密钥为空！请检查控制台。")
        await bot.send("[鸣潮] OCRspace API密钥未配置，请检查控制台。")
        return False

    # 检查可用引擎
    engine_num = await check_ocr_engine_accessible()
    logger.info(f"[鸣潮]OCR.space服务engine：{engine_num}")
    # 初始化密钥和引擎
    API_KEY = None
    NEGINE_NUM = None

    bool_i, image = await upload_discord_bot_card(ev)
    if not bool_i:
        return await bot.send("[鸣潮]获取dc卡片图失败！卡片分析已停止。")
    # 获取dc卡片与共鸣链
    chain_num, cropped_images = await cut_card_to_ocr(image)

    # 遍历密钥
    ocr_results =  None
    for key in api_key_list:
        if not key: 
            continue

        API_KEY = key
        NEGINE_NUM = engine_num
        if key[0] != "K":
            NEGINE_NUM = 3 # 激活PRO计划

        if NEGINE_NUM == 0:
            return await bot.send("[鸣潮] OCR服务暂时不可用，请稍后再试。")
        elif NEGINE_NUM == -1:
            return await bot.send("[鸣潮] 服务器访问OCR服务失败，请检查服务器网络状态。")
        
        ocr_results = await images_ocrspace(API_KEY, NEGINE_NUM, cropped_images)
        logger.info(f"[鸣潮][OCRspace]dc卡片识别数据:\n{ocr_results}")
        if not ocr_results[0]['error']:
            logger.success("[鸣潮]OCRspace 识别成功！")
            break

    if API_KEY is None:
        return await bot.send("[鸣潮] OCRspace API密钥不可用！请等待额度恢复或更换密钥")
    
    if ocr_results[0]['error'] or not ocr_results:
        logger.warning("[鸣潮]OCRspace识别失败！请检查服务器网络是否正常。")
        return await bot.send("[鸣潮]OCRspace识别失败！请检查服务器网络是否正常。")

    bool_d, final_result = await ocr_results_to_dict(chain_num, ocr_results)
    if not bool_d:
        return await bot.send("[鸣潮]Please use chinese card！")

    name, char_id = await which_char(bot, ev, final_result["角色信息"]["角色名"])
    if char_id is None:
        logger.warning(f"[鸣潮][dc卡片识别] 角色{name}识别错误！")
        return await bot.send(f"[鸣潮]识别结果为角色{name}不存在")
    final_result["角色信息"]["角色名"] = name
    final_result["角色信息"]["角色ID"] = char_id

    
    await save_card_dict_to_json(bot, ev, final_result)

        
    

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
        elif content.type == "text" and content.data and isinstance(content.data, str) and content.data.startswith("http"):
            res.append(content.data)

    if not res and ev.image:
        res.append(ev.image)

    return res

async def upload_discord_bot_card(ev: Event):
    """
    上传Discord机器人的卡片
    change from .upload_card.upload_custom_card
    """
    upload_images = await get_image(ev)
    if not upload_images:
        return False, None

    logger.info(f"[鸣潮]卡片分析上传链接{upload_images}")
    success = False
    url = upload_images[0] # 处理一张图片
    if url:
        if httpx.__version__ >= "0.28.0":
            ssl_context = ssl.create_default_context()
            # ssl_context.set_ciphers("AES128-GCM-SHA256")
            ssl_context.set_ciphers("DEFAULT")
            sess = httpx.AsyncClient(verify=ssl_context)
        else:
            sess = httpx.AsyncClient()

        try:
            if isinstance(sess, httpx.AsyncClient):
                res = await sess.get(url)
                image_data = res.read()
                retcode = res.status_code
            else:
                async with sess.get(url) as resp:
                    image_data = await resp.read()
                    retcode = resp.status

            if retcode == 200:
                success = True
                logger.success('[鸣潮]图片获取完成！')
            else:
                logger.warning(f"[鸣潮]图片获取失败！错误码{retcode}")

        except Exception as e:
            logger.error(e)
            logger.warning("[鸣潮]图片获取失败！")

    if success:
        image = Image.open(BytesIO(image_data))
        return True, image
    else:
        return False, None

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
            logger.warning("[鸣潮]卡片分析 共鸣链识别出现断裂错误")
            return 0
        
    return chain_num

async def cut_card_to_ocr(image):
    """
    裁切卡片：角色，技能树*5，声骸*5，武器
        （按比例适配任意分辨率，1920*1080识别效果优良）
    """
    
    # 分析角色共鸣链数据
    chain_num = analyze_chain_num(image)

    # 裁切卡片，分割识别范围
    cropped_images = cut_image(image, crop_ratios)

    # 进一步裁切角色图
    image_char = cropped_images[0]
    cropped_images[0] = cut_image_need_data(image_char, char_crop_ratios)

    # 进一步裁剪拼接声骸图
    for i in range(7, 12):  # 替换索引7-11，即5张声骸图
        image_echo = cropped_images[i]
        cropped_images[i] = cut_image_need_data(image_echo, echo_crop_ratios) 

    # 调用 images_ocrspace 函数并获取识别结果
    return chain_num, cropped_images

async def images_ocrspace(api_key, engine_num, cropped_images):
    """
    使用 OCR.space 免费API识别碎块图片
    """
    API_KEY = api_key
    FREE_URL = 'https://api.ocr.space/parse/image'
    PRO_URL = 'https://apipro2.ocr.space/parse/image'
    if engine_num == 3:
        API_URL = PRO_URL
        ENGINE_NUM = 2
    else:
        API_URL = FREE_URL
        ENGINE_NUM = engine_num
    logger.info(f"[鸣潮]使用 {API_URL} 识别图片")

    session = await get_global_session()  # 复用全局会话
    tasks = []
    payloads = []  # 存储所有payload
    for img in cropped_images:
        # 将PIL.Image转换为base64
        try:
            buffered = BytesIO()
            img.save(buffered, format='PNG')
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            logger.warning(f"图像转换错误: {e}")
            continue
                
        # 构建请求参数
        """
        language: 仅繁体中文（正确参数值）
        isOverlayRequired: 需要坐标信息
        OCREngine: 使用引擎2, 识别效果更好，声骸识别差一些
        isTable: 启用表格识别模式
        detectOrientation: 自动检测方向
        scale: 图像缩放增强
        """
        payload = {
            'apikey': API_KEY,
            'language': 'cht',          
            'isOverlayRequired': True, 
            'base64Image': f'data:image/png;base64,{img_base64}',
            'OCREngine': ENGINE_NUM,             
            'isTable': True,    
            'detectOrientation': True, 
            'scale': True              
        }
        payloads.append(payload)

    # 添加0.1秒固定延迟的请求函数
    async def delayed_fetch(payload):
        await asyncio.sleep(0.5)  # 固定0.5秒延迟
        return await fetch_ocr_result(session, API_URL, payload)
    
    # 创建所有任务
    tasks = [delayed_fetch(payload) for payload in payloads]

    # 限制并发数为2防止超过API限制
    semaphore = asyncio.Semaphore(2)
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
        async with session.post(url, data=payload, timeout=10) as response: # ✅ 添加单次请求超时
            # 检查HTTP状态码
            if response.status != 200:
                # 修改错误返回格式为字典（与其他成功结果结构一致）
                return [{'error': f'HTTP Error {response}', 'text': None}]
                
            data = await response.json()
            
            # 解析结果
            if not data.get('ParsedResults'):
                return [{'error': 'No Results', 'text': None}]
                
            # 提取识别结果
            for result in data.get('ParsedResults', []):
                # 补充完整文本
                if result.get('ParsedText'):
                    return [{'error': None, 'text': result.get('ParsedText')}]
                
            return [{'error': 'No Results', 'text': None}]
                
    except Exception as e:
        return [{'error': f'Processing Error:{e}', 'text': None}]

async def ocr_results_to_dict(chain_num, ocr_results):
    """
    适配OCR.space输出结构的增强版结果解析
    输入结构: [{'text': '...', 'error': ...}, ...]
    """
    # 识别结果容器
    final_result = {
        "用户信息": {},
        "角色信息": {},
        "技能等级": [],
        "装备数据": [],
        "武器信息": {}
    }
    
    # 保存角色共鸣链
    if not final_result["角色信息"].get("共鸣链"):
        final_result["角色信息"]["共鸣链"] = chain_num

    # 增强正则模式（适配多行文本处理）
    patterns = {
        "name": re.compile(r'^([A-Za-z\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3\u00C0-\u00FF]+)'), # 支持英文、中文、日文、韩文，以及西班牙文、德文和法文中的扩展拉丁字符，为后续逻辑判断用
        "level": re.compile(r'(?i)^(?:.*?V)?\s*?(\d+)$'), # 兼容纯数字
        "skill_level": re.compile(r'(\d+)\s*[/ ]\s*\d*'),  # 兼容 L.10/10、LV.10/1、4 10、4/ 等格式
        "player_info": re.compile(r'玩家名(?:稱)?\s*[:：]?\s*(.*)$'),
        "uid_info": re.compile(r'.[馬碼]\s*[:：]?\s*(\d+)'),
        "echo_value": re.compile(r'([\u4e00-\u9fa5]+)\s*\D*([\d.]+%?)'), # 不支持英文词条(空格不好处理), 支持处理"暴擊傷害 器44%", "攻擊 ×18%"
        "weapon_info": re.compile(r'([\u4e00-\u9fa5]+)\s+LV\.(\d+)')
    }

    cc = OpenCC('t2s')  # 繁体转简体

    # 处理角色信息（第一个识别结果）0
    if ocr_results:
        first_result = ocr_results[0]
        if first_result['error'] is None:
            lines = first_result['text'].split('\t') # 支持"◎\t洛可可\tLV.90\t"
            for line in lines:
                # 玩家名称
                player_match = patterns["player_info"].search(line)
                if player_match:
                    final_result["用户信息"]["玩家名称"] = player_match.group(1)
                    continue # 避免玩家名称在前被识别为角色名

                # 文本预处理：删除非数字中英文的符号及多余空白
                line_clean = re.sub(r'[^\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3\u00C0-\u00FFA-Za-z0-9\s]', '', line)  # 先删除特殊符号, 匹配“漂泊者·湮灭”
                line_clean = re.sub(r'\s+', ' ', line_clean).strip()  # 再合并多余空白

                # 角色名提取
                if not final_result["角色信息"].get("角色名"):
                    name_match = patterns["name"].search(line_clean)
                    if name_match:
                        name = name_match.group()
                        name = name.replace("吟槑", "吟霖")
                        if not re.match(r'^[\u4e00-\u9fa5]+$', name):
                            logger.warning(f" [鸣潮][dc卡片识别] 识别出非中文角色名:{name}，退出识别！")
                            return False, final_result
                        final_result["角色信息"]["角色名"] = cc.convert(name)
                
                # 等级提取
                line_num = re.sub(r'[oOQ○◌θ]', "0", line_clean) # 处理0的错误识别
                line_num = re.sub(r'[^0-9\s]', '', line_num)
                level_match = patterns["level"].search(line_num)
                if level_match and not final_result["角色信息"].get("等级"):
                    final_result["角色信息"]["等级"] = int(level_match.group(1))
                
                # UID提取
                uid_match = patterns["uid_info"].search(line_clean)
                if uid_match:
                    final_result["用户信息"]["UID"] = uid_match.group(1)

    # 处理武器信息（第二个结果）1
    if len(ocr_results) > 1 and ocr_results[1]['error'] is None:
        text = ocr_results[1]['text']
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 武器名称（取第一行有效文本）
        for line in lines:
            # 文本预处理：删除非数字中英文的符号及多余空白
            line_clean = re.sub(r'[oOQ○◌θ]', "0", line) # 处理0的错误识别
            line_clean = re.sub(r'[^0-9\u4e00-\u9fa5\s]', '', line_clean)  # 先删除非数字中英文的符号, 匹配“源能臂铠·测肆”
            line_clean = re.sub(r'\s+', ' ', line_clean).strip()  # 再合并多余空白
            if patterns["name"].search(line_clean):
                line_clean = re.sub(r'.*古洑流$', '千古洑流', line_clean)
                final_result["武器信息"]["武器名"] = cc.convert(line_clean)
                continue

            level_match = patterns["level"].search(line_clean)
            if level_match:
                final_result["武器信息"]["等级"] = int(level_match.group(1))
                continue

    # 处理技能等级（第3-7个结果）下标：2 3 4 5 6
    for idx in range(2, 7):
        if idx >= len(ocr_results) or ocr_results[idx]['error'] is not None:
            final_result["技能等级"].append(1)
            continue
            
        text = ocr_results[idx]['text']
        # 强化文本清洗
        text_clean = re.sub(r'[oOQ○◌θ]', "0", text) # 处理0的错误识别
        text_clean = re.sub(r'[^0-9/]', ' ', text_clean)  # 将非数字字符替换为空格
        match = patterns["skill_level"].search(text_clean)
        if match:
            level = int(match.group(1))
            level = level if level > 0 else 1 # 限制最小等级为1
            final_result["技能等级"].append(min(level, 10))  # 限制最大等级为10
        else:
            logger.warning(f"[鸣潮][dc卡片识别]无法识别的技能等级：{text}")
            final_result["技能等级"].append(1)

    # 处理声骸装备（第8-12个结果）下标：7 8 9 10 11
    for idx in range(7, 12):
        if idx >= len(ocr_results) or ocr_results[idx]['error'] is not None:
            continue
            
        equipment = {"mainProps": [], "subProps": []}
        text = ocr_results[idx]['text']
        
        # 文本预处理：去除多余的空白符
        text_clean = re.sub(r'\s+', ' ', text).strip()  # 使用 \s+ 匹配所有空白符，并替换为单个空格
        text_clean = re.sub(r'[·，,、,]', '.', text_clean) # 将·与逗号替换为句号(中文全角逗号（简体和繁体）、英文半角逗号、日文逗号（全角顿号）、韩文逗号)
        text_clean = text_clean.replace("％", "%")

        # 提取属性对
        matches = patterns["echo_value"].findall(text_clean)
        valid_entries = []
        for attr, value in matches:
            # 属性清洗
            attr = attr.strip()
            # 自定义替换优先执行（在繁转简之前）
            if re.search(r'暴.(傷害)?', attr):
                attr = re.sub(r'暴.(傷害)?', r'暴擊\1', attr)
            attr = attr.replace("箓擎傷害", "暴擊傷害").replace("箓擎", "暴擊")
            attr = re.sub(r'^攻.*$', '攻擊', attr)
            attr = re.sub(r'.*效率$', '共鳴效率', attr)
            attr = re.sub(r'^重.傷害加成*$', '重擊傷害加成', attr)
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

    logger.info(f" [鸣潮][dc卡片识别] 最终提取内容:\n{final_result}")
    return True, final_result

async def which_char(bot: Bot, ev: Event, char: str):
    at_sender = True if ev.group_id else False
    # 角色信息
    candidates = []
    for char_id, info in DETAIL.items():
        normalized_name = info["name"].replace("·", "").replace(" ", "")
        if char in normalized_name:
            candidates.append((char_id, info))
    logger.debug(f"[鸣潮][dc卡片识别] 角色匹配结果：{candidates}")

    if len(candidates) == 0:  # 无匹配
        return char, None

    if len(candidates) == 1:  # 唯一匹配
        char_id, info = candidates[0]
        return info["name"], char_id

    # 为漂泊者？
    options = []
    flat_choices = []  # 存储 (角色名, id)
    for idx, (char_id, info) in enumerate(candidates, 1):
        sex = info.get("sex", "未配置")
        options.append(f"{idx:>2}: [{sex}] {info['name']}")
        flat_choices.append((info['name'], char_id))
    
    # 构建双列布局
    paired_options = []
    for i in range(0, len(options), 2):
        line = []
        if i < len(options):
            line.append(options[i])
        if i+1 < len(options):
            line.append(options[i+1].ljust(30))  # 控制列宽
        paired_options.append("    ".join(line))  # 两列间用4空格分隔
    
    prompt = (
        f"[鸣潮] 检测到{char}的多个分支：\n"
        + "\n".join(paired_options) 
        + f"\n请于30秒内输入序号选择（1-{len(candidates)}）"
    )
    await bot.send(prompt, at_sender=at_sender)
    
    # 第四步：处理用户响应
    try:
        async with timeout(30):
            while True:
                resp = await bot.receive_resp()
            
                if resp is not None and resp.content[0].type == "text" and resp.content[0].data.isdigit():
                    choice_idx = int(resp.content[0].data) - 1
                    if 0 <= choice_idx < len(flat_choices):
                        return flat_choices[choice_idx]
                await bot.send(f"无效序号，请输入范围[1-{len(candidates)}]的数字选择", at_sender=at_sender)
    except asyncio.TimeoutError:
        default_name, default_id = flat_choices[0] if flat_choices else (char, None)
        await bot.send(f"[鸣潮] 选择超时，已自动使用 {default_name}", at_sender=at_sender)
        return default_name, default_id