import os
import yaml
import glob
import time
import pytz
from pathlib import Path
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request

# Define paths
dir_path = os.path.dirname(os.path.realpath(__file__))

# Read config file
with open(os.path.join(dir_path, 'config.yaml'), 'r') as s:
    config = yaml.safe_load(s)

# Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(dir_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024

# Create upload directory
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

# Auth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username in config['users']:
        return True if config['users'][username].get('password') == password else False
    return False

@app.route('/status')
@auth.login_required
def upload_status():

    # Get specific account
    account = request.args.get('account')
    is_admin = config['users'][auth.username()].get('is_admin', False)
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], auth.username())
    if account and is_admin:
        if account in config['users']:
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], account)
        else:
            resp = jsonify({'message' : 'User does not exist'})
            resp.status_code = 404
            return resp
    else:
        account = auth.username()

    # Create upload directory
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    
    # Get last backup time
    datetime_format = '%d.%m.%Y %H:%M'
    datetime_tz = pytz.timezone(os.getenv('TZ', 'Europe/Oslo'))
    
    list_of_files = glob.glob(os.path.join(upload_dir, '*.tar'))
    if len(list_of_files) > 0:        
        latest_file = max(list_of_files, key=os.path.getmtime)
        last_backup = datetime.fromtimestamp(os.path.getmtime(latest_file),
                      tz = datetime_tz).replace(tzinfo=None).strftime(datetime_format)
    else:
        last_backup = '01.01.1970 00:00'
        
    # Calculate days ago since last backup
    backup_diff = datetime.now(datetime_tz).replace(tzinfo=None) - \
                  datetime.strptime(last_backup, datetime_format)

    # Return response
    json_resp =  {
        'account': account,
        'backups': len(list_of_files),
        'days_ago': backup_diff.days,
        'latest_backup': last_backup
    }
    
    resp = jsonify(json_resp)
    resp.status_code = 200
    return resp

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    # Make sure there is a file part
    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    
    # Make sure a file has been selected for upload
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
        
    # Make sure it is a tar file
    if file and (file.filename.endswith('.tar')):
        # Create upload directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], auth.username())
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, datetime.now().strftime('ha_backup_%Y%m%d_%H%M%S%f.tar'))       
        file.save(file_path)
        
        # Remove old files
        list_of_files = glob.glob(os.path.join(upload_dir, '*.tar'))
        list_of_files.sort(key=os.path.getmtime, reverse=True)
        for f in list_of_files[7:]:
            os.remove(os.path.join(upload_dir, f))
        
        # Discard files smaller than 10 bytes
        file_size = Path(file_path).stat().st_size
        if file_size < 10:
            os.remove(file_path)
            resp = jsonify({'message' : 'File could not be uploaded'})
            resp.status_code = 400
            return resp

        # Return response
        resp = jsonify({'message' : 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
    
        # Return response
        resp = jsonify({'message' : 'File format not supported'})
        resp.status_code = 400
        return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)