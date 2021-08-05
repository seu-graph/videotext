from __future__ import annotations
from typing import List
import sys
#import multiprocessing
import cv2
from paddleocr import PaddleOCR, draw_ocr
import os
import codecs
from PIL import Image

from . import utils
from .datamodel import PredictedFrame, PredictedSubtitle, Predictedtextline
from .video_util import Capture, manual_cricumscribe_bound


class Video:
    path: str
    num_frames: int
    fps: float
    height: int
    width: int
    ocr_engine: PaddleOCR
    pred_frames: List[PredictedFrame]
    pred_subs: List[PredictedSubtitle]
    subtitle_bound: list # [left_up_point, right_down_point]
    manual_cricumscribe: bool = False     # TODO   添加手动标定subtitle_bound选项

    def __init__(self, path: str, manual_cri=False):
        self.path = path
        self.manual_cricumscribe = manual_cri
        with Capture(path) as v:
            self.num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = v.get(cv2.CAP_PROP_FPS)
            self.height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.width = int(v.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.subtitle_bound = [[0, self.height*2/3], [self.width, self.height]]  # 默认区域为底部1/3区域
            self.pred_frames = []
    
    def config_ocr_engine(self, lang, use_gpu = True, drop_score = 0.6):  # ### TODO   使用argparse
        det_path = './infer_model/det'
        rec_path = './infer_model/rec'
        cls_path = './infer_model/cls'
        rec_dic_path = '/opt/videotext/infer_model/ppocr_keys_v1.txt'
        det_path_big = '/opt/videotext/infer_model/ch_ppocr_server_v2.0_det_infer'
        rec_path_big = '/opt/videotext/infer_model/ch_ppocr_server_v2.0_rec_infer'
        self.ocr_engine = PaddleOCR(lang=lang, drop_score=drop_score, rec_model_dir=rec_path_big, rec_char_dict_path = rec_dic_path,
                                        det_model_dir=det_path_big)
        #self.ocr_engine = PaddleOCR(lang=lang, drop_score=drop_score, rec_model_dir=rec_path, det_model_dir=det_path, cls_model_dir=cls_path, rec_char_dict_path = rec_dic_path)
        # self.ocr_engine = PaddleOCR(lang=lang, drop_score=drop_score)

    def run_ocr(self, time_start=None, time_end=None) -> None:

        ocr_start = utils.get_frame_index(time_start, self.fps) if time_start else 0
        ocr_end = utils.get_frame_index(time_end, self.fps) if time_end else self.num_frames
        
        if ocr_end < ocr_start:
            raise ValueError('time_start is later than time_end')
        num_ocr_frames = ocr_end - ocr_start

        # 处理手动选框的情况
        if self.manual_cricumscribe:
            self.subtitle_bound = manual_cricumscribe_bound(self.path)
        else:
            self.subtitle_bound = [[0, self.height*2/3], [self.width, self.height]]  # 默认区域为底部1/3区域

        # get frames from ocr_start to ocr_end
        with Capture(self.path) as v:   
            v.set(cv2.CAP_PROP_POS_FRAMES, ocr_start)
            frames = (v.read()[1] for _ in range(num_ocr_frames))   # 生成器
            # paddleocr引擎不支持多进程
            for i, frame in enumerate(frames):  # 均匀抽帧
                if i % int(self.fps/10) == 0:   #每秒抽10帧
                    newframe = PredictedFrame(i+ocr_start, self._image_to_data(frame), subtitle_bound=self.subtitle_bound)
                    print('----------- 字 幕 ------------\n'+newframe.subtitle_text)
                    print('----------- 背 景 ------------\n'+newframe.background_text)
                    self.pred_frames.append(newframe)
            '''
            # perform ocr to frames in parallel
            it_ocr = pool.imap(self._image_to_data, frames, chunksize=10)
            self.pred_frames = [
                PredictedFrame(i + ocr_start, textline_res, subtitle_bound = self.subtitle_bound) for i, textline_res in enumerate(it_ocr)
            ]
            '''
    def run_ocr_keyframe(self, index_list, visual_dir=None):
        # 处理手动选框的情况
        if self.manual_cricumscribe:
            self.subtitle_bound = manual_cricumscribe_bound(self.path)
        else:
            self.subtitle_bound = [[0, self.height*2/3], [self.width, self.height]]  # 默认区域为底部1/3区域

        # get frames from ocr_start to ocr_end
        with Capture(self.path) as v: 
            for index in index_list:
                if index < 0 or index > self.num_frames:
                    print("this index [{}] out of range, please check again! continue next...".format(index))
                    continue
                v.set(cv2.CAP_PROP_POS_FRAMES, index)
                success, frame = v.read()
                if not success:
                    print("read current frame:{} failed, continue next....".format(index))
                    continue
                newframe = PredictedFrame(index, self._image_to_data(frame), subtitle_bound=self.subtitle_bound)
                self.pred_frames.append(newframe)
                print('********* 视频帧：{} **********\n'.format(index))
                print('----------- 字 幕 ------------\n'+newframe.subtitle_text)
                print('----------- 背 景 ------------\n'+newframe.background_text)
                #可视化结果保存
                if visual_dir:
                    save_path = os.path.join( visual_dir, str(index) + '_result.jpg')
                    boxes = newframe.get_text_box_list("all")
                    texts = newframe.get_text_ocr_list("all")
                    scores = newframe.get_confidence_list("all")
                    im_show = draw_ocr(frame, boxes, texts, scores, font_path = "./simfang.ttf")
                    im_show = Image.fromarray(im_show)
                    im_show.save(save_path)
        return
        
                
                



    def estimate_subtitle_bound(self):  # 统计文本框出现最频繁的范围
        pass    # TODO
        # self.bound =

    def _image_to_data(self, img) -> list:
        try:
            return self.ocr_engine.ocr(img, cls=True)
        except Exception as e:
            sys.exit('{}: {}'.format(e.__class__.__name__, e))

    def get_subtitles(self, sim_threshold: int, srt_format = False) -> str:   
        self._generate_subtitles(sim_threshold)
        if srt_format:
            return ''.join('{}\t frame: {} ---> {}\n{} --> {}\n{}\n\n'.format(
                    i, sub.index_start, sub.index_end, 
                    utils.get_srt_timestamp(sub.index_start, self.fps), 
                    utils.get_srt_timestamp(sub.index_end, self.fps),
                    sub.text
                    ) for i, sub in enumerate(self.pred_subs))
        # 否则返回无格式的字幕文本
        #return ''.join('{}\n'.format( sub.text ) for sub in self.pred_subs)
        return '\n'.join(sub.text for sub in self.pred_subs)

    # 滑动窗口字幕分割
    def _generate_subtitles(self, sim_threshold: int) -> None:
        self.pred_subs = []
        if self.pred_frames is None:
            raise AttributeError('Please call self.run_ocr() first to perform ocr on frames')
        pred_frames_len = len(self.pred_frames)
        # 不固定长度的滑动窗口
        l = 0
        while l < pred_frames_len - 1 and self.pred_frames[l].subtitle_text == '':
            l += 1
        r = l+1
        self._append_new_sub(PredictedSubtitle([self.pred_frames[l]], sim_threshold))
        while r < pred_frames_len and l < pred_frames_len:
            fl, fr = self.pred_frames[l], self.pred_frames[r]
            # 跳过没有字幕的情况
            if fr.subtitle_text == '':
                r += 1
                continue
            if fl.with_same_subtitle(fr, sim_threshold):
                self.pred_subs[-1].update(fr)
            else:
                l = r
                self._append_new_sub(PredictedSubtitle([self.pred_frames[l]], sim_threshold))
            r += 1

    # 根据关键帧的index获取背景文字
    def get_background_text(self, index_list: int) -> str:
        return self.pred_frames[index_list].background_text

    def _append_new_sub(self, subobj: PredictedSubtitle):
        self.pred_subs.append(subobj)



