from videotextextractor import api

#api.get_subtitles(video_path="./test_data/video-test.mp4", lang='ch', manual=False, srt_format=True)
api.get_subtitles(video_path="./test_data/video-test.mp4", lang='ch', manual=False)

# 关键帧
num_frames = 500  #最大帧数
begin = 1  #开始帧数
interval = 32 #间隔
indexlst = [i for i in range(begin, num_frames, interval)]
api.get_keyframe_text(video_path="./test_data/video-test.mp4", indexlst = indexlst)