# subtitle detection & ocr

- 使用paddleocr引擎进行文本行的检测与识别

本项目搭建了基本的新闻字幕及背景文字检测框架
### 已实现功能
- 根据文本行和置信度以及字幕范围的先验实现对字幕及背景文字的自动区分
- 提供了手动框选字幕区域限定范围的接口

### 更新功能
-  前后字幕去重: 不固定长度的滑动窗口去重，因为考虑到识别的误差，对于前后帧字幕结果字符串相似度高于80%认为是重复帧。把它们放入一个结果当中，并且最终结果字符串是这所有相似结果字符串中正确率最高的那个。
- 字幕区域范围: 在识别之前提供一个截选功能，如果检测算法的文字框定位在截选框内的文字，认定为字幕，外部的或者不全在里面的都认为是背景文字。如果不使用截选功能，这使用默认的底部1/3范围
- 对于两个以上的多行字幕，直接实现字符串的拼接操作。
- 增加一个根据关键帧序号去识别该帧图片中所有内容的功能接口。


### 主要类型说明

#### Predictedtextline:
    
- dataclass类型（根据tbox信息在post_init方法中初始化
- 识别的文本行的相关信息
- 包含
    - tbox：文本框信息（四个点）
    - text：ocr文本
    - confidence：识别置信度
    - rotation：文本框倾斜角度（init设置为false，在post_init中根据tbox信息后初始化

#### PredictedFrame：

- 主要记录一帧画面中识别的文本行，并根据一定的策略自动划分subtitle和背景中文字行

#### PredictedSubtitle：

- 主要记录一个字幕出现在一连续帧片段的范围

#### Video：

- 整个视频字幕检测的主体，主要包含所有识别帧，以及检测出来的字幕对象列表

- 核心算法：前后字幕去重 Video._generate_subtitles()


### 使用说明

#### 环境安装

1. 安装[飞桨paddle](https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/conda/linux-conda.html#anchor-0)（根据本机配置安装对应版本，建议安装2.0以上版本）

2. 安装paddleocr库：`pip install "paddleocr>=2.0.1" # 推荐使用2.0.1+版本`

3. 首次使用，会自动下载mobile_model模型参数。在`../infer_model`目录下。默认使用的是ppocr的移动端模型。

4. 如果需要使用更加精准的识别模型，下载地址: 'https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_server_v2.0_rec_infer.tar'. 下载后把所有模型文件解压到'../rec/'目录下.

5. 使用接口, video_path指定视频路径，'ch'支持中英，数字同时识别，manual指定是否使用截选字幕框。使用例子如下：
<pre>
import api
api.get_subtitles(video_path="../test_data/YueYu.mp4", lang='ch', manual=True)
</pre>

6. 运行demo `python demo.py`
- 结果保存在output目录下

7. 评估视频字幕识别正确率 `python eval.py`


### 接口更新

#### 2021-8-29

- api.py文件中新增ocr接口，传入视频文件路径、语言类型、手动截选选项，返回json格式结果。同时提供了demo使用示例`python ocr.py`

#### 2021-9-5

- flask 封装成 restful 接口。

使用说明：

    - 启动dacker `sudo nvidia-docker run -d -p 5555:5555 ppocr:5.0 /bin/bash -c "cd /videotext && python flask_main.py"`。web服务绑定端口5555

    - 请求路由 `<ip>:5555/video_text` , 暴露的参数：lang：语言类型（默认'ch'）；video：视频文件（必须传递）。

示例：

```bash
$ curl --location --request POST '10.201.45.xxx:5555/video_text' --form 'lang="ch"' --form 'video=@"/Users/liuhuan/Desktop/test.mp4"'

# 返回结果

[
  {
    "No": 0,
    "data": "你们吃就吃香港的",
    "frameNo": [
      0,
      40
    ],
    "frameTime": "00:00:00,00:00:01"
  },
  {
    "No": 1,
    "data": "吃父母的",
    "frameNo": [
      42,
      82
    ],
    "frameTime": "00:00:01,00:00:03"
  },
  {
    "No": 2,
    "data": "看医生都是看香港的",
    "frameNo": [
      86,
      124
    ],
    "frameTime": "00:00:03,00:00:05"
  },
  {
    "No": 3,
    "data": "你以为你们有什啊",
    "frameNo": [
      134,
      174
    ],
    "frameTime": "00:00:05,00:00:07"
  },
  {
    "No": 4,
    "data": "有书又不",
    "frameNo": [
      176,
      206
    ],
    "frameTime": "00:00:07,00:00:08"
  },
  {
    "No": 5,
    "data": "如果你们在火车裹搞事情",
    "frameNo": [
      210,
      260
    ],
    "frameTime": "00:00:08,00:00:10"
  },
  {
    "No": 6,
    "data": "一定打死你",
    "frameNo": [
      320,
      382
    ],
    "frameTime": "00:00:13,00:00:15"
  },
  {
    "No": 7,
    "data": "我不理你什磨",
    "frameNo": [
      442,
      500
    ],
    "frameTime": "00:00:18,00:00:20"
  },
  {
    "No": 8,
    "data": "你们黑社会又算不上",
    "frameNo": [
      502,
      524
    ],
    "frameTime": "00:00:20,00:00:21"
  },
  {
    "No": 9,
    "data": "简直是垃圾中的垃圾",
    "frameNo": [
      526,
      614
    ],
    "frameTime": "00:00:21,00:00:25"
  },
  {
    "No": 10,
    "data": "在你啊垃圾",
    "frameNo": [
      736,
      830
    ],
    "frameTime": "00:00:30,00:00:34"
  },
  {
    "No": 11,
    "data": "现在全部人都在工作",
    "frameNo": [
      928,
      984
    ],
    "frameTime": "00:00:38,00:00:41"
  },
  {
    "No": 12,
    "data": "你们现在一搞事情",
    "frameNo": [
      994,
      1016
    ],
    "frameTime": "00:00:41,00:00:42"
  },
  {
    "No": 13,
    "data": "影著香港市民啊",
    "frameNo": [
      1018,
      1062
    ],
    "frameTime": "00:00:42,00:00:44"
  },
  {
    "No": 14,
    "data": "你们有什啊",
    "frameNo": [
      1082,
      1118
    ],
    "frameTime": "00:00:45,00:00:46"
  },
  {
    "No": 15,
    "data": "有书又不去",
    "frameNo": [
      1128,
      1148
    ],
    "frameTime": "00:00:47,00:00:47"
  },
  {
    "No": 16,
    "data": "遗不是向老爸老妈拿",
    "frameNo": [
      1226,
      1226
    ],
    "frameTime": "00:00:51,00:00:51"
  },
  {
    "No": 17,
    "data": "向香港政府拿",
    "frameNo": [
      1228,
      1282
    ],
    "frameTime": "00:00:51,00:00:53"
  },
  {
    "No": 18,
    "data": "你吃什啊你",
    "frameNo": [
      1286,
      1338
    ],
    "frameTime": "00:00:53,00:00:55"
  },
  {
    "No": 19,
    "data": "你自己设你吃什磨",
    "frameNo": [
      1340,
      1370
    ],
    "frameTime": "00:00:55,00:00:57"
  },
  {
    "No": 20,
    "data": "SHARE.COMMENT LIKE",
    "frameNo": [
      1572,
      1618
    ],
    "frameTime": "00:01:05,00:01:07"
  }
]
```