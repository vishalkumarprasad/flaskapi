import io
import zipfile

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import time
from werkzeug.utils import secure_filename
from validator.main import wrapper_validator

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'validator/conf'
app.config['DOWNLOAD_FOLDER'] = 'validator/report'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    if 'old_log' not in request.files or 'new_log' not in request.files:
        return jsonify(success=False, message='No file part')

    old_log = request.files['old_log']
    new_log = request.files['new_log']
    comparison_options = request.form['comparison_options']
    gv_exchange = request.form.get('gvExchange')
    gv_market = request.form.get('gvmarket')
    gv_memo_content = request.form.get('gvmemocontent')
    gv_exception_list = request.form.get('gvExceptionList')

    if old_log.filename == '' or new_log.filename == '':
        return jsonify(success=False, message='No selected file')

    old_log_filename = secure_filename(old_log.filename)
    new_log_filename = secure_filename(new_log.filename)
    old_log_path = os.path.join(app.config['UPLOAD_FOLDER'], old_log_filename)
    new_log_path = os.path.join(app.config['UPLOAD_FOLDER'], new_log_filename)
    old_log.save(old_log_path)
    new_log.save(new_log_path)

    # Simulate processing time
    time.sleep(2)

    # Compare the logs and generate the report
    wrapper_validator(vftype=comparison_options,
                      gvP10_file1=old_log_filename,
                      gvP10_file2=new_log_filename,
                      gvExchange=gv_exchange,
                      gvmarket=gv_market,
                      gvmemocontent=gv_memo_content,
                      gvExceptionList=gv_exception_list)



    # Prepare the download URL
    download_url = url_for('download_reports')

    # Delete the input files
    os.remove(old_log_path)
    os.remove(new_log_path)

    return jsonify(success=True, download_url=download_url)


@app.route('/download')
def download_reports():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer,'w', zipfile.ZIP_DEFLATED) as zip_files:
        for filename in os.listdir(app.config['DOWNLOAD_FOLDER']):
            file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            zip_files.write(file_path,filename)

    zip_buffer.seek(0)
    # Delete the report after sending
    for filename in os.listdir(app.config['DOWNLOAD_FOLDER']):
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        os.remove(file_path)

    # Send zip file as a download
    return send_file(zip_buffer, as_attachment=True, download_name='All_reports.zip', mimetype= 'appliaction/zip')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4000, debug=True)