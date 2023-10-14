from pytube import YouTube

class Youtube:
    def audio_info(self,url: str):
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