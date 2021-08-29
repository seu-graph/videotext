
from .video import Video
from .datamodel import PredictedFrame
from cv2 import cv2
from paddleocr import draw_ocr
import os
import json

def ocr(video:str, lang="ch", manual=False):
    v = Video(video, manual_cri=manual)
    v.config_ocr_engine(lang = lang, drop_score=0.85)
    v.run_ocr()
    res = v.get_subtitles(sim_threshold=0.7, srt_format=True)
    json_res = json.dumps(res, ensure_ascii=False)
    print(json_res)
    return json_res


def get_subtitles(video_path: str, lang="ch", manual=False, srt_format=True, outfile=None) -> str:
    v = Video(video_path, manual_cri=manual)    # 自动判别字幕和背景
    v.config_ocr_engine(lang=lang, drop_score=0.85)
    v.run_ocr()
    result_subtitle = v.get_subtitles(sim_threshold=0.7, srt_format=srt_format)    # 设置判断两句字幕是否相同的thres
    result_path = "./output/result_subtitle.txt"
    if outfile is not None:
        result_path = outfile
    
    with open(result_path, 'w') as f:
        f.write(result_subtitle)
    print("The ocr result saved!")
    return 


def get_keyframe_text(video_path:str, indexlst, lang = "ch", outfile=None):
    v = Video(video_path)    # 自动判别字幕和背景
    v.config_ocr_engine(lang=lang, drop_score=0.8)
    video_name = os.path.basename(os.path.splitext(video_path)[0])
    visual_dir = os.path.join("./output", video_name + "_visual")
    if not os.path.exists(visual_dir):
        os.mkdir(visual_dir)
    result_bg = v.run_ocr_keyframe(indexlst, visual_dir)  #传入关键帧index列表，保存可视化结果到visual_dir
    # 保存文本提取结果
    result_path = "./output/result_keyframe.txt"
    if outfile is not None:
        result_path = outfile
    
    with open(result_path, 'w') as f:
        f.write(result_bg)
    print("The ocr result saved!")
    return


