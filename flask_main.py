from videotextextractor import api
import os
#import argparse
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from werkzeug.datastructures import FileStorage


def creat_app():
    app = Flask(__name__)
    api = Api(app)
    #接口路由
    api.add_resource(VideoText, "/video_text", endpoint="video_text")
    return app

class VideoText(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("video", type=FileStorage, required=True, location="files")
        self.parser.add_argument("lang", default='ch', type=str)

    @classmethod
    def main_func(cls, videoPath, lang):
        #dirName = os.path.dirname(videoPath)
        res = api.ocr(videoPath, lang)
        return res

    def post(self):
        args = self.parser.parse_args()
        video = args["video"]
        videoPath = os.path.join("input/video/", video.filename)
        video.save(videoPath)
        
        res = self.main_func(videoPath, args["lang"])
        return jsonify(res)


if __name__ == "__main__":
    app = creat_app()
    CORS(app)
    app.config['JSON_AS_ASCII'] = False
    app.run(host="0.0.0.0", port=5555, debug=True)


