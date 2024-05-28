from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def compare_logs(old_log_path, new_log_path):
    with open(old_log_path, 'r') as f1, open(new_log_path, 'r') as f2:
        old_log_lines = f1.readlines()
        new_log_lines = f2.readlines()

    report_lines = []
    for line in old_log_lines:
        if line not in new_log_lines:
            report_lines.append(f"- {line}")

    for line in new_log_lines:
        if line not in old_log_lines:
            report_lines.append(f"+ {line}")

    return report_lines


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit_form():
    if 'old_log' not in request.files or 'new_log' not in request.files:
        return jsonify(success=False, message='No file part')

    old_log = request.files['old_log']
    new_log = request.files['new_log']
    comparison = request.form['comparison']

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
    report_lines = compare_logs(old_log_path, new_log_path)
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], 'comparison_report.txt')
    with open(report_path, 'w') as report_file:
        report_file.writelines(report_lines)


    return_file = wrapper_validator(vftype, mkdfk, dfm, sdmf, dfm, dsfm)

    # Prepare the download URL
    download_url = url_for('download_report', filename='comparison_report.txt')

    # Delete the input files
    os.remove(old_log_path)
    os.remove(new_log_path)

    return jsonify(success=True, download_url=download_url)


@app.route('/download/<filename>')
def download_report(filename):
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    response = send_file(report_path, as_attachment=True, download_name=filename, mimetype='text/plain')

    # Delete the report after sending
    os.remove(report_path)

    return response


if __name__ == '__main__':
    app.run(debug=True)
