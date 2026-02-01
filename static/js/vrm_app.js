// VRMアバター表示アプリケーション（簡潔テスト版）
import * as THREE from 'https://esm.sh/three@0.150.0';
import { GLTFLoader } from 'https://esm.sh/three@0.150.0/examples/jsm/loaders/GLTFLoader.js';
import { VRM, VRMLoaderPlugin } from 'https://esm.sh/@pixiv/three-vrm@3.2.0/lib/three-vrm.min.js';

// VRMアプリケーション
class VRMApp {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.vrm = null;
        this.isLoaded = false;
        console.log('🚀 VRMアプリコンストラクタ開始');
    }
    
    async init() {
        console.log('🚀 VRMアプリ初期化開始');
        
        try {
            // Canvas取得
            const canvas = document.getElementById('vrm-canvas');
            if (!canvas) {
                throw new Error('キャンバスが見つかりません');
            }
            
            // シーン作成
            this.scene = new THREE.Scene();
            this.scene.background = new THREE.Color(0x667eea);
            console.log('✅ シーン作成完了');
            
            // カメラ設定
            const aspect = canvas.clientWidth / canvas.clientHeight;
            this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
            this.camera.position.set(0, 1.2, 2.5);
            console.log('✅ カメラ設定完了');
            
            // レンダラー設定
            this.renderer = new THREE.WebGLRenderer({
                canvas: canvas,
                antialias: true,
                alpha: true
            });
            this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);
            console.log('✅ レンダラー設定完了');
            
            // ライト設定
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            this.scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(1, 1, 1);
            this.scene.add(directionalLight);
            console.log('✅ ライト設定完了');
            
            // VRMロード
            await this.loadVRM();
            
            // アニメーション開始
            this.animate();
            
            console.log('✅ VRMアプリ初期化完了');
            
        } catch (error) {
            console.error('❌ VRMアプリ初期化エラー:', error);
            this.showError('VRMアプリの初期化に失敗しました: ' + error.message);
        }
    }
    
    async loadVRM() {
        try {
            console.log('🔄 VRMロード開始');
            
            // VRMファイルパス（FastAPIサーバー経由）
            const vrmPath = 'http://localhost:8001/static/avatar.vrm';
            console.log('📁 VRMファイルパス:', vrmPath);
            
            // VRMLoader設定
            const loader = new THREE.GLTFLoader();
            loader.register((parser) => {
                return new VRMLoaderPlugin(parser);
            });
            
            // VRM読み込み
            const gltf = await new Promise((resolve, reject) => {
                loader.load(
                    vrmPath,
                    (gltf) => {
                        console.log('✅ VRMファイル読み込み完了');
                        resolve(gltf);
                    },
                    (progress) => {
                        const percent = (progress.loaded / progress.total) * 100;
                        console.log(`📈 VRMロード進捗: ${percent.toFixed(1)}%`);
                    },
                    (error) => {
                        console.error('❌ VRM読み込みエラー:', error);
                        reject(new Error('VRMファイルの読み込みに失敗しました'));
                    }
                );
            });
            
            // VRMインスタンス作成
            this.vrm = await VRM.from(gltf);
            this.scene.add(this.vrm.scene);
            console.log('✅ VRMインスタンス作成完了');
            
            // カメラ調整
            this.adjustCamera();
            
            this.isLoaded = true;
            console.log('✅ VRMロード完了');
            
        } catch (error) {
            console.error('❌ VRMロードエラー:', error);
            this.showError('VRMファイルの読み込みに失敗しました: ' + error.message);
        }
    }
    
    adjustCamera() {
        if (!this.vrm) return;
        
        try {
            const box = new THREE.Box3().setFromObject(this.vrm.scene);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = this.camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 2;
            
            this.camera.position.set(center.x, center.y + 0.5, center.z + cameraZ);
            this.camera.lookAt(center);
            
            console.log('✅ カメラ位置調整完了');
        } catch (error) {
            console.error('❌ カメラ位置調整エラー:', error);
        }
    }
    
    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        if (!this.isLoaded) return;
        
        // VRM更新
        if (this.vrm) {
            this.vrm.update(0.016);
        }
        
        // レンダリング
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    updateVrmExpression(name) {
        if (!this.vrm || !this.vrm.expressionManager) {
            console.warn('⚠️ 表情マネージャーが利用できません');
            return;
        }
        
        console.log(`🎭 表情変更: ${name}`);
        
        try {
            this.vrm.expressionManager.clear();
            
            switch (name.toLowerCase()) {
                case 'happy':
                case 'joy':
                    this.vrm.expressionManager.setExpression('joy');
                    break;
                case 'sad':
                    this.vrm.expressionManager.setExpression('sad');
                    break;
                case 'angry':
                    this.vrm.expressionManager.setExpression('angry');
                    break;
                case 'surprised':
                    this.vrm.expressionManager.setExpression('surprised');
                    break;
                default:
                    break;
            }
            
            console.log(`✅ 表情変更完了: ${name}`);
            
        } catch (error) {
            console.error('❌ 表情変更エラー:', error);
        }
    }
    
    showError(message) {
        console.error('❌ エラー表示:', message);
        
        const canvas = document.getElementById('vrm-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        ctx.fillStyle = '#667eea';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('🤖 VRMアバター', canvas.width/2, canvas.height/2 - 40);
        
        ctx.font = '16px Arial';
        ctx.fillText('エラーが発生しました', canvas.width/2, canvas.height/2);
        
        ctx.font = '14px Arial';
        ctx.fillText(message, canvas.width/2, canvas.height/2 + 30);
    }
}

// グローバル変数
let vrmApp = null;

// 表情更新関数
window.updateVrmExpression = function(name) {
    if (vrmApp) {
        vrmApp.updateVrmExpression(name);
    } else {
        console.warn('⚠️ VRMアプリが初期化されていません');
    }
};

// 初期化関数
async function initVRMSystem() {
    console.log('🚀 VRMシステム初期化開始');
    
    try {
        // DOM準備完了を待機
        if (document.readyState === 'loading') {
            await new Promise(resolve => {
                document.addEventListener('DOMContentLoaded', resolve);
            });
        }
        
        // Canvas確認
        const canvas = document.getElementById('vrm-canvas');
        if (!canvas) {
            throw new Error('キャンバス要素が見つかりません');
        }
        
        console.log('✅ Canvas要素確認完了');
        
        // VRMアプリ初期化
        vrmApp = new VRMApp();
        await vrmApp.init();
        
        console.log('✅ VRMシステム初期化完了');
        
    } catch (error) {
        console.error('❌ VRMシステム初期化エラー:', error);
        
        const canvas = document.getElementById('vrm-canvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillStyle = '#667eea';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = 'white';
                ctx.font = 'bold 20px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('🤖 VRMアバター', canvas.width/2, canvas.height/2 - 40);
                
                ctx.font = '16px Arial';
                ctx.fillText('初期化エラー', canvas.width/2, canvas.height/2);
                
                ctx.font = '14px Arial';
                ctx.fillText(error.message, canvas.width/2, canvas.height/2 + 30);
            }
        }
    }
}

// 実行
initVRMSystem().catch(console.error);

console.log('✅ VRMアプリ読み込み完了');