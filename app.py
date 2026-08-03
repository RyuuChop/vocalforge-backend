import os
import subprocess
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'separated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "VocalForge AI Server Active!"})

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        cmd = f'demucs -n htdemucs --two-stems=vocals "{file_path}" -o "{OUTPUT_FOLDER}"'
        subprocess.run(cmd, shell=True, check=True)

        track_name = os.path.splitext(filename)[0]
        
        return jsonify({
            'status': 'success',
            'vocals': f'/download/{track_name}/vocals.wav',
            'bgm': f'/download/{track_name}/no_vocals.wav'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<track_name>/<stem_type>', methods=['GET'])
def download_stem(track_name, stem_type):
    folder = os.path.join(OUTPUT_FOLDER, "htdemucs", track_name)
    return send_from_directory(folder, stem_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
