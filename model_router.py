#!/usr/bin/env python3
"""
モデル・ルーターシステム
タスクに応じて最適なローカルモデルを選択・切り替える
"""

import streamlit as st
import json
import re
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
from pathlib import Path
import hashlib

class ModelRole(Enum):
    """モデル役割"""
    FAST = "fast"           # 雑談・簡単な返答用
    SMART = "smart"         # 複雑な推論・コーディング用
    VISION = "vision"       # 画像解析用

class TaskComplexity(Enum):
    """タスク複雑度"""
    SIMPLE = "simple"       # 簡単な質問・雑談
    MODERATE = "moderate"   # 中程度の推論
    COMPLEX = "complex"     # 複雑な問題解決・コーディング
    VISION = "vision"       # 画像関連タスク

@dataclass
class ModelConfig:
    """モデル設定"""
    role: ModelRole
    model_name: str
    ollama_name: str
    max_tokens: int
    temperature: float
    context_window: int
    description: str
    capabilities: List[str] = field(default_factory=list)
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    last_used: datetime = field(default_factory=datetime.now)

@dataclass
class RoutingDecision:
    """ルーティング決定"""
    selected_model: ModelRole
    complexity: TaskComplexity
    confidence: float
    reasoning: str
    processing_time: float
    fallback_used: bool = False

class ModelRouter:
    """インテリジェント・モデル・ルーター"""
    
    def __init__(self):
        self.name = "model_router"
        self.description = "タスクに応じて最適なローカルモデルを選択・切り替えるシステム"
        
        # モデル設定
        self.models = {
            ModelRole.FAST: ModelConfig(
                role=ModelRole.FAST,
                model_name="Llama-3.2-3B",
                ollama_name="llama3.2:3b",
                max_tokens=2048,
                temperature=0.7,
                context_window=8192,
                description="高速応答モデル。雑談や簡単な質問に最適。",
                capabilities=["text_generation", "conversation", "quick_response"],
                avg_response_time=0.5
            ),
            ModelRole.SMART: ModelConfig(
                role=ModelRole.SMART,
                model_name="Llama-3.1-8B",
                ollama_name="llama3.1:8b",
                max_tokens=4096,
                temperature=0.1,
                context_window=32768,
                description="高性能推論モデル。複雑な問題解決やコーディングに最適。",
                capabilities=["reasoning", "coding", "analysis", "problem_solving"],
                avg_response_time=2.0
            ),
            ModelRole.VISION: ModelConfig(
                role=ModelRole.VISION,
                model_name="Llama-3.2-Vision",
                ollama_name="llama3.2-vision",
                max_tokens=2048,
                temperature=0.2,
                context_window=8192,
                description="ビジョンモデル。画像解析やマルチモーダルタスクに最適。",
                capabilities=["image_analysis", "visual_reasoning", "multimodal"],
                avg_response_time=3.0
            )
        }
        
        # ルーティング統計
        self.routing_stats = {
            'total_requests': 0,
            'model_usage': {role.value: 0 for role in ModelRole},
            'complexity_distribution': {comp.value: 0 for comp in TaskComplexity},
            'avg_routing_time': 0.0,
            'fallback_count': 0
        }
        
        # パフォーマンス監視
        self.performance_history = []
        self.current_model = ModelRole.FAST  # デフォルト
        
        # 共有メモリ
        self.shared_memory = {}
        self.memory_lock = threading.Lock()
        
        # ルーティングルール
        self.routing_rules = self._initialize_routing_rules()
    
    def _initialize_routing_rules(self) -> Dict:
        """ルーティングルールを初期化"""
        return {
            # タスク複雑度判定ルール
            'complexity_keywords': {
                TaskComplexity.SIMPLE: [
                    'こんにちは', 'ありがとう', 'おはよう', 'こんばんは', 'さようなら',
                    '元気', '調子', '天気', '時間', '名前', '趣味', '好き', '嫌い',
                    '簡単', '教えて', '知ってる', 'どう', '何', 'どこ', 'いつ'
                ],
                TaskComplexity.MODERATE: [
                    'なぜ', 'どうして', '方法', 'やり方', '説明', '比較', '違い',
                    '意味', '定義', '例', '使い方', '設定', 'インストール',
                    '基本的な', '一般的な', '標準的な'
                ],
                TaskComplexity.COMPLEX: [
                    '実装', '開発', '設計', 'アーキテクチャ', 'アルゴリズム',
                    '最適化', 'パフォーマンス', 'セキュリティ', 'データベース',
                    '複雑な', '高度な', '専門的な', '詳細な', '完全な',
                    'コード', 'プログラミング', 'システム', 'フレームワーク'
                ],
                TaskComplexity.VISION: [
                    '画像', '写真', '図', 'グラフ', 'スクリーンショット',
                    '見て', '確認して', '解析して', '認識して', '描写して',
                    'visual', 'image', 'picture', 'photo', 'screenshot'
                ]
            },
            
            # コード検出ルール
            'code_patterns': [
                r'```[\s\S]*```',  # コードブロック
                r'def\s+\w+\s*\(',  # Python関数
                r'function\s+\w+\s*\(',  # JavaScript関数
                r'class\s+\w+',  # クラス定義
                r'import\s+\w+',  # インポート文
                r'#include\s*<',  # C/C++インクルード
                r'<html',  # HTMLタグ
                r'{.*}',  # JSON/オブジェクト
            ],
            
            # 数式・技術用語検出
            'technical_patterns': [
                r'\$\$[\s\S]*\$\$',  # LaTeX数式
                r'\w+\(\w+\)',  # 関数呼び出し
                r'\w+\.\w+',  # ドット表記
                r'https?://',  # URL
                r'\d+\.\d+\.\d+',  # バージョン番号
            ],
            
            # 長さベースの判定
            'length_thresholds': {
                TaskComplexity.SIMPLE: (0, 50),
                TaskComplexity.MODERATE: (51, 150),
                TaskComplexity.COMPLEX: (151, float('inf'))
            }
        }
    
    def route_request(self, user_input: str, context: Dict = None) -> RoutingDecision:
        """リクエストをルーティング"""
        start_time = time.time()
        
        # タスク複雑度を判定
        complexity = self._analyze_task_complexity(user_input, context)
        
        # 最適なモデルを選択
        selected_model = self._select_optimal_model(complexity, user_input, context)
        
        # ルーティング決定を作成
        decision = RoutingDecision(
            selected_model=selected_model,
            complexity=complexity,
            confidence=self._calculate_confidence(complexity, user_input),
            reasoning=self._generate_reasoning(selected_model, complexity, user_input),
            processing_time=time.time() - start_time
        )
        
        # 統計を更新
        self._update_routing_stats(decision)
        
        # 現在のモデルを更新
        self.current_model = selected_model
        
        return decision
    
    def _analyze_task_complexity(self, user_input: str, context: Dict = None) -> TaskComplexity:
        """タスク複雑度を分析"""
        # 画像関連のチェック
        if self._contains_image_keywords(user_input) or (context and context.get('has_image')):
            return TaskComplexity.VISION
        
        # キーワードベースの判定
        complexity_scores = {comp: 0 for comp in TaskComplexity}
        
        for complexity, keywords in self.routing_rules['complexity_keywords'].items():
            for keyword in keywords:
                if keyword.lower() in user_input.lower():
                    complexity_scores[complexity] += 1
        
        # コード検出
        if self._contains_code(user_input):
            complexity_scores[TaskComplexity.COMPLEX] += 3
        
        # 技術用語検出
        if self._contains_technical_terms(user_input):
            complexity_scores[TaskComplexity.MODERATE] += 2
            complexity_scores[TaskComplexity.COMPLEX] += 1
        
        # 長さベースの判定
        input_length = len(user_input)
        for complexity, (min_len, max_len) in self.routing_rules['length_thresholds'].items():
            if min_len <= input_length <= max_len:
                complexity_scores[complexity] += 1
        
        # 最もスコアの高い複雑度を選択
        if complexity_scores[TaskComplexity.VISION] > 0:
            return TaskComplexity.VISION
        
        max_score = max(complexity_scores.values())
        if max_score == 0:
            return TaskComplexity.SIMPLE
        
        for complexity, score in complexity_scores.items():
            if score == max_score:
                return complexity
        
        return TaskComplexity.SIMPLE
    
    def _contains_image_keywords(self, text: str) -> bool:
        """画像関連キーワードを検出"""
        image_keywords = self.routing_rules['complexity_keywords'][TaskComplexity.VISION]
        return any(keyword.lower() in text.lower() for keyword in image_keywords)
    
    def _contains_code(self, text: str) -> bool:
        """コードを含むか検出"""
        for pattern in self.routing_rules['code_patterns']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _contains_technical_terms(self, text: str) -> bool:
        """技術用語を含むか検出"""
        for pattern in self.routing_rules['technical_patterns']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _select_optimal_model(self, complexity: TaskComplexity, user_input: str, context: Dict = None) -> ModelRole:
        """最適なモデルを選択"""
        # 基本ルール
        if complexity == TaskComplexity.VISION:
            return ModelRole.VISION
        elif complexity == TaskComplexity.COMPLEX:
            return ModelRole.SMART
        elif complexity == TaskComplexity.SIMPLE:
            return ModelRole.FAST
        else:  # MODERATE
            # 文脈や過去のパフォーマンスを考慮
            if self._should_use_smart_for_moderate(user_input, context):
                return ModelRole.SMART
            else:
                return ModelRole.FAST
    
    def _should_use_smart_for_moderate(self, user_input: str, context: Dict = None) -> bool:
        """中程度の複雑度でSMARTモデルを使用すべきか判定"""
        # 過去のパフォーマンスをチェック
        recent_performance = self._get_recent_performance(ModelRole.SMART)
        
        # SMARTモデルの成功率が高い場合
        if recent_performance['success_rate'] > 0.8:
            return True
        
        # 技術的な内容を含む場合
        if self._contains_technical_terms(user_input):
            return True
        
        # 会話が続いている場合（文脈が必要）
        if context and context.get('conversation_length', 0) > 5:
            return True
        
        return False
    
    def _calculate_confidence(self, complexity: TaskComplexity, user_input: str) -> float:
        """ルーティングの信頼度を計算"""
        base_confidence = {
            TaskComplexity.SIMPLE: 0.9,
            TaskComplexity.MODERATE: 0.7,
            TaskComplexity.COMPLEX: 0.8,
            TaskComplexity.VISION: 0.95
        }
        
        confidence = base_confidence.get(complexity, 0.5)
        
        # キーワードの明確さで調整
        keyword_count = sum(1 for keywords in self.routing_rules['complexity_keywords'].values()
                           for keyword in keywords if keyword.lower() in user_input.lower())
        
        if keyword_count > 2:
            confidence += 0.1
        elif keyword_count == 0:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _generate_reasoning(self, selected_model: ModelRole, complexity: TaskComplexity, user_input: str) -> str:
        """ルーティングの理由を生成"""
        reasons = {
            ModelRole.FAST: [
                "短い応答で十分な簡単な質問のため高速モデルを選択",
                "雑談・挨拶のため軽量モデルで対応",
                "基本的な情報提供のため高速モデルを使用"
            ],
            ModelRole.SMART: [
                "複雑な推論が必要なため高性能モデルを選択",
                "コーディング・技術的な質問のため専門モデルを使用",
                "詳細な分析・説明が必要なため重厚なモデルで対応"
            ],
            ModelRole.VISION: [
                "画像解析が必要なためビジョンモデルを選択",
                "マルチモーダルタスクのため対応モデルを使用",
                "視覚的な情報処理が必要なため専用モデルで対応"
            ]
        }
        
        model_reasons = reasons.get(selected_model, ["タスク特性に基づき最適なモデルを選択"])
        return model_reasons[0] if model_reasons else "ルーティングルールに基づき選択"
    
    def _update_routing_stats(self, decision: RoutingDecision):
        """ルーティング統計を更新"""
        self.routing_stats['total_requests'] += 1
        self.routing_stats['model_usage'][decision.selected_model.value] += 1
        self.routing_stats['complexity_distribution'][decision.complexity.value] += 1
        
        # 平均ルーティング時間を更新
        total_time = self.routing_stats['avg_routing_time'] * (self.routing_stats['total_requests'] - 1)
        self.routing_stats['avg_routing_time'] = (total_time + decision.processing_time) / self.routing_stats['total_requests']
    
    def get_model_config(self, role: ModelRole) -> ModelConfig:
        """モデル設定を取得"""
        return self.models.get(role, self.models[ModelRole.FAST])
    
    def switch_model(self, target_role: ModelRole, force: bool = False) -> bool:
        """モデルを切り替え"""
        if not force and target_role == self.current_model:
            return False
        
        # モデルの可用性をチェック
        if self._is_model_available(target_role):
            self.current_model = target_role
            return True
        
        return False
    
    def _is_model_available(self, role: ModelRole) -> bool:
        """モデルが利用可能かチェック"""
        # 実際のOllama接続チェックを実装
        try:
            import requests
            model_config = self.get_model_config(role)
            response = requests.get(f"http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model_config.ollama_name in model.get('name', '') for model in models)
        except:
            pass
        
        return False
    
    def update_shared_memory(self, key: str, value: Any):
        """共有メモリを更新"""
        with self.memory_lock:
            self.shared_memory[key] = {
                'value': value,
                'timestamp': datetime.now(),
                'model_used': self.current_model.value
            }
    
    def get_shared_memory(self, key: str) -> Any:
        """共有メモリを取得"""
        with self.memory_lock:
            return self.shared_memory.get(key, {}).get('value')
    
    def _get_recent_performance(self, role: ModelRole, minutes: int = 30) -> Dict:
        """最近のパフォーマンスを取得"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_performances = [
            perf for perf in self.performance_history
            if perf['model'] == role.value and perf['timestamp'] > cutoff_time
        ]
        
        if not recent_performances:
            return {'success_rate': 0.5, 'avg_response_time': 1.0, 'count': 0}
        
        success_count = sum(1 for perf in recent_performances if perf['success'])
        avg_response_time = sum(perf['response_time'] for perf in recent_performances) / len(recent_performances)
        
        return {
            'success_rate': success_count / len(recent_performances),
            'avg_response_time': avg_response_time,
            'count': len(recent_performances)
        }
    
    def record_performance(self, model_role: ModelRole, success: bool, response_time: float):
        """パフォーマンスを記録"""
        performance_record = {
            'model': model_role.value,
            'success': success,
            'response_time': response_time,
            'timestamp': datetime.now()
        }
        
        self.performance_history.append(performance_record)
        
        # 古い記録を削除（24時間以上前）
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.performance_history = [
            perf for perf in self.performance_history if perf['timestamp'] > cutoff_time
        ]
        
        # モデル設定を更新
        model_config = self.get_model_config(model_role)
        recent_perf = self._get_recent_performance(model_role, minutes=60)
        
        if recent_perf['count'] > 0:
            model_config.success_rate = recent_perf['success_rate']
            model_config.avg_response_time = recent_perf['avg_response_time']
    
    def get_routing_statistics(self) -> Dict:
        """ルーティング統計を取得"""
        return {
            'routing_stats': self.routing_stats,
            'current_model': self.current_model.value,
            'model_configs': {role.value: {
                'name': config.model_name,
                'description': config.description,
                'avg_response_time': config.avg_response_time,
                'success_rate': config.success_rate,
                'last_used': config.last_used.isoformat()
            } for role, config in self.models.items()},
            'shared_memory_size': len(self.shared_memory),
            'performance_history_size': len(self.performance_history)
        }
    
    def reset_statistics(self):
        """統計をリセット"""
        self.routing_stats = {
            'total_requests': 0,
            'model_usage': {role.value: 0 for role in ModelRole},
            'complexity_distribution': {comp.value: 0 for comp in TaskComplexity},
            'avg_routing_time': 0.0,
            'fallback_count': 0
        }
        self.performance_history = []

class ModelRouterGUI:
    """モデルルーターGUI"""
    
    def __init__(self, router: ModelRouter):
        self.router = router
    
    def render(self):
        """GUIを描画"""
        st.subheader("🧠 モデル・ルーター")
        
        # 現在の状態
        stats = self.router.get_routing_statistics()
        
        # メトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "現在のモデル",
                stats['current_model'].upper(),
                help="現在アクティブなモデル"
            )
        
        with col2:
            st.metric(
                "総リクエスト数",
                stats['routing_stats']['total_requests'],
                help="ルーティングされた総リクエスト数"
            )
        
        with col3:
            st.metric(
                "平均ルーティング時間",
                f"{stats['routing_stats']['avg_routing_time']:.3f}秒",
                help="ルーティング決定の平均時間"
            )
        
        with col4:
            st.metric(
                "共有メモリ",
                f"{stats['shared_memory_size']}項目",
                help="モデル間で共有されるメモリ項目数"
            )
        
        # モデル使用状況
        st.write("**モデル使用状況**")
        usage_data = stats['routing_stats']['model_usage']
        
        if sum(usage_data.values()) > 0:
            for role, count in usage_data.items():
                if count > 0:
                    percentage = (count / stats['routing_stats']['total_requests']) * 100
                    st.write(f"- {role.upper()}: {count}回 ({percentage:.1f}%)")
        else:
            st.info("まだ使用実績がありません")
        
        # タスク複雑度分布
        st.write("**タスク複雑度分布**")
        complexity_data = stats['routing_stats']['complexity_distribution']
        
        if sum(complexity_data.values()) > 0:
            for complexity, count in complexity_data.items():
                if count > 0:
                    st.write(f"- {complexity}: {count}回")
        else:
            st.info("まだタスク実績がありません")
        
        # モデル詳細情報
        st.write("**モデル詳細情報**")
        selected_role = st.selectbox(
            "モデルを選択",
            [role.value for role in ModelRole],
            format_func=lambda x: x.upper()
        )
        
        role = ModelRole(selected_role)
        config = stats['model_configs'][selected_role]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**モデル名**: {config['name']}")
            st.write(f"**説明**: {config['description']}")
            st.write(f"**平均応答時間**: {config['avg_response_time']:.2f}秒")
        
        with col2:
            st.write(f"**成功率**: {config['success_rate']:.2%}")
            st.write(f"**最終使用**: {config['last_used'][:19]}")
        
        # 手動モデル切り替え
        st.write("**手動モデル切り替え**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 FASTモデルに切り替え"):
                if self.router.switch_model(ModelRole.FAST):
                    st.success("✅ FASTモデルに切り替えました")
                    st.rerun()
                else:
                    st.warning("⚠️ モデルの切り替えに失敗しました")
        
        with col2:
            if st.button("🧠 SMARTモデルに切り替え"):
                if self.router.switch_model(ModelRole.SMART):
                    st.success("✅ SMARTモデルに切り替えました")
                    st.rerun()
                else:
                    st.warning("⚠️ モデルの切り替えに失敗しました")
        
        # ビジョンモデル切り替え
        if st.button("👁️ VISIONモデルに切り替え"):
            if self.router.switch_model(ModelRole.VISION):
                st.success("✅ VISIONモデルに切り替えました")
                st.rerun()
            else:
                st.warning("⚠️ モデルの切り替えに失敗しました")
        
        # テストルーティング
        st.write("**テストルーティング**")
        test_input = st.text_area(
            "テスト入力",
            value="こんにちは！元気ですか？",
            height=100
        )
        
        if st.button("🧪 ルーティングテスト"):
            decision = self.router.route_request(test_input)
            
            st.success(f"🎯 選択モデル: {decision.selected_model.value.upper()}")
            st.info(f"📊 複雑度: {decision.complexity.value}")
            st.info(f"🎲 信頼度: {decision.confidence:.2f}")
            st.info(f"⏱️ 処理時間: {decision.processing_time:.3f}秒")
            st.write(f"💡 理由: {decision.reasoning}")
        
        # 共有メモリ管理
        st.write("**共有メモリ管理**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            memory_key = st.text_input("メモリキー")
            memory_value = st.text_input("メモリ値")
            
            if st.button("💾 メモリ保存") and memory_key and memory_value:
                self.router.update_shared_memory(memory_key, memory_value)
                st.success("✅ メモリを保存しました")
        
        with col2:
            if st.button("📋 メモリ表示") and memory_key:
                value = self.router.get_shared_memory(memory_key)
                if value is not None:
                    st.info(f"📝 値: {value}")
                else:
                    st.warning("⚠️ メモリが見つかりません")
        
        # 統計リセット
        if st.button("🗑️ 統計リセット"):
            self.router.reset_statistics()
            st.success("✅ 統計をリセットしました")
            st.rerun()
        
        # 詳細統計
        if st.button("📊 詳細統計"):
            st.json(stats)

# メイン関数
def create_model_router_gui(router: ModelRouter):
    """モデルルーターGUIを作成"""
    gui = ModelRouterGUI(router)
    gui.render()
