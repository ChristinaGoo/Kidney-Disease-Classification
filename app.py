from flask import Flask, jsonify, render_template, request
import os
from flask_cors import CORS, cross_origin
from cnnClassifier.utils.common import decodeImage
from cnnClassifier.pipeline.prediction import PredictionPipeline


# some libs (base64/image decoding) behave inconsistently without an explicit UTF-8 locale
os.putenv("LANG", "en_US.UTF-8")
os.putenv("LC_ALL", "en_US.UTF-8")

app = Flask(__name__)
CORS(app)


class ClientApp:
    # fixed filename incoming images get decoded to, plus the prediction pipeline that reads it
    def __init__(self):
        self.filename = "inputImage.jpg"
        self.classifier = PredictionPipeline(self.filename)


# module-level so it exists under any WSGI server, not just `python app.py`
clApp = ClientApp()

@app.route("/", methods=["GET"])
@cross_origin()
def home():
    # serves the upload/predict UI (template/index.html)
    return render_template("index.html")


@app.route("/train", methods=["GET", "POST"])
@cross_origin()
def trainRoute():
    #os.system("python main.py")
    # reruns the DVC pipeline; only stages whose deps/params actually changed get re-executed
    os.system("dvc repro")
    return "Training completed successfully!"

@app.route("/predict", methods=["POST"])
@cross_origin()
def predictRoute():
    # request body carries the image as base64; decode it to clApp.filename, then classify it
    image = request.json["image"]
    decodeImage(image, clApp.filename)
    result = clApp.classifier.predict()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) #for AWS deployment