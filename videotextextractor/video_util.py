# 封装 cv2.videocapture
import cv2


class Capture:
    def __init__(self, video_path):
        self.path = video_path

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.path)
        if not self.cap.isOpened():
            raise IOError('Can not open video {}.'.format(self.path))
        return self.cap

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()


# opencv交互式矩形框绘制

class Rect(object):
    def __init__(self):
        self.tl = (0, 0)
        self.br = (0, 0)

    def regularize(self):
        """
        make sure tl = TopLeft point, br = BottomRight point
        """
        pt1 = (min(self.tl[0], self.br[0]), min(self.tl[1], self.br[1]))
        pt2 = (max(self.tl[0], self.br[0]), max(self.tl[1], self.br[1]))
        self.tl = pt1
        self.br = pt2


class DrawRects(object):
    def __init__(self, image, color=(0, 255, 0), thickness=1):
        self.original_image = image
        self.image_for_show = image.copy()
        self.color = color
        self.thickness = thickness
        self.current_rect = Rect()
        self.left_button_down = False

    def refresh_image(self, img):
        self.image_for_show = img
        self.draw_current_rect()

    def shrink_point(self, x, y):
        """
        clip x, y in image boundary
        """
        height, width = self.image_for_show.shape[0:2]
        x_shrink = x if x > 0 else 0
        x_shrink = x_shrink if x_shrink < width else width
        y_shrink = y if y > 0 else 0
        y_shrink = y_shrink if y_shrink < height else height
        return (x_shrink, y_shrink)

    def reset_image(self):
        """
        reset image_for_show using original image
        """
        self.image_for_show = self.original_image.copy()

    def draw_current_rect(self):
        """
        draw current rect on image_for_show
        """
        cv2.rectangle(self.image_for_show,
                      self.current_rect.tl, self.current_rect.br,
                      color=self.color, thickness=self.thickness)


def onmouse_draw_rect(event, x, y, flags, draw_rects):
    if event == cv2.EVENT_LBUTTONDOWN:
        # pick first point of rect
        print('pt1: x = %d, y = %d' % (x, y))
        draw_rects.left_button_down = True
        draw_rects.current_rect.tl = (x, y)
    if draw_rects.left_button_down and event == cv2.EVENT_MOUSEMOVE:
        # pick second point of rect and draw current rect
        draw_rects.current_rect.br = draw_rects.shrink_point(x, y)
        draw_rects.reset_image()
        draw_rects.draw_current_rect()
    if event == cv2.EVENT_LBUTTONUP:
        # finish drawing current rect and append it to rects list
        draw_rects.left_button_down = False
        draw_rects.current_rect.br = draw_rects.shrink_point(x, y)
        print('pt2: x = %d, y = %d' % (draw_rects.current_rect.br[0],
                                       draw_rects.current_rect.br[1]))
        draw_rects.current_rect.regularize()


# 手动绘制subtitle_bound函数接口
def manual_cricumscribe_bound(video_path, start_frame=0, end_frame=None):
    subtitle_bound = None
    with Capture(video_path) as video_cap:
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        num_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if end_frame is None:
            end_frame = num_frames
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        frames = (video_cap.read()[1] for _ in range(start_frame, end_frame))   # 生成器
        first_frame = next(frames) 
        draw_rects = DrawRects(first_frame, (0, 255, 0), 2)
        cv2.namedWindow('subtitle_ocr')
        cv2.setMouseCallback('subtitle_ocr', onmouse_draw_rect, draw_rects)
        for frame in frames:
            cv2.imshow('subtitle_ocr', draw_rects.image_for_show)
            # draw_rects = DrawRects(frame, (0, 255, 0), 2)
            draw_rects.refresh_image(frame)
            k = cv2.waitKey(int(1000 / fps)) & 0xFF
            if k == ord('s'):   # press "s" 保存bound box并返回
                subtitle_bound = [list(draw_rects.current_rect.tl), list(draw_rects.current_rect.br)]
                break
    
    print("the subtitle boundary: ", subtitle_bound)
    cv2.destroyWindow('subtitle_ocr')
    return subtitle_bound


if __name__ == "__main__":     # test manual_cricumscribe
    video_path = "../videotest.mp4"
    manual_cricumscribe_bound(video_path)
