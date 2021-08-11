from __future__ import annotations
from typing import List
from dataclasses import dataclass, field
import numpy as np
from fuzzywuzzy import fuzz
from zhconv import convert
from opencc import OpenCC


@dataclass
class Predictedtextline:
    tbox: list[list] #4*point
    text: str
    confidence: float
    rotation: int = field(init=False)

    def __post_init__(self):
        # 计算文本框角度
        self.rotation = self._getrotation()
        # 繁简体转换
        #self.text = convert(self.text, 'zh-cn')
        self.text = OpenCC('t2s').convert(self.text)
    

    def _getrotation(self):
        def _get_distance(pa, pb):
            return pow((pa[0]-pb[0])*(pa[0]-pb[0])+(pa[1]-pb[1])*(pa[1]-pb[1]), 0.5)
        ########  tbox__4point  ##############
        #   point0----------point1
        #      |              |
        #      |              |
        #   point3----------point2
        #####################################
        horp1 = [(self.tbox[0][0]+self.tbox[3][0])/2, (self.tbox[0][1]+self.tbox[3][1])/2]
        horp2 = [(self.tbox[1][0]+self.tbox[2][0])/2, (self.tbox[1][1]+self.tbox[2][1])/2]
        verp1 = [(self.tbox[0][0]+self.tbox[1][0])/2, (self.tbox[0][1]+self.tbox[1][1])/2]
        verp2 = [(self.tbox[2][0]+self.tbox[3][0])/2, (self.tbox[2][1]+self.tbox[3][1])/2]
        if _get_distance(horp1, horp2) >= _get_distance(verp1, verp2):
            point1, point2 = horp1, horp2 
        else:
            point1, point2 = verp1, verp2
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]; 
        if x2 - x1 == 0:        #竖直
            result=90
        elif y2 - y1 == 0 :     #水平
            result=0
        else:
            k = -(y2 - y1) / (x2 - x1)          # 计算斜率
            result = np.arctan(k) * 57.29577 #180/pi    # 求反正切，再将得到的弧度转换为度
        return result #(-90-90]

    def __repr__(self):
        return "textbox:{}\t rotation:{}\t text:{} [confidence:{}]\n".format(self.tbox, self.rotation, self.text, self.confidence)

    def __eq__(self, other):
        # iou > 0.85 && text 相似度 > 0.9 // iou-> TODO
        thred = 0.8
        if len(self.text) <= 5 or len(other.text) <= 5:
            thred = 0.6
        return fuzz.partial_ratio(self.text, other.text)/100 >= thred

    #def __hash__(self): //None

class PredictedFrame:
    _index: int  # 0-based index of the frame
    _textlines: List[Predictedtextline] = []
    _subtitles: List[Predictedtextline] = []
    _subtitle_average_conf: float
    _backtextlines: List[Predictedtextline] = []
    _rota_thresh: float = 1.5
    _conf_thresh: float = 0.8
    _subtitle_bound: list[list] # 2 point: left-up and right-down

    def __init__(self, index, ocr_result:list, rota_thresh = 1.5, conf_thresh = 0.8, subtitle_bound = None):
        self._index = index
        self._rota_thresh = rota_thresh
        self._conf_thresh = conf_thresh
        self._subtitle_bound = subtitle_bound
        self._textlines = []
        self._subtitles = []
        self._backtextlines = []
        # 构造predictedtextline
        for line in ocr_result:
            self._textlines.append(Predictedtextline(line[0], line[1][0], line[1][1])) 
            # line[0] 是四个边框点，line[1][0]是识别内容。 line[1][1]是识别正确率
        
        self._split_title_background()
        self._subtitle_average_conf = self._calculate_subtitle_average_conf()

    # 获取当前帧的文本行边框信息列表
    def get_text_box_list(self, label):
        ret = []
        if label == "all":
            ret = [tl.tbox for tl in self._textlines]
        elif label == "subtitle":
            ret = [tl.tbox for tl in self._subtitles]
        elif label == "background":
            ret = [tl.tbox for tl in self._backtextlines]

        return ret

    # 获取当前帧的文本行text识别结果列表
    def get_text_ocr_list(self, label):
        ret = []
        if label == "all":
            ret = [tl.text for tl in self._textlines]
        elif label == "subtitle":
            ret = [tl.text for tl in self._subtitles]
        elif label == "background":
            ret = [tl.text for tl in self._backtextlines]

        return ret

    # 获取当前帧的文本行识别置信度列表
    def get_confidence_list(self, label):
        ret = []
        if label == "all":
            ret = [tl.confidence for tl in self._textlines]
        elif label == "subtitle":
            ret = [tl.confidence for tl in self._subtitles]
        elif label == "background":
            ret = [tl.confidence for tl in self._backtextlines]

        return ret

    @property
    def index(self):
        return self._index

    @property
    def subtitle_conf(self):
        return self._subtitle_average_conf

    @property
    def subtitle_text(self):
        texts = [line.text for line in self._subtitles]
        if texts:
            return " ".join(texts)
        else:
            return ''

    @property
    def all_text(self):
        texts = [line.text for line in self._textlines]
        if texts:
            return "\n".join(texts)
        else:
            return ''

    @property
    def background_text(self):
        texts = [line.text for line in self._backtextlines]
        if texts:
            return "\n".join(texts)
        else:
            return ''
    
    @property
    def background_textlines(self):
        return self._backtextlines

    def with_no_subtitle(self):
        return len(self._subtitles) == 0

    @staticmethod
    def filter_textlines(textlines):
        #return [line if len(line.text) > 3 for line in textlines ]
        return list(filter(lambda line : len(line.text)>3, textlines))

    def _split_title_background(self):
        condidate_lines = []
        filtered_lines = self.filter_textlines(self._textlines)
        if self._subtitle_bound is not None:    # 如果设置了bound范围，则先过滤一遍得到候选文本行
            for textline in filtered_lines:
                point_leup, point_ridw = textline.tbox[0], textline.tbox[2]
                bound_leup, bound_ridw = self._subtitle_bound[0], self._subtitle_bound[1]
                if point_leup[0] >= bound_leup[0] and point_leup[1] >= bound_leup[1] and point_ridw[0] <= bound_ridw[0] and point_ridw[1] <= bound_ridw[1]:
                    condidate_lines.append(textline)
                else:
                    self._backtextlines.append(textline)
        else:                                   # 否则候选文本列表为所有检测到的文本行
            condidate_lines = filtered_lines  
        for textline in condidate_lines:
            if textline.confidence >= self._conf_thresh and abs(textline.rotation) < self._rota_thresh:
                self._subtitles.append(textline)
            else:
                self._backtextlines.append(textline)

    def _calculate_subtitle_average_conf(self):       # 获取subtitles的平均置信度
        from numpy import mean
        conf_list = [textline.confidence for textline in self._subtitles]
        if conf_list:
            return mean(conf_list)
        else:
            return 0
    
    def with_same_subtitle(self, other: PredictedFrame, sim_thresh = 0.7):
        return fuzz.partial_ratio(self.subtitle_text, other.subtitle_text)/100 >= sim_thresh   # 忽略顺序匹配

    @property
    def rota_thresh(self):
        return self._rota_thresh

    @rota_thresh.setter
    def rota_thresh(self, value):
        self._rota_thresh = value
    
    @property
    def conf_thresh(self):
        return self._conf_thresh
        
    @conf_thresh.setter
    def conf_thresh(self, value):
        self._conf_thresh = value

    @property
    def subtitle_bound(self):
        return self._subtitle_bound
        
    @subtitle_bound.setter
    def subtitle_bound(self, value):
        self._subtitle_bound = value

    def __str__(self):
        res = "\n The ocr textline result in this frame [{}]:\n".format(self._index)
        res += "subtitle:\n"
        for line in self._subtitles:
            res += str(line)
        res += "others:\n"
        for line in self._backtextlines:
            res += str(line)
        return res


class PredictedSubtitle:
    frames: List[PredictedFrame]
    candidate_frame: PredictedFrame
    sim_threshold: float
    text: str

    def __init__(self, frames: List[PredictedFrame], sim_threshold: int):
        self.frames = frames
        self.sim_threshold = sim_threshold

        if self.frames:
            self.candidate_frame = max(self.frames, key=lambda f: f.subtitle_conf)
            self.text = self.candidate_frame.subtitle_text
        else:
            self.candidate_frame = None
            self.text = ''

    @property
    def index_start(self) -> int:
        if self.frames:
            return self.frames[0].index
        return 0

    @property
    def index_end(self) -> int:
        if self.frames:
            return self.frames[-1].index
        return 0
    '''
    @staticmethod
    def bbox_iou(bbox1: list, bbox2: list):  #对于字幕，倾斜角度很小，看成是标准矩形来计算IOU
        x1min, y1min = 
        x1max, y1max = 
        x2min, y2min = 
        x2max, y2max =   #TODO
        return iou
    '''
    def is_similar_to(self, newframe: PredictedFrame) -> bool:

        return fuzz.token_sort_ratio(self.text, newframe.subtitle_text)/100 >= self.sim_threshold   # 忽略顺序匹配

    def update(self, newframe: PredictedFrame):   # 添加新的frame到当前predictsubtitle
        self.frames.append(newframe)
        if newframe.subtitle_conf > self.candidate_frame.subtitle_conf:
            self.candidate_frame = newframe
            self.text = newframe.subtitle_text

    def __repr__(self):
        return '{} - {}:   {}'.format(self.index_start, self.index_end, self.text)



if __name__ == "__main__":
    from paddleocr import PaddleOCR, draw_ocr
    ocr = PaddleOCR(using_angle_cls=True, lang="ch")
    # test_img_path = './test_data/video_3.jpg'
    test_img_path = '../test2.jpg'
    result = ocr.ocr(test_img_path, cls=True)
    # print(result)
    pred_frame_res = PredictedFrame(0, result)
    print(pred_frame_res)



