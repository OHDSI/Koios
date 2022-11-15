import base64
import numpy as np
import os
from glob import glob
import gzip
import time
from flask import Flask, render_template, request, send_file, session
from werkzeug.utils import secure_filename
import shutil
import app.constants as c
import app.main as app_main
import app.move_old_files as move
import re
import string
import random
from io import BytesIO
from zipfile import ZipFile


shutil.rmtree(c.hgvsg_folder_path)
shutil.rmtree(c.temp_folder_path)
shutil.rmtree(c.input_dir_path)
shutil.rmtree(c.output_dir_path)

hgvs_folder = c.hgvsg_folder_path
temp_folder = c.temp_folder_path
upload_folder = c.input_dir_path
output_folder = c.output_dir_path

# configuring the allowed extensions
allowed_extensions = ['vcf', 'csv', 'txt']

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_PATH'] = 10000000
app.secret_key = SECRET_KEY = os.urandom(28)

@app.before_request
def clear_session():
    session.permanent=True
    session.clear()



def configure_app():
    if not os.path.exists(upload_folder):
        os.mkdir(upload_folder)
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    if not os.path.exists(hgvs_folder):
        os.mkdir(hgvs_folder)


def check_file_extension(filename):
    return filename.split('.')[-1] in allowed_extensions


# The path for uploading the file
@app.route('/')
def upload_file():
    configure_app()
    return render_template('index.html', show_download=False, show_upload=True, show_loading=False)


# The path to about file
@app.route('/about')
def show_about():
    return render_template('about.html')


@app.route('/upload', methods=['GET', 'POST'])
def uploadfile():
    print("request received......")
    configure_app()

    if request.method == 'POST':  # check if the method is post
        # request.form['file']
        files = request.files.getlist('files')  # get the file from the files object
        n_files = len(files)
        count_files = 0
        count_success_outputs = 0
        print(files)

        for f in files:
            if not os.path.exists(hgvs_folder):
                os.mkdir(hgvs_folder)
            if not os.path.exists(temp_folder):
                os.mkdir(temp_folder)

            print(f.filename)
            # Saving the file in the required destination
            if check_file_extension(f.filename):
                f.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))  # this will secure the file
            else:
                return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
                #sys.exit('Unsupported file extension')

            fname = f.filename.replace(' ', '_')

            try:
                output = process_file(fname)
            except:
                os.remove(os.path.join(upload_folder,fname))
                return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)


            shutil.rmtree(hgvs_folder)
            shutil.rmtree(temp_folder)


            if output != 0:
                count_success_outputs+=1
            count_files+=1

            if count_files==n_files:

                session_postfix = string.ascii_letters
                #random_file_substring_session = ''.join(random.choice(session_postfix) for i in range(5))
                current_time_str = str(time.time())
                random_file_substring_session = re.findall('(\d+)\.',current_time_str)[0]



                for filename in os.listdir(upload_folder):
                    os.rename(upload_folder+filename, upload_folder+random_file_substring_session+'_'+filename)

                for filename in os.listdir(output_folder):
                    os.rename(output_folder+filename, output_folder+random_file_substring_session+'_'+filename)

                move.move_old_input_files(upload_folder, c.input_archive_user)
                move.move_old_input_files(output_folder, c.output_archive_user)
                #shutil.move(user_output_folder, c.export_dir_path)

                #delete_temp_directories(c.project_dir)
                del_paths = glob(os.path.join(c.project_dir, 'input_*'))
                print(del_paths)
                for del_path in del_paths:
                    shutil.rmtree(del_path)

                del_paths_2 = glob(os.path.join(c.project_dir, 'output_*'))
                for del_path2 in del_paths_2:
                    shutil.rmtree(del_path2)


                current_postfix = get_current_postfix()
                print('current post ', current_postfix)

                if count_success_outputs != 0:
                    return render_template('index.html', show_download=True, show_upload=False, show_loading=False, show_error=False)  # Display this message after uploading
                else:
                    return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
    else:
        return render_template('index.html', show_download=False, show_upload=True, show_loading=False,  show_error=False)


def get_next_file(file_name, dest_dir):
    dest = os.path.join(dest_dir, file_name)
    num = 0

    while os.path.exists(dest):
        num += 1

        period = file_name.rfind('.')
        if period == -1:
            period = len(file_name)

        new_file = f'{file_name[:period]}({num}){file_name[period:]}'

        dest = os.path.join(dest_dir, new_file)

    return dest

def delete_temp_directories(current_dir):
    for directory in os.listdir(current_dir) :
        if re.fullmatch('.*input_.*',directory):
            shutil.rmtree(directory)
    for directory in os.listdir(current_dir) :
        if re.fullmatch('.*output_.*',directory):
            shutil.rmtree(directory)


def write_output(filename, data):
    with open(output_folder + filename + '_result', 'a') as f:
        f.write(data)


def process_file(upload_folder_path):
    app_main.main(upload_folder_path, c.opts_options_array, website_mode=True)



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


'''
@app.route('/downloadhgvs')
def downloadFileHGVSg():
    # For windows you need to use drive name [ex: F:/Example.pdf]
    path = hgvs_folder + "outputHGVSg.csv"
    return send_file(path, as_attachment=True)
'''


@app.route('/downloadclingen')
def downloadFileClingen():
    # For windows you need to use drive name [ex: F:/Example.pdf]

    path = c.output_archive_user + "outputClingen_" +c.random_user_substring + ".csv"
    return send_file(path, as_attachment=True)


def get_current_postfix():
    input_files = os.listdir(c.input_archive_user)
    current_time_str = str(time.time())
    currently = re.findall('(\d+)\.',current_time_str)[0]


    print('current ', currently)
    time_diffs = []
    for f in input_files:
        print(f)
        if f.endswith('.vcf') or f.endswith('.txt') or f.endswith('.csv') or f.endswith('.xml'):
            timest = re.findall(r'(\d+)', f)[0]
            print(timest)
            dif = int(currently) - int(timest)
            time_diffs.append(dif)
            print('time dif ', dif)


    print(time_diffs)
    min_time_diff = min(time_diffs)
    index_min = time_diffs.index(min_time_diff)

    return(re.findall(r'(\d+)', input_files[index_min])[0])



@app.route('/download')
def downloadFile():
    current_postfix = get_current_postfix()
    print(current_postfix)
    #substr = "outputOMOP_"
    output_files = os.listdir(c.output_archive_user)
    print(output_files)
    for f in output_files:
        print(f)
        if f.endswith('.csv') and 'OMOP' in f and str(current_postfix) in f:
            path = c.output_archive_user + f
            return send_file(path, as_attachment=True)

    return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)



@app.route('/download_archive')
def downloadFileArchive():

    target = c.output_archive_user

    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        for file in glob(os.path.join(target, '*outputOMOP*.csv')):
            zf.write(file, os.path.basename(file))
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        attachment_filename='archive.zip'
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
