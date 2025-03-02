import aiohttp
import asyncio
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path

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
    (650/REF_WIDTH, 250/REF_HEIGHT, 720/REF_WIDTH, 350/REF_HEIGHT), # 变奏技能
    (501/REF_WIDTH, 250/REF_HEIGHT, 571/REF_WIDTH, 350/REF_HEIGHT), # 共鸣回路
    ( 10/REF_WIDTH, 360/REF_HEIGHT, 214/REF_WIDTH, 590/REF_HEIGHT), # 声骸1
    (221/REF_WIDTH, 360/REF_HEIGHT, 425/REF_WIDTH, 590/REF_HEIGHT), # 声骸2
    (430/REF_WIDTH, 360/REF_HEIGHT, 634/REF_WIDTH, 590/REF_HEIGHT), # 声骸3
    (639/REF_WIDTH, 360/REF_HEIGHT, 843/REF_WIDTH, 590/REF_HEIGHT), # 声骸4
    (848/REF_WIDTH, 360/REF_HEIGHT, 1052/REF_WIDTH, 590/REF_HEIGHT), # 声骸5
    (800/REF_WIDTH, 240/REF_HEIGHT, 1020/REF_WIDTH, 350/REF_HEIGHT), # 武器
]

# 原始声骸裁切区域参考分辨率，from crop_ratios
ECHO_WIDTH = 204
ECHO_HEIGHT = 230

echo_crop_ratios = [
    (110/ECHO_WIDTH,  40/ECHO_HEIGHT, 204/ECHO_WIDTH,  85/ECHO_HEIGHT), # 右上角主词条(忽略声骸cost，暂不处理)
    ( 26/ECHO_WIDTH, 105/ECHO_HEIGHT, 204/ECHO_WIDTH, 230/ECHO_HEIGHT), # 下部6条副词条
]


def cut_image(image, img_width, img_height, crop_ratios):
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

def cut_echo_data_ocr(image_echo):
    """
    裁切声骸卡片拼接词条数据: 右上角主词条与余下6条副词条
    目的: 优化ocrspace 模型2识别
    """
    img_width, img_height = image_echo.size
    
    # 获取裁切后的子图列表
    cropped_images = cut_image(image_echo, img_width, img_height, echo_crop_ratios)

    # 计算拼接后图片的总高度和最大宽度
    total_height = sum(img.height for img in cropped_images)
    max_width = max(img.width for img in cropped_images) if cropped_images else 0

    # 创建新画布并逐个粘贴子图
    image_echo_only_data = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for img in cropped_images:
        image_echo_only_data.paste(img, (0, y_offset))
        y_offset += img.height  # 累加y轴偏移量

    return image_echo_only_data

async def cut_card_ocr():
    """
    裁切卡片：角色，技能树*5，声骸*5，武器
        （按比例适配任意分辨率，1920*1080识别效果优良）
    """

    # 打开图片
    image = Image.open(CARD_PATH).convert('RGB')
    img_width, img_height = image.size  # 获取实际分辨率
    
    cropped_images = cut_image(image, img_width, img_height, crop_ratios)

    # 进一步裁剪拼接声骸图
    for i in range(6, 11):  # 替换索引6-10，即5张声骸图
        image_echo = cropped_images[i]
        cropped_images[i] = cut_echo_data_ocr(image_echo) 

    for i, cropped_image in enumerate(cropped_images):
        # 保存裁切后的图片
        cropped_image.save(f"{SRC_PATH}/_{i}.png")
    
    return cropped_images

async def card_part_ocr(cropped_images):
    """
    使用 OCR.space 免费API识别碎块图片
    """
    API_KEY = 'K84320745188957'  # 请替换为你的API密钥
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

async def fetch_ocr_result(session, url, payload, retries=3):
    """发送OCR请求并处理响应, 错误重试次数: retries=3"""
    for attempt in range(retries):
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
                            'text': parsed_text.strip(),
                            'error': None  # 统一数据结构
                        })
                
                return output
                
        except aiohttp.ClientError as e:
            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)
                continue
            return [{'error': f'Network Error:{str(e)}', 'text': None}]
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)
                continue
            return [{'error': f'Processing Error:{str(e)}', 'text': None}]


# 使用示例
async def main():
    cropped_images = await cut_card_ocr()
    # 假设 cropped_images 是包含PIL.Image对象的列表
    results = await card_part_ocr(cropped_images)
    # print(results)
    
    if results:
        for i, item in enumerate(results):
            print(f"识别结果 {i+1}:")
            print(f"文本内容: \n{item['text']}")
            print(f"error内容: \n{item['error']}")
            print("-" * 30)
   


if __name__ == '__main__':
    asyncio.run(main())