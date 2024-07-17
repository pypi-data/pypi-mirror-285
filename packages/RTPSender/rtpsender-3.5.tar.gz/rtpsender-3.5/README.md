## usage examples
```python
from RTPSender import RTPSender

ip_address = '127.0.0.1'
port = 7777
image_file = 'frame_0.png'
audio_file = 'bgroup.wav'

rtpSender = RTPSender(ip_address, port)

rtpSender.send_video_rtp_from_file(image_file)
# 只支持采样率48000HZ，单通道 20ms
rtpSender.send_audio_rtp_from_file(audio_file)

img = cv2.imread(image_file)
rtpSender.send_video_rtp_from_img(img)

audio = AudioSegment.from_file(audio_file, format="wav")
audio_data = audio.raw_data
# 只支持采样率48000HZ，单通道 20ms
rtpSender.send_audio_rtp_from_bytes(audio_data)
```