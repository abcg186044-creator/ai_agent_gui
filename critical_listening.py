#!/usr/bin/env python3
"""
クリティカル・リスニングシステム
ユーザーの矛盾・曖昧さを検知し、質問を投げ返す高度な対話機能
"""

import streamlit as st
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class ContradictionType(Enum):
    """矛盾タイプの定義"""
    LOGICAL = "論理的矛盾"
    SPECIFICITY = "具体性の欠如"
    CONFLICT = "指示の衝突"
    AMBIGUITY = "曖昧さ"
    FEASIBILITY = "実現可能性"
    COMPLETENESS = "情報不足"

@dataclass
class ContradictionFinding:
    """矛盾検知結果"""
    type: ContradictionType
    severity: float  # 0.0-1.0
    description: str
    suggested_question: str
    context: str
    confidence: float

class CriticalListeningSystem:
    """クリティカル・リスニングシステム"""
    
    def __init__(self):
        self.name = "critical_listening"
        self.description = "ユーザーの矛盾・曖昧さを検知し、質問を投げ返すシステム"
        
        # 矛盾検知パターン
        self.contradiction_patterns = {
            ContradictionType.LOGICAL: [
                r"(?:しかし|だが|けど|でも).*(?:また|そして|さらに)",
                r"(?:全部|すべて).*(?:ない|除く|除いて)",
                r"(?:同時に|一緒に).*(?:別々に|個別に)",
                r"(?:常に|いつも).*(?:時々|たまに|時折)",
                r"(?:簡単に|容易に).*(?:難しい|困難|不可能)",
                r"(?:増やす|追加).*(?:減らす|削除|削減)"
            ],
            ContradictionType.SPECIFICITY: [
                r"(?:なんか|なんとなく|適当に).*(?:作って|実装して|やって)",
                r"(?:それっぽく|それらしい).*(?:デザインして|作成して)",
                r"(?:雰囲気|感じ).*(?:だけで|だけでいい)",
                r"(?:詳しくは後で|後で決める).*(?:まず|とりあえず)",
                r"(?:一般的な|普通の).*(?:だけでOK)"
            ],
            ContradictionType.CONFLICT: [
                r"(?:速く|早く).*(?:丁寧に|慎重に|注意深く)",
                r"(?:安く|コストを抑えて).*(?:高品質|最高の|最高級)",
                r"(?:シンプルに|簡単に).*(?:多機能|機能豊富|全部入り)",
                r"(?:すぐに|即座に).*(?:慎重に|よく検討して)",
                r"(?:自由に).*(?:制限付き|制約あり)"
            ],
            ContradictionType.AMBIGUITY: [
                r"(?:あれ|これ|それ).*(?:やつ|もの)",
                r"(?:たぶん|多分|おそらく).*((?:でしょ|だろう|はず))",
                r"(?:場合によって|時と場合による).*(?:適宜|適当に)",
                r"(?:ある程度|ある範囲で).*(?:調整する)",
                r"(?:可能な限り|できるだけ).*((?:頑張る|努力する))"
            ],
            ContradictionType.FEASIBILITY: [
                r"(?:1分で|瞬時に).*(?:完成|実装|作成)",
                r"(?:無料で|0円で).*(?:高品質|プロレベル)",
                r"(?:初心者でも).*(?:簡単に|誰でも).*(?:完璧に|完璧な)",
                r"(?:一度も|絶対に).*(?:失敗しない|エラーなし)",
                r"(?:すべて|全て).*(?:自動で|自動的に).*(?:解決する)"
            ],
            ContradictionType.COMPLETENESS: [
                r"(?:作って|実装して).*(?:ください|お願い)",
                r"(?:欲しいです|必要です).*(?:作成して)",
                r"(?:どうすれば|どのように).*(?:いいかわかりません",
                r"(?:助けて|教えて).*(?:ください",
                r"(?:具体的な|詳細な).*(?:方法は？|やり方は？)"
            ]
        }
        
        # 質問テンプレート
        self.question_templates = {
            ContradictionType.LOGICAL: [
                "ちょっと待って、さっきと言ってることが違う気がするぞ！{part1}と{part2}は両立できないんじゃないかな？どっちを優先するべきだ？",
                "おっと、ここで論理的に矛盾があるかも！{context}について、もう一度整理してくれないかな？",
                "論理的に考えると、{part1}と{part2}は同時に難しいかもしれない。どちらかを選ぶ必要があると思うんだけど、どう思う？"
            ],
            ContradictionType.SPECIFICITY: [
                "今の指示だと、{vague_part}が少し曖昧で動かないかもしれない。具体的にはどうしたい？",
                "{vague_part}について、もう少し詳しく教えてくれないかな？これだと僕も完璧には理解できないんだ。",
                "その「{vague_part}」っていう部分、具体的にどんなイメージ？例えば、こういう感じでいい？"
            ],
            ContradictionType.CONFLICT: [
                "おっと、{part1}と{part2}は少し相反する要求かもしれない！どっちを重視するべきかな？",
                "面白い組み合わせだね！{part1}と{part2}を両立させるには、ちょっと工夫が必要そうだ。どのくらいのバランスがいい？",
                "ここで難しい選択だね！{part1}と{part2}、どちらを優先したい？トレードオフを考えないといけないよ。"
            ],
            ContradictionType.AMBIGUITY: [
                "今の話、{ambiguous_part}の部分が少し曖昧で心配だ。もっと具体的に教えてくれると助かるよ！",
                "{ambiguous_part}について、もう少し明確にしてもらえるかな？これだと解釈が分かれちゃうかもしれない。",
                "その{ambiguous_part}っていう部分、例えばどんな状況を想定してる？具体的な例があるとイメージしやすいよ。"
            ],
            ContradictionType.FEASIBILITY: [
                "うーん、{unrealistic_part}は少し難しいかもしれないな。現実的な範囲で、どこまでなら可能だと思う？",
                "その{unrealistic_part}、すごい目標だね！でも現実的に考えて、少し調整した方がいいかもしれない。どう思う？",
                "その{unrealistic_part}、理想的だけど少し難しいかもしれない。代替案として、こういうのはどうかな？"
            ],
            ContradictionType.COMPLETENESS: [
                "その{missing_part}について、もう少し情報が欲しいな。これだと完璧なものは作れないかもしれない。",
                "良い質問だね！{missing_part}を決めないと先に進めないよ。一緒に考えよう！",
                "その{missing_part}、具体的にどうしたい？僕も一緒に最適解を探したいよ！"
            ]
        }
        
        # 感情対応テンプレート
        self.emotion_templates = {
            "confused": [
                "少し混乱しているみたいだね。落ち着いて、一つずつ確認していこうか。",
                "難しい話だよね。一緒に整理していこう！",
                "焦らないで、ゆっくり考えよう。僕が手伝うよ！"
            ],
            "tired": [
                "疲れているみたいだね。無理しないで、少しずつ進めようか。",
                "大変だね。休憩しながら進めようよ。",
                "疲れている時こそ、慎重に進めるべきだね。一緒に考えよう！"
            ],
            "anxious": [
                "不安に思う気持ち、わかるよ。でも大丈夫、僕がついてるから！",
                "焦る必要はないよ。一つずつ解決していこう。",
                "心配しないで、一緒に最適解を見つけよう！"
            ]
        }
        
        # 検知履歴
        self.analysis_history = []
    
    def analyze_user_input(self, user_input: str, context: Dict = None) -> List[ContradictionFinding]:
        """ユーザー入力を分析して矛盾を検知"""
        findings = []
        
        # 各矛盾タイプをチェック
        for contradiction_type, patterns in self.contradiction_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, user_input, re.IGNORECASE)
                
                for match in matches:
                    # 重大度と確信度を計算
                    severity = self._calculate_severity(contradiction_type, match.group(), user_input)
                    confidence = self._calculate_confidence(contradiction_type, match.group(), user_input)
                    
                    # 説明文と質問を生成
                    description = self._generate_description(contradiction_type, match.group(), user_input)
                    suggested_question = self._generate_question(contradiction_type, match.group(), user_input)
                    
                    finding = ContradictionFinding(
                        type=contradiction_type,
                        severity=severity,
                        description=description,
                        suggested_question=suggested_question,
                        context=match.group(),
                        confidence=confidence
                    )
                    
                    findings.append(finding)
        
        # 検知結果をフィルタリング
        filtered_findings = self._filter_findings(findings)
        
        # 履歴に保存
        self.analysis_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'findings': [f.__dict__ for f in filtered_findings],
            'context': context
        })
        
        return filtered_findings
    
    def _calculate_severity(self, contradiction_type: ContradictionType, matched_text: str, full_input: str) -> float:
        """重大度を計算"""
        base_severity = {
            ContradictionType.LOGICAL: 0.8,
            ContradictionType.CONFLICT: 0.7,
            ContradictionType.FEASIBILITY: 0.6,
            ContradictionType.COMPLETENESS: 0.5,
            ContradictionType.SPECIFICITY: 0.4,
            ContradictionType.AMBIGUITY: 0.3
        }
        
        severity = base_severity.get(contradiction_type, 0.5)
        
        # 文脈による調整
        if "絶対" in full_input or "必ず" in full_input:
            severity += 0.1
        
        if "ちょっと" in full_input or "少し" in full_input:
            severity -= 0.1
        
        return min(1.0, max(0.0, severity))
    
    def _calculate_confidence(self, contradiction_type: ContradictionType, matched_text: str, full_input: str) -> float:
        """確信度を計算"""
        base_confidence = 0.7
        
        # マッチしたテキストの長さで調整
        if len(matched_text) > 10:
            base_confidence += 0.1
        
        # 文脈の明確さで調整
        if "具体的に" in full_input or "詳細に" in full_input:
            base_confidence += 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def _generate_description(self, contradiction_type: ContradictionType, matched_text: str, full_input: str) -> str:
        """説明文を生成"""
        descriptions = {
            ContradictionType.LOGICAL: f"論理的に矛盾する表現が見つかりました: '{matched_text}'",
            ContradictionType.SPECIFICITY: f"具体性に欠ける表現が見つかりました: '{matched_text}'",
            ContradictionType.CONFLICT: f"相反する要求が見つかりました: '{matched_text}'",
            ContradictionType.AMBIGUITY: f"曖昧な表現が見つかりました: '{matched_text}'",
            ContradictionType.FEASIBILITY: f"実現可能性に疑問がある表現が見つかりました: '{matched_text}'",
            ContradictionType.COMPLETENESS: f"情報不足な部分が見つかりました: '{matched_text}'"
        }
        
        return descriptions.get(contradiction_type, "問題のある表現が見つかりました")
    
    def _generate_question(self, contradiction_type: ContradictionType, matched_text: str, full_input: str) -> str:
        """質問を生成"""
        templates = self.question_templates.get(contradiction_type, [])
        
        if not templates:
            return f"この「{matched_text}」について、もう少し詳しく教えてくれないかな？"
        
        # テンプレートを選択
        template = templates[0]  # 簡略化のため最初のテンプレートを使用
        
        # プレースホルダーを置換
        if contradiction_type == ContradictionType.LOGICAL:
            # 論理矛盾の場合、対立する部分を抽出
            parts = self._extract_contradictory_parts(matched_text)
            if len(parts) >= 2:
                return template.format(part1=parts[0], part2=parts[1], context=matched_text)
        
        elif contradiction_type in [ContradictionType.SPECIFICITY, ContradictionType.AMBIGUITY]:
            return template.format(vague_part=matched_text, ambiguous_part=matched_text)
        
        elif contradiction_type == ContradictionType.CONFLICT:
            parts = self._extract_conflicting_parts(matched_text)
            if len(parts) >= 2:
                return template.format(part1=parts[0], part2=parts[1])
        
        elif contradiction_type == ContradictionType.FEASIBILITY:
            return template.format(unrealistic_part=matched_text)
        
        elif contradiction_type == ContradictionType.COMPLETENESS:
            return template.format(missing_part=matched_text)
        
        return template.format(context=matched_text)
    
    def _extract_contradictory_parts(self, text: str) -> List[str]:
        """矛盾する部分を抽出"""
        # 簡易的な実装
        if "しかし" in text:
            parts = text.split("しかし")
            return [parts[0].strip(), parts[1].strip()]
        elif "だが" in text:
            parts = text.split("だが")
            return [parts[0].strip(), parts[1].strip()]
        return [text]
    
    def _extract_conflicting_parts(self, text: str) -> List[str]:
        """対立する部分を抽出"""
        # 簡易的な実装
        if "と" in text:
            parts = text.split("と")
            if len(parts) >= 2:
                return [parts[0].strip(), parts[1].strip()]
        return [text]
    
    def _filter_findings(self, findings: List[ContradictionFinding]) -> List[ContradictionFinding]:
        """検知結果をフィルタリング"""
        # 確信度でフィルタリング
        filtered = [f for f in findings if f.confidence > 0.5]
        
        # 重大度でソート
        filtered.sort(key=lambda x: x.severity, reverse=True)
        
        # 上位3つに制限
        return filtered[:3]
    
    def should_ask_clarification(self, findings: List[ContradictionFinding], threshold: float = 0.6) -> bool:
        """質問すべきか判定"""
        if not findings:
            return False
        
        # 最も重大な問題が閾値を超えているか
        max_severity = max(f.severity for f in findings)
        return max_severity > threshold
    
    def generate_clarification_question(self, findings: List[ContradictionFinding], user_emotion: str = None) -> str:
        """明確化質問を生成"""
        if not findings:
            return ""
        
        # 最も重大な問題を選択
        primary_finding = findings[0]
        
        # 感情対応プレフィックス
        emotion_prefix = ""
        if user_emotion and user_emotion in self.emotion_templates:
            templates = self.emotion_templates[user_emotion]
            emotion_prefix = templates[0] + " "
        
        # 質問を構成
        base_question = primary_finding.suggested_question
        
        # 親友としての口調を調整
        friendly_question = self._adjust_to_friendly_tone(base_question)
        
        return emotion_prefix + friendly_question
    
    def _adjust_to_friendly_tone(self, question: str) -> str:
        """親友らしい口調に調整"""
        # 敬語をカジュアルに
        question = question.replace("ください", "くれないかな")
        question = question.replace("教えてください", "教えてくれないかな")
        question = question.replace("説明してください", "説明してくれないかな")
        
        # 硬い表現を柔らかく
        question = question.replace("必要があります", "必要なんだよ")
        question = question.replace("確認してください", "確認してほしいな")
        
        return question
    
    def get_analysis_summary(self) -> Dict:
        """分析サマリーを取得"""
        if not self.analysis_history:
            return {
                'total_analyses': 0,
                'contradiction_types': {},
                'average_severity': 0.0,
                'most_common_type': None
            }
        
        # 矛盾タイプの集計
        type_counts = {}
        total_severity = 0.0
        
        for analysis in self.analysis_history:
            for finding in analysis['findings']:
                finding_type = finding['type']
                type_counts[finding_type] = type_counts.get(finding_type, 0) + 1
                total_severity += finding['severity']
        
        # 最も一般的なタイプ
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        
        return {
            'total_analyses': len(self.analysis_history),
            'contradiction_types': type_counts,
            'average_severity': total_severity / sum(len(a['findings']) for a in self.analysis_history) if self.analysis_history else 0.0,
            'most_common_type': most_common_type
        }

class AskClarificationTool:
    """聞き返し専用ツール"""
    
    def __init__(self, critical_listening: CriticalListeningSystem):
        self.name = "ask_clarification"
        self.description = "ユーザーに明確化質問を投げかけるツール"
        self.critical_listening = critical_listening
    
    def run(self, question: str) -> str:
        """質問を実行"""
        try:
            # 質問を保存
            self.critical_listening.analysis_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'clarification_question',
                'question': question
            })
            
            return f"🤔 質問: {question}"
            
        except Exception as e:
            return f"質問エラー: {str(e)}"

# Streamlit GUIコンポーネント
def create_critical_listening_gui(critical_system: CriticalListeningSystem):
    """クリティカル・リスニングGUIを作成"""
    st.subheader("🧠 クリティカル・リスニング")
    
    # 分析サマリー
    summary = critical_system.get_analysis_summary()
    
    # メトリクス表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "分析回数",
            summary['total_analyses'],
            help="ユーザー入力の分析回数"
        )
    
    with col2:
        st.metric(
            "平均重大度",
            f"{summary['average_severity']:.2f}",
            help="検出された問題の平均重大度"
        )
    
    with col3:
        most_common = summary['most_common_type'] or "なし"
        st.metric(
            "最も多い問題",
            most_common,
            help="最も頻繁に検出される問題タイプ"
        )
    
    # 矛盾タイプ分布
    if summary['contradiction_types']:
        st.write("**問題タイプ分布**")
        for type_name, count in summary['contradiction_types'].items():
            st.write(f"- {type_name}: {count}回")
    
    # 最近の分析履歴
    if st.button("📋 分析履歴"):
        if critical_system.analysis_history:
            recent_analyses = critical_system.analysis_history[-5:]
            for i, analysis in enumerate(recent_analyses, 1):
                with st.expander(f"分析 {i}: {analysis['timestamp'][:19]}"):
                    st.write(f"入力: {analysis.get('user_input', 'N/A')[:100]}...")
                    
                    findings = analysis.get('findings', [])
                    if findings:
                        for finding in findings:
                            st.write(f"**{finding['type']}** (重大度: {finding['severity']:.2f})")
                            st.write(f"説明: {finding['description']}")
                            st.write(f"質問: {finding['suggested_question']}")
                            st.divider()
        else:
            st.info("分析履歴がありません")
    
    # テスト入力
    st.write("**テスト入力**")
    test_input = st.text_area(
        "矛盾を含むテキストを入力",
        value="簡単に高品質なものをすぐに作ってください",
        height=100
    )
    
    if st.button("🧪 分析テスト"):
        findings = critical_system.analyze_user_input(test_input)
        
        if findings:
            st.success(f"🔍 {len(findings)}個の問題を検出しました")
            
            for finding in findings:
                with st.expander(f"🚨 {finding.type.value} (重大度: {finding.severity:.2f})"):
                    st.write(f"**説明**: {finding.description}")
                    st.write(f"**文脈**: {finding.context}")
                    st.write(f"**提案質問**: {finding.suggested_question}")
                    st.write(f"**確信度**: {finding.confidence:.2f}")
        else:
            st.info("問題は検出されませんでした")
    
    # 設定
    st.write("**設定**")
    threshold = st.slider(
        "質問閾値",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.1,
        help="この値を超える重大度の問題が検出された場合に質問します"
    )
    
    if st.button("💾 設定保存"):
        st.success("設定を保存しました")
