import alsaaudio
import wave
import time
import numpy as np

# 参数设置
CHUNK = 1024
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
CHANNELS = 1
RATE = 16000
THRESHOLD = 0.1  # 阈值，根据实际情况调整
SILENCE_LIMIT = 2  # 静默限制时间，单位秒

# 打开音频输入流
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device='plughw:Device,0')
# inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device='sysdefault:CARD=Device')
# inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device='usbstream:Device')
inp.setchannels(CHANNELS)
inp.setrate(RATE)
inp.setformat(FORMAT)
inp.setperiodsize(CHUNK)

print("* recording")
iii = 0

frames = []
silent_frames = 0  # 静默帧数计数器

start_time = time.time()

while True:
    iii += 1
    # 读取数据
    l, data = inp.read()
    if l:
        # print(l)
        # 将数据转换为numpy数组
        audio_data = np.frombuffer(data, dtype=np.int16) / 32768
        # print(np.min(audio_data),np.max(audio_data))
        if np.isnan(audio_data).any():
            print('error datas have nan!!!!')
        
        # 计算能量
        rms = np.sqrt(np.mean(np.square(audio_data)))
        # print(rms.dtype,np.max(np.square(audio_data)),np.min(np.square(audio_data)))
        if rms > THRESHOLD:
            silent_frames = 0
            frames.append(data)
        else:
            # print(rms)
            # print('silent frame!!!!')
            silent_frames += 1
            frames.append(data)
        
        # 如果连续静默超过设定的时间，停止录音
        if silent_frames > int(SILENCE_LIMIT * RATE / CHUNK):
            break

print("* done recording",time.time()-start_time)

# 停止音频流
inp.close()

# 将录音保存为WAV文件
WAVE_OUTPUT_FILENAME = "output.wav"
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(2)  # 16-bit PCM
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print("Recording saved as:", WAVE_OUTPUT_FILENAME)
