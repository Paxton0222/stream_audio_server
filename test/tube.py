from pytube import Playlist

# 合辑URL
playlist_url = 'https://www.youtube.com/watch?list=RDxhUQlrijwkY'

# 初始化合辑对象
playlist = Playlist(playlist_url)

print(playlist.video_urls)

# 打印合辑信息
for video in playlist.video_urls:
    print(video)
