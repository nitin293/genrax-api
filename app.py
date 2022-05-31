from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import re
import requests
from genrax import predict

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
MODEL_PATH = 'genrax/models/model.h5'
SHAPE = (130, 20)

ALLOWED_EXTENSIONS = set(["wav", "mp3"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validateURL(url):
    valid = True

    if url:
        if re.findall("(^http[s]*://|^ftp[s]*://|^sftp://|^scp://)", url):
            if re.findall("(.mp3$|.wav$)", url):
                return valid

    else:
        valid = False
        return valid

def download(url, filename):
    response = requests.get(url)

    if response.status_code==200:
        data = response.content

        file = open(filename, "wb")
        file.write(data)
        file.close()


@app.route('/file-upload', methods=['POST'])
def fileAPI_says():

    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400

        return resp

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        uploaded_file = f"{UPLOAD_FOLDER}/{filename}"

        resp = {
            'message': 'File successfully uploaded',
            'status code': 200
        }

        resp["label"] = predict.predict(FILE_PATH=uploaded_file, MODEL_PATH=MODEL_PATH, SHAPE=SHAPE)
        os.remove(uploaded_file)
        resp = jsonify(resp)

        return resp

    else:
        resp = jsonify({'message': 'Allowed file types are wav, mp3'})
        resp.status_code = 400

        return resp


@app.route('/url-upload', methods=['POST'])
def urlAPI_says():

    if "url" in request.form.keys():
        url = request.form.get('url')

        if not url:
            resp = {
                "message": "no url specifies",
                "status code": 400
            }


        else:
            valid_url = validateURL(url)

            if valid_url:
                filename = url.split('/')[-1]

                outfile = f"{UPLOAD_FOLDER}/{filename}"
                download(url=url, filename=outfile)

                resp = {
                    'url': url,
                    'status code': 200
                }

                resp["label"] = predict.predict(FILE_PATH=outfile, MODEL_PATH=MODEL_PATH, SHAPE=SHAPE)
                os.remove(outfile)

            else:
                resp = {
                    "message": "Invalid music url",
                    "status code": 400
                }


    else:
        resp = {
            "message": "invalid parameter",
            "status code": 400
        }


    resp = jsonify(resp)

    return resp



@app.route('/')
def main():
    return render_template(["index.html"])



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

