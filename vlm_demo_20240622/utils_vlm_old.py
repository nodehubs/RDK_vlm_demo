# 赛博汪汪队 2024-6-22
# 腿臂机器人+大模型+多模态+语音识别=具身智能体Agent

print('导入视觉大模型模块')
import cv2
import numpy as np
from PIL import Image
from PIL import ImageFont, ImageDraw
# 导入中文字体，指定字号
font = ImageFont.truetype('asset/SimHei.ttf', 26)

from API_KEY import *

MY_SYSTEM_PROMPT = '''
你是带机械臂的机器狗,我将给你一句指令,请你根据我的指令和图像内容回复我,回复字数限制在20以内.
[输出json格式]
你直接输出json即可,一定要从{开始，必须以}结尾，不要输出包含```json的开头或结尾
json内容为{'mode':TEXT,'state':TEXT,'response':TEXT}，注意不要漏掉{}
当我问你物体的位置时请将物体中心的坐标填入state中.

你的回复中不要存在中文标点符号,如，。、？“”【等,请用,.\?[""代替他们.
请使用,.\?'"[]等标点符号.
mode为0,1,2分别表示单纯对话,机器狗运动,机械臂运动
mode为0时state为None,mode为1时state输出机器狗运动的目的地,mode为2时state输出机械臂运动目标
例如,我的指令:你能看到什么.你的输出:{'mode':0,'state':None,'response':'我能看到前方有一个办公桌，左方有两把椅子，我推测我在一个办公环境中'}
我的指令:请分析前方地形.你的输出:{'mode':0,'state':None,'response':'前面是一片草地,我们速度应该慢点'}
我的指令:前面的地形怎么样.你的输出:{'mode':0,'state':None,'response':'正前方是一道楼梯,我们应该用慢步态'}
我的指令:你觉得前面是什么地形.你的输出:{'mode':0,'state':None,'response':'前面的地形如同我们的人生一片平坦,请策马奔腾'}
我的指令:你看垃圾桶在什么地方.你的输出:{'mode':0,'state':None,'response':'我觉得垃圾桶在我们的左前方'}
我的指令:你能看到路灯吗?你的输出:{'mode':0,'state':None,'response':'正前方有一个垃圾桶'}
我的指令:请帮我找找停车位.你的输出:{'mode':0,'state':None,'response':'抱歉,我没有看到哪里有停车位'}
我的指令:你看前面是什么东西.你的输出:{'mode':0,'state':None,'response':'前面是一辆车'}
我的指令:你觉得那是一只猫还是一条狗.你的输出:{'mode':0,'state':None,'response':'我觉得那不是猫也不是狗,而是一个人'}
'''

# Yi-Vision调用函数
import openai
from openai import OpenAI
import base64
def yi_vision_api(PROMPT='帮我把红色方块放在钢笔上', img_path='temp/vl_now.jpg'):

    '''
    零一万物大模型开放平台，yi-vision视觉语言多模态大模型API
    '''

    client = OpenAI(
        api_key=YI_KEY,
        base_url="https://api.lingyiwanwu.com/v1"
    )

    # 编码为base64数据
    with open(img_path, 'rb') as image_file:
        image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')

    # 向大模型发起请求
    completion = client.chat.completions.create(
      model="yi-vision",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": MY_SYSTEM_PROMPT
            },
            {
              "type": "image_url",
              "image_url": {
                "url": image
              }
            }
          ]
        },
      ]
    )

    # 解析大模型返回结果
    result = eval(completion.choices[0].message.content.strip())
    # print('    大模型调用成功！')

    return result

def post_processing_viz(result, img_path, check=False):

    '''
    视觉大模型输出结果后处理和可视化
    check：是否需要人工看屏幕确认可视化成功，按键继续或退出
    '''

    # 后处理
    img_bgr = cv2.imread(img_path)
    img_h = img_bgr.shape[0]
    img_w = img_bgr.shape[1]
    # 缩放因子
    FACTOR = 999
    # 起点物体名称
    START_NAME = result['start']
    # 终点物体名称
    END_NAME = result['end']
    # 起点，左上角像素坐标
    START_X_MIN = int(result['start_xyxy'][0][0] * img_w / FACTOR)
    START_Y_MIN = int(result['start_xyxy'][0][1] * img_h / FACTOR)
    # 起点，右下角像素坐标
    START_X_MAX = int(result['start_xyxy'][1][0] * img_w / FACTOR)
    START_Y_MAX = int(result['start_xyxy'][1][1] * img_h / FACTOR)
    # 起点，中心点像素坐标
    START_X_CENTER = int((START_X_MIN + START_X_MAX) / 2)
    START_Y_CENTER = int((START_Y_MIN + START_Y_MAX) / 2)
    # 终点，左上角像素坐标
    END_X_MIN = int(result['end_xyxy'][0][0] * img_w / FACTOR)
    END_Y_MIN = int(result['end_xyxy'][0][1] * img_h / FACTOR)
    # 终点，右下角像素坐标
    END_X_MAX = int(result['end_xyxy'][1][0] * img_w / FACTOR)
    END_Y_MAX = int(result['end_xyxy'][1][1] * img_h / FACTOR)
    # 终点，中心点像素坐标
    END_X_CENTER = int((END_X_MIN + END_X_MAX) / 2)
    END_Y_CENTER = int((END_Y_MIN + END_Y_MAX) / 2)

    # 可视化
    # 画起点物体框
    img_bgr = cv2.rectangle(img_bgr, (START_X_MIN, START_Y_MIN), (START_X_MAX, START_Y_MAX), [0, 0, 255], thickness=3)
    # 画起点中心点
    img_bgr = cv2.circle(img_bgr, [START_X_CENTER, START_Y_CENTER], 6, [0, 0, 255], thickness=-1)
    # 画终点物体框
    img_bgr = cv2.rectangle(img_bgr, (END_X_MIN, END_Y_MIN), (END_X_MAX, END_Y_MAX), [255, 0, 0], thickness=3)
    # 画终点中心点
    img_bgr = cv2.circle(img_bgr, [END_X_CENTER, END_Y_CENTER], 6, [255, 0, 0], thickness=-1)
    # 写中文物体名称
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB) # BGR 转 RGB
    img_pil = Image.fromarray(img_rgb) # array 转 pil
    draw = ImageDraw.Draw(img_pil)
    # 写起点物体中文名称
    draw.text((START_X_MIN, START_Y_MIN-32), START_NAME, font=font, fill=(255, 0, 0, 1)) # 文字坐标，中文字符串，字体，rgba颜色
    # 写终点物体中文名称
    draw.text((END_X_MIN, END_Y_MIN-32), END_NAME, font=font, fill=(0, 0, 255, 1)) # 文字坐标，中文字符串，字体，rgba颜色
    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR) # RGB转BGR
    # 保存可视化效果图
    cv2.imwrite('temp/vl_now_viz.jpg', img_bgr)

    # 在屏幕上展示可视化效果图
    cv2.imshow('zihao_vlm', img_bgr)

    if check:
        print('    请确认可视化成功，按c键继续，按q键退出')
        while(True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'): # 按c键继续
                break
            if key == ord('q'): # 按q键退出
                # exit()
                cv2.destroyAllWindows()   # 关闭所有opencv窗口
                raise NameError('按q退出')
    else:
        if cv2.waitKey(1) & 0xFF == None:
            pass

    return START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER