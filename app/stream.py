import subprocess
import requests
import tempfile
import time
import os

from app.exceptions import YoutubeAudioExpired

class Stream:
    def process_cmd(self, cmd: str, debug: bool):
        """處理 Command 指令"""
        return subprocess.Popen(cmd, stdout=subprocess.PIPE if not debug else None, stderr=subprocess.PIPE if not debug else None,shell=True)

    def download_image(self, temp_dir, url):
        """下載圖片到 temp 資料夾中"""
        # 使用 tempfile 模組創建臨時目錄
        try:
            # 發送 GET 請求以下載圖片
            response = requests.get(url)
            if response.status_code == 200:
                # 從 URL 中提取文件名
                filename = os.path.basename(url)
                # 構建臨時文件的完整路徑
                temp_image_path = os.path.join(temp_dir, filename)
                # 寫入圖片內容到臨時文件
                with open(temp_image_path, 'wb') as file:
                    file.write(response.content)
                return temp_image_path
            else:
                print('無法下載圖片，狀態碼:', response.status_code)
        except Exception as e:
            print('下載圖片時出現錯誤:', str(e))
        return None
    
    def waiting_for_file_ready(self, m3u8_file: str, timeout: int) -> None:
        """等待 m3u8 檔案開始寫入"""
        end_time = time.time() + timeout
        while not os.path.exists(m3u8_file) and time.time() < end_time:
            # print('Waiting for:', m3u8_file , '...')
            time.sleep(0.1)
        if not os.path.exists(m3u8_file):
            raise YoutubeAudioExpired()

    def download_audio(self, temp_dir: str, audio_url: str, debug: bool) -> str:
        """
        下載音訊，並且轉換成 m3u8 格式
        """
        m3u8_file = os.path.join(temp_dir, "output.m3u8")
        cmd = f"""ffmpeg -i "{audio_url}" -c:v copy -ac 2 -y -f segment -segment_time 2 -segment_list "{m3u8_file}" -segment_format mpegts '{os.path.join(temp_dir, "output%03d.ts")}'"""
        self.process_cmd(cmd,debug)
        return m3u8_file

    def live_stream_audio(self, audio_url: str, streaming_url: str,debug: bool):
        """推送緩存好的音訊檔案到 rtmp 伺服器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = self.download_audio(temp_dir,audio_url,debug)
            self.waiting_for_file_ready(m3u8_file,2)
            cmd = f"""ffmpeg -i "{m3u8_file}" -c:v libx264 -c:a aac -f flv - | ffmpeg -re -i - -c:v copy -c:a copy -ac 2 -preset veryfast -b:v 3500k -maxrate 3500k -bufsize 7000k -f flv -flvflags no_duration_filesize {streaming_url}"""
            process = self.process_cmd(cmd, debug)
            process.wait()
    
    def live_stream_audio_with_image(self, image_url: str, audio_url: str, streaming_url: str, debug: bool):
        """推送合成照片過後的影片檔到 rtmp 伺服器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = self.download_audio(temp_dir,audio_url,debug)
            self.waiting_for_file_ready(m3u8_file,2)
            temp_image = self.download_image(temp_dir, image_url)
            temp_image = temp_image if temp_image != None else "image.jpeg"
            cmd = f"""ffmpeg -loop 1 -i "{temp_image}" -i "{m3u8_file}" -tune stillimage -pix_fmt yuv420p -c:v libx264 -c:a aac -strict experimental -b:a 192k -vf "scale=1920:1080" -shortest -f flv - | ffmpeg -re -i - -c:v copy -c:a copy -ac 2 -preset veryfast -b:v 3500k -maxrate 3500k -bufsize 7000k -f flv -flvflags no_duration_filesize {streaming_url}"""
            process = self.process_cmd(cmd, debug) 
            process.wait()
