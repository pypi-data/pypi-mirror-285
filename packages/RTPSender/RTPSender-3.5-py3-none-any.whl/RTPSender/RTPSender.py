from scapy.all import IP, UDP, Raw, send
import cv2
import av
from pydub import AudioSegment
import queue
import threading
import ctypes
import copy
import numpy as np
from numba import njit
import socket
from time import sleep, time

class RTPSender:
    def __init__(self, ip_address, port, open_log=False):
        self.image_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.image_queue2 = queue.Queue()
        self.audio_queue2 = queue.Queue()
        self.image_file = ""
        self.audio_file = ""
        self.ip_address = ip_address
        self.port = port
        self.output_path = 'output.mp4'
        self.open_log = open_log

        self.RTP_VERSION = 2
        self.RTP_SSRC = 12345

        # 默认video file RTP header参数
        self.RTP_VIDEO_PAYLOAD_TYPE = 96
        self.RTP_VIDEO_FILE_SEQUENCE_NUMBER = 0
        self.RTP_VIDEO_FILE_TIMESTAMP = 0

        # 默认video img RTP header参数
        self.RTP_VIDEO_IMG_SEQUENCE_NUMBER = 0
        self.RTP_VIDEO_IMG_TIMESTAMP = 0

        # 默认音频file RTP header 参数
        self.RTP_AUDIO_PAYLOAD_TYPE = 97
        self.RTP_AUDIO_FILE_SEQUENCE_NUMBER = 0
        self.RTP_AUDIO_FILE_TIMESTAMP = 0

        # 默认音频bytes RTP header 参数
        self.RTP_AUDIO_BYTES_SEQUENCE_NUMBER = 0
        self.RTP_AUDIO_BYTES_TIMESTAMP = 0

        self.max_payload_size = 1400

        # 初始化输出容器
        self.output_container = av.open(self.output_path, mode='w')

        # 创建视频流
        self.video_stream = self.output_container.add_stream('libx264', rate=25)

        self.video_stream.options = {'g': str(25), 'tune': 'zerolatency'}  # 设置GOP大小为25帧，实现低延迟
        self.video_stream.bit_rate = 1000000
        # self.video_stream.width = frame_size[0]
        # self.video_stream.height = frame_size[1]

        self.video_stream.width = 1080
        self.video_stream.height = 1920

        self.video_frame_cnt = 0
        self.audio_frame_cnt = 0


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 655360)  # 设置为64KB


        self.video_thread = threading.Thread(target=self.process_video_queue)
        self.video_thread2 = threading.Thread(target=self.process_video_queue2)
        self.audio_thread = threading.Thread(target=self.process_audio_queue)
        self.audio_thread2 = threading.Thread(target=self.process_audio_queue2)

        self.video_thread.start()
        self.video_thread2.start()
        self.audio_thread.start()
        self.audio_thread2.start()

    def create_video_file_rtp_packet(self, payload, marker=0):
        rtp_header = bytearray(12)

        # 设置 RTP Header
        rtp_header[0] = (self.RTP_VERSION << 6)
        rtp_header[1] = (marker << 7) | self.RTP_VIDEO_PAYLOAD_TYPE
        rtp_header[2] = (self.RTP_VIDEO_FILE_SEQUENCE_NUMBER >> 8) & 0xFF
        rtp_header[3] = self.RTP_VIDEO_FILE_SEQUENCE_NUMBER & 0xFF
        rtp_header[4] = (self.RTP_VIDEO_FILE_TIMESTAMP >> 24) & 0xFF
        rtp_header[5] = (self.RTP_VIDEO_FILE_TIMESTAMP >> 16) & 0xFF
        rtp_header[6] = (self.RTP_VIDEO_FILE_TIMESTAMP >> 8) & 0xFF
        rtp_header[7] = self.RTP_VIDEO_FILE_TIMESTAMP & 0xFF
        rtp_header[8] = (self.RTP_SSRC >> 24) & 0xFF
        rtp_header[9] = (self.RTP_SSRC >> 16) & 0xFF
        rtp_header[10] = (self.RTP_SSRC >> 8) & 0xFF
        rtp_header[11] = self.RTP_SSRC & 0xFF

        
        return rtp_header + payload
    
    def create_video_img_rtp_packet(self, payload, marker=0):
        rtp_header = bytearray(12)

        # 设置 RTP Header
        rtp_header[0] = (self.RTP_VERSION << 6)
        rtp_header[1] = (marker << 7) | self.RTP_VIDEO_PAYLOAD_TYPE
        rtp_header[2] = (self.RTP_VIDEO_IMG_SEQUENCE_NUMBER >> 8) & 0xFF
        rtp_header[3] = self.RTP_VIDEO_IMG_SEQUENCE_NUMBER & 0xFF
        rtp_header[4] = (self.RTP_VIDEO_IMG_TIMESTAMP >> 24) & 0xFF
        rtp_header[5] = (self.RTP_VIDEO_IMG_TIMESTAMP >> 16) & 0xFF
        rtp_header[6] = (self.RTP_VIDEO_IMG_TIMESTAMP >> 8) & 0xFF
        rtp_header[7] = self.RTP_VIDEO_IMG_TIMESTAMP & 0xFF
        rtp_header[8] = (self.RTP_SSRC >> 24) & 0xFF
        rtp_header[9] = (self.RTP_SSRC >> 16) & 0xFF
        rtp_header[10] = (self.RTP_SSRC >> 8) & 0xFF
        rtp_header[11] = self.RTP_SSRC & 0xFF
        
        return rtp_header + payload
    
    def create_audio_file_rtp_packet(self, payload, marker=0):
        rtp_header = bytearray(12)

        # 设置 RTP Header
        rtp_header[0] = (self.RTP_VERSION << 6)
        rtp_header[1] = (marker << 7) | self.RTP_AUDIO_PAYLOAD_TYPE
        rtp_header[2] = (self.RTP_AUDIO_FILE_SEQUENCE_NUMBER >> 8) & 0xFF
        rtp_header[3] = self.RTP_AUDIO_FILE_SEQUENCE_NUMBER & 0xFF
        rtp_header[4] = (self.RTP_AUDIO_FILE_TIMESTAMP >> 24) & 0xFF
        rtp_header[5] = (self.RTP_AUDIO_FILE_TIMESTAMP >> 16) & 0xFF
        rtp_header[6] = (self.RTP_AUDIO_FILE_TIMESTAMP >> 8) & 0xFF
        rtp_header[7] = self.RTP_AUDIO_FILE_TIMESTAMP & 0xFF
        rtp_header[8] = (self.RTP_SSRC >> 24) & 0xFF
        rtp_header[9] = (self.RTP_SSRC >> 16) & 0xFF
        rtp_header[10] = (self.RTP_SSRC >> 8) & 0xFF
        rtp_header[11] = self.RTP_SSRC & 0xFF
        
        return rtp_header + payload
    
    def create_audio_bytes_rtp_packet(self, payload, marker=0):
        rtp_header = bytearray(12)

        # 设置 RTP Header
        rtp_header[0] = (self.RTP_VERSION << 6)
        rtp_header[1] = (marker << 7) | self.RTP_AUDIO_PAYLOAD_TYPE
        rtp_header[2] = (self.RTP_AUDIO_BYTES_SEQUENCE_NUMBER >> 8) & 0xFF
        rtp_header[3] = self.RTP_AUDIO_BYTES_SEQUENCE_NUMBER & 0xFF
        rtp_header[4] = (self.RTP_AUDIO_BYTES_TIMESTAMP >> 24) & 0xFF
        rtp_header[5] = (self.RTP_AUDIO_BYTES_TIMESTAMP >> 16) & 0xFF
        rtp_header[6] = (self.RTP_AUDIO_BYTES_TIMESTAMP >> 8) & 0xFF
        rtp_header[7] = self.RTP_AUDIO_BYTES_TIMESTAMP & 0xFF
        rtp_header[8] = (self.RTP_SSRC >> 24) & 0xFF
        rtp_header[9] = (self.RTP_SSRC >> 16) & 0xFF
        rtp_header[10] = (self.RTP_SSRC >> 8) & 0xFF
        rtp_header[11] = self.RTP_SSRC & 0xFF
        
        return rtp_header + payload
    
    def send_video_rtp_from_file(self, image_file, frame_size=(1080, 1920)):

        self.video_stream.width = frame_size[0]
        self.video_stream.height = frame_size[1]

        img = cv2.imread(image_file)
        img_frame = av.VideoFrame.from_ndarray(img, format='rgb24')
        packets = self.video_stream.encode(img_frame)

        # packets = self.video_stream.encode(None)
        for packet in packets:
            buffer_ptr = packet.buffer_ptr
            buffer_size = packet.buffer_size
            buffer = (ctypes.c_char * buffer_size).from_address(buffer_ptr)

            data = self.video_stream.codec_context.extradata
            buffer_copy = copy.deepcopy(buffer)
            self.image_queue.put((buffer_copy, data))


    def process_video_queue(self):
        print("Processing video queue from file")
        while True:
            buffer, data = self.image_queue.get()

            # 初始化输出容器
            # output_container = av.open(self.output_path, mode='w')

            buffer_bytes = bytes(buffer)

            # 要检查的前缀
            begin = b'\x00\x00\x01\x06'
            end = b'\x00\x00\x00\x01\x65'

            # 判断缓冲区是否以指定前缀开头
            if buffer_bytes.startswith(begin):
                pos = buffer_bytes.find(end)
                if pos != -1:
                    buffer = data + buffer[pos:]
            elif buffer_bytes.startswith(end):
                buffer = data + buffer

            # print("buffer: ", buffer[:5])

            j = 0
            while j < len(buffer):
                payload = buffer[j:j + self.max_payload_size]
                
                # 创建 RTP 包
                marker = 1 if len(payload) < self.max_payload_size else 0
                rtp_packet = self.create_video_file_rtp_packet(payload, marker)
                
                # ip = IP(dst=self.ip_address)
                # udp = UDP(dport=self.port)
                # raw = Raw(load=rtp_packet)

                # packet = ip / udp / raw
                # send(packet, verbose=False)
                self.sock.sendto(bytes(rtp_packet), (self.ip_address, self.port))
                
                self.RTP_VIDEO_FILE_SEQUENCE_NUMBER += 1
                j += self.max_payload_size
                
                # 如果当前负载不足1400字节，说明当前帧处理完了，增加时间戳准备发送下一帧
                if len(payload) < self.max_payload_size:
                    self.RTP_VIDEO_FILE_TIMESTAMP += 3000

            # 关闭容器
            # output_container.close()

    def send_audio_rtp_from_file(self, audio_file, is_16k=False):
        # print("Received audio file, and put it into queue")
        audio = AudioSegment.from_file(audio_file, format="wav")
        audio_data = audio.raw_data
        # 将音频数据放入队列，等待另一个线程处理
        self.audio_queue.put((audio_data, is_16k))


    def process_audio_queue(self):
        print("Processing audio queue from file")
        while True:
            audio_data, is_16k = self.audio_queue.get()

            frame_size = 640 if is_16k else 1920

            # 将音频数据分割为frame_size字节的帧
            i = 0
            while i < len(audio_data):
                frame_data = audio_data[i:i + frame_size]
                i += frame_size

                j = 0
                while j < len(frame_data):
                    payload = frame_data[j:j + self.max_payload_size]

                    marker = 1 if len(payload) < self.max_payload_size else 0

                    # print(f"Sending audio frame {j} to {j + self.max_payload_size} bytes")

                    # 创建 RTP 包
                    rtp_packet = self.create_audio_file_rtp_packet(payload, marker)
                    
                    # ip = IP(dst=self.ip_address)
                    # udp = UDP(dport=self.port)
                    # raw = Raw(load=rtp_packet)

                    # packet = ip / udp / raw
                    # send(packet, verbose=False)
                    self.sock.sendto(bytes(rtp_packet), (self.ip_address, self.port))
                    
                    self.RTP_AUDIO_FILE_SEQUENCE_NUMBER += 1
                    j += self.max_payload_size

                    # 如果当前负载不足1400字节，说明音频流帧处理完了
                    if len(payload) < self.max_payload_size:
                        self.RTP_AUDIO_FILE_TIMESTAMP += 3000

            # sleep(0.018)
    
    def send_video_rtp_from_img(self, img, frame_size=(1080, 1920)):

        self.video_stream.width = frame_size[0]
        self.video_stream.height = frame_size[1]

        img_frame = av.VideoFrame.from_ndarray(img, format='rgb24')

        packets = self.video_stream.encode(img_frame)

        # print("len(packets): ", len(packets))

        data = self.video_stream.codec_context.extradata

        # packets = self.video_stream.encode(None)

        # print("len(packets): ", len(packets))

        for packet in packets:
            buffer_ptr = packet.buffer_ptr
            buffer_size = packet.buffer_size
            # print("buffer_size: ", buffer_size)
            buffer = (ctypes.c_char * buffer_size).from_address(buffer_ptr)

            buffer_copy = copy.deepcopy(buffer)

            self.image_queue2.put((buffer_copy, data))

        return len(packets)


    def process_video_queue2(self):
        print("Processing video queue from img")

        while True:
            buffer, data = self.image_queue2.get()
            if self.open_log:
                print("len(image_queue2)", self.image_queue2.qsize())
            buffer_bytes = bytes(buffer)

            # 要检查的前缀
            begin = b'\x00\x00\x01\x06'
            end = b'\x00\x00\x00\x01\x65'
            
            # 判断关键帧
            if buffer_bytes.startswith(begin):
                pos = buffer_bytes.find(end)
                if pos != -1:
                    buffer = data + buffer[pos:]
            elif buffer_bytes.startswith(end):
                buffer = data + buffer

            # print("buffer: ", buffer[:5])

            j = 0
            while j < len(buffer):
                payload = buffer[j:j + self.max_payload_size]
                marker = 1 if len(payload) < self.max_payload_size else 0
                
                # 创建 RTP 包
                rtp_packet = self.create_video_img_rtp_packet(payload, marker)

                # print("rtp_packet: ", rtp_packet[:5])
                
                # ip = IP(dst=self.ip_address)
                # udp = UDP(dport=self.port)
                # raw = Raw(load=rtp_packet)

                # packet = ip / udp / raw
                t1 = time()
                # send(packet, verbose=False, socket=self.sock)
                # self.sock.sendto(bytes(packet), ip.dst, udp.dport)
                self.sock.sendto(bytes(rtp_packet), (self.ip_address, self.port))
                t2 = time()
                if self.open_log:
                    print("send time: ", t2 - t1)

                # if j == 0:
                #     print("first packet sent time: ", time())
                
                self.RTP_VIDEO_IMG_SEQUENCE_NUMBER += 1
                j += self.max_payload_size
                
                # 如果当前负载不足1400字节，说明当前帧处理完了，增加时间戳准备发送下一帧
                if len(payload) < self.max_payload_size:
                    self.RTP_VIDEO_IMG_TIMESTAMP += 3000
            
            self.video_frame_cnt += 1
            if self.open_log:
                print("video_frame_cnt: ", self.video_frame_cnt)

        # 关闭容器
        # output_container.close()

    def send_audio_rtp_from_bytes(self, audio_bytes, is_16k=False):
        # 将音频数据放入队列，等待另一个线程处理
        self.audio_queue2.put((audio_bytes, is_16k))


    def process_audio_queue2(self):
        print("Processing audio queue from bytes")

        while True:
            audio_data, is_16k = self.audio_queue2.get()

            if self.open_log:
                print("len(audio_queue2)", self.audio_queue2.qsize())

            frame_size = 640 if is_16k else 1920

            # 将音频数据分割为frame_size字节的帧
            i = 0
            while i < len(audio_data):
                frame_data = audio_data[i:i + frame_size]
                i += frame_size

                j = 0
                while j < len(frame_data):
                    payload = frame_data[j:j + self.max_payload_size]

                    marker = 1 if len(payload) < self.max_payload_size else 0

                    # print(f"Sending audio frame {j} to {j + self.max_payload_size} bytes")

                    # 创建 RTP 包
                    rtp_packet = self.create_audio_bytes_rtp_packet(payload, marker)
                    
                    # ip = IP(dst=self.ip_address)
                    # udp = UDP(dport=self.port)
                    # raw = Raw(load=rtp_packet)

                    # packet = ip / udp / raw
                    # send(packet, verbose=False)
                    self.sock.sendto(bytes(rtp_packet), (self.ip_address, self.port))
                    
                    self.RTP_AUDIO_BYTES_SEQUENCE_NUMBER += 1
                    j += self.max_payload_size

                    # 如果当前负载不足1400字节，说明音频流处理完了
                    if len(payload) < self.max_payload_size:
                        self.RTP_AUDIO_BYTES_TIMESTAMP += 3000
            self.audio_frame_cnt += 1
            if self.open_log:
                print("audio_frame_cnt: ", self.audio_frame_cnt)

from pydub import AudioSegment
import cv2
from time import sleep, time

if __name__ == '__main__':
    ip_address = "10.253.101.36"
    # ip_address = "127.0.0.1"
    port = 7777
    image_file = "/Users/a58/Code/python/rtp/images/frame_0.png"
    image_files = ["/Users/a58/Code/python/rtp/images/frame_%d.png" % i for i in range(5)]
    audio_file = "/Users/a58/Code/python/rtp/audios/bgroup.wav"
    audio_16k_file = "/Users/a58/Code/python/rtp/audios/bgroup16k.wav"

    rtpSender = RTPSender(ip_address, port)

    audio = AudioSegment.from_file(audio_16k_file, format="wav")
    audio_data = audio.raw_data
    i = 0
    cnt = 0
    t1 = time()

    imgs = [cv2.imread(image_file) for image_file in image_files]

    frame_cnt = 0

    while True:
        for img in imgs:
            if i >= len(audio_data) - 640:
                i = 0
            for j in range(25):
                print("time: ", time())
                packets_len = rtpSender.send_video_rtp_from_img(img)
                # rtpSender.send_video_rtp_from_img(img)
                if packets_len > 0:
                    print("packets_len: ", packets_len, ", frame_cnt: ", frame_cnt)
                frame_cnt += 1
                rtpSender.send_audio_rtp_from_bytes(audio_data[i:i+640], True)
                i += 640
                rtpSender.send_audio_rtp_from_bytes(audio_data[i:i+640], True)
                cnt += 1
                i += 640
                t2 = time()
                t = t1 + cnt*0.03 - t2
                # print("t: ", t)
                if t > 0:
                    # print("sleep: ", t)
                    sleep(t)
            # img = cv2.imread(image_file)
            # rtpSender.send_audio_rtp_from_file(audio_file)
            # t1 = time()
            

    # 只支持采样率48000HZ，单通道 20ms
    # rtpSender.send_audio_rtp_from_file(audio_file)
    # img = cv2.imread(image_file)
    # rtpSender.send_video_rtp_from_img(img)

    # audio = AudioSegment.from_file(audio_file, format="wav")
    # audio_data = audio.raw_data
    # # 只支持采样率48000HZ，单通道 20ms
    # rtpSender.send_audio_rtp_from_bytes(audio_data)