from videotextextractor import api

video_path = "test_data/video-test.mp4"
api.ocr(video_path)   #return json format string
