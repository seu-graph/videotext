from videotextextractor.video import Video
import os
from fuzzywuzzy import fuzz


def eval_single_video(video_path: str, gt_path: str, lang="ch", srt_format=False) -> str:
    v = Video(video_path)   
    v.config_ocr_engine(lang=lang)
    v.run_ocr()
    result_subtitle = v.get_subtitles(sim_threshold=0.7, srt_format=srt_format)    # 设置判断两句字幕是否相同的thres
    print("***** result *******\n")
    print(result_subtitle)
    # 读取字幕groundtrue
    with open(gt_path, "r") as f:  # 打开文件
        gt_subtitle = f.read() 
    ratio = fuzz.partial_ratio(result_subtitle, gt_subtitle)/100
    print("--------------------\nThe accurate rate: {}".format(ratio))
    return 

if __name__ == "__main__":
    video_path = "./test_data/video-test.mp4"
    gt_path = "./test_data/video-test_groundtruth.txt"
    eval_single_video(video_path, gt_path, lang='ch')
