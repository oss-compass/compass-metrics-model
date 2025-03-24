import os

import re
from utils_code_readability import load_json,check_github_gitee,clone_repo,save_json

from utils_code_readability import save_json,JSON_BASEPATH,TMP_PATH
BASEPATH = TMP_PATH

# Define comment syntax for different languages
COMMENT_SYNTAX = {
    'python': '#',
    'java': '//',
    'c': '//',
    'cpp': '//',
    'javascript': '//',
    'ruby': '#',
    'perl': '#',
    'shell': '#',
    'r': '#',
    'php': '//',
    'go': '//'
}

MULTILINE_COMMENT_SYNTAX = {
    'python': ('"""', '"""'),
    'java': ('/*', '*/'),
    'c': ('/*', '*/'),
    'cpp': ('/*', '*/'),
    'javascript': ('/*', '*/'),
    'ruby': ('=begin', '=end'),
    'perl': ('=pod', '=cut'),
    'php': ('/*', '*/'),
    'go': ('/*', '*/')
}

def detect_language(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension in ['.py']:
        return 'python'
    elif extension in ['.java']:
        return 'java'
    elif extension in ['.c']:
        return 'c'
    elif extension in ['.cpp', '.cc', '.cxx']:
        return 'cpp'
    elif extension in ['.js']:
        return 'javascript'
    elif extension in ['.rb']:
        return 'ruby'
    elif extension in ['.pl']:
        return 'perl'
    elif extension in ['.sh']:
        return 'shell'
    elif extension in ['.r']:
        return 'r'
    elif extension in ['.php']:
        return 'php'
    elif extension in ['.go']:
        return 'go'
    else:
        return None

def calculate_comment_ratio(file_path, comment_syntax):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        total_lines = len(lines)
        comment_lines = sum(1 for line in lines if comment_syntax in line.strip())
        
        # Handle multiline comments
        language = detect_language(file_path)
        if language in MULTILINE_COMMENT_SYNTAX:
            start_syntax, end_syntax = MULTILINE_COMMENT_SYNTAX[language]
            in_multiline_comment = False
            for line in lines:
                stripped_line = line.strip()
                if in_multiline_comment:
                    comment_lines += 1
                    #多行注释的结束
                    if end_syntax in stripped_line:
                        in_multiline_comment = False
                #使用多行注释符号包裹的单行注释
                elif start_syntax in stripped_line and end_syntax in stripped_line:
                    comment_lines += 1
                #多行注释的开始
                elif start_syntax in stripped_line and end_syntax not in stripped_line:
                    in_multiline_comment = True
                    comment_lines += 1
        
        comment_ratio = (comment_lines / total_lines) * 100 if total_lines > 0 else 0
        return comment_ratio,comment_lines,total_lines

def is_modular(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        function_count = 0
        class_count = 0
        language = detect_language(file_path)
        
        if language in ['python', 'ruby', 'perl', 'shell', 'r']:
            function_syntax = 'def '
            class_syntax = 'class '
        elif language in ['java', 'javascript', 'php', 'go']:
            function_syntax = 'function' if language == 'javascript' else 'def '
            class_syntax = 'class '
        elif language in ['c', 'cpp']:
            function_syntax = re.compile(r'\w+\s+\w+\s*\([^)]*\)\s*{')
            class_syntax = 'class '
        
        for line in lines:
            stripped_line = line.strip()
            if language in ['c', 'cpp']:
                if function_syntax.search(stripped_line):
                    function_count += 1
                if class_syntax in stripped_line:
                    class_count += 1
                continue

            if stripped_line.startswith(function_syntax):
                function_count += 1
            if stripped_line.startswith(class_syntax):
                class_count += 1
            
        
        return function_count, class_count


def calculate_code_features(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())

        avg_line_numbers = sum(len(line.split(' ')) for line in lines) / total_lines if total_lines > 0 else 0
        
        identifiers = []
        keywords = []
        identifier_pattern = re.compile(r'\b[A-Za-z_]\w*\b')
        keyword_pattern = re.compile(r'\b(def|class|if|else|elif|for|while|return|import|from|as|try|except|finally|with|yield|lambda|global|nonlocal|assert|break|continue|pass|raise|del|and|or|not|is|in|True|False|None)\b')
        
        for line in lines:
            identifiers.extend(identifier_pattern.findall(line))
            keywords.extend(keyword_pattern.findall(line))
        
        avg_identifier_length = sum(len(identifier) for identifier in identifiers) / len(identifiers) if identifiers else 0
        identifier_word_ratio = sum(1 for identifier in identifiers if identifier.isalpha()) / len(identifiers) if identifiers else 0
        keyword_frequency = len(keywords) / total_lines if total_lines > 0 else 0
        avg_identifiers_per_line = len(identifiers) / total_lines if total_lines > 0 else 0
        
        return {
            'blank_lines': blank_lines,
            'avg_line_word_numbers': avg_line_numbers,
            'avg_identifier_length': avg_identifier_length,
            'total_lines': total_lines,
            'identifier_word_ratio': identifier_word_ratio,
            'keyword_frequency': keyword_frequency,
            'avg_identifiers_per_line': avg_identifiers_per_line,

        }

def evaluate_code_readability1(url):
    '''
    Description: Evaluate code readability of all files in a directory. 
    Args:
        directory_path (str): Path to the directory containing files to evaluate.
        
    Returns:
        list: List of dictionaries containing the evaluation results for each file.
    '''
    repo_name = os.path.basename(url)
    
    if repo_name not in os.listdir(BASEPATH):
        print(f"Cloning {repo_name} repository...")
        clone_repo(url)
    directory_path = os.path.join(BASEPATH, repo_name)

    ans ={"evaluate_code_readability":0,"detail":[]}
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)

            language = detect_language(file_path)
            if language is None:
                continue
            
            comment_syntax = COMMENT_SYNTAX[language]
            comment_ratio, comment_lines, total_lines = calculate_comment_ratio(file_path, comment_syntax)
            modular = is_modular(file_path)
            code_features = calculate_code_features(file_path)
            
            res = {
                'File': os.path.join(os.path.basename(directory_path), file_path.replace(directory_path + '\\', '')),
                'Language': language,
                'Comment': {
                    'comment_ratio': comment_ratio,
                    'comment_lines': comment_lines,
                    'total_lines': total_lines,
                },
                'Is Modular': {
                    "function_count": modular[0],
                    "class_count": modular[1]
                }
            }
            res.update(code_features)
            ans['detail'].append(res)
            if "avg_line_word_numbers" in res.keys():
                ans['evaluate_code_readability'] += comment_ratio/0.5*100 + res['avg_line_word_numbers']/100 + res['avg_identifier_length']/10 + res['identifier_word_ratio']*100 + res['keyword_frequency']*100 + res['avg_identifiers_per_line']*100
            else:
                ans['evaluate_code_readability'] += comment_ratio/0.5*100 
    
    # ans['evaluate_code_readability'] = ans['evaluate_code_readability']/len(ans['detail'])


    return ans
def evaluate_code_readability(repo_list):
    ans = {}
    for i in repo_list:
        ans[i] = evaluate_code_readability1(i)
    evaluate_code_readability = ans

    ans = {
        "evaluate_code_readability": 0,
        "evaluate_code_readability_detail": []
    }

    for i in evaluate_code_readability:
        ans["evaluate_code_readability"] += evaluate_code_readability[i]["evaluate_code_readability"] / len(evaluate_code_readability)
        ans["evaluate_code_readability_detail"].append(
            {
                "repo": i,
                "evaluate_code_readability": evaluate_code_readability[i]["detail"]
            }
        )
        # if i not in ans["detail"]:
        #     ans["detail"][i] = {}
        # ans["detail"][i] = evaluate_code_readability[i]



    return ans

if __name__ == "__main__":
    file_path = ['https://github.com/numpy/numpy']
    # print(os.path.basename(file_path))

    # print(evaluate_code_readability(file_path))
    save_json(evaluate_code_readability(file_path), f'{os.path.basename(file_path[0])}.json')