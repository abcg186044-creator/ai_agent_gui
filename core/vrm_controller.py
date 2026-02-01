"""
VRMコントローラーモジュール
VRMモデルのロードと表示、表情制御ロジックを管理
"""

import json
import os
from constants import *

class VRMAvatarController:
    def __init__(self):
        self.vrm_path = None
        self.vrm_scale = 1.0
        self.vrm_rotation = 0
        self.vrm_expression = "neutral"
        self.vrm_visible = True
        self.expressions = {
            "neutral": "neutral",
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "surprised": "surprised"
        }
    
    def load_vrm(self, vrm_file_path):
        """VRMファイルをロード"""
        try:
            if os.path.exists(vrm_file_path):
                self.vrm_path = vrm_file_path
                return True
            else:
                print(f"VRMファイルが見つかりません: {vrm_file_path}")
                return False
        except Exception as e:
            print(f"VRMロードエラー: {e}")
            return False
    
    def set_expression(self, expression_name):
        """表情を設定"""
        if expression_name in self.expressions:
            self.vrm_expression = expression_name
            return True
        else:
            print(f"不明な表情: {expression_name}")
            return False
    
    def set_scale(self, scale):
        """スケールを設定"""
        self.vrm_scale = max(0.1, min(3.0, scale))
    
    def set_rotation(self, rotation):
        """回転を設定"""
        self.vrm_rotation = rotation % 360
    
    def toggle_visibility(self):
        """表示/非表示を切り替え"""
        self.vrm_visible = not self.vrm_visible
    
    def get_vrm_html(self):
        """VRM表示用のHTMLを生成"""
        if not self.vrm_path or not self.vrm_visible:
            return self._get_empty_html()
        
        return f"""
        <div id="vrm-container" style="width: 100%; height: 600px; position: relative;">
            <canvas id="vrm-canvas" style="width: 100%; height: 100%;"></canvas>
            
            <script src="https://unpkg.com/@pixiv/three-vrm@0.6.7/lib/three-vrm.min.js"></script>
            <script>
                // VRM表示ロジック
                const canvas = document.getElementById('vrm-canvas');
                const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
                renderer.setSize(canvas.clientWidth, canvas.clientHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                
                // シーン設定
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(30.0, canvas.clientWidth / canvas.clientHeight, 0.1, 20.0);
                camera.position.set(0.0, 1.0, 5.0);
                
                // ライト設定
                const light = new THREE.DirectionalLight(0xffffff, 1.0);
                light.position.set(1.0, 1.0, 1.0);
                scene.add(light);
                
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
                scene.add(ambientLight);
                
                // VRMロード
                let currentVrm = null;
                
                const loader = new THREE.VRMLoader();
                loader.load(
                    '{self.vrm_path}',
                    (vrm) => {{
                        if (currentVrm) {{
                            scene.remove(currentVrm.scene);
                        }}
                        
                        currentVrm = vrm;
                        scene.add(vrm.scene);
                        
                        // スケールと回転を設定
                        vrm.scene.scale.setScalar({self.vrm_scale});
                        vrm.scene.rotation.y = THREE.MathUtils.degToRad({self.vrm_rotation});
                        
                        // 表情を設定
                        if (vrm.blendShapeProxy) {{
                            vrm.blendShapeProxy.setValue('{self.vrm_expression}', 1.0);
                        }}
                    }},
                    (progress) => {{
                        console.log('VRMロード進捗:', (progress.loaded / progress.total * 100) + '%');
                    }},
                    (error) => {{
                        console.error('VRMロードエラー:', error);
                    }}
                );
                
                // アニメーションループ
                function animate() {{
                    requestAnimationFrame(animate);
                    
                    if (currentVrm) {{
                        currentVrm.update(clock.getDelta());
                    }}
                    
                    renderer.render(scene, camera);
                }}
                
                const clock = new THREE.Clock();
                animate();
                
                // リサイズ対応
                window.addEventListener('resize', () => {{
                    camera.aspect = canvas.clientWidth / canvas.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
                }});
            </script>
        </div>
        """
    
    def _get_empty_html(self):
        """VRM非表示時の空HTML"""
        return """
        <div style="width: 100%; height: 600px; display: flex; align-items: center; justify-content: center; background-color: #f0f0f0; border-radius: 18px;">
            <div style="text-align: center; color: #666;">
                <div style="font-size: 48px; margin-bottom: 16px;">🐿️</div>
                <div>エゾモモンガ</div>
                <div style="font-size: 14px; margin-top: 8px;">VRMアバターは非表示です</div>
            </div>
        </div>
        """
    
    def get_status(self):
        """VRMの状態を取得"""
        return {
            "loaded": self.vrm_path is not None,
            "visible": self.vrm_visible,
            "expression": self.vrm_expression,
            "scale": self.vrm_scale,
            "rotation": self.vrm_rotation
        }
    
    def to_dict(self):
        """VRM設定を辞書に変換"""
        return {
            "vrm_path": self.vrm_path,
            "vrm_scale": self.vrm_scale,
            "vrm_rotation": self.vrm_rotation,
            "vrm_expression": self.vrm_expression,
            "vrm_visible": self.vrm_visible
        }
    
    def from_dict(self, data):
        """辞書からVRM設定を復元"""
        self.vrm_path = data.get("vrm_path")
        self.vrm_scale = data.get("vrm_scale", 1.0)
        self.vrm_rotation = data.get("vrm_rotation", 0)
        self.vrm_expression = data.get("vrm_expression", "neutral")
        self.vrm_visible = data.get("vrm_visible", True)
