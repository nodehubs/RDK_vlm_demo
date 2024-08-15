import sounddevice as sd
import pyaudio
 
# 打开蓝牙音频输入设备
device_info = sd.query_devices()
bluez_device = [device for device in device_info if 'BlueZ' in device['name']][0]
 
# 参数设置
fs = 44100  # 采样率
duration = 5  # 采样时间
bluez_device_id = bluez_device['id']
 
# 开始录音
print("开始录音...")
my_recording = sd.rec(int(duration * fs), samplerate=fs, device=bluez_device_id)
sd.wait()  # Wait until recording is finished
print("录音结束!")
 
# 保存音频文件
sd.play(my_recording, fs)
sd.wait()  # Wait until playback is finished
 
# 写入WAV文件
wav_file = 'blue_tooth_input.wav'
sd.write(my_recording, wav_file, fs)
 
print("录音已保存为", wav_file)