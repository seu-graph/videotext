from video import Video
from cv2 import cv2
from paddleocr import PaddleOCR


def get_subtitles(video_path: str, lang="ch", manual=False) -> str:
    v = Video(video_path, manual_cri=manual)    # 测试手动框选
    v.config_ocr_engine(lang=lang)
    v.run_ocr()
    result_subtitle = v.get_subtitles(sim_threshold=0.7)    # 设置判断两句字幕是否相同的thres
    print(result_subtitle)
    return result_subtitle


def get_keyframe_background_text(video_path:str, index:int, lang = "ch") -> str:
    v = cv2.VideoCapture(video_path)
    num_frames = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ocr = PaddleOCR(True, lang)  # 第一个是定义是否使用angle_cls
    for i in range(num_frames):
        frame = v.read()[1]
        if i == index:
            result = ocr.ocr(frame, cls=True)
            break
    return ''.join('{}\t    ------>    {}\n'.format(line[1][1], line[1][0]) for line in result)

# def get_subtitiles_by_manual()
# TODO


# get_subtitles(video_path="../test_data/Multiline_Example.mp4", lang='ch', manual=True)
#get_subtitles(video_path="../test_data/YueYu.mp4", lang='ch', manual=True)
