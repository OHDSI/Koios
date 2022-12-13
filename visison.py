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
import traceback
import smtplib



shutil.rmtree(c.hgvsg_folder_path)
shutil.rmtree(c.temp_folder_path)
#shutil.rmtree(c.input_dir_path)
#shutil.rmtree(c.output_dir_path)

hgvs_folder = c.hgvsg_folder_path
temp_folder = c.temp_folder_path
upload_folder = c.input_dir_path
output_folder = c.output_dir_path
userinfo_folder = c.user_info_path


# Get environment variables
gmail_user = os.getenv('GMAIL_USER')
gmail_password = os.environ.get('GMAIL_PASSWORD')

# configuring the allowed extensions
allowed_extensions = ['vcf', 'csv', 'txt']

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

app.secret_key = SECRET_KEY = os.urandom(32)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "memcached"
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_PATH'] = 10000000
#@app.before_request
#def clear_session():
#    session.permanent=True
#    session.clear()


def configure_app():
    symbols = string.ascii_letters


    if not "RNDUSERSTR" in session:
        session["RNDUSERSTR"] = ''.join(random.choice(symbols) for i in range(10)) 
        print("created random user substring: ", session["RNDUSERSTR"])
    else:
        print("reused random user substring: ", session["RNDUSERSTR"])

    #if not os.path.exists(upload_folder):
    #    os.mkdir(upload_folder)

    if not os.path.exists(upload_folder + session["RNDUSERSTR"]):
        os.mkdir(upload_folder + session["RNDUSERSTR"])

    if not os.path.exists(userinfo_folder):
        os.mkdir(userinfo_folder)

    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    #if not os.path.exists(output_folder):
    #    os.mkdir(output_folder)     

    if not os.path.exists(output_folder + session["RNDUSERSTR"]):
        os.mkdir(output_folder + session["RNDUSERSTR"])

    if not os.path.exists(userinfo_folder + session["RNDUSERSTR"]):
        os.mkdir(userinfo_folder + session["RNDUSERSTR"])

    if not os.path.exists(hgvs_folder):
        os.mkdir(hgvs_folder)

    input_archive_user = os.path.join(c.input_old_path, c.input_dir) + session["RNDUSERSTR"] + "/"
    output_archive_user = os.path.join(c.export_dir_path, c.output_dir) + session["RNDUSERSTR"] + "/"

    if not os.path.exists(input_archive_user):
        os.mkdir(input_archive_user)

    if not os.path.exists(output_archive_user):
        os.mkdir(output_archive_user)


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


def send_email(user_name, user_email, user_organization, user_comments):
    sent_from = gmail_user
    to = [gmail_user]
    subject = 'Message from KOIOS user'
    body = ""
    body = body + "User info:\r\n\r\n"
    body = body + "NAME AND SURNAME:\r\n"
    body = body + user_name + "\r\n"
    body = body + "EMAIL:\r\n"
    body = body + user_email + "\r\n"
    body = body + "ORGANIZATION:\r\n"
    body = body + user_organization + "\r\n"
    body = body + "QUESTIONS AND COMMENTS:\r\n"
    body = body + user_comments

    email_text = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
    except Exception as e:
        print(e)
        print('Something went wrong at the send_email step...')

def save_user_info(user_name, user_email, user_organization, user_comments):
    userfile_name = userinfo_folder + session["RNDUSERSTR"] + "/user_info.txt"
    with open(userfile_name, 'w') as f:
        f.write("NAME AND SURNAME:\n")
        f.write(user_name + "\n")
        f.write("EMAIL:\n")
        f.write(user_email + "\n")
        f.write("ORGANIZATION:\n")
        f.write(user_organization + "\n")
        f.write("QUESTIONS AND COMMENTS:\n")
        f.write(user_comments.replace("\r","") + "\n")

@app.route('/upload', methods=['GET', 'POST'])
def uploadfile():
    print("request received......")
    configure_app()

    user_upload_folder = upload_folder + session["RNDUSERSTR"] + "/"
    user_output_folder = output_folder + session["RNDUSERSTR"] + "/"
    input_archive_user = os.path.join(c.input_old_path, c.input_dir) + session["RNDUSERSTR"] + "/"
    output_archive_user = os.path.join(c.export_dir_path, c.output_dir) + session["RNDUSERSTR"] + "/"

    if request.method == 'POST':  # check if the method is post
        #print(str(request.form))
        user_name = request.form['user_name']
        user_email = request.form['user_email']
        user_organization = request.form['user_organization']
        user_comments = request.form['user_comments']
        save_user_info(user_name, user_email, user_organization, user_comments)

        send_email(user_name, user_email, user_organization, user_comments)
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
                    os.path.join(user_upload_folder, secure_filename(f.filename)))  # this will secure the file
            else:
                
                return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)
                #sys.exit('Unsupported file extension')

            fname = f.filename.replace(' ', '_')

            try:
                output = process_file(fname)
            except Exception as e:
                print("SOMETHING WRONG")
                print(str(traceback.format_exc()))
                os.remove(os.path.join(user_upload_folder, fname))
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



                for filename in os.listdir(user_upload_folder):
                    os.rename(user_upload_folder+filename, user_upload_folder+random_file_substring_session+'_'+filename)

                for filename in os.listdir(user_output_folder):
                    os.rename(user_output_folder+filename, user_output_folder+random_file_substring_session+'_'+filename)

                move.move_old_input_files(user_upload_folder, input_archive_user)
                move.move_old_input_files(user_output_folder, output_archive_user)
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
    if "RNDUSERSTR" in session:
        input_archive_user = os.path.join(c.input_old_path, c.input_dir) + session["RNDUSERSTR"] + "/"
        output_archive_user = os.path.join(c.export_dir_path, c.output_dir) + session["RNDUSERSTR"] + "/"

        path = output_archive_user + "outputClingen_" + session["RNDUSERSTR"] + ".csv"
        return send_file(path, as_attachment=True)
    else:
        # redirect to start page
        return None


def get_current_postfix():
    input_archive_user = os.path.join(c.input_old_path, c.input_dir) + session["RNDUSERSTR"] + "/"
    output_archive_user = os.path.join(c.export_dir_path, c.output_dir) + session["RNDUSERSTR"] + "/"

    input_files = os.listdir(input_archive_user)
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
    # For windows you need to use drive name [ex: F:/Example.pdf]
    current_postfix = get_current_postfix()
    print(current_postfix)
    #substr = "outputOMOP_"
    input_archive_user = os.path.join(c.input_old_path, c.input_dir) + session["RNDUSERSTR"] + "/"
    output_archive_user = os.path.join(c.export_dir_path, c.output_dir) + session["RNDUSERSTR"] + "/"

    output_files = os.listdir(output_archive_user)
    print(output_files)
    for f in output_files:
        print(f)
        if f.endswith('.csv') and 'OMOP' in f and str(current_postfix) in f:
            path = output_archive_user + f
            return send_file(path, as_attachment=True)
            
    return render_template('index.html', show_download=False, show_upload=False, show_loading=False, show_error=True)



@app.route('/download_archive')
def downloadFileArchive():
    input_archive_user = os.path.join(c.input_old_path, c.input_dir) + session["RNDUSERSTR"] + "/"
    output_archive_user = os.path.join(c.export_dir_path, c.output_dir) + session["RNDUSERSTR"] + "/"

    target = output_archive_user

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
