# from pytube import YouTube
import yt_dlp as youtube_dl

class Youtube:
    def audio_info(self, url: str):
        # video = YouTube(url, use_oauth=False, allow_oauth_cache=False)
        try:
            # audio_stream = video.streams.filter(only_audio=True).first()
            # audio_url = audio_stream.url + "&from_cache=True"
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': True,
                'simulate': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
            
            title = info_dict.get('title', 'N/A')
            author = info_dict.get('uploader', 'N/A')
            thumbnail_url = info_dict.get('thumbnail', 'N/A')
            video_duration = info_dict.get('duration', 0)

            return {
                "url": url,
                "title": title,
                "author": author,
                "thumb_url": thumbnail_url,
                "length": video_duration
            }
        except Exception as e:
            print(e)
        return None
