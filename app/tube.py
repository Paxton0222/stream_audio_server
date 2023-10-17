from pytube import YouTube
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC


class Youtube:
    def audio_info(self,url: str):
        video = YouTube(url,use_oauth=False, allow_oauth_cache=False)
        try:
            audio_stream = video.streams.filter(only_audio=True).first()
            audio_url = audio_stream.url + "&from_cache=True"

            return {
                "url": url,
                "audio_url": audio_url,
                "title": video.title,
                "author": video.author,
                "thumb_url": video.thumbnail_url,
                "length": video.length
            }
        except Exception as e:
            print(e)
        return None