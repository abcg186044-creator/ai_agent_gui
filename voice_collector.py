#!/usr/bin/env python3
"""
YouTube音声収集スクリプト
RVC学習用データセットの作成を支援
"""

import os
import json
import subprocess
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
import yt_dlp
from typing import List, Dict, Optional
import argparse

class VoiceCollector:
    def __init__(self, output_dir: str = "voice_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # サブディレクトリを作成
        (self.output_dir / "raw").mkdir(exist_ok=True)
        (self.output_dir / "processed").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        self.metadata = {
            "collected_videos": [],
            "total_duration": 0,
            "sample_rate": 22050,
            "created_at": None
        }
    
    def download_audio(self, url: str, quality: str = "best") -> Optional[str]:
        """YouTubeから音声をダウンロード"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.output_dir / "raw" / "%(title)s.%(ext)s"),
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'unknown')
                duration = info.get('duration', 0)
                
                # WAVファイルパスを取得
                wav_path = self.output_dir / "raw" / f"{title}.wav"
                
                if wav_path.exists():
                    print(f"✅ 音声ダウンロード完了: {title}")
                    print(f"📁 保存先: {wav_path}")
                    print(f"⏱️ 長さ: {duration}秒")
                    
                    # メタデータを記録
                    self.metadata["collected_videos"].append({
                        "title": title,
                        "url": url,
                        "duration": duration,
                        "file_path": str(wav_path),
                        "collected_at": str(Path(wav_path).stat().st_mtime)
                    })
                    
                    return str(wav_path)
                else:
                    print("❌ WAVファイルが見つかりません")
                    return None
                    
        except Exception as e:
            print(f"❌ ダウンロードエラー: {str(e)}")
            return None
    
    def process_audio(self, wav_path: str, segment_length: float = 10.0) -> List[str]:
        """音声をRVC学習用に処理"""
        try:
            # 音声を読み込み
            y, sr = librosa.load(wav_path, sr=22050)
            
            # 無音区間を検出して分割
            intervals = librosa.effects.split(y, top_db=20)
            
            processed_files = []
            base_name = Path(wav_path).stem
            
            for i, (start, end) in enumerate(intervals):
                segment = y[start:end]
                
                # 短すぎるセグメントはスキップ
                if len(segment) / sr < 1.0:
                    continue
                
                # 長すぎるセグメントは分割
                if len(segment) / sr > segment_length:
                    sub_segments = self._split_long_segment(segment, sr, segment_length)
                    for j, sub_seg in enumerate(sub_segments):
                        output_path = self.output_dir / "processed" / f"{base_name}_seg{i}_{j}.wav"
                        sf.write(output_path, sub_seg, sr)
                        processed_files.append(str(output_path))
                else:
                    output_path = self.output_dir / "processed" / f"{base_name}_seg{i}.wav"
                    sf.write(output_path, segment, sr)
                    processed_files.append(str(output_path))
            
            print(f"✅ 音声処理完了: {len(processed_files)}個のセグメント")
            return processed_files
            
        except Exception as e:
            print(f"❌ 音声処理エラー: {str(e)}")
            return []
    
    def _split_long_segment(self, segment: np.ndarray, sr: int, max_length: float) -> List[np.ndarray]:
        """長いセグメントを分割"""
        max_samples = int(max_length * sr)
        segments = []
        
        for i in range(0, len(segment), max_samples):
            end = min(i + max_samples, len(segment))
            segments.append(segment[i:end])
        
        return segments
    
    def create_dataset_metadata(self, processed_files: List[str]):
        """データセットメタデータを作成"""
        dataset_info = {
            "files": [],
            "total_files": len(processed_files),
            "total_duration": 0,
            "sample_rate": 22050,
            "created_at": str(Path().cwd())
        }
        
        for file_path in processed_files:
            try:
                duration = librosa.get_duration(filename=file_path)
                dataset_info["files"].append({
                    "path": file_path,
                    "duration": duration,
                    "name": Path(file_path).name
                })
                dataset_info["total_duration"] += duration
            except Exception as e:
                print(f"⚠️ ファイル情報取得エラー: {file_path} - {str(e)}")
        
        # メタデータを保存
        metadata_path = self.output_dir / "metadata" / "dataset_info.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ データセットメタデータ保存: {metadata_path}")
        print(f"📊 総ファイル数: {dataset_info['total_files']}")
        print(f"⏱️ 総時間: {dataset_info['total_duration']:.2f}秒")
        
        return dataset_info
    
    def create_rvc_config(self, target_voice_name: str):
        """RVC学習用設定ファイルを作成"""
        config = {
            "model_name": target_voice_name,
            "sample_rate": 22050,
            "pitch_extraction_algorithm": "harvest",
            "feature_index": 1,
            "feature_index_file": "added_IVF512_Flat_nprobe_1_v2.index",
            "index_rate": 0.8,
            "device": "cuda:0",
            "is_half": True,
            "f0_method": "harvest",
            "filter_radius": 3,
            "resample_sr": 0,
            "rms_mix_rate": 0.25,
            "protect": 0.33,
            "crepe_hop_length": 128,
            "spk2id": {
                target_voice_name: 0
            }
        }
        
        config_path = self.output_dir / "metadata" / "rvc_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ RVC設定ファイル保存: {config_path}")
        return config_path
    
    def save_metadata(self):
        """収集メタデータを保存"""
        metadata_path = self.output_dir / "metadata" / "collection_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        print(f"✅ 収集メタデータ保存: {metadata_path}")

def main():
    parser = argparse.ArgumentParser(description="YouTube音声収集ツール")
    parser.add_argument("--url", required=True, help="YouTube動画URL")
    parser.add_argument("--output", default="voice_dataset", help="出力ディレクトリ")
    parser.add_argument("--voice-name", default="target_voice", help="目標音声名")
    parser.add_argument("--segment-length", type=float, default=10.0, help="セグメント長（秒）")
    
    args = parser.parse_args()
    
    collector = VoiceCollector(args.output)
    
    print("🎤 YouTube音声収集を開始します...")
    print(f"📺 URL: {args.url}")
    print(f"📁 出力先: {args.output}")
    
    # 音声ダウンロード
    wav_path = collector.download_audio(args.url)
    if not wav_path:
        print("❌ 音声ダウンロードに失敗しました")
        return
    
    # 音声処理
    processed_files = collector.process_audio(wav_path, args.segment_length)
    if not processed_files:
        print("❌ 音声処理に失敗しました")
        return
    
    # データセットメタデータ作成
    dataset_info = collector.create_dataset_metadata(processed_files)
    
    # RVC設定作成
    collector.create_rvc_config(args.voice_name)
    
    # メタデータ保存
    collector.save_metadata()
    
    print("🎉 音声収集完了！")
    print(f"📊 処理されたファイル: {len(processed_files)}個")
    print(f"⏱️ 総時間: {dataset_info['total_duration']:.2f}秒")
    print(f"🔧 RVC学習準備完了: {args.output}")

if __name__ == "__main__":
    main()
