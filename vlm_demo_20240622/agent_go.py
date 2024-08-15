# 赛博汪汪队
# 腿臂机器人+大模型+多模态+语音识别=具身智能体Agent

# 导入常用函数
from utils_asr import *             # 录音+语音识别
from utils_llm import *             # 大语言模型API
from utils_agent import *           # 智能体Agent编排
from utils_tts import *             # 语音合成模块

# print('播放欢迎词')
# pump_off()
# back_zero()
play_wav('asset/welcome.wav')


def agent_play():
    '''
    主函数，语音控制机械臂智能体编排动作
    '''
    # 归零
    # back_zero()

    # print('测试摄像头')
    # check_camera()

    # 输入指令
    # 先回到原点，再把LED灯改为墨绿色，然后把绿色方块放在篮球上
    start_record_ok = input('是否开启录音，输入数字录音指定时长，按k打字输入，按c输入默认指令\n')
    if str.isnumeric(start_record_ok):
        DURATION = int(start_record_ok)
        record(DURATION=DURATION)   # 录音
        order = speech_recognition() # 语音识别
    elif start_record_ok == 'k':
        order = input('请输入指令')
    elif start_record_ok == 'c':
        order = '先归零，再摇头，然后把绿色方块放在篮球上'
    else:
        print('无指令，退出')
        # exit()
        raise NameError('无指令，退出')

    # 智能体Agent编排动作
    agent_plan_output = eval(agent_plan(order))

    print('智能体编排动作如下\n', agent_plan_output)
    # plan_ok = input('是否继续？按c继续，按q退出')
    plan_ok = 'c'
    if plan_ok == 'c':
        response = agent_plan_output['response'] # 获取机器人想对我说的话
        print('开始语音合成')
        tts(response)                     # 语音合成，导出wav音频文件
        play_wav('temp/tts.wav')          # 播放语音合成音频文件
        for each in agent_plan_output['function']: # 运行智能体规划编排的每个函数
            print('开始执行动作', each)
            eval(each)
    elif plan_ok =='q':
        # exit()
        raise NameError('按q退出')

# agent_play()
if __name__ == '__main__':
    agent_play()

