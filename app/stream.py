import subprocess
import requests
import tempfile
import time
import signal
import os


class Stream:
    def __init__(self):
        self.subprocesses = []

    def process_cmd(self, cmd: str, debug: bool):
        """處理 Command 指令"""
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if not debug else None,
            stderr=subprocess.PIPE if not debug else None,
            shell=True,
            preexec_fn=os.setpgrp
        )
        self.subprocesses.append(process)
        return process

    def live_stream_audio(self, audio_url: str, streaming_url: str, debug: bool):
        """推送緩存好的音訊檔案到 rtmp 伺服器"""
        """ feature 從中斷開始
        --download-sections "*60-120" https://www.reddit.com/r/youtubedl/wiki/howdoidownloadpartsofavideo/
        """
        cmd = f"""
        yt-dlp -f bestaudio -x --retries infinite "{audio_url}" -o - | ffmpeg -re -i - -c:v copy -c:a aac -ac 2 -strict experimental -f flv "{streaming_url}" 
        """
        process = self.process_cmd(cmd, debug)
        return process
