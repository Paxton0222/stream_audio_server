from pytube import YouTube
import requests
import subprocess
import tempfile
import time
import os

RTMP_TARGET = "rtmp://localhost:1935/live/test"
YT_RTMP_TARGET = "rtmp://a.rtmp.youtube.com/live2/0h8b-0ubr-z852-wjm6-96x7"

def video_info(url: str):
    video = YouTube(url,use_oauth=True, allow_oauth_cache=True)
    try:
        audio = video.streams.filter(only_audio=True).first().url + "&from_cache=True"
        return {
            "audio_url": audio,
            "title": video.title,
            "author": video.author,
            "thumb_url": video.thumbnail_url
        }
    except Exception as e:
        print(e)
    return None

def process_cmd(cmd: str, debug: bool):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE if not debug else None, stderr=subprocess.PIPE if not debug else None,shell=True)

def download_image(temp_dir, url):
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

def download_audio(temp_dir: str, audio_url: str, debug: bool) -> str:
    m3u8_file = os.path.join(temp_dir, "output.m3u8")
    cmd = f"""ffmpeg -i "{audio_url}" -c:v copy -ac 2 -y -f segment -segment_time 2 -segment_list "{m3u8_file}" -segment_format mpegts '{os.path.join(temp_dir, "output%03d.ts")}'"""
    process_cmd(cmd,debug)
    return m3u8_file

def waiting_for_file_ready(m3u8_file: str) -> None:
    while not os.path.exists(m3u8_file):
        # print('Waiting for:', m3u8_file , '...')
        time.sleep(1)

def live_stream_audio(audio_url: str, streaming_url: str,debug: bool):
    with tempfile.TemporaryDirectory() as temp_dir:
        m3u8_file = download_audio(temp_dir,audio_url,debug)
        waiting_for_file_ready(m3u8_file)
        cmd = f"""ffmpeg -re -i "{m3u8_file}" -c:v libx264 -c:a aac -f flv - | ffmpeg -re -i - -c:v copy -c:a copy -ac 2 -preset veryfast -b:v 3500k -maxrate 3500k -bufsize 7000k -f flv -flvflags no_duration_filesize {streaming_url}"""
        process = process_cmd(cmd, debug)
        process.wait()

def live_stream_audio_with_image(image_url: str, audio_url: str, streaming_url: str, debug: bool):
    with tempfile.TemporaryDirectory() as temp_dir:
        m3u8_file = download_audio(temp_dir,audio_url,debug)
        waiting_for_file_ready(m3u8_file)
        temp_image = download_image(temp_dir, image_url)
        temp_image = temp_image if temp_image != None else "image.jpeg"
        cmd = f"""ffmpeg -loop 1 -re -i "{temp_image}" -i "{m3u8_file}" -tune stillimage -pix_fmt yuv420p -c:v libx264 -c:a aac -strict experimental -b:a 192k -vf "scale=1920:1080" -shortest -f flv - | ffmpeg -re -i - -c:v copy -c:a copy -ac 2 -preset veryfast -b:v 3500k -maxrate 3500k -bufsize 7000k -f flv -flvflags no_duration_filesize {streaming_url}"""
        process = process_cmd(cmd, debug) 
        process.wait()

def send_to_server(name: str, num: int, url: str):
    res = requests.get(f"http://localhost:8000/stream/add/{name}/{num}?url={url}")
    print(res.json())

if __name__ == "__main__":
    # Long time audio
    # url = "https://www.youtube.com/watch?v=qfFmZa9jgoY"
    # url = "https://www.youtube.com/watch?v=NJuSStkIZBg"
    # url = "https://www.youtube.com/watch?v=y2ECgOhoDGs"
    # https://www.youtube.com/watch?v=nizfv91mcpA
    # Short time audio
    urls = [
        # "https://www.youtube.com/watch?v=nizfv91mcpA"
        # "https://www.youtube.com/watch?v=UDVtMYqUAyw&pp=ygUV5pif6Zqb5pWI5oeJ5Li76aGM5puy",

        # "https://www.youtube.com/watch?v=BwBr2B2AilM&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=41",
        # "https://youtube.com/watch?v=mddFKeYaD3Q&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=13",
        "https://www.youtube.com/watch?v=TFHd-B9Yu_0",
        "https://www.youtube.com/watch?v=qrFdCuOi5n8",
        "https://www.youtube.com/watch?v=uaFntToH2-I",
        "https://www.youtube.com/watch?v=6saUWkJ3Gms",
        "https://www.youtube.com/watch?v=6NImgmZKLfo",
        "https://www.youtube.com/watch?v=gbmLFbrv1js",
        "https://www.youtube.com/watch?v=5iqdEb74SK4&list=RDiviT0HIOm1M&index=2",
        "https://www.youtube.com/watch?v=1edQR-pijJw&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=4",
        "https://www.youtube.com/watch?v=4bmRziNgRGk&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=40",
        "https://www.youtube.com/watch?v=Pswx6OQp1Ks&list=RDMM&index=10",
        "https://www.youtube.com/watch?v=pex10KVmz2I&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=14",
        "https://www.youtube.com/watch?v=mqIF115ph28&list=RDMM&index=8",
        "https://www.youtube.com/watch?v=317RHaFF7Xk&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=27",
        "https://www.youtube.com/watch?v=EVfrrugW8JI&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=27",
        "https://www.youtube.com/watch?v=0JL8q27C_k8&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=15",
        "https://www.youtube.com/watch?v=nTPL3N5QCh4&list=RDMM&start_radio=1&rv=Z_3BzA5ZSLY",
        "https://www.youtube.com/watch?v=3EwLdxmJxyM&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=12",
        "https://www.youtube.com/watch?v=iLl-wxYC64A&list=RDMM&index=2",
        "https://www.youtube.com/watch?v=3F5PBLEOwp4&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=11",
        "https://www.youtube.com/watch?v=nIBIMOzPWtA&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&start_radio=1&rv=6saUWkJ3Gms",
        "https://www.youtube.com/watch?v=-NxIQYQsaXc&list=RDiviT0HIOm1M&index=8",
        "https://www.youtube.com/watch?v=WqPnSh3jJic",
        'https://www.youtube.com/watch?v=FDyz-4zHNh4&list=RDFDyz-4zHNh4&start_radio=1',
        "https://www.youtube.com/watch?v=dE9B-oMNNAs",
        "https://www.youtube.com/watch?v=bLef1wGJrD4",
    ]
    i = 0
    while i < 10000:
        for url in urls:
            send_to_server("paxton","1",url)
            i += 1
    # while True:
    #     for url in urls:
    #         info = video_info(url)
    #         if info != None:
    #             print(info["title"],"-",info["author"])
    #             live_stream_audio(info["audio_url"],RTMP_TARGET,True)
    #             # live_stream_audio_with_image(info['thumb_url'],info["audio_url"],RTMP_TARGET,True)
    #             # live_stream_audio_with_image(info['thumb_url'],info["audio_url"],YT_RTMP_TARGET,True)