import base64
import dlib
import io
import math
import mediapipe as mp
import numpy as np
import os
import os
import pandas as pd
import random
import shutil
import sys
import gzip
import time
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import shutil
import constants
import main

shutil.rmtree(constants.hgvsg_folder_path)
shutil.rmtree(constants.temp_folder_path)
shutil.rmtree(constants.input_dir_path)
shutil.rmtree(constants.output_dir_path)


upload_folder = 'input/'
temp_folder = 'temp/'
output_folder = 'output/'
hgvs_folder = 'hgvsg/'

if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
if not os.path.exists(hgvs_folder):
    os.mkdir(hgvs_folder)

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_PATH'] = 10000000
app.secret_key = SECRET_KEY = os.urandom(28)

# configuring the allowed extensions
allowed_extensions = ['vcf', 'csv', 'txt']


def check_file_extension(filename):
    return filename.split('.')[-1] in allowed_extensions


# The path for uploading the file
@app.route('/')
def upload_file():
    return render_template('index.html', show_download=False, show_upload=True, show_loading=False)


# The path to about file
@app.route('/about')
def show_about():
    return render_template('about.html')


@app.route('/upload', methods=['GET', 'POST'])
def uploadfile():
    print("request received......")

    if request.method == 'POST':  # check if the method is post
        # request.form['file']
        files = request.files.getlist('files')  # get the file from the files object
        print(files)

        for f in files:
            print(f.filename)
            # Saving the file in the required destination
            if check_file_extension(f.filename):
                f.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))  # this will secure the file
            else:
                return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
                #sys.exit('Unsupported file extension')

            output = process_file(upload_folder)

            if output != 0:
                return render_template('index.html', show_download=True, show_upload=False, show_loading=False, show_error=False)  # Display this message after uploading
            else:
                return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)

    else:
        return render_template('index.html', show_download=False, show_upload=True, show_loading=False,  show_error=False)




def write_output(filename, data):
    with open(output_folder + filename + '_result', 'a') as f:
        f.write(data)


def process_file(upload_folder_path):
    main.main(upload_folder_path, constants.opts_options_array, website_mode=True)


def get_vcf_names(vcf_path):
    if vcf_path.endswith(".vcf.gz"):
        with gzip.open(vcf_path, "rt") as ifile:
            for line in ifile:
                if line.startswith("#CHROM"):
                    vcf_names = [x for x in line.split('\t')]
                    return vcf_names
        ifile.close()

    if vcf_path.endswith(".vcf"):
        with open(vcf_path, "rt") as ifile:
            for line in ifile:
                if line.startswith("#CHROM"):
                    vcf_names = [x for x in line.split('\t')]
                    return vcf_names
    else:
        vcf_names = 'wrong'  # id files like .DS_Store are present in the directory
        return vcf_names


def save_base64(base64_str):
    decoded_bytes = base64.b64decode(bytes(base64_str, "utf-8"))
    return np.frombuffer(decoded_bytes, dtype=np.uint8)

#Unknown...
#@app.route("/", methods=["GET"])
#def get_results():
#    return render_template('index.html', content="")


@app.route('/downloadhgvs')
def downloadFileHGVSg():
    # For windows you need to use drive name [ex: F:/Example.pdf]
    path = hgvs_folder + "outputHGVSg.csv"
    return send_file(path, as_attachment=True)


@app.route('/downloadclingen')
def downloadFileClingen():
    # For windows you need to use drive name [ex: F:/Example.pdf]

    path = output_folder + "outputClingen.csv"
    return send_file(path, as_attachment=True)


@app.route('/download')
def downloadFile():

    path = output_folder + "outputOMOP.csv"
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run()
