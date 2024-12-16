# 赛博汪汪队 2024-6-22
# 腿臂机器人+大模型+多模态+语音识别=具身智能体Agent

# 导入常用函数
from utils_asr import *             # 录音+语音识别
from utils_robot import *           # 发送机器狗控制指令
from utils_llm import *             # 大语言模型API
from utils_agent import *           # 智能体Agent编排
from utils_tts import *             # 语音合成模块
import lcm
from lcm_types.vlm_dog import vlm_dog
import rospy
import ros_numpy
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Int16
import sensor_msgs
import cv2
import cv_bridge
from utils_vlm import *

# play_wav('asset/welcome.wav')
lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=255")
# print('播放欢迎词')
# pump_off()
# back_zero()
# print('111111111')

depth_image = np.zeros((480,640))
color_image = np.zeros((480,640,3))
odom_r = np.zeros((3,3))
odom_l = np.zeros((3,1))

ros_time = 0

def odomhandle(msg):
    global odom_r, odom_l
    xx = msg.pose.pose.position.x
    yy = msg.pose.pose.position.y
    zz = msg.pose.pose.position.z
    wx = msg.pose.pose.orientation.x
    wy = msg.pose.pose.orientation.y
    wz = msg.pose.pose.orientation.z
    ww = msg.pose.pose.orientation.w
    odom_r[0,0] = -2 * (wy**2 + wz**2) + 1
    odom_r[0,1] = 2 * (wx*wy - ww*wz)
    odom_r[0,2] = 2 * (wx*wz + ww*wy)
    odom_r[1,0] = 2 * (wx*wy + ww*wz)
    odom_r[1,1] = -2 * (wx**2 + wz**2) + 1
    odom_r[1,2] = 2 * (wy*wz - ww*wx)
    odom_r[2,0] = 2 * (wx*wz - ww*wy)
    odom_r[2,1] = 2 * (wy*wz + ww*wx)
    odom_r[2,2] = -2 * (wx**2 + wy**2) + 1
    odom_l[0] = xx
    odom_l[1] = yy
    odom_l[2] = zz
    # global ros_time
    # ros_time = msg.header.stamp
    # print(ros_time)

def control_mode(modes):
    start_time = time.time()
    for i in range(1):
    # while(1):
        msg = vlm_dog()
        msg.mode = int(modes)
        msg.velocity_x = 0
        msg.velocity_y = 0
        msg.omega_z = 0
        lc.publish('llm2dog', msg.encode())
    if not modes:
        msg.mode = 1
        lc.publish('llm2arm', msg.encode())
    # print('222222')
    # lc.handle()
    # time.sleep(8)
    # msg.mode = 0
    # lc.publish('llm2dog', msg.encode())
    print(msg.mode)
    pass

def control_vel(velocity):
    for i in range(1):
    # while(1):
        msg = vlm_dog()
        msg.velocity_x = velocity['x']
        msg.omega_z = velocity['z']
        msg.velocity_y = 0
        msg.mode = 6
        lc.publish('llm2dog', msg.encode())
    # lc.handle()
    # print(velocity)
    pass

def control_nav(goal):
    pub = rospy.Publisher('/goal_point_llm', PointStamped, queue_size=10)
    msg = PointStamped()
    msg.header.frame_id = 'map'
    # msg.header.stamp = ros_time
    msg.point.x = goal['x']
    msg.point.y = goal['y']
    msg.point.z = 0.6
    for i in range(2):
        pub.publish(msg)
        # print('111')

def control_vlm(odoer):
    # result = yi_vision_api(odoer)
    # depth_image = cv2.imread('temp/vl_depth.png')
    result = yi_vision_api(odoer)
    if int(result['mode']):
        pos = result['state']
        if pos['x'] > 0 and pos['x'] == 0:
            color_pos = np.array([pos['x'] * 0.48, pos['y'] * 0.64])
            # print(color_pos)
            world_pos = c2d_trans(depth_image[:,:], color_pos)
            world_pos[world_pos==0] = 0.05
            if not ((world_pos) < 5).any() and not ((world_pos > -1)).any():
                world_pos[:] = 0
                print(world_pos)
                world_pos = odom_r @ world_pos + odom_l
                control_nav({'x':0.0,'y':0.0})
            else:
                print(world_pos)
                world_pos = odom_r @ world_pos + odom_l
                control_nav({'x':world_pos[0],'y':world_pos[1]})
            # pub = rospy.Publisher('/way_point', PointStamped, queue_size=10)
            # msg = PointStamped()
            # msg.header.frame_id = 'map'
            # msg.header.stamp = ros_time
            # msg.point.x = world_pos[0]
            # msg.point.y = world_pos[1]
            # msg.point.z = 0.6
            # for i in range(2):
                # print('publish waypoint ok!!!')
                # pub.publish(msg)
            '''
            if world_pos[2] < 0.5 and world_pos[2] > 0.2:
                if np.sqrt(world_pos[0]**2 + world_pos[1]**2) > 0.65:
                    world_pos[0] = 0.3
                    world_pos[1] = world_pos[1] / (world_pos[0]+0.1) * 0.3
                    world_pos[2] = 0
                    msg = vlm_dog()
                    msg.velocity_x = world_pos[0]
                    msg.velocity_y = world_pos[1]
                    msg.omega_z = world_pos[2]
                    msg.mode = 6
                    lc.publish('llm2dog', msg.encode())
                else:
                    msg = vlm_dog()
                    msg.velocity_x = world_pos[0] + 0.22
                    msg.velocity_y = world_pos[1]
                    msg.omega_z = world_pos[2] - 0.1
                    msg.mode = 4
                    lc.publish('llm2arm', msg.encode())
            '''
    tts(result['response'])
    play_wav('temp/tts.wav')
    print(result)
    pass

def control_arm(order):
    msg = vlm_dog()
    msg.velocity_x = 0
    msg.velocity_y = 0
    msg.omega_z = 0
    msg.mode = int(order['state'])
    lc.publish('llm2arm', msg.encode())

def imghandle(msg):
    bridge = cv_bridge.CvBridge()
    cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    global color_image
    color_image = cv_image
    cv2.imwrite('temp/vl_now.jpg', cv_image)

def depthhandle(msg):
    global depth_image
    depth_img = ros_numpy.numpify(msg)
    depth_image = depth_img
    cv2.imwrite('temp/vl_depth.png', depth_image)

def ipstatuhandle(msg):
    print('\n\n\n\nhave receive ip status!!!')
    # print(msg)
    if int(msg.data)==1:
        print('\n\n\n\narm will move!!!')
        msg = vlm_dog()
        # msg.velocity_x = world_pos[0] + 0.22
        # msg.velocity_y = world_pos[1]
        # msg.omega_z = world_pos[2] - 0.1
        msg.mode = 4
        lc.publish('llm2arm', msg.encode())

def agent_play():
    '''
    主函数，语音控制机械臂智能体编排动作
    '''
    # 归零
    # back_zero()

    # print('测试摄像头')
    # check_camera()

    node_name = "goal_publisher"
    rospy.init_node(node_name, anonymous=False)
    rospy.Subscriber('/camera/color/image_raw', sensor_msgs.msg.Image, imghandle)
    rospy.Subscriber('/camera/aligned_depth_to_color/image_raw', sensor_msgs.msg.Image, depthhandle)
    rospy.Subscriber('/ip_planner_status', Int16, ipstatuhandle)
    rospy.Subscriber('/Odometry', Odometry, odomhandle)

    while(1):
        while(1):
            my_record_auto()
            order = speech_recognition()
            if '小狗' in order or '汪汪' in order:
                break
            if '旺旺' in order:
                break
        play_wav('asset/response.wav')
        # time.sleep(1)
        my_record_auto()
        order = speech_recognition()
        # 输入指令
        # 先回到原点，再把LED灯改为墨绿色，然后把绿色方块放在篮球上
        # start_record_ok = input('是否开启录音，输入数字录音指定时长，按k打字输入，按c图像输入\n')
        '''
        start_record_ok = input('步进调试，输入数字开始录音,输入c识别图像\n')
        if str.isnumeric(start_record_ok):
            DURATION = int(start_record_ok)
            record(DURATION=DURATION)   # 录音
            order = speech_recognition() # 语音识别
        elif start_record_ok == 'k':
            order = input('请输入指令')
        elif start_record_ok == 'c':
            order = input('请输入图像+指令')  # '先归零，再摇头，然后把绿色方块放在篮球上'
        else:
            print('无指令，退出')
            # exit()
            raise NameError('无指令，退出')
        '''
        start_record_ok = 1
        # 智能体Agent编排动作
        if start_record_ok == 'c': control_vlm(order)
        else:
            agent_plan_output = eval(agent_plan(order))
            # agent_plan_output = agent_plan(order)
            # print(agent_plan_output)

            # print('智能体编排动作如下\n', agent_plan_output)
            # plan_ok = input('是否继续？按c继续，按q退出')
            plan_ok = 'c'
            if plan_ok == 'c':
                mode = agent_plan_output['mode']
                state = agent_plan_output['state']
                response = agent_plan_output['response'] # 获取机器人想对我说的话
                # print(len(response))
                print('开始语音合成')
                tts(response)                     # 语音合成，导出wav音频文件
                # play_wav('temp/tts.wav')          # 播放语音合成音频文件
                # vision_ok = input('是否描述画面')
                # if not int(vision_ok):
                # play_wav('temp/tts.wav')
                # if int(vision_ok):
                    # print(vision_ok)
                if mode == 1:
                    play_wav('temp/tts.wav')          # 播放语音合成音频文件
                    control_mode(state)
                    print(agent_plan_output)
                elif mode == 2:
                    play_wav('temp/tts.wav')          # 播放语音合成音频文件
                    control_vel(state)
                    print(agent_plan_output)
                elif mode == 3:
                    play_wav('temp/tts.wav')          # 播放语音合成音频文件
                    control_nav(state)
                    print(agent_plan_output)
                elif mode == 4:
                    play_wav('temp/tts.wav')
                    control_vlm(order)
                elif mode == 5:
                    play_wav('temp/tts.wav')
                    control_arm(agent_plan_output)
                else:
                    play_wav("temp/tts.wav")
                # else:
                    # control_vlm(order)
                    # play_wav('temp/tts.wav')          # 播放语音合成音频文件
                    # msg = example_t()
                    # msg.mode = mode
                    # msg.state = state
                    # msg.response = response
                    # lc.publish("EXAMPLE", msg.encode())
                    # lc.handle()
                # for each in agent_plan_output['function']: # 运行智能体规划编排的每个函数
                    # print('开始执行动作', each)
                    # eval(each)
            elif plan_ok =='q':
                exit()
                raise NameError('按q退出')

# agent_play()
if __name__ == '__main__':
    agent_play()

