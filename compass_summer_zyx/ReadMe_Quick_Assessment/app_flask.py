'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-09-20 08:52:51
LastEditors: zyx
LastEditTime: 2024-09-23 08:28:36
'''
from flask import Flask, request, jsonify
from Qwen_model import QwenModelDeployment
import time
# 初始化 Flask app
app = Flask(__name__)

# 实例化部署类，模型路径为 "Qwen-1.5-7B"
model_deployment = QwenModelDeployment("Qwen1.5-7B")

# 定义路由，用于处理文本生成的请求
@app.route('/generate', methods=['POST'])
def generate():
    '''调用模型请求'''
    data = request.json
    input_text = data.get("input_text", "")
    
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400
    
    try:
        # 调用模型生成文本
        generated_text = model_deployment.generate_text(input_text)
        return jsonify({"generated_text": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


# 定义路由，用于处理 ReadMe 文档的评分请求
@app.route('/evaluate_readme_completeness', methods=['POST'])
def evaluate_readme_completeness():
    '''文档评估请求'''
    data = request.json
    readme_documents = data.get("readme_documents", [])
    
    if not readme_documents or not isinstance(readme_documents, dict):
        return jsonify({"error": "No valid ReadMe documents provided"}), 400
    
    try:
        # 调用模型评估 ReadMe 文档
        results = model_deployment.evaluate_readme_completeness(readme_documents)
        return jsonify({"evaluation_results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 定义路由，用于处理 ReadMe 文档的评分请求
@app.route('/evaluate_readme_definition', methods=['POST'])
def evaluate_readme_definition():
    '''文档评估请求'''
    data = request.json
    readme_documents = data.get("readme_documents", [])
    
    if not readme_documents or not isinstance(readme_documents, dict):
        return jsonify({"error": "No valid ReadMe documents provided"}), 400
    
    try:
        # 调用模型评估 ReadMe 文档
        results = model_deployment.evaluate_readme_definition(readme_documents)
        return jsonify({"evaluation_results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 启动服务
if __name__ == '__main__':
    # start = time.time()
    app.run(host='0.0.0.0', port=5000)
    #print(time.time()-start)
