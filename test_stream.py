from pytube import YouTube
import subprocess
import tempfile
import time
import os

RTMP_TARGET = "rtmp://localhost:1935/live/test"

def video_info(url: str):
    video = YouTube(url)
    return {
        "audio_url": video.streams.filter(only_audio=True).first().url + "&from_cache=True",
        "title": video.title,
        "author": video.author,
        "thumb_url": video.thumbnail_url
    }

def live_stream_audio(audio_url: str, streaming_url: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        m3u8_file = os.path.join(temp_dir, "output.m3u8")
        cmd = f"""ffmpeg -i "{audio_url}" -c:v copy -ac 2 -y -f segment -segment_time 2 -segment_list "{m3u8_file}" -segment_format mpegts '{os.path.join(temp_dir, "output%03d.ts")}'"""
        subprocess.Popen(cmd, shell=True)
        while not os.path.exists(m3u8_file):
            print('Waiting for:', m3u8_file , '...')
            time.sleep(1)
        cmd = f"""ffmpeg -i "{m3u8_file}" -c:v libx264 -c:a aac -f flv - | ffmpeg -re -i - -c:v copy -c:a copy -ac 2 -preset veryfast -b:v 3500k -maxrate 3500k -bufsize 7000k -f flv -flvflags no_duration_filesize {streaming_url}"""
        process = subprocess.Popen(cmd,shell=True)
        process.wait()

if __name__ == "__main__":
    # Long time audio
    # url = "https://www.youtube.com/watch?v=qfFmZa9jgoY"
    # url = "https://www.youtube.com/watch?v=NJuSStkIZBg"
    # url = "https://www.youtube.com/watch?v=y2ECgOhoDGs"
    # Short time audio
    urls = [
        "https://www.youtube.com/watch?v=nTPL3N5QCh4&list=RDMM&start_radio=1&rv=Z_3BzA5ZSLY",
        "https://www.youtube.com/watch?v=iLl-wxYC64A&list=RDMM&index=2",
        "https://www.youtube.com/watch?v=gbmLFbrv1js",
        "https://www.youtube.com/watch?v=5iqdEb74SK4&list=RDiviT0HIOm1M&index=2",
        "https://www.youtube.com/watch?v=-NxIQYQsaXc&list=RDiviT0HIOm1M&index=8",
        'https://www.youtube.com/watch?v=FDyz-4zHNh4&list=RDFDyz-4zHNh4&start_radio=1',
        "https://www.youtube.com/watch?v=dE9B-oMNNAs",
    ]
    for url in urls:
        info = video_info(url)
        live_stream_audio(info["audio_url"],RTMP_TARGET)