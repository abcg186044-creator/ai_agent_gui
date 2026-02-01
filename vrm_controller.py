#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRMアバター制御クラス
"""

import base64
from pathlib import Path

class VRMAvatarController:
    def __init__(self):
        self.vrm_path = self._find_vrm_file()
        self.current_personality = "friendly_engineer"
        self.expressions = {
            "friendly_engineer": "happy",
            "split_personality": "joy", 
            "expert": "neutral"
        }
    
    def _get_vrm_base64(self):
        """VRMファイルをbase64エンコードして返す"""
        vrm_file_path = self._find_vrm_file()
        
        if vrm_file_path:
            try:
                if vrm_file_path.startswith("/static/"):
                    vrm_file_path = vrm_file_path.replace("/static/", "static/")
                
                print("🎭 VRMファイルを読み込み: " + vrm_file_path)
                
                with open(vrm_file_path, "rb") as f:
                    vrm_data = f.read()
                    encoded_data = base64.b64encode(vrm_data).decode('utf-8')
                    print("✅ VRMファイルのbase64エンコード成功: " + str(len(encoded_data)) + " 文字")
                    return encoded_data
                        
            except Exception as e:
                print("❌ VRMファイルのbase64エンコードエラー: " + str(e))
        
        print("❌ VRMファイルが見つかりません")
        return None
    
    def _get_vrm_binary_array(self):
        """VRMファイルをバイナリ配列として返す"""
        vrm_base64 = self._get_vrm_base64()
        if not vrm_base64:
            return ""
        
        try:
            import base64
            binary_data = base64.b64decode(vrm_base64)
            
            chunk_size = 1000
            array_parts = []
            
            for i in range(0, len(binary_data), chunk_size):
                chunk = binary_data[i:i+chunk_size]
                chunk_str = ",".join(str(b) for b in chunk)
                array_parts.append(chunk_str)
            
            array_literal = "new Uint8Array([" + ",".join(array_parts) + "])"
            print("✅ VRMバイナリ配列生成成功: " + str(len(binary_data)) + " バイト")
            return array_literal
            
        except Exception as e:
            print("❌ VRMバイナリ配列生成エラー: " + str(e))
            return ""
    
    def _find_vrm_file(self):
        """VRMファイルを検索"""
        desktop_ezo_subfolder = Path("C:/Users/GALLE/Desktop/EzoMomonga_Free/EzoMomonga_Free")
        desktop_ezo_path = Path("C:/Users/GALLE/Desktop/EzoMomonga_Free")
        static_path = Path("static")
        assets_vrm_path = Path("assets/vrm")
        
        if desktop_ezo_subfolder.exists():
            for vrm_file in desktop_ezo_subfolder.glob("*.vrm"):
                print(f"✅ EzoMomonga_FreeサブフォルダのVRMファイルを検出: {vrm_file}")
                static_path.mkdir(exist_ok=True)
                static_vrm = static_path / vrm_file.name
                if not static_vrm.exists():
                    import shutil
                    shutil.copy2(vrm_file, static_vrm)
                return f"/static/{vrm_file.name}"
        
        if desktop_ezo_path.exists():
            for vrm_file in desktop_ezo_path.glob("*.vrm"):
                print(f"✅ デスクトップのVRMファイルを検出: {vrm_file}")
                static_path.mkdir(exist_ok=True)
                static_vrm = static_path / vrm_file.name
                if not static_vrm.exists():
                    import shutil
                    shutil.copy2(vrm_file, static_vrm)
                return f"/static/{vrm_file.name}"
        
        if static_path.exists():
            for vrm_file in static_path.glob("*.vrm"):
                print(f"✅ staticディレクトリのVRMファイルを検出: {vrm_file}")
                return f"/static/{vrm_file.name}"
        
        if assets_vrm_path.exists():
            for vrm_file in assets_vrm_path.glob("*.vrm"):
                print(f"✅ assets/vrmディレクトリのVRMファイルを検出: {vrm_file}")
                static_path.mkdir(exist_ok=True)
                static_vrm = static_path / vrm_file.name
                if not static_vrm.exists():
                    import shutil
                    shutil.copy2(vrm_file, static_vrm)
                return f"/static/{vrm_file.name}"
        
        print("❌ VRMファイルが見つかりませんでした")
        return None
    
    def update_personality(self, personality):
        self.current_personality = personality
        return self.expressions.get(personality, "neutral")
    
    def set_personality(self, personality):
        return self.update_personality(personality)
    
    def _check_vrm_command(self, text):
        """VRM制御コマンドをチェック"""
        vrm_commands = {
            "アバターを非表示": {"action": "hide", "target": "avatar"},
            "アバターを表示": {"action": "show", "target": "avatar"},
            "アバターを消して": {"action": "hide", "target": "avatar"},
            "アバターを出して": {"action": "show", "target": "avatar"},
            "VRMを非表示": {"action": "hide", "target": "avatar"},
            "VRMを表示": {"action": "show", "target": "avatar"},
            "自分を隠して": {"action": "hide", "target": "avatar"},
            "自分を見せて": {"action": "show", "target": "avatar"},
            "大きくして": {"action": "scale", "target": "avatar", "value": 1.2},
            "小さくして": {"action": "scale", "target": "avatar", "value": 0.8},
            "拡大して": {"action": "scale", "target": "avatar", "value": 1.2},
            "縮小して": {"action": "scale", "target": "avatar", "value": 0.8},
            "回転して": {"action": "rotate", "target": "avatar", "value": 45},
            "左に回転": {"action": "rotate", "target": "avatar", "value": -45},
            "右に回転": {"action": "rotate", "target": "avatar", "value": 45},
            "表情を変えて": {"action": "expression", "target": "avatar"},
            "笑って": {"action": "expression", "target": "avatar", "value": "happy"},
            "喜んで": {"action": "expression", "target": "avatar", "value": "joy"},
            "普通の表情": {"action": "expression", "target": "avatar", "value": "neutral"},
            "悲しい表情": {"action": "expression", "target": "avatar", "value": "sad"},
            "怒って": {"action": "expression", "target": "avatar", "value": "angry"},
        }
        
        for command, action in vrm_commands.items():
            if command in text:
                return action
        return None
    
    def _execute_vrm_command(self, command):
        """VRM制御コマンドを実行"""
        action = command["action"]
        target = command["target"]
        
        if action == "hide":
            return {"action": "hide", "message": "VRMアバターを非表示にしました。"}
        elif action == "show":
            return {"action": "show", "message": "VRMアバターを表示しました。"}
        elif action == "scale":
            return {"action": "scale", "value": command["value"], "message": f"VRMアバターを{command['value']}倍に拡大縮小しました。"}
        elif action == "rotate" or action == "rotation":
            rot_value = command.get("value", 45)
            return {"action": "rotation", "value": rot_value, "message": f"VRMアバターを{rot_value}度回転させました。"}
        elif action == "expression":
            expression = command.get("value", "happy")
            return {"action": "expression", "value": expression, "message": f"VRMアバターの表情を{expression}に変更しました。"}
        
        return {"action": "unknown", "message": "VRMコマンドを実行しました。"}
    
    def get_vrm_html(self, vrm_scale=1.0, vrm_rotation=0, vrm_expression="neutral"):
        """VRM HTMLを生成"""
        vrm_base64 = self._get_vrm_base64()
        if not vrm_base64:
            return """
            <div style="width: 100%; height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                <div style="text-align: center; color: #666;">
                    <h3>🤖 VRMアバター</h3>
                    <p>VRMファイルが見つかりません</p>
                </div>
            </div>
            """
        
        vrm_file_name = self.vrm_path.split('/')[-1] if self.vrm_path else "unknown"
        
        js_template = """
        <script type="importmap">
        {
          "imports": {
            "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
            "three/examples/jsm/loaders/GLTFLoader": "https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js",
            "@pixiv/three-vrm": "https://unpkg.com/@pixiv/three-vrm@3.2.0/lib/three-vrm.min.js"
          }
        }
        </script>
        
        <script type="module">
        import * as THREE from 'three';
        import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
        import { VRM } from '@pixiv/three-vrm';
        
        async function start() {
            try {
                const canvas = document.getElementById('vrm-canvas-unique');
                if (!canvas) {
                    throw new Error("キャンバスが見つかりません");
                }
                
                const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
                renderer.setSize(canvas.clientWidth, canvas.clientHeight);
                renderer.setClearColor(0x333333);
                
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x333333);
                
                const camera = new THREE.PerspectiveCamera(30, canvas.clientWidth / canvas.clientHeight, 0.1, 20);
                camera.position.set(0, 1.2, 3.0);
                
                const ambientLight = new THREE.AmbientLight(0xffffff, 2.0);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 2.0);
                directionalLight.position.set(1, 1, 1);
                scene.add(directionalLight);
                
                const binaryDataElement = document.getElementById('vrm-binary-data');
                if (!binaryDataElement) {
                    throw new Error("VRMバイナリデータが見つかりません");
                }
                
                const uint8Array = eval(binaryDataElement.textContent);
                const blob = new Blob([uint8Array], { type: 'application/octet-stream' });
                const blobUrl = URL.createObjectURL(blob);
                
                const loader = new GLTFLoader();
                loader.load(blobUrl, async (gltf) => {
                    const vrm = await VRM.from(gltf);
                    if (vrm) {
                        scene.add(vrm.scene);
                        vrm.scene.rotation.y = Math.PI;
                        vrm.scene.scale.set(20, 20, 20);
                        
                        renderer.render(scene, camera);
                        animate();
                    }
                }, undefined, (error) => {
                    console.error('❌ VRM読み込みエラー:', error);
                });
                
                function animate() {
                    requestAnimationFrame(animate);
                    if (vrm) {
                        vrm.update(0.016);
                    }
                    renderer.render(scene, camera);
                }
                
            } catch (e) {
                console.error("🚫 初期化エラー:", e);
            }
        }
        
        start().catch(console.error);
        </script>
        """
        
        html_template = """
        <div style='width: 100%; height: 600px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow: hidden;'>
            <div style='position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px; z-index: 10;'>
                🎭 {{vrm_file_name}}
            </div>
            <div id="vrm-binary-data" style="display:none;">{{vrm_binary_array}}</div>
            <canvas id='vrm-canvas-unique' style='width: 100%; height: 600px; border-radius: 15px; display: block;'></canvas>
            {{js_code}}
        </div>
        """
        
        html_code = html_template.replace("{{vrm_file_name}}", vrm_file_name)
        html_code = html_code.replace("{{vrm_binary_array}}", self._get_vrm_binary_array() if self._get_vrm_base64() else "")
        html_code = html_code.replace("{{js_code}}", js_template)
        
        return html_code
