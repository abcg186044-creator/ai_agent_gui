#!/usr/bin/env python3
"""
高度知識システム
マルチ検索エージェント、自己検証、RAG統合、長文コンテキスト管理
"""

import streamlit as st
import requests
import json
import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from collections import defaultdict
import threading
import time

class SourceType(Enum):
    """情報ソースタイプ"""
    DUCKDUCKGO = "duckduckgo"
    ARXIV = "arxiv"
    GITHUB = "github"
    LOCAL_KNOWLEDGE = "local_knowledge"
    PERSONAL_MEMORY = "personal_memory"

@dataclass
class SearchResult:
    """検索結果"""
    source: SourceType
    title: str
    content: str
    url: Optional[str] = None
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

@dataclass
class KnowledgeItem:
    """知識アイテム"""
    content: str
    embedding: np.ndarray
    source: SourceType
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

class MultiSearchAgent:
    """マルチ検索エージェント"""
    
    def __init__(self):
        self.name = "multi_search_agent"
        self.description = "複数の情報源から検索・統合する高度検索システム"
        
        # 検索ソース設定
        self.search_sources = {
            SourceType.DUCKDUCKGO: self._search_duckduckgo,
            SourceType.ARXIV: self._search_arxiv,
            SourceType.GITHUB: self._search_github
        }
        
        # 検索結果キャッシュ
        self.search_cache = {}
        self.cache_ttl = 3600  # 1時間キャッシュ
        
        # 検索統計
        self.search_stats = defaultdict(int)
    
    async def search_all_sources(self, query: str, max_results_per_source: int = 5) -> List[SearchResult]:
        """すべての情報源から検索"""
        all_results = []
        
        # 並列検索
        tasks = []
        for source_type, search_func in self.search_sources.items():
            task = asyncio.create_task(self._safe_search(search_func, query, source_type, max_results_per_source))
            tasks.append(task)
        
        # 結果を待機
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を集約
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            elif isinstance(result, Exception):
                print(f"検索エラー: {str(result)}")
        
        # 信頼度でソート
        all_results.sort(key=lambda x: x.confidence, reverse=True)
        
        # 統計更新
        self.search_stats['total_searches'] += 1
        for result in all_results:
            self.search_stats[f'source_{result.source.value}'] += 1
        
        return all_results[:20]  # 上位20件を返却
    
    async def _safe_search(self, search_func, query: str, source_type: SourceType, max_results: int) -> List[SearchResult]:
        """安全な検索実行"""
        try:
            return await search_func(query, max_results)
        except Exception as e:
            print(f"{source_type.value}検索エラー: {str(e)}")
            return []
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """DuckDuckGo検索"""
        try:
            # DuckDuckGo HTML検索API
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'jp-jp'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # 結果を解析
                        results = []
                        # 簡易的なHTML解析（実際はBeautifulSoupを使用）
                        matches = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html)
                        
                        for i, (url, title) in enumerate(matches[:max_results]):
                            # 内容の抜粋を取得
                            content_match = re.search(f'<a[^>]*href="{re.escape(url)}"[^>]*>.*?</a>.*?<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>', html, re.DOTALL)
                            content = content_match.group(1) if content_match else title
                            
                            results.append(SearchResult(
                                source=SourceType.DUCKDUCKGO,
                                title=title.strip(),
                                content=content.strip(),
                                url=url,
                                confidence=0.8
                            ))
                        
                        return results
            
        except Exception as e:
            print(f"DuckDuckGo検索エラー: {str(e)}")
        
        return []
    
    async def _search_arxiv(self, query: str, max_results: int) -> List[SearchResult]:
        """arXiv検索"""
        try:
            # arXiv API
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'all:"{query}"',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        xml = await response.text()
                        
                        # XML解析
                        results = []
                        entries = re.findall(r'<entry>.*?</entry>', xml, re.DOTALL)
                        
                        for entry in entries[:max_results]:
                            title_match = re.search(r'<title>([^<]*)</title>', entry)
                            summary_match = re.search(r'<summary>([^<]*)</summary>', entry)
                            id_match = re.search(r'<id>([^<]*)</id>', entry)
                            
                            if title_match and summary_match:
                                results.append(SearchResult(
                                    source=SourceType.ARXIV,
                                    title=title_match.group(1).strip(),
                                    content=summary_match.group(1).strip(),
                                    url=id_match.group(1).strip() if id_match else None,
                                    confidence=0.9,
                                    metadata={'type': 'academic_paper'}
                                ))
                        
                        return results
            
        except Exception as e:
            print(f"arXiv検索エラー: {str(e)}")
        
        return []
    
    async def _search_github(self, query: str, max_results: int) -> List[SearchResult]:
        """GitHub検索"""
        try:
            # GitHub API（認証なしの場合制限あり）
            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('items', [])[:max_results]:
                            results.append(SearchResult(
                                source=SourceType.GITHUB,
                                title=item.get('name', ''),
                                content=item.get('description', ''),
                                url=item.get('html_url'),
                                confidence=0.7,
                                metadata={
                                    'stars': item.get('stargazers_count', 0),
                                    'language': item.get('language', ''),
                                    'updated_at': item.get('updated_at', '')
                                }
                            ))
                        
                        return results
            
        except Exception as e:
            print(f"GitHub検索エラー: {str(e)}")
        
        return []

class SelfReflectionSystem:
    """自己検証システム"""
    
    def __init__(self):
        self.name = "self_reflection"
        self.description = "AI回答の自己検証と改善システム"
        
        # 検証基準
        self.validation_criteria = {
            'factual_accuracy': '事実の正確性',
            'logical_consistency': '論理的一貫性',
            'source_reliability': '情報源の信頼性',
            'completeness': '回答の完全性',
            'clarity': '明確さ'
        }
        
        # 検証履歴
        self.reflection_history = []
    
    def reflect_on_answer(self, answer: str, sources: List[SearchResult], original_query: str) -> Dict:
        """回答の自己検証"""
        reflection_result = {
            'original_answer': answer,
            'validation_scores': {},
            'issues_found': [],
            'improvements_suggested': [],
            'confidence_score': 0.0,
            'needs_revision': False,
            'timestamp': datetime.now()
        }
        
        # 各基準で検証
        for criterion, description in self.validation_criteria.items():
            score = self._validate_criterion(criterion, answer, sources, original_query)
            reflection_result['validation_scores'][criterion] = {
                'score': score,
                'description': description,
                'status': 'good' if score >= 0.7 else 'needs_improvement'
            }
        
        # 問題点の特定
        issues = self._identify_issues(reflection_result['validation_scores'])
        reflection_result['issues_found'] = issues
        
        # 改善提案
        if issues:
            improvements = self._suggest_improvements(issues, answer, sources, original_query)
            reflection_result['improvements_suggested'] = improvements
            reflection_result['needs_revision'] = True
        
        # 全体的な信頼度
        scores = [v['score'] for v in reflection_result['validation_scores'].values()]
        reflection_result['confidence_score'] = np.mean(scores)
        
        # 履歴に保存
        self.reflection_history.append(reflection_result)
        
        return reflection_result
    
    def _validate_criterion(self, criterion: str, answer: str, sources: List[SearchResult], query: str) -> float:
        """個別基準の検証"""
        if criterion == 'factual_accuracy':
            return self._check_factual_accuracy(answer, sources)
        elif criterion == 'logical_consistency':
            return self._check_logical_consistency(answer)
        elif criterion == 'source_reliability':
            return self._check_source_reliability(sources)
        elif criterion == 'completeness':
            return self._check_completeness(answer, query)
        elif criterion == 'clarity':
            return self._check_clarity(answer)
        
        return 0.5
    
    def _check_factual_accuracy(self, answer: str, sources: List[SearchResult]) -> float:
        """事実の正確性をチェック"""
        if not sources:
            return 0.3
        
        # 情報源の信頼性を考慮
        reliable_sources = [s for s in sources if s.confidence >= 0.7]
        if not reliable_sources:
            return 0.4
        
        # 回答が情報源と一致しているかを簡易チェック
        accuracy_score = 0.0
        for source in reliable_sources:
            # キーワードの一致度をチェック
            source_words = set(source.content.lower().split())
            answer_words = set(answer.lower().split())
            
            if source_words:
                overlap = len(source_words & answer_words) / len(source_words)
                accuracy_score = max(accuracy_score, overlap)
        
        return min(1.0, accuracy_score + 0.3)  # ベーススコアを追加
    
    def _check_logical_consistency(self, answer: str) -> float:
        """論理的一貫性をチェック"""
        # 矛盾表現の検出
        contradiction_patterns = [
            r'しかし.*しかし',
            r'だが.*だが',
            r'.*ではない.*です',
            r'常に.*時々',
            r'すべて.*ない'
        ]
        
        contradictions = 0
        for pattern in contradiction_patterns:
            if re.search(pattern, answer):
                contradictions += 1
        
        # 矛盾が少ないほど高スコア
        consistency_score = max(0.0, 1.0 - (contradictions * 0.2))
        
        return consistency_score
    
    def _check_source_reliability(self, sources: List[SearchResult]) -> float:
        """情報源の信頼性をチェック"""
        if not sources:
            return 0.3
        
        # 情報源タイプごとの信頼性
        reliability_weights = {
            SourceType.ARXIV: 0.9,
            SourceType.DUCKDUCKGO: 0.7,
            SourceType.GITHUB: 0.6,
            SourceType.LOCAL_KNOWLEDGE: 0.8,
            SourceType.PERSONAL_MEMORY: 0.5
        }
        
        total_weight = 0.0
        total_reliability = 0.0
        
        for source in sources:
            weight = reliability_weights.get(source.source, 0.5)
            total_weight += weight
            total_reliability += weight * source.confidence
        
        if total_weight > 0:
            return total_reliability / total_weight
        
        return 0.5
    
    def _check_completeness(self, answer: str, query: str) -> float:
        """回答の完全性をチェック"""
        # クエリのキーワードが回答に含まれているか
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        
        if not query_words:
            return 0.5
        
        coverage = len(query_words & answer_words) / len(query_words)
        
        # 回答の長さも考慮
        length_factor = min(1.0, len(answer) / 200)  # 200文字以上で満点
        
        return (coverage * 0.7) + (length_factor * 0.3)
    
    def _check_clarity(self, answer: str) -> float:
        """明確さをチェック"""
        # 文章の構造を評価
        sentences = re.split(r'[。！？]', answer)
        if not sentences:
            return 0.3
        
        # 平均文長
        avg_sentence_length = np.mean([len(s.strip()) for s in sentences if s.strip()])
        length_score = 1.0 if 10 <= avg_sentence_length <= 100 else 0.5
        
        # 専門用語の過度な使用チェック
        technical_terms = ['API', 'アルゴリズム', 'フレームワーク', 'アーキテクチャ']
        tech_ratio = sum(1 for term in technical_terms if term in answer) / len(sentences)
        clarity_score = max(0.0, 1.0 - (tech_ratio * 0.2))
        
        return (length_score + clarity_score) / 2
    
    def _identify_issues(self, validation_scores: Dict) -> List[Dict]:
        """問題点を特定"""
        issues = []
        
        for criterion, score_info in validation_scores.items():
            if score_info['score'] < 0.7:
                issues.append({
                    'criterion': criterion,
                    'description': score_info['description'],
                    'score': score_info['score'],
                    'severity': 'high' if score_info['score'] < 0.5 else 'medium'
                })
        
        return issues
    
    def _suggest_improvements(self, issues: List[Dict], answer: str, sources: List[SearchResult], query: str) -> List[str]:
        """改善提案を生成"""
        improvements = []
        
        for issue in issues:
            criterion = issue['criterion']
            
            if criterion == 'factual_accuracy':
                improvements.append("より信頼性の高い情報源を参照して、事実関係を再確認してください")
            elif criterion == 'logical_consistency':
                improvements.append("回答全体の論理的な一貫性を確認し、矛盾する表現を修正してください")
            elif criterion == 'source_reliability':
                improvements.append("学術論文や公式ドキュメントなど、より信頼性の高い情報源を追加で検索してください")
            elif criterion == 'completeness':
                improvements.append("ユーザーの質問に対して、より完全な回答を提供してください")
            elif criterion == 'clarity':
                improvements.append("回答をより明確に、分かりやすい表現に修正してください")
        
        return improvements

class AdvancedRAGSystem:
    """高度RAGシステム"""
    
    def __init__(self, knowledge_base_path: str = "./knowledge_base"):
        self.name = "advanced_rag"
        self.description = "完全統合RAGシステム"
        self.knowledge_base_path = Path(knowledge_base_path)
        
        # 埋め込みモデル
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384
        
        # FAISSインデックス
        self.index = None
        self.knowledge_items = []
        
        # 初期化
        self._initialize_system()
    
    def _initialize_system(self):
        """システム初期化"""
        # 知識ベースフォルダ作成
        self.knowledge_base_path.mkdir(exist_ok=True)
        
        # 既存のインデックスを読み込み
        self._load_index()
        
        # ナレッジベースのスキャン
        self._scan_knowledge_base()
    
    def _load_index(self):
        """インデックス読み込み"""
        index_file = self.knowledge_base_path / "faiss_index.bin"
        items_file = self.knowledge_base_path / "knowledge_items.pkl"
        
        if index_file.exists() and items_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(items_file, 'rb') as f:
                    self.knowledge_items = pickle.load(f)
                print(f"✅ 既存のナレッジベースを読み込み: {len(self.knowledge_items)}件")
            except Exception as e:
                print(f"❌ インデックス読み込みエラー: {str(e)}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """新しいインデックス作成"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.knowledge_items = []
    
    def _scan_knowledge_base(self):
        """ナレッジベースをスキャン"""
        if not self.knowledge_base_path.exists():
            return
        
        # サポートするファイル形式
        supported_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json'}
        
        for file_path in self.knowledge_base_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                try:
                    # ファイル読み込み
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content.strip()) > 10:  # 短すぎる内容は無視
                        # チャンクに分割
                        chunks = self._split_content(content)
                        
                        for chunk in chunks:
                            self._add_knowledge_item(
                                content=chunk,
                                source=SourceType.LOCAL_KNOWLEDGE,
                                metadata={
                                    'file_path': str(file_path),
                                    'file_type': file_path.suffix,
                                    'original_file': file_path.name
                                }
                            )
                
                except Exception as e:
                    print(f"ファイル読み込みエラー {file_path}: {str(e)}")
    
    def _split_content(self, content: str, chunk_size: int = 500) -> List[str]:
        """コンテンツをチャンクに分割"""
        chunks = []
        
        # 段落で分割
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk + paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
                else:
                    # 長い段落は文で分割
                    sentences = paragraph.split('。')
                    for sentence in sentences:
                        if len(current_chunk + sentence) <= chunk_size:
                            current_chunk += sentence + "。"
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _add_knowledge_item(self, content: str, source: SourceType, metadata: Dict = None):
        """知識アイテムを追加"""
        # 埋め込み生成
        embedding = self.embedding_model.encode([content])[0]
        
        # 知識アイテム作成
        item = KnowledgeItem(
            content=content,
            embedding=embedding,
            source=source,
            metadata=metadata or {}
        )
        
        # インデックスに追加
        self.index.add(np.array([embedding]).astype('float32'))
        self.knowledge_items.append(item)
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """ナレッジベース検索"""
        if len(self.knowledge_items) == 0:
            return []
        
        # クエリ埋め込み
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # 検索
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.knowledge_items)))
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.knowledge_items):
                item = self.knowledge_items[idx]
                
                # アクセス統計更新
                item.access_count += 1
                item.last_accessed = datetime.now()
                
                # 類似度スコア計算
                similarity = 1.0 / (1.0 + distance)
                
                results.append(SearchResult(
                    source=item.source,
                    title=item.metadata.get('original_file', 'ローカル知識'),
                    content=item.content,
                    confidence=similarity,
                    metadata=item.metadata
                ))
        
        return results
    
    def add_personal_memory(self, content: str, metadata: Dict = None):
        """個人メモリを追加"""
        self._add_knowledge_item(
            content=content,
            source=SourceType.PERSONAL_MEMORY,
            metadata=metadata or {'type': 'personal_memory'}
        )
        
        # 定期的な保存
        self._save_index()
    
    def _save_index(self):
        """インデックス保存"""
        try:
            index_file = self.knowledge_base_path / "faiss_index.bin"
            items_file = self.knowledge_base_path / "knowledge_items.pkl"
            
            faiss.write_index(self.index, str(index_file))
            with open(items_file, 'wb') as f:
                pickle.dump(self.knowledge_items, f)
            
            print(f"✅ ナレッジベースを保存: {len(self.knowledge_items)}件")
        except Exception as e:
            print(f"❌ インデックス保存エラー: {str(e)}")

class LongContextManager:
    """長文コンテキスト管理"""
    
    def __init__(self, max_context_length: int = 8000):
        self.name = "long_context_manager"
        self.description = "長文コンテキスト管理システム"
        self.max_context_length = max_context_length
        
        # 会話履歴
        self.conversation_history = []
        self.summaries = []
        
        # 要約モデル
        self.summarization_threshold = 10  # 10メッセージごとに要約
    
    def add_message(self, role: str, content: str, timestamp: datetime = None):
        """メッセージを追加"""
        message = {
            'role': role,
            'content': content,
            'timestamp': timestamp or datetime.now()
        }
        
        self.conversation_history.append(message)
        
        # 要約が必要かチェック
        if len(self.conversation_history) >= self.summarization_threshold:
            self._create_summary()
    
    def _create_summary(self):
        """要約を作成"""
        if len(self.conversation_history) < self.summarization_threshold:
            return
        
        # 最近のメッセージを要約
        recent_messages = self.conversation_history[-self.summarization_threshold:]
        
        # 簡易的な要約（実際は要約モデルを使用）
        summary_content = self._generate_summary(recent_messages)
        
        summary = {
            'content': summary_content,
            'message_count': len(recent_messages),
            'timestamp': datetime.now(),
            'key_topics': self._extract_key_topics(recent_messages)
        }
        
        self.summaries.append(summary)
        
        # 古いメッセージを削除
        self.conversation_history = self.conversation_history[:-self.summarization_threshold//2]
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """要約を生成"""
        # 簡易的な要約ロジック
        user_messages = [m['content'] for m in messages if m['role'] == 'user']
        assistant_messages = [m['content'] for m in messages if m['role'] == 'assistant']
        
        summary = f"会話要約（{len(messages)}メッセージ）:\n"
        
        if user_messages:
            summary += f"主な質問: {user_messages[0][:100]}...\n"
        
        if assistant_messages:
            summary += f"主な回答: {assistant_messages[0][:100]}...\n"
        
        summary += f"主要トピック: 技術開発、コーディング、問題解決"
        
        return summary
    
    def _extract_key_topics(self, messages: List[Dict]) -> List[str]:
        """主要トピックを抽出"""
        # 簡易的なトピック抽出
        all_content = " ".join([m['content'] for m in messages])
        
        # 技術キーワード
        tech_keywords = ['Python', 'JavaScript', 'API', 'データベース', 'AI', '機械学習', 'Web開発']
        topics = [keyword for keyword in tech_keywords if keyword.lower() in all_content.lower()]
        
        return topics[:5]  # 上位5トピック
    
    def get_context_summary(self) -> str:
        """コンテキスト要約を取得"""
        if not self.summaries:
            return ""
        
        # 最近の要約を結合
        recent_summaries = self.summaries[-3:]  # 最近3つの要約
        
        context = "これまでの会話の要約:\n"
        for i, summary in enumerate(recent_summaries, 1):
            context += f"{i}. {summary['content']}\n"
        
        return context
    
    def get_full_context(self) -> str:
        """フルコンテキストを取得"""
        context_parts = []
        
        # 要約を追加
        if self.summaries:
            context_parts.append(self.get_context_summary())
        
        # 最近のメッセージを追加
        recent_messages = self.conversation_history[-5:]  # 最近5メッセージ
        for message in recent_messages:
            role_emoji = "👤" if message['role'] == 'user' else "🤖"
            context_parts.append(f"{role_emoji} {message['content']}")
        
        return "\n".join(context_parts)

class AdvancedKnowledgeSystem:
    """高度知識システム統合"""
    
    def __init__(self):
        self.name = "advanced_knowledge_system"
        self.description = "情報の正確性と回答の深さを極大化する統合システム"
        
        # サブシステム
        self.multi_search = MultiSearchAgent()
        self.self_reflection = SelfReflectionSystem()
        self.rag_system = AdvancedRAGSystem()
        self.context_manager = LongContextManager()
        
        # 知識統合設定
        self.source_priorities = {
            SourceType.LOCAL_KNOWLEDGE: 1.0,
            SourceType.ARXIV: 0.9,
            SourceType.DUCKDUCKGO: 0.7,
            SourceType.GITHUB: 0.6,
            SourceType.PERSONAL_MEMORY: 0.8
        }
    
    async def process_query(self, query: str, use_context: bool = True) -> Dict:
        """クエリ処理"""
        start_time = time.time()
        
        # コンテキスト取得
        context = ""
        if use_context:
            context = self.context_manager.get_full_context()
        
        # マルチソース検索
        search_results = await self.multi_search.search_all_sources(query)
        
        # RAG検索
        rag_results = self.rag_system.search_knowledge(query)
        
        # すべての結果を統合
        all_sources = search_results + rag_results
        
        # 優先度でソート
        all_sources.sort(key=lambda x: (
            self.source_priorities.get(x.source, 0.5) * x.confidence
        ), reverse=True)
        
        return {
            'query': query,
            'context': context,
            'sources': all_sources[:10],  # 上位10件
            'processing_time': time.time() - start_time,
            'source_counts': {
                source.value: len([s for s in all_sources if s.source == source])
                for source in SourceType
            }
        }
    
    def reflect_and_improve(self, answer: str, sources: List[SearchResult], query: str) -> Dict:
        """自己検証と改善"""
        reflection = self.self_reflection.reflect_on_answer(answer, sources, query)
        
        # 改善が必要な場合
        if reflection['needs_revision']:
            # 改善提案を元に再検索
            improvement_queries = self._generate_improvement_queries(reflection['improvements_suggested'])
            
            # 追加検索（非同期）
            # asyncio.create_task(self._additional_search(improvement_queries))
        
        return reflection
    
    def _generate_improvement_queries(self, improvements: List[str]) -> List[str]:
        """改善クエリを生成"""
        queries = []
        
        for improvement in improvements:
            if "信頼性" in improvement:
                queries.append("学術論文 公式ドキュメント")
            elif "完全性" in improvement:
                queries.append("詳細な情報 具体的な方法")
            elif "事実関係" in improvement:
                queries.append("公式情報 正確なデータ")
        
        return queries
    
    def add_conversation_message(self, role: str, content: str):
        """会話メッセージを追加"""
        self.context_manager.add_message(role, content)
    
    def get_system_prompt_enhancement(self) -> str:
        """システムプロンプト拡張"""
        context_summary = self.context_manager.get_context_summary()
        
        if context_summary:
            return f"\n\n【会話コンテキスト】\n{context_summary}\n\nこのコンテキストを考慮して回答してください。"
        
        return ""
    
    def get_statistics(self) -> Dict:
        """統計情報取得"""
        return {
            'multi_search': self.multi_search.search_stats,
            'self_reflection': {
                'total_reflections': len(self.self_reflection.reflection_history),
                'average_confidence': np.mean([
                    r['confidence_score'] for r in self.self_reflection.reflection_history
                ]) if self.self_reflection.reflection_history else 0.0
            },
            'rag_system': {
                'knowledge_items': len(self.rag_system.knowledge_items),
                'personal_memories': len([
                    item for item in self.rag_system.knowledge_items
                    if item.source == SourceType.PERSONAL_MEMORY
                ])
            },
            'context_manager': {
                'conversation_length': len(self.context_manager.conversation_history),
                'summary_count': len(self.context_manager.summaries)
            }
        }

# Streamlit GUIコンポーネント
def create_advanced_knowledge_gui(advanced_system: AdvancedKnowledgeSystem):
    """高度知識システムGUI"""
    st.subheader("🧠 高度知識システム")
    
    # 統計情報
    stats = advanced_system.get_statistics()
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "知識アイテム",
            stats['rag_system']['knowledge_items'],
            help="ナレッジベースのアイテム数"
        )
    
    with col2:
        st.metric(
            "自己検証回数",
            stats['self_reflection']['total_reflections'],
            help="実行された自己検証の回数"
        )
    
    with col3:
        st.metric(
            "平均信頼度",
            f"{stats['self_reflection']['average_confidence']:.2f}",
            help="回答の平均信頼度"
        )
    
    with col4:
        st.metric(
            "会話長",
            stats['context_manager']['conversation_length'],
            help="現在の会話メッセージ数"
        )
    
    # 検索ソース分布
    if stats['multi_search']:
        st.write("**検索ソース分布**")
        for source, count in stats['multi_search'].items():
            if source.startswith('source_') and count > 0:
                source_name = source.replace('source_', '').title()
                st.write(f"- {source_name}: {count}回")
    
    # ナレッジベース管理
    st.write("**ナレッジベース管理**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 ナレッジベース再スキャン"):
            advanced_system.rag_system._scan_knowledge_base()
            st.success("📚 ナレッジベースを再スキャンしました")
    
    with col2:
        if st.button("💾 インデックス保存"):
            advanced_system.rag_system._save_index()
            st.success("💾 インデックスを保存しました")
    
    # 個人メモリ追加
    st.write("**個人メモリ追加**")
    memory_content = st.text_area("メモリする内容", height=100)
    
    if st.button("🧠 メモリ追加") and memory_content:
        advanced_system.rag_system.add_personal_memory(
            memory_content,
            {'type': 'manual_addition', 'timestamp': datetime.now().isoformat()}
        )
        st.success("🧠 個人メモリを追加しました")
    
    # コンテキスト要約表示
    if st.button("📝 コンテキスト要約"):
        summary = advanced_system.context_manager.get_context_summary()
        if summary:
            st.info(summary)
        else:
            st.info("コンテキスト要約がありません")
    
    # 詳細統計
    if st.button("📊 詳細統計"):
        st.json(stats)
