#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多言語プログラミングサポートクラス
"""

import datetime

class MultiLanguageCodeGenerator:
    def __init__(self):
        self.supported_languages = {
            "python": {
                "name": "Python",
                "extension": ".py",
                "template": '''# {filename}
# {description}
# 自動生成された{language}コード

def main():
    """
    メイン関数
    """
    print("Hello, World!")

if __name__ == "__main__":
    main()
''',
                "keywords": ["def", "class", "import", "from", "if", "else", "for", "while", "try", "except", "with", "lambda", "return"]
            },
            "javascript": {
                "name": "JavaScript",
                "extension": ".js",
                "template": '''// {filename}
// {description}
// 自動生成された{language}コード

function main() {{
    console.log("Hello, World!");
}}

// イベントリスナー
document.addEventListener('DOMContentLoaded', main);
''',
                "keywords": ["function", "const", "let", "var", "if", "else", "for", "while", "try", "catch", "finally", "class", "return", "async", "await"]
            },
            "java": {
                "name": "Java",
                "extension": ".java",
                "template": '''// {filename}
// {description}
// 自動生成された{language}コード

public class {classname} {{
    public static void main(String[] args) {{
        System.out.println("Hello, World!");
    }}
}}
''',
                "keywords": ["public", "private", "static", "void", "class", "interface", "extends", "implements", "import", "package", "if", "else", "for", "while", "try", "catch", "finally", "return"]
            },
            "cpp": {
                "name": "C++",
                "extension": ".cpp",
                "template": '''// {filename}
// {description}
// 自動生成された{language}コード

#include <iostream>
#include <string>

int main() {{
    std::cout << "Hello, World!" << std::endl;
    return 0;
}}
''',
                "keywords": ["#include", "using", "namespace", "class", "struct", "public", "private", "static", "void", "int", "if", "else", "for", "while", "try", "catch", "return"]
            },
            "html": {
                "name": "HTML",
                "extension": ".html",
                "template": '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
</body>
</html>''',
                "keywords": ["<!DOCTYPE", "<html>", "<head>", "<body>", "<div>", "<script>", "<style>", "class", "id", "href", "src"]
            },
            "css": {
                "name": "CSS",
                "extension": ".css",
                "template": '''/* {filename} */
/* {description} */
/* 自動生成された{language}コード */

body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f0f0f0;
}}

.container {{
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

h1 {{
    color: #333;
    text-align: center;
}}

p {{
    line-height: 1.6;
    color: #666;
}}
''',
                "keywords": ["body", "container", "h1", "h2", "p", "div", "span", "class", "id", "margin", "padding", "background", "color", "font-family"]
            }
        }
    
    def get_supported_languages(self):
        """サポートする言語の一覧を取得"""
        return list(self.supported_languages.keys())
    
    def get_language_info(self, language):
        """言語情報を取得"""
        return self.supported_languages.get(language.lower(), None)
    
    def generate_code(self, language, filename, description="", custom_template=None):
        """指定された言語でコードを生成"""
        language = language.lower()
        if language not in self.supported_languages:
            return None, f"サポートされていない言語です: {language}"
        
        lang_info = self.supported_languages[language]
        
        template = custom_template or lang_info["template"]
        
        template = template.replace("{filename}", filename)
        template = template.replace("{description}", description)
        template = template.replace("{language}", lang_info["name"])
        template = template.replace("{app_name}", filename.replace(lang_info["extension"], ""))
        template = template.replace("{app_description}", description)
        template = template.replace("{db_name}", "mydatabase")
        template = template.replace("{port}", "8080")
        template = template.replace("{base_image}", "node:18")
        template = template.replace("{timestamp}", datetime.datetime.now().isoformat())
        template = template.replace("{classname}", filename.replace(lang_info["extension"], "").capitalize())
        template = template.replace("{namespace}", "MyApp")
        template = template.replace("{title}", description or filename)
        
        return template, f"{lang_info['name']}コードを生成しました"
    
    def detect_optimal_language(self, instruction):
        """指示内容から最適なプログラミング言語を検出"""
        instruction_lower = instruction.lower()
        
        language_patterns = {
            "python": {
                "keywords": ["python", "py", "def", "import", "from", "class", "ai", "機械学習", "データ分析", "pandas", "numpy", "tensorflow", "pytorch"],
                "weight": 3
            },
            "javascript": {
                "keywords": ["javascript", "js", "node", "react", "vue", "angular", "frontend", "web", "ブラウザ"],
                "weight": 2
            },
            "java": {
                "keywords": ["java", "spring", "android", "jsp", "servlet"],
                "weight": 2
            },
            "cpp": {
                "keywords": ["c++", "cpp", "c++", "システム", "パフォーマンス", "ゲーム"],
                "weight": 2
            },
            "html": {
                "keywords": ["html", "web", "サイト", "ページ", "マークアップ"],
                "weight": 1
            },
            "css": {
                "keywords": ["css", "スタイル", "デザイン", "見た目"],
                "weight": 1
            }
        }
        
        scores = {}
        for lang, pattern in language_patterns.items():
            score = 0
            for keyword in pattern["keywords"]:
                if keyword in instruction_lower:
                    score += pattern["weight"]
            scores[lang] = score
        
        if not any(scores.values()):
            return "python", "デフォルトでPythonを選択しました"
        
        optimal_language = max(scores, key=scores.get)
        return optimal_language, f"最適な言語として{optimal_language}を検出しました"
    
    def create_file(self, language, filename, description="", custom_template=None):
        """指定された言語でファイルを作成"""
        code, message = self.generate_code(language, filename, description, custom_template)
        
        if code is None:
            return None, message
        
        try:
            lang_info = self.get_language_info(language)
            if not lang_info:
                return None, f"サポートされていない言語です: {language}"
            
            if not filename.endswith(lang_info["extension"]):
                filename += lang_info["extension"]
            
            from pathlib import Path
            file_path = Path(filename)
            file_path.write_text(code, encoding='utf-8')
            
            return file_path, f"{lang_info['name']}ファイル `{filename}` を作成しました"
            
        except Exception as e:
            return None, f"{lang_info['name']}ファイル作成エラー: {str(e)}"
    
    def create_file_from_instruction(self, instruction, filename=""):
        """指示内容から最適な言語を選択してファイルを作成"""
        optimal_language, message = self.detect_optimal_language(instruction)
        
        if not filename:
            lang_info = self.get_language_info(optimal_language)
            filename = f"generated_code{lang_info['extension']}"
        
        file_path, create_message = self.create_file(optimal_language, filename, instruction)
        
        if file_path:
            return file_path, optimal_language, f"{message}\n{create_message}"
        else:
            return None, optimal_language, f"{message}\n{create_message}"
