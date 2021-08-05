import getopt
import cv2
import os
import sys
import time

def frame_read(video_path, interval=1, start=0, end=None, save_path=None):
    if save_path == None:
        save_path = os.path.splitext(video_path)[0] + "_frames"

    if not os.path.exists(save_path):
        os.mkdir(save_path)
        print('make savafile:', save_path)
    if start < 0:
        start = 0
    if interval < 1:
        interval = 1
    # 图像帧读取索引记录
    read_index = start
    # 开始读视频
    videoCapture = cv2.VideoCapture(video_path)
    frames_num = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
    if end == None or end < 0 or end > frames_num:
        end = frames_num
    
    while read_index < end:
        videoCapture.set(cv2.CAP_PROP_POS_FRAMES, read_index)
        success, frame = videoCapture.read()
        if success:
            # 保存图片
            savedname = 'frame-' + str(read_index) + '.jpg'
            cv2.imwrite(os.path.join(save_path, savedname), frame)
            print('image of %s is saved' % (savedname))
        
        read_index += interval

    print("all frame saved!")
    videoCapture.release()
    time.sleep(2)
    return

if __name__ == "__main__":
    video_path = None
    start = 0
    end = None
    interval = 1
    save_path = None

    argv = sys.argv[1:]
 
    try:
        opts, args = getopt.getopt(argv, "v:o:s:i:e:", ["video_dir=","out_dir=","start=","interval=","end="])  # 长选项模式
    except:
        print("Error")
 
    for opt, arg in opts:
        if opt in ['-v', '--video_dir']:
            video_path = arg
        elif opt in ['-o', '--out_dir']:
            save_path = arg
        elif opt in ['-s', '--start']:
            start = int(arg)
        elif opt in ['-i', '--interval']:
            interval = int(arg)
        elif opt in ['-e', '--end']:
            end = int(arg)
    
    if video_path == None:
        print("please input video path")
    frame_read(video_path, interval, start, end, save_path)

            
