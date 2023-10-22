# from pytube import YouTube
import yt_dlp as youtube_dl


class Youtube:
    def info(self, url: str):
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': True,
                'simulate': True,
                'dump_single_json': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)

            # 初始化返回的字典，包含一致的键
            result = {
                "url": url,
                "title": info_dict.get('title', 'N/A'),
                "author": info_dict.get('uploader', 'N/A'),
                "thumb_url": info_dict.get('thumbnail', 'N/A'),
                "length": info_dict.get("duration", None),
                # is_live 是否直播
                # playlist null 代表不是 playlist
            }

            # 更新字典以包含 `yt-dlp` 提供的信息
            result.update(info_dict)

            return result
        except Exception as e:
            print(e)
        return None
