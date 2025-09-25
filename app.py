from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from knowledge_base import import_pdfs, query_knowledge, ask_question

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = './pdfs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "未选择文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 处理上传的PDF
        from knowledge_base import process_pdf, init_vectorstore
        vectorstore = init_vectorstore()
        success, message = process_pdf(file_path, vectorstore)
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 500
    
    return jsonify({"error": "无效文件类型"}), 400

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    mode = data.get('mode', 'vector')  # vector 或 llm
    
    if not query:
        return jsonify({"error": "查询内容为空"}), 400
    
    if mode == 'llm':
        result = ask_question(query)
        return jsonify(result)
    else:
        results = query_knowledge(query)
        return jsonify({"results": results})

@app.route('/batch_import', methods=['POST'])
def batch_import():
    results = import_pdfs()
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)