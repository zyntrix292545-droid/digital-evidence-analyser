import os
import uuid
from flask import Flask, request, jsonify, render_template, send_file

# 1. Import analyzer functions
from analyzer.metadata import extract_metadata
from analyzer.steganography import detect_steganography
from analyzer.report import generate_report

app = Flask(__name__)

# 2. Automatically create the "uploads/" folder on startup if it doesn't exist
UPLOAD_FOLDER = os.path.abspath('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ROUTE 1: GET /
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# ROUTE 2: POST /analyze
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    if file:
        # Save the file to the uploads/ folder with a unique name
        _, ext = os.path.splitext(file.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(filepath)
        
        # Run analyses
        metadata = extract_metadata(filepath)
        stego_results = detect_steganography(filepath)
        report_path = generate_report(filepath, metadata, stego_results)
        
        # Return JSON response
        return jsonify({
            "metadata": metadata,
            "steganography": stego_results,
            "report": report_path
        })

# ROUTE 3: GET /download/<path:filename>
@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    try:
        if not os.path.exists(filename):
            return jsonify({"error": "File not found"}), 404
        # Send the file as a downloadable attachment
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": "File not found"}), 404

# 4. Global error handler
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# 5. Run the app with debug=True on port 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)
