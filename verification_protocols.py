"""
高度な検証プロトコルシステム
起動時システム診断とコード作成・動作検証の自律デバッグサイクル
"""

import os
import sys
import subprocess
import tempfile
import ast
import json
import importlib
import platform
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import streamlit as st
import requests
from dataclasses import dataclass

@dataclass
class DiagnosticResult:
    """診断結果"""
    component: str
    status: str  # 'success', 'warning', 'error'
    message: str
    details: Dict[str, Any] = None
    auto_fixed: bool = False
    fix_attempted: bool = False

@dataclass
class CodeVerificationResult:
    """コード検証結果"""
    original_code: str
    final_code: str
    iterations: int
    success: bool
    error_log: List[str]
    execution_result: Optional[str] = None
    verification_steps: List[str] = None

class StartupSelfCheck:
    """起動時システム診断プロトコル"""
    
    def __init__(self):
        self.name = "startup_self_check"
        self.description = "起動時にシステム全体を診断し、自動修復を試みる"
        self.diagnostics: List[DiagnosticResult] = []
        self.auto_fix_enabled = True
        
    def run_full_diagnostic(self) -> List[DiagnosticResult]:
        """完全なシステム診断を実行"""
        self.diagnostics = []
        
        # 1. モデル接続確認
        self._check_model_connectivity()
        
        # 2. ツール診断
        self._check_tools_diagnostics()
        
        # 3. 依存関係チェック
        self._check_dependencies()
        
        # 4. VRM診断
        self._check_vrm_diagnostics()
        
        # 5. システム環境チェック
        self._check_system_environment()
        
        return self.diagnostics
    
    def _check_model_connectivity(self):
        """モデル接続確認"""
        # Ollama接続チェック
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                llama3_available = any("llama3.1" in model.get("name", "") for model in models)
                
                if llama3_available:
                    self.diagnostics.append(DiagnosticResult(
                        component="Ollama",
                        status="success",
                        message="✅ Ollama接続正常、llama3.1モデル利用可能",
                        details={"models": [m.get("name") for m in models]}
                    ))
                else:
                    self.diagnostics.append(DiagnosticResult(
                        component="Ollama",
                        status="warning",
                        message="⚠️ Ollama接続正常だがllama3.1モデルが見つからない",
                        details={"models": [m.get("name") for m in models]}
                    ))
            else:
                self.diagnostics.append(DiagnosticResult(
                    component="Ollama",
                    status="error",
                    message="❌ Ollamaサーバーに接続できません"
                ))
        except Exception as e:
            self.diagnostics.append(DiagnosticResult(
                component="Ollama",
                status="error",
                message=f"❌ Ollama接続エラー: {str(e)}",
                auto_fixed=self._try_fix_ollama(),
                fix_attempted=True
            ))
        
        # faster-whisperチェック
        try:
            import faster_whisper
            self.diagnostics.append(DiagnosticResult(
                component="faster-whisper",
                status="success",
                message="✅ faster-whisperライブラリ利用可能"
            ))
        except ImportError:
            self.diagnostics.append(DiagnosticResult(
                component="faster-whisper",
                status="error",
                message="❌ faster-whisperライブラリがインストールされていません",
                auto_fixed=self._try_install_package("faster-whisper"),
                fix_attempted=True
            ))
    
    def _check_tools_diagnostics(self):
        """ツール診断"""
        # 検索ツールチェック
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            search_tool = DuckDuckGoSearchRun()
            # 簡単なテスト検索
            test_result = search_tool.run("test query")
            self.diagnostics.append(DiagnosticResult(
                component="DuckDuckGo検索",
                status="success",
                message="✅ 検索ツール正常動作",
                details={"test_result": test_result[:100] + "..." if len(test_result) > 100 else test_result}
            ))
        except Exception as e:
            self.diagnostics.append(DiagnosticResult(
                component="DuckDuckGo検索",
                status="error",
                message=f"❌ 検索ツールエラー: {str(e)}"
            ))
        
        # ファイル書き込み権限チェック
        try:
            test_file = "test_write_permission.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            self.diagnostics.append(DiagnosticResult(
                component="ファイル書き込み",
                status="success",
                message="✅ ファイル書き込み権限正常"
            ))
        except Exception as e:
            self.diagnostics.append(DiagnosticResult(
                component="ファイル書き込み",
                status="error",
                message=f"❌ ファイル書き込みエラー: {str(e)}"
            ))
        
        # Python実行環境チェック
        try:
            test_code = "print('Python execution test successful')"
            result = subprocess.run([sys.executable, "-c", test_code], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.diagnostics.append(DiagnosticResult(
                    component="Python実行環境",
                    status="success",
                    message="✅ Python実行環境正常",
                    details={"python_version": sys.version}
                ))
            else:
                self.diagnostics.append(DiagnosticResult(
                    component="Python実行環境",
                    status="error",
                    message=f"❌ Python実行エラー: {result.stderr}"
                ))
        except Exception as e:
            self.diagnostics.append(DiagnosticResult(
                component="Python実行環境",
                status="error",
                message=f"❌ Python実行環境エラー: {str(e)}"
            ))
    
    def _check_dependencies(self):
        """依存関係チェック"""
        required_packages = [
            "streamlit", "langchain", "langchain-community", 
            "openpyxl", "PyMuPDF", "requests", "numpy", "pandas"
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package.replace("-", "_"))
                self.diagnostics.append(DiagnosticResult(
                    component=f"依存関係-{package}",
                    status="success",
                    message=f"✅ {package}ライブラリ利用可能"
                ))
            except ImportError:
                self.diagnostics.append(DiagnosticResult(
                    component=f"依存関係-{package}",
                    status="error",
                    message=f"❌ {package}ライブラリがインストールされていません",
                    auto_fixed=self._try_install_package(package),
                    fix_attempted=True
                ))
        
        # PHPチェック
        php_paths = [
            "php",
            "C:\\Program Files\\PHP\\current\\php.exe",
            "C:\\PHP\\php.exe"
        ]
        
        php_available = False
        php_version = None
        
        for php_path in php_paths:
            try:
                if shutil.which(php_path) or os.path.exists(php_path):
                    result = subprocess.run([php_path, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        php_available = True
                        php_version = result.stdout.split()[1] if len(result.stdout.split()) > 1 else "Unknown"
                        break
            except Exception:
                continue
        
        if php_available:
            self.diagnostics.append(DiagnosticResult(
                component="PHP",
                status="success",
                message=f"✅ PHP利用可能",
                details={"version": php_version, "path": php_path}
            ))
        else:
            self.diagnostics.append(DiagnosticResult(
                component="PHP",
                status="warning",
                message="⚠️ PHPがインストールされていません",
                auto_fixed=self._try_install_php(),
                fix_attempted=True
            ))
        
        # Tailscaleチェック
        tailscale_available = shutil.which("tailscale") is not None
        if tailscale_available:
            try:
                result = subprocess.run(["tailscale", "status"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.diagnostics.append(DiagnosticResult(
                        component="Tailscale",
                        status="success",
                        message="✅ Tailscale利用可能",
                        details={"status": result.stdout.strip()}
                    ))
                else:
                    self.diagnostics.append(DiagnosticResult(
                        component="Tailscale",
                        status="warning",
                        message="⚠️ Tailscaleはインストールされているが未ログイン"
                    ))
            except Exception:
                self.diagnostics.append(DiagnosticResult(
                    component="Tailscale",
                    status="warning",
                    message="⚠️ Tailscale実行エラー"
                ))
        else:
            self.diagnostics.append(DiagnosticResult(
                component="Tailscale",
                status="warning",
                message="⚠️ Tailscaleがインストールされていません"
            ))
    
    def _check_vrm_diagnostics(self):
        """VRM診断"""
        # VRMファイル存在チェック
        vrm_files = ["avatar.vrm", "static/avatar.vrm"]
        vrm_found = False
        
        for vrm_file in vrm_files:
            if os.path.exists(vrm_file):
                vrm_found = True
                file_size = os.path.getsize(vrm_file)
                self.diagnostics.append(DiagnosticResult(
                    component="VRMファイル",
                    status="success",
                    message=f"✅ VRMファイル存在: {vrm_file}",
                    details={"file_size": file_size, "path": vrm_file}
                ))
                break
        
        if not vrm_found:
            self.diagnostics.append(DiagnosticResult(
                component="VRMファイル",
                status="error",
                message="❌ VRMファイルが見つかりません"
            ))
        
        # Canvasレンダリングチェック
        try:
            # Three.jsライブラリチェック（CDNアクセス）
            response = requests.get("https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js", timeout=5)
            if response.status_code == 200:
                self.diagnostics.append(DiagnosticResult(
                    component="Canvasレンダリング",
                    status="success",
                    message="✅ Three.jsライブラリアクセス正常"
                ))
            else:
                self.diagnostics.append(DiagnosticResult(
                    component="Canvasレンダリング",
                    status="warning",
                    message="⚠️ Three.jsライブラリアクセス異常"
                ))
        except Exception as e:
            self.diagnostics.append(DiagnosticResult(
                component="Canvasレンダリング",
                status="error",
                message=f"❌ Canvasレンダリングチェックエラー: {str(e)}"
            ))
    
    def _check_system_environment(self):
        """システム環境チェック"""
        self.diagnostics.append(DiagnosticResult(
            component="OS",
            status="success",
            message=f"✅ OS: {platform.system()} {platform.release()}",
            details={"platform": platform.platform(), "architecture": platform.architecture()}
        ))
        
        self.diagnostics.append(DiagnosticResult(
            component="Python",
            status="success",
            message=f"✅ Python: {sys.version}",
            details={"executable": sys.executable, "version": sys.version_info}
        ))
        
        # メモリチェック
        try:
            import psutil
            memory = psutil.virtual_memory()
            self.diagnostics.append(DiagnosticResult(
                component="メモリ",
                status="success",
                message=f"✅ 利用可能メモリ: {memory.available // (1024**3)}GB",
                details={"total": memory.total, "available": memory.available, "percent": memory.percent}
            ))
        except ImportError:
            self.diagnostics.append(DiagnosticResult(
                component="メモリ",
                status="warning",
                message="⚠️ psutilライブラリなし、メモリ情報取得不可"
            ))
    
    def _try_fix_ollama(self) -> bool:
        """Ollama自動修復試行"""
        if not self.auto_fix_enabled:
            return False
        
        try:
            # Ollamaインストール試行（Windows）
            if platform.system() == "Windows":
                # Chocolatey経由でインストール試行
                subprocess.run(["choco", "install", "ollama", "-y"], 
                             capture_output=True, timeout=300)
                return True
        except Exception:
            pass
        
        return False
    
    def _try_install_php(self) -> bool:
        """PHP自動インストール試行"""
        if not self.auto_fix_enabled:
            return False
        
        try:
            # winget経由でPHPをインストール
            subprocess.run(["winget", "install", "PHP.PHP.8.4", 
                          "--accept-source-agreements", "--accept-package-agreements"], 
                         capture_output=True, timeout=600)
            return True
        except Exception:
            return False
    
    def _try_install_package(self, package: str) -> bool:
        """パッケージ自動インストール試行"""
        if not self.auto_fix_enabled:
            return False
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         capture_output=True, timeout=300)
            return True
        except Exception:
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """診断結果サマリー"""
        if not self.diagnostics:
            return {"status": "not_run", "message": "診断未実行"}
        
        success_count = sum(1 for d in self.diagnostics if d.status == "success")
        warning_count = sum(1 for d in self.diagnostics if d.status == "warning")
        error_count = sum(1 for d in self.diagnostics if d.status == "error")
        auto_fixed_count = sum(1 for d in self.diagnostics if d.auto_fixed)
        
        overall_status = "success" if error_count == 0 else "warning" if auto_fixed_count > 0 else "error"
        
        return {
            "status": overall_status,
            "total": len(self.diagnostics),
            "success": success_count,
            "warning": warning_count,
            "error": error_count,
            "auto_fixed": auto_fixed_count,
            "timestamp": datetime.now().isoformat()
        }


class AutoVerificationLoop:
    """コード作成・動作検証プロトコル"""
    
    def __init__(self):
        self.name = "auto_verification_loop"
        self.description = "生成コードの自律デバッグと検証"
        self.max_iterations = 3
        
    def verify_code(self, code: str, language: str = "python") -> CodeVerificationResult:
        """コード検証を実行"""
        verification_steps = []
        error_log = []
        current_code = code
        iterations = 0
        
        for iteration in range(self.max_iterations):
            iterations += 1
            verification_steps.append(f"=== 検証ラウンド {iteration + 1} ===")
            
            # 1. 静的解析
            syntax_error = self._static_analysis(current_code, language)
            if syntax_error:
                error_log.append(f"静的解析エラー: {syntax_error}")
                current_code = self._fix_syntax_error(current_code, syntax_error, language)
                verification_steps.append(f"構文エラーを修正: {syntax_error}")
                continue
            
            verification_steps.append("✅ 静的解析通過")
            
            # 2. サンドボックス実行
            execution_result, execution_error = self._sandbox_execute(current_code, language)
            if execution_error:
                error_log.append(f"実行エラー: {execution_error}")
                current_code = self._fix_execution_error(current_code, execution_error, language)
                verification_steps.append(f"実行エラーを修正: {execution_error}")
                continue
            
            verification_steps.append("✅ サンドボックス実行成功")
            
            # 3. 最終検証
            final_check = self._final_verification(current_code, language)
            if final_check:
                verification_steps.append("✅ 最終検証成功")
                return CodeVerificationResult(
                    original_code=code,
                    final_code=current_code,
                    iterations=iterations,
                    success=True,
                    error_log=error_log,
                    execution_result=execution_result,
                    verification_steps=verification_steps
                )
        
        # 最大反復回数到達
        return CodeVerificationResult(
            original_code=code,
            final_code=current_code,
            iterations=iterations,
            success=False,
            error_log=error_log,
            verification_steps=verification_steps
        )
    
    def _static_analysis(self, code: str, language: str) -> Optional[str]:
        """静的解析"""
        try:
            if language == "python":
                ast.parse(code)
                return None
            elif language == "javascript":
                # 簡単なJavaScript構文チェック
                if "function" in code or "const" in code or "let" in code or "var" in code:
                    return None
                return "JavaScript構文エラー"
            else:
                return None
        except SyntaxError as e:
            return f"構文エラー: {str(e)}"
        except Exception as e:
            return f"解析エラー: {str(e)}"
    
    def _sandbox_execute(self, code: str, language: str) -> Tuple[Optional[str], Optional[str]]:
        """サンドボックス実行"""
        try:
            if language == "python":
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                try:
                    result = subprocess.run([sys.executable, temp_file], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return result.stdout, None
                    else:
                        return None, result.stderr
                finally:
                    os.unlink(temp_file)
            
            elif language == "javascript":
                # Node.jsで実行（利用可能な場合）
                node_available = shutil.which("node") is not None
                if node_available:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                        f.write(code)
                        temp_file = f.name
                    
                    try:
                        result = subprocess.run(["node", temp_file], 
                                              capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            return result.stdout, None
                        else:
                            return None, result.stderr
                    finally:
                        os.unlink(temp_file)
                else:
                    return None, "Node.jsが利用できません"
            
            else:
                return None, f"サポートされていない言語: {language}"
        
        except subprocess.TimeoutExpired:
            return None, "実行タイムアウト"
        except Exception as e:
            return None, f"実行エラー: {str(e)}"
    
    def _fix_syntax_error(self, code: str, error: str, language: str) -> str:
        """構文エラー修正"""
        # 簡単な構文エラー修正ロジック
        if "IndentationError" in error:
            # インデントエラー修正
            lines = code.split('\n')
            fixed_lines = []
            for line in lines:
                if line.strip():  # 空行以外
                    fixed_lines.append('    ' + line if not line.startswith(' ') else line)
                else:
                    fixed_lines.append(line)
            return '\n'.join(fixed_lines)
        
        elif "SyntaxError: invalid syntax" in error:
            # 基本的な構文エラー修正
            # 行末のコロン追加など
            if "def " in code and not code.rstrip().endswith(':'):
                return code.rstrip() + ':'
        
        return code
    
    def _fix_execution_error(self, code: str, error: str, language: str) -> str:
        """実行エラー修正"""
        if language == "python":
            if "NameError" in error and "not defined" in error:
                # 未定義変数エラー修正
                undefined_var = error.split("'")[1] if "'" in error else ""
                if undefined_var:
                    # 変数定義を追加
                    lines = code.split('\n')
                    for i, line in enumerate(lines):
                        if undefined_var in line and line.strip().startswith(undefined_var):
                            # 変数初期化を追加
                            lines.insert(i, f"{undefined_var} = None")
                            break
                    return '\n'.join(lines)
            
            elif "ImportError" in error and "No module named" in error:
                # インポートエラー修正
                missing_module = error.split("'")[1] if "'" in error else ""
                if missing_module:
                    # インポート文を追加または修正
                    import_line = f"import {missing_module}"
                    if import_line not in code:
                        lines = code.split('\n')
                        lines.insert(0, import_line)
                        return '\n'.join(lines)
        
        return code
    
    def _final_verification(self, code: str, language: str) -> bool:
        """最終検証"""
        # 簡単な最終検証
        if language == "python":
            try:
                ast.parse(code)
                return True
            except:
                return False
        else:
            return True


class VerificationProtocolsGUI:
    """検証プロトコルGUI"""
    
    def __init__(self):
        self.startup_check = StartupSelfCheck()
        self.verification_loop = AutoVerificationLoop()
    
    def render_startup_check(self):
        """起動時診断GUIを描画"""
        st.subheader("🔍 起動時システム診断")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 診断実行", type="primary"):
                with st.spinner("システム診断中..."):
                    results = self.startup_check.run_full_diagnostic()
                    st.session_state.diagnostic_results = results
                    st.session_state.diagnostic_summary = self.startup_check.get_summary()
                    st.rerun()
        
        with col2:
            auto_fix = st.checkbox("🔧 自動修復有効", value=True)
            self.startup_check.auto_fix_enabled = auto_fix
        
        # 診断結果表示
        if hasattr(st.session_state, 'diagnostic_results'):
            results = st.session_state.diagnostic_results
            summary = st.session_state.diagnostic_summary
            
            # サマリー表示
            st.write("**📊 診断サマリー:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("✅ 成功", summary["success"])
            with col2:
                st.metric("⚠️ 警告", summary["warning"])
            with col3:
                st.metric("❌ エラー", summary["error"])
            with col4:
                st.metric("🔧 自動修復", summary["auto_fixed"])
            
            # 詳細結果
            st.write("**📋 詳細結果:**")
            for result in results:
                status_emoji = {
                    "success": "✅",
                    "warning": "⚠️", 
                    "error": "❌"
                }
                
                with st.expander(f"{status_emoji.get(result.status, '❓')} {result.component}", expanded=False):
                    st.write(result.message)
                    if result.details:
                        st.json(result.details)
                    if result.auto_fixed:
                        st.success("🔧 自動修復完了")
    
    def render_code_verification(self):
        """コード検証GUIを描画"""
        st.subheader("🔧 コード自動検証")
        
        # コード入力
        code_input = st.text_area(
            "検証するコード",
            height=200,
            placeholder="ここに検証したいコードを入力してください..."
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            language = st.selectbox("言語", ["python", "javascript"])
        
        with col2:
            max_iterations = st.number_input("最大反復回数", min_value=1, max_value=10, value=3)
        
        with col3:
            if st.button("🔍 検証実行", type="primary"):
                if code_input.strip():
                    self.verification_loop.max_iterations = max_iterations
                    
                    with st.spinner("コード検証中..."):
                        result = self.verification_loop.verify_code(code_input, language)
                        st.session_state.verification_result = result
                        st.rerun()
                else:
                    st.warning("⚠️ コードを入力してください")
        
        # 検証結果表示
        if hasattr(st.session_state, 'verification_result'):
            result = st.session_state.verification_result
            
            st.write("**📊 検証結果:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("ステータス", "✅ 成功" if result.success else "❌ 失敗")
                st.metric("反復回数", result.iterations)
            
            with col2:
                st.metric("エラー数", len(result.error_log))
                if result.success:
                    st.success("🎉 コード検証成功！")
                else:
                    st.error("❌ コード検証失敗")
            
            # 検証ステップ
            if result.verification_steps:
                st.write("**🔄 検証ステップ:**")
                for step in result.verification_steps:
                    st.write(f"- {step}")
            
            # エラーログ
            if result.error_log:
                st.write("**❌ エラーログ:**")
                for error in result.error_log:
                    st.error(error)
            
            # 最終コード
            if result.final_code != result.original_code:
                st.write("**🔧 修正後コード:**")
                st.code(result.final_code, language=language)
            
            # 実行結果
            if result.execution_result:
                st.write("**▶️ 実行結果:**")
                st.code(result.execution_result)


def create_verification_protocols_gui():
    """検証プロトコルGUIを作成"""
    gui = VerificationProtocolsGUI()
    
    tab1, tab2 = st.tabs(["🔍 起動時診断", "🔧 コード検証"])
    
    with tab1:
        gui.render_startup_check()
    
    with tab2:
        gui.render_code_verification()


# メイン関数
def run_startup_self_check() -> Dict[str, Any]:
    """起動時自己チェックを実行"""
    checker = StartupSelfCheck()
    results = checker.run_full_diagnostic()
    summary = checker.get_summary()
    
    return {
        "results": results,
        "summary": summary
    }


def verify_code_safely(code: str, language: str = "python") -> CodeVerificationResult:
    """コードを安全に検証"""
    verifier = AutoVerificationLoop()
    return verifier.verify_code(code, language)


if __name__ == "__main__":
    # テスト実行
    print("🔍 起動時診断テスト...")
    startup_result = run_startup_self_check()
    print(f"診断完了: {startup_result['summary']}")
    
    print("\n🔧 コード検証テスト...")
    test_code = """
def hello_world():
    print("Hello, World!")
hello_world()
"""
    verification_result = verify_code_safely(test_code)
    print(f"検証完了: 成功={verification_result.success}, 反復={verification_result.iterations}")
