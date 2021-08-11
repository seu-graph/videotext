from videotextextractor import api
import os
import cv2
import sys
import getopt

if __name__ == "__main__":
    video_path = None
    start = 0
    end = None
    interval = 1
    out_name = None

    argv = sys.argv[1:]
 
    try:
        opts, args = getopt.getopt(argv, "v:o:s:i:e:", ["video_dir=","out_name=","start=","interval=","end="])  # 长选项模式
    except:
        print("Error")
 
    for opt, arg in opts:
        if opt in ['-v', '--video_dir']:
            video_path = arg
        elif opt in ['-o', '--out_name']:
            out_name = arg
        elif opt in ['-s', '--start']:
            start = int(arg)
        elif opt in ['-i', '--interval']:
            interval = int(arg)
        elif opt in ['-e', '--end']:
            end = int(arg)
    
    if video_path == None:
        print("please input video path")

    if out_name is None:    
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        out_name = video_name
    
    subtitle_out_path = out_name + "_subtitle.txt"
    keyframe_out_path = out_name + "_keyback.txt"
    # subtitle
    api.get_subtitles(video_path=video_path, lang = 'ch', manual = False, outfile = subtitle_out_path)

    # key frame
    v = cv2.VideoCapture(video_path)
    num_frames = int(v.get(cv2.CAP_PROP_FRAME_COUNT))
    v.release()

    if end and end < num_frames and end < start:
        indexlst = [i for i in range(start, end, interval)]
    else:
        indexlst = [i for i in range(start, num_frames, interval)]

    api.get_keyframe_text(video_path=video_path, indexlst = indexlst, lang='ch', outfile=keyframe_out_path)
