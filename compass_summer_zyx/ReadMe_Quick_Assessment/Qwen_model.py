'''
Descripttion: 包含类QwenModelDeployment
version: V1.0
Author: zyx
Date: 2024-09-20 09:10:36
LastEditors: zyx
LastEditTime: 2024-09-23 09:02:09
'''
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from prompt import prompt_case #prompt文档基本情况
import utils
import os
import time
from tqdm import tqdm

# 全局变量
MODEL_PATH = r"Qwen1.5-7B"
TRAIN_PATH_WONDERFUL = r"train/WONDERFUL"
TRAIN_PATH_ORDINARY = r"train/ORDINARY"
SAVE_PATH = r"save_path1"
SAVE_PATH1 = r"save_path2"
# 创建保存路径
if not os.path.exists(SAVE_PATH):
    os.mkdir(SAVE_PATH)
if not os.path.exists(SAVE_PATH1):
    os.mkdir(SAVE_PATH1)

# Qwen_model
class QwenModelDeployment:

    def __init__(self, model_path = MODEL_PATH):
        # 加载 tokenizer 和 模型
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.train_wonderful_data,self.train_ordinary_data = self.read_train_file()
        self.model.to(self.device)
        print("==================train_evaluate_readme_completeness==========================")
        self.train_evaluate_readme_completeness()
        print("==================train_evaluate_readme_definition==========================")
        self.train_evaluate_readme_definition()

    def generate_text(self, input_texts) -> str:
        '''调用模型函数，如果需要使用模型进行工作产生结果'''
        messages = []        
        for input_text in input_texts:
            dict1 = {"role": "user", "content": input_text}
            messages.append(dict1) 

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
            )

        # 编码输入
        inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        # 模型推理生成
        generated_ids = self.model.generate(
            inputs.input_ids, 
            max_new_tokens=512
        ).to(self.device)

        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        # 解码生成的文本
        generated_text = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text
    
    def read_train_file(self) -> dict:
        """
        读取训练集的readme
        :return: wonderful:["wonderful: readmexxx",..], ordinary:["ordinary: readmexxx",..]
        """
        wonderful = {}
        ordinary = {}
        

        #读取wonderful
        for file_dir in os.listdir(TRAIN_PATH_WONDERFUL):
            for file in os.listdir(os.path.join(TRAIN_PATH_WONDERFUL,file_dir)):
                wonderful["wonderful_"+file_dir] = "Please study the four key points just mentioned, Give a rating, and one of the wonderful documents is as follows: "+ utils.read_md_file(os.path.join(TRAIN_PATH_WONDERFUL,file_dir,file))+". Please give us a score for completeness"


        #读取ordinary
        for file_dir in os.listdir(TRAIN_PATH_ORDINARY):
            for file in os.listdir(os.path.join(TRAIN_PATH_ORDINARY,file_dir)):
                ordinary["ordinary"+file_dir] = "Please study the four key points just mentioned, Give a rating, and one of the ordinary documents are is follows:  "+ utils.read_md_file(os.path.join(TRAIN_PATH_ORDINARY,file_dir,file))+". Please give us a score for completeness"

        return wonderful,ordinary


    def train_evaluate_readme_completeness(self) -> list:
        """
        训练提供的 ReadMe 文档的完整性，返回最终的结果
        
        :param 
            readme_documents: 提供的 ReadMe 文档列表
            
        : return: 
            评分结果字典列表
        """
        prompt1 = prompt_case("completeness1")
        prompt2 = prompt_case("completeness2")
        prompt3 = prompt_case("completeness3")


        # 输入prompt评估基本步骤
        print("==========================输入prompt===============================\n")
        generated_text = self.generate_text([prompt1])
        #print(generated_text)
        generated_text = self.generate_text([prompt2])
        #print(generated_text)
        
        # 训练数据,调用生成函数，获取模型生成的评分结果
        print("========================== 训练数据,对比学习调用生成函数，获取模型生成的评分结果===============================\n")
        results = []
        # for (wonderful_name,wonderful),(ordinary_name,ordinary) in tqdm(zip(self.train_wonderful_data.items(),self.train_ordinary_data.items())):

        #     generated_text = self.generate_text([prompt2,wonderful])
        #     utils.save_markdown(generated_text,os.path.join(SAVE_PATH,wonderful_name+".md"))
        #     results.append(generated_text)

        #     generated_text = self.generate_text([prompt2,ordinary])
        #     utils.save_markdown(generated_text,os.path.join(SAVE_PATH,ordinary_name+".md"))
        #     results.append(generated_text)

        for (wonderful_name,wonderful),(ordinary_name,ordinary) in tqdm(zip(self.train_wonderful_data.items(),self.train_ordinary_data.items())):

            generated_text = self.generate_text([wonderful])
            utils.save_markdown(generated_text,os.path.join(SAVE_PATH1,wonderful_name+".md"))
            results.append(generated_text)

            generated_text = self.generate_text([ordinary])
            utils.save_markdown(generated_text,os.path.join(SAVE_PATH1,ordinary_name+".md"))
            results.append(generated_text)
        
        return results
    
    def evaluate_readme_completeness(self,readme_documents) -> list:
        """
        评估提供的 ReadMe 文档的完整性，返回最终的结果
        
        :param 
            readme_documents: 提供的 ReadMe 文档列表
            
        : return: 
            评分结果字典列表
        """

        prompt3 = prompt_case("completeness3")
        results = []
        for readme_name,readme in readme_documents.items():
            generated_text = self.generate_text([prompt3,readme])
            utils.save_markdown(generated_text,os.path.join(SAVE_PATH1,readme_name+".md"))
            results.append(generated_text)
        
        return results

    def train_evaluate_readme_definition(self):
        """
        评估提供的 ReadMe 文档，返回格式分数和语法拼写错误分数
        :param readme_documents: 提供的 ReadMe 文档列表
        :return: 评分结果字典列表
        """
        prompt1 = prompt_case("definition1")
        prompt2 = prompt_case("definition2")
        # prompt3 = prompt_case("definition3")


        # 输入prompt评估基本步骤
        print("==========================输入prompt===============================\n")
        generated_text = self.generate_text([prompt1])
        #print(generated_text)
        generated_text = self.generate_text([prompt2])
        #print(generated_text)
        
        # 训练数据,调用生成函数，获取模型生成的评分结果
        print("========================== 训练数据,对比学习调用生成函数，获取模型生成的评分结果===============================\n")
        results = []
        # for (wonderful_name,wonderful),(ordinary_name,ordinary) in tqdm(zip(self.train_wonderful_data.items(),self.train_ordinary_data.items())):

        #     generated_text = self.generate_text([prompt2,wonderful]s)
        #     utils.save_markdown(generated_text,os.path.join(SAVE_PATH,wonderful_name+".md"))
        #     results.append(generated_text)

        #     generated_text = self.generate_text([prompt2,ordinary])
        #     utils.save_markdown(generated_text,os.path.join(SAVE_PATH,ordinary_name+".md"))
        #     results.append(generated_text)

        for (wonderful_name,wonderful),(ordinary_name,ordinary) in tqdm(zip(self.train_wonderful_data.items(),self.train_ordinary_data.items())):

            generated_text = self.generate_text([wonderful])
            utils.save_markdown(generated_text,os.path.join(SAVE_PATH,wonderful_name+".md"))
            results.append(generated_text)

            generated_text = self.generate_text([ordinary])
            utils.save_markdown(generated_text,os.path.join(SAVE_PATH,ordinary_name+".md"))
            results.append(generated_text)
        
        return results
    
    def evaluate_readme_definition(self,readme_documents) -> list:
        """
        评估提供的 ReadMe 文档的完整性，返回最终的结果
        
        :param 
            readme_documents: 提供的 ReadMe 文档列表,dict
            
        : return: 
            评分结果字典列表
        """

        prompt3 = prompt_case("definition3")
        results = []
        for readme_name,readme in readme_documents.items():
            generated_text = self.generate_text([prompt3,readme])
            utils.save_markdown(generated_text,os.path.join(SAVE_PATH1,readme_name+".md"))
            results.append(generated_text)
        
        return results

# if __name__=="__main__":
#     a = QwenModelDeployment()
    # start = time.time()
    # text = a.generate_text("hello")
    # print(text)
    
    # # a.train_evaluate_readme_completeness()
    # print(time.time()-start)