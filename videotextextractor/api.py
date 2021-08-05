
from .video import Video
from .datamodel import PredictedFrame
from cv2 import cv2
from paddleocr import draw_ocr
import os

def get_subtitles(video_path: str, lang="ch", manual=False, srt_format=False) -> str:
    v = Video(video_path, manual_cri=manual)    # 自动判别字幕和背景
    v.config_ocr_engine(lang=lang)
    v.run_ocr()
    result_subtitle = v.get_subtitles(sim_threshold=0.7, srt_format=srt_format)    # 设置判断两句字幕是否相同的thres
    result_path = "./output/result.txt"
    if srt_format:
        result_path = "./output/result.srt"
    with open(result_path, 'w') as f:
        f.write(result_subtitle)
    print("The ocr result saved!")
    return 


def get_keyframe_text(video_path:str, indexlst, lang = "ch"):
    v = Video(video_path)    # 自动判别字幕和背景
    v.config_ocr_engine(lang=lang)
    video_name = os.path.basename(os.path.splitext(video_path)[0])
    visual_dir = os.path.join("./output", video_name + "_visual")
    if not os.path.exists(visual_dir):
        os.mkdir(visual_dir)
    v.run_ocr_keyframe(indexlst, visual_dir)  #传入关键帧index列表，保存可视化结果
    return

# def get_subtitiles_by_manual()
# TODO


# get_subtitles(video_path="../test_data/Multiline_Example.mp4", lang='ch', manual=True)
#get_subtitles(video_path="../test_data/YueYu.mp4", lang='ch', manual=True)
