# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-07-17
### Added
- **translate_filesメソッドを追加**
  - ファイル翻訳APIに複数のファイルを登録、取得するメソッド `translate_files` を追加

### Refactored
- コードのリファクタリング
  - classを3つに分類し、別のファイルに分割

## [0.3.0] - 2024-07-16
### Added
- **重複登録の防止機能**:
  - ファイル翻訳の登録メソッド `set_file`に重複登録の防止機能を実装
  - `set_file` メソッドに `force` オプションを追加。 `force=True`の場合は重複にかかわらず登録する

### Changed
- **スリープ機能**:
  - サーバーへの負荷を考慮してレクエスト時に3秒の遅延を設定
  - コンストラクタのsleep引数により調整可能
- **ファイル拡張子の処理**:
  - ファイル翻訳の登録メソッド `set_file`実行時に、サポート外拡張子の場合は`.txt`に変更する機能を実装

### Removed
- `set_file` メソッドは `pid` を直接返さなくなった。より詳細な情報を提供する `APIResponseParser` のインスタンスを返すようになった。


### [0.2.0] - 2024-07-15

#### Added
- 🆕 ファイル翻訳APIの新機能を追加。
  - `set_file(path)` で翻訳元のファイルパスを指定し、PID を返す機能。
  - `file_status()` で翻訳状況を確認する機能。
  - `get_file(pid, encoding="utf-8", path=None)` で翻訳済みファイルを取得し、保存する機能。

#### Changed
- 📖 READMEにファイル翻訳APIの使用方法を追記。
  - 各エンドポイントの詳細な説明を追加。
  - 使用例のコードスニペットを含め、実際の利用方法を記述。
