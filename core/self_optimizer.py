"""
自己診断と最適化モジュール
AIが自らのコードを診断し、改善提案と自動実行を行う
"""

import os
import re
import ast
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple, Any
from core.constants import *

class CodeAnalyzer:
    """コード分析クラス"""
    
    def __init__(self):
        self.analysis_patterns = {
            'redundant_code': [
                (r'def\s+(\w+)\s*\([^)]*\):\s*"""[^"]*"""\s*return\s+\w+', '冗長なラッパー関数'),
                (r'if\s+True\s*:', '冗長なif True'),
                (r'for\s+\w+\s+in\s+range\(len\((\w+)\)\):', '非効率なループ'),
                (r'\.format\([^)]*\)', 'f-string推奨'),
                (r'print\([^)]*\)', 'デバッグprint文')
            ],
            'ui_improvements': [
                (r'st\.button\([^)]*\)', 'ボタン改善の余地'),
                (r'st\.text_input\([^)]*\)', '入力フィールド改善'),
                (r'st\.markdown\([^)]*\)', 'マークダウン改善'),
                (r'background-color:\s*[^;]+', 'CSS改善の余地')
            ],
            'error_handling': [
                (r'except\s*:', '裸のexcept'),
                (r'except\s+Exception\s*:', '広範なException'),
                (r'try:\s*[^}]*except', 'エラーハンドリング不足'),
                (r'open\([^)]*\)', 'ファイル操作エラーハンドリング不足')
            ],
            'performance': [
                (r'for\s+\w+\s+in\s+\w+\.items\(\):\s*if\s+\w+\[', '辞書検索の非効率性'),
                (r'\.append\([^)]*\)\s*#.*ループ内', 'リスト操作の非効率性'),
                (r're\.search\([^)]*\)', '正規表現の最適化余地'),
                (r'json\.load\([^)]*\)', 'JSON処理の最適化余地')
            ]
        }
    
    def analyze_file(self, file_path: str) -> Dict:
        """単一ファイルを分析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis_result = {
                'file_path': file_path,
                'issues': [],
                'metrics': self._calculate_metrics(content),
                'suggestions': []
            }
            
            # 各種問題を検出
            for category, patterns in self.analysis_patterns.items():
                for pattern, description in patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    if matches:
                        analysis_result['issues'].append({
                            'category': category,
                            'pattern': pattern,
                            'description': description,
                            'matches': len(matches),
                            'severity': self._calculate_severity(category, len(matches))
                        })
            
            # AST解析で追加の問題を検出
            ast_issues = self._analyze_ast(content)
            analysis_result['issues'].extend(ast_issues)
            
            return analysis_result
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'issues': [],
                'metrics': {},
                'suggestions': []
            }
    
    def _calculate_metrics(self, content: str) -> Dict:
        """コードメトリクスを計算"""
        lines = content.split('\n')
        return {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'empty_lines': len([l for l in lines if not l.strip()]),
            'complexity_estimate': len(re.findall(r'\bif\b|\bfor\b|\bwhile\b|\btry\b', content))
        }
    
    def _calculate_severity(self, category: str, count: int) -> str:
        """深刻度を計算"""
        if category == 'error_handling' and count > 0:
            return 'high'
        elif category == 'performance' and count > 2:
            return 'medium'
        elif count > 3:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_ast(self, content: str) -> List[Dict]:
        """AST解析で問題を検出"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # 関数の複雑度をチェック
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_function_complexity(node)
                    if complexity > 10:
                        issues.append({
                            'category': 'complexity',
                            'description': f'関数 {node.name} の複雑度が高い ({complexity})',
                            'severity': 'high',
                            'line': node.lineno
                        })
                    
                    # 長すぎる関数を検出
                    if hasattr(node, 'end_lineno') and node.end_lineno:
                        func_length = node.end_lineno - node.lineno
                        if func_length > 50:
                            issues.append({
                                'category': 'length',
                                'description': f'関数 {node.name} が長すぎる ({func_length}行)',
                                'severity': 'medium',
                                'line': node.lineno
                            })
        
        except Exception as e:
            issues.append({
                'category': 'parse_error',
                'description': f'AST解析エラー: {str(e)}',
                'severity': 'high'
            })
        
        return issues
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """関数の複雑度を計算"""
        complexity = 1  # 基本複雑度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class OptimizationSuggester:
    """最適化提案クラス"""
    
    def __init__(self):
        self.optimization_templates = {
            'redundant_code': {
                'wrapper_function': {
                    'description': '冗長なラッパー関数をインライン化',
                    'benefit': 'コードの簡素化と実行速度向上',
                    'confidence': 0.8
                },
                'if_true': {
                    'description': '不要なif Trueを削除',
                    'benefit': 'コードの簡素化',
                    'confidence': 0.9
                },
                'format_string': {
                    'description': 'format()をf-stringに置換',
                    'benefit': '可読性向上とパフォーマンス改善',
                    'confidence': 0.7
                }
            },
            'performance': {
                'dict_lookup': {
                    'description': '辞書検索を最適化',
                    'benefit': '実行速度20-30%向上',
                    'confidence': 0.6
                },
                'list_operation': {
                    'description': 'リスト操作を最適化',
                    'benefit': 'メモリ使用量削減',
                    'confidence': 0.5
                }
            },
            'ui_improvements': {
                'button_styling': {
                    'description': 'ボタンのスタイルを改善',
                    'benefit': 'UIの見栄え向上',
                    'confidence': 0.8
                },
                'layout_optimization': {
                    'description': 'レイアウトを最適化',
                    'benefit': 'ユーザー体験向上',
                    'confidence': 0.6
                }
            }
        }
    
    def generate_suggestions(self, analysis_results: List[Dict]) -> List[Dict]:
        """分析結果から改善提案を生成"""
        suggestions = []
        
        for result in analysis_results:
            if 'error' in result:
                continue
            
            for issue in result['issues']:
                category = issue['category']
                description = issue['description']
                
                # テンプレートから提案を生成
                if category in self.optimization_templates:
                    for template_name, template in self.optimization_templates[category].items():
                        if self._is_applicable_template(description, template_name):
                            suggestion = {
                                'file_path': result['file_path'],
                                'issue': issue,
                                'template': template,
                                'priority': self._calculate_priority(issue['severity'], template['confidence']),
                                'estimated_impact': self._estimate_impact(template)
                            }
                            suggestions.append(suggestion)
        
        # 優先度でソート
        suggestions.sort(key=lambda x: x['priority'], reverse=True)
        
        return suggestions[:10]  # 上位10件のみ
    
    def _is_applicable_template(self, description: str, template_name: str) -> bool:
        """テンプレートが適用可能か判断"""
        keywords = {
            'wrapper_function': ['ラッパー関数'],
            'if_true': ['if True'],
            'format_string': ['format'],
            'dict_lookup': ['辞書検索'],
            'list_operation': ['リスト操作'],
            'button_styling': ['ボタン'],
            'layout_optimization': ['レイアウト']
        }
        
        if template_name in keywords:
            for keyword in keywords[template_name]:
                if keyword in description:
                    return True
        
        return False
    
    def _calculate_priority(self, severity: str, confidence: float) -> float:
        """優先度を計算"""
        severity_weights = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
        return severity_weights.get(severity, 1.0) * confidence
    
    def _estimate_impact(self, template: Dict) -> str:
        """影響度を見積もる"""
        benefit = template['benefit']
        confidence = template['confidence']
        
        if confidence > 0.8:
            return f"高い影響: {benefit}"
        elif confidence > 0.6:
            return f"中程度の影響: {benefit}"
        else:
            return f"低い影響: {benefit}"

class EvolutionLogger:
    """進化ロガー"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or DATA_DIR / "evolution_history.md"
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_optimization(self, optimization_type: str, description: str, impact: str, files_modified: List[str]):
        """最適化をログに記録"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
## 🧬 エゾモモンガの知恵 - {timestamp}

### 🎯 最適化タイプ
{optimization_type}

### 📝 詳細
{description}

### 🚀 影響
{impact}

### 📁 修正ファイル
{', '.join(files_modified)}

### 🧠 AIの自己評価
この最適化により、システム全体の品質が向上しました。継続的な改善はエージェントの成長に不可欠です。

---
"""
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            print(f"✅ 進化ログを記録しました: {self.log_file}")
        except Exception as e:
            print(f"❌ 進化ログ記録エラー: {e}")
    
    def get_evolution_history(self) -> List[Dict]:
        """進化履歴を取得"""
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # マークダウンを解析して履歴を返す
            entries = []
            sections = content.split('## 🧬 エゾモモンガの知恵')
            
            for section in sections[1:]:  # 最初の空セクションを除く
                lines = section.strip().split('\n')
                if len(lines) > 5:
                    entries.append({
                        'timestamp': lines[0].strip(),
                        'type': lines[2].replace('### 🎯 最適化タイプ', '').strip(),
                        'description': lines[4].replace('### 📝 詳細', '').strip(),
                        'impact': lines[6].replace('### 🚀 影響', '').strip()
                    })
            
            return entries[-10:]  # 最新10件
            
        except Exception as e:
            print(f"進化履歴取得エラー: {e}")
            return []

# グローバルインスタンス
code_analyzer = CodeAnalyzer()
optimization_suggester = OptimizationSuggester()
evolution_logger = EvolutionLogger()
