# マイク選択ガイド

## 🎤️ マイク選択ツール

AI Agent Systemでは、起動前にマイクを選択・テストできるツールを提供します。

## 🚀 使用方法

### 1. 自動マイク選択（推奨）
```cmd
start_ai.bat
```
- 起動時に自動的にマイク選択ツールが起動します
- 利用可能なマイクから選択できます
- テスト機能で動作確認ができます

### 2. 手動マイク選択
```cmd
python select_microphone.py
```
- いつでもマイク選択ツールを起動できます
- マイクの変更やテストができます

## 📋 マイク選択ツールの機能

### 1. マクリスト表示
```
Available Microphones:
--------------------------------------------------
1. ヘッドセット (ATH-CK150BT)
   ID: 1
   Channels: 1
   Sample Rate: 44100.0

2. マイク (Realtek HD Audio Mic input)
   ID: 19
   Channels: 2
   Sample Rate: 44100.0

3. Line (Steinberg UR22mkII)
   ID: 2
   Channels: 2
   Sample Rate: 44100.0
```

### 2. テスト機能
- **'t'**: マイクテストモード
- 選択したマイクで2秒間の録音テスト
- 音声エネルギーを測定
- 音声検出の確認

### 3. 選択オプション
- **数字**: マイクを選択
- **'t'**: テストモード
- **'d'**: 既定マイクを使用
- **'q'**: 終了

## 🎯 使用例

### 基本的な使用
```
Select microphone (1-3), or 't' to test, 'd' for default, 'q' to quit: 1

Selected: ヘッドセット (ATH-CK150BT)
Testing selected microphone...
Please speak into the microphone...
✅ Test successful!
   Energy: 47.555605
🎤 Voice detected! Microphone is working.
Use this microphone? (y/n): y
```

### テストモード
```
Select microphone (1-3), or 't' to test, 'd' for default, 'q' to quit: t
Enter microphone number to test (1-3): 1

Testing ヘッドセット (ATH-CK150BT)...
Please speak into the microphone...
✅ Test successful!
   Energy: 47.555605
   Max Value: 2458
   Samples: 32000
🎤 Voice detected!
```

## 🔧 設定の保存

- 選択したマイクは `selected_microphone.txt` に保存されます
- 次回起動時に自動的に読み込まれます
- 手動で設定を変更することも可能です

## 🛠️ トラブルシューティング

### マイクが見つからない場合
1. **接続確認**: マイクが正しく接続されているか確認
2. **ドライバ**: 音声ドライバが最新であるか確認
3. **権限**: Windowsのマイク権限を確認

### テストで音声が検出されない場合
1. **音量**: マイクに近づいて、もっと大きな声で話す
2. **設定**: マイクの入力レベルを調整
3. **ミュート**: マイクがミュートされていないか確認

### 既定マイクが反映されない場合
1. **Windows設定**: サウンド設定で既定マイクを設定
2. **再起動**: PCを再起動して設定を反映
3. **アプリ再起動**: AI Agent Systemを再起動

## 🎯 推奨マイク

### 高品質な音声入力
- **USBマイク**: 高品質で安定した音声入力
- **Bluetoothヘッドセット**: 便利なワイヤレス接続
- **内蔵マイク**: 手軽だが周囲の音を拾いやすい

### 設定推奨値
- **サンプルレート**: 16000 Hz（音声認識に最適）
- **チャンネル**: 1（モノラル）
- **フォーマット**: int16

---

**これで簡単にマイクを選択・設定できます！** 🎤️
