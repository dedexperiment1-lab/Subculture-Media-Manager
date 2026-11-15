# 📂 Subculture Media Manager & Launcher (v2.7)
### 서브컬처 미디어 매니저 & 스마트 랜덤 런처 / サブカルチャーメディアマネージャー & ランチャー

[🇰🇷 한국어](#-한국어-korean) | [🇺🇸 English](#-english) | [🇯🇵 日本語](#-日本語-japanese)

---

<br>

# 🇰🇷 한국어 (Korean)

## 1. 개요
**서브컬처 미디어 매니저 & 스마트 랜덤 런처(Subculture Media Manager & Launcher)**는 방대한 분량의 만화/동인지 압축파일 및 미디어 영상을 효율적으로 보관·분류하고, 단축키 하나로 무작위 감상할 수 있도록 설계된 올인원 Windows 데스크톱 유틸리티입니다.

복잡한 부가 설치 없이 단일 실행 파일(`RandomMediaOpener.exe`)로 즉시 구동되며, 대용량 외장 드라이브에서도 0.01초 만에 로딩되는 초고속 캐싱과 안전한 파일 정리 알고리즘을 제공합니다.

---

## 2. 주요 기능

### 🎲 모듈 ①: 스마트 랜덤 미디어 런처 (Smart Random Launcher)
* **원클릭 / 전역 단축키 무작위 실행**:
  * 창이 백그라운드에 최소화되어 있어도 전역 단축키(기본값: 만화 **`F8`**, 영상 **`F7`**)로 즉각 무작위 작품을 실행합니다.
  * 단축키는 UI에서 F1~F12 중 원하는 키로 자유롭게 변경 가능합니다.
* **단일 창 플레이어 연동 (Single-Instance Integration)**:
  * 팟플레이어(PotPlayer) 실행 시 `/current` 인수를 적용하여 영상 실행 시마다 새 창이 무한정 뜨는 현상을 방지하고 기존 플레이어 창에서 바로 재생합니다.
  * 반디뷰(BandiView), 꿀뷰(Honeyview) 등 주요 만화 뷰어를 자동 감지합니다.
* **대용량 드라이브 0.01초 초고속 캐시 (`media_cache.json`)**:
  * 수만~수십만 개의 파일이 보관된 대용량 드라이브(`E:/` 등)도 최초 1회 색인 후 로컬 캐시를 활용해 재실행 시 딜레이 없이 0.01초 만에 즉시 준비 상태가 됩니다.
* **시스템 보호 폴더 자동 스킵**:
  * 드라이브 루트 탐색 시 Windows 권한 오류를 유발하는 `$RECYCLE.BIN`, `System Volume Information` 등을 지능적으로 건너뜁니다.
* **최근 감상 히스토리**:
  * 최근 재생된 30개의 목록을 기록하며, 더블클릭 시 재실행 또는 해당 폴더 위치를 바로 열 수 있습니다.

### 📁 모듈 ②: 작가/서클/시리즈 스마트 자동 정리기 (Smart Organizer)
* **위치 기반 괄호 메타데이터 파서 (Positional Bracket Tokenizer)**:
  * 초반 1~2번째 괄호 위치를 지능적으로 분석하여, 뒷부분의 원작 태그(`(Fate/Grand Order)`, `(아이돌마스터)` 등)나 언어 태그(`[Korean]`, `[中国翻訳]`)를 작가명으로 오인하지 않습니다.
* **행사 및 플랫폼 태그 자동 필터링**:
  * 코믹마켓 행사명(`[C100]`, `[Comic Market 98]`, `[例大祭]`, `[こみトレ]` 등)과 후원 플랫폼 태그(`[FANBOX]`, `[Fantia]`, `[ci-en]` 등)를 자동으로 건너뛰고 순수 작가/서클명을 추출합니다.
* **일반 연재 만화(단행본) 권수/화수 자동 제거 및 시리즈 통합**:
  * 작가 괄호 표기가 없는 일반 코믹스(`공포학교01.zip`, `공포학교15완결.zip`, `HyperPolice02.zip`, `エイリアン9 03권.zip`)의 권수와 말단 숫자를 지능적으로 정제하여 단일 시리즈 폴더로 깔끔하게 묶어 정리합니다. (단, `エイリアン9`처럼 고유명사에 포함된 숫자는 보존)
* **스마트 판본 비교 및 안전한 휴지통 이동 (Deduplication & Safety)**:
  * 웹 다운로드 시 발생하는 중복 넘버링(`(1)`, `(2)`)과 파일 수정 날짜(`mtime`)를 정밀 대조합니다.
  * 최신본을 보존하고 이전/구버전 파일은 영구 삭제가 아닌 **Windows Shell API를 통해 휴지통으로 안전하게 이동**시킵니다.

### 🛡️ v2.7 신규 추가 기능: 안전 경고 체계 및 실수 복구 도구
1. **`[Auto]` 폴더 자동 생성 기본값 OFF**:
   * 제목만 적힌 단편 파일들이 잘못된 개별 폴더로 흩어지는 것을 방지하기 위해 기본값을 꺼짐(`False`)으로 제공합니다. 옵션 해제 시에는 매칭 폴더가 없는 파일은 원래 자리에 안전하게 스킵 보존됩니다.
2. **2중 안전 경고 시스템**:
   * **1차 경고**: 사용자가 `[Auto] 폴더 자동생성` 옵션을 체크할 때 안내 팝업창을 띄워 제목만 있는 파일의 수작업 선행 정리를 권장합니다.
   * **2차 경고**: `[Auto]` 옵션이 켜진 상태에서 `[ ▶ 스마트 자동 정리 시작 ]` 버튼을 누르면 최종 확인 대화상자가 표시됩니다.
3. **실수 복구 도구: `[ ↩ 하위 폴더 내용물 꺼내기 (되돌리기) ]` 버튼 신설**:
   * 실수로 분류되어 하위 폴더마다 파일이 1개씩 분산되었을 때, 단 한 번의 클릭으로 하위 폴더 안의 파일들을 전부 상위 폴더로 꺼내고 빈 폴더들을 자동 삭제합니다.
   * 동일 파일명이 존재할 경우 `_1`, `_2` 넘버링을 적용하여 파일 유실을 100% 방지합니다.
   * 원치 않는 기존 폴더가 풀리는 사고를 방지하기 위해, 실행 전 안내 경고창이 반드시 팝업됩니다.

---

## 3. 사용 방법

### 1) 실행
* 별도의 설치 없이 **`RandomMediaOpener.exe`**를 더블클릭하여 실행합니다.
* 상단 우측 언어 메뉴에서 `한국어`, `English`, `日本語`를 자유롭게 전환할 수 있습니다.

### 2) 🎲 스마트 랜덤 런처 탭
1. **만화 폴더** 및 **영상 폴더** 경로를 지정합니다.
2. PC에 설치된 만화 뷰어(반디뷰, 꿀뷰 등) 및 영상 플레이어(팟플레이어 등) 경로를 설정합니다. (자동 감지 지원)
3. UI의 큰 버튼을 누르거나, 키보드의 단축키(**`F8`**, **`F7`**)를 눌러 즉시 감상합니다.

### 3) 📁 작가/서클 스마트 정리기 탭
1. **정리 대상 폴더(다운로드 받은 폴더)**와 **기준 보관 폴더(기존 라이브러리)**를 지정합니다.
2. 정리 옵션을 확인합니다:
   * `신규 작가는 '작가명 [Auto]' 폴더 자동 생성`: 기존 보관 폴더에 없는 작가/시리즈의 새 폴더를 생성할지 여부 (권장: 꺼짐 유지 후 필요시에만 켬)
   * `동일 파일 충돌 시 '수정한 날짜' 최신본 남기고 구버전 휴지통 이동`: 최신본 자동 교체 및 구버전 안전 폐기
3. **`[ ▶ 스마트 자동 정리 시작 ]`**을 클릭하여 정리를 진행합니다.

### 4) ↩ 하위 폴더 파일 꺼내기 (되돌리기) 사용법
1. 의도치 않게 하위 폴더가 너무 많이 생겼다면, 작업할 대상 폴더들만 별도의 작업용 폴더로 옮겨둡니다.
2. **`[ ↩ 하위 폴더 내용물 꺼내기 (되돌리기) ]`** 버튼을 누릅니다.
3. 경고창을 확인한 뒤 대상 폴더를 선택하면 모든 파일이 상위로 꺼내어지고 빈 폴더가 정리됩니다.

---

<br>

# 🇺🇸 English

## 1. Overview
**Subculture Media Manager & Launcher** is an all-in-one Windows desktop application designed to organize massive collections of comic archives and subculture media videos while providing instant, randomized playback via global hotkeys.

Distributed as a standalone portable executable (`RandomMediaOpener.exe`), it features high-speed indexing for multi-terabyte drives, intelligent metadata parsing, collision-safe deduplication, and a robust recovery toolkit.

---

## 2. Key Features

### 🎲 Module 1: Smart Random Media Opener
* **One-Click / Global Hotkey Random Playback**:
  * Launch random comics or videos instantly using global hotkeys (Default: Comic **`F8`**, Video **`F7`**) even while minimized in the background.
  * Hotkeys are fully customizable from `F1` to `F12`.
* **Single-Instance Player Integration**:
  * Integrates with PotPlayer using the `/current` argument, preventing dozens of player instances from cluttering your desktop.
  * Automatically detects BandiView and Honeyview comic viewers.
* **Ultra-Fast Local Cache (`media_cache.json`)**:
  * Fast 0.01-second instant startup for large external hard drives (`E:/`, etc.) after the initial scan.
* **Protected System Folder Filtering**:
  * Automatically bypasses Windows restricted folders such as `$RECYCLE.BIN` and `System Volume Information`.
* **Recent History**:
  * Keeps track of the last 30 played files with double-click relaunching and direct folder access.

### 📁 Module 2: Smart Author & Series Organizer
* **Positional Bracket Tokenizer**:
  * Accurately parses circle and author names from early bracket positions while ignoring parody work tags (`(Fate/Grand Order)`), language tags (`[Korean]`), and release groups.
* **Event & Platform Tag Stripping**:
  * Ignores convention tags (`[C100]`, `[Comic Market 98]`, `[例大祭]`, etc.) and subscription platform prefixes (`[FANBOX]`, `[Fantia]`, `[ci-en]`, etc.).
* **Commercial Manga Volume Stripping & Series Grouping**:
  * Strips volume markers (`Vol.01`, `01`, `~15 End`) from commercial titles without brackets (`HorrorSchool01.zip`, `HyperPolice02.zip`), grouping them into unified series folders while preserving intrinsic title numbers (e.g., `Alien 9`).
* **Safe Deduplication & Version Resolution**:
  * Resolves download duplicates (`(1)`, `(2)`) by comparing download suffixes and file modification timestamps (`mtime`).
  * Older versions are safely sent to the **Windows Recycle Bin via native Windows Shell API** rather than being permanently deleted.

### 🛡️ What's New in v2.7: Safety Alerts & Undo Recovery Tool
1. **`[Auto]` Folder Creation Disabled by Default**:
   * Set to `False` by default to prevent title-only single files from cluttering your library. When unchecked, unmatched files remain untouched in their original directory.
2. **2-Step Safety Warning Dialogs**:
   * **1st Dialog**: Alerts the user upon enabling the `[Auto]` checkbox, recommending manual sorting of title-only files first.
   * **2nd Dialog**: Confirms again before batch execution if `[Auto]` is active.
3. **Recovery Tool: `[ ↩ Extract Files from Subfolders (Undo / Flatten) ]`**:
   * Unpacks all files from subfolders up into the parent folder and deletes the emptied subfolders in seconds.
   * Resolves name collisions using `_1`, `_2` numbering to ensure zero data loss.
   * Requires confirmation through a safety warning dialog before execution.

---

## 3. How to Use

1. **Launch**:
   * Run **`RandomMediaOpener.exe`** directly (no installation needed).
   * Switch languages anytime in the top-right menu (`한국어`, `English`, `日本語`).
2. **Launcher Tab**:
   * Configure your Comic and Video folders and viewer executable paths.
   * Press **`F8`** (Comic) or **`F7`** (Video) to enjoy random media.
3. **Organizer Tab**:
   * Set the **Source Folder** (e.g., downloads) and **Library Folder** (existing collection).
   * Review options (`Auto-create folder`, `Conflict resolution`).
   * Click **`[ ▶ Start Auto-Organizing ]`**.
4. **Subfolder Extraction (Undo)**:
   * If folders were created accidentally, click **`[ ↩ Extract Files from Subfolders (Undo / Flatten) ]`**, review the warning, and select the folder to flatten.

---

<br>

# 🇯🇵 日本語 (Japanese)

## 1. 概要
**サブカルチャーメディアマネージャー & スマートランダムランチャー (Subculture Media Manager & Launcher)** は、膨大な漫画・同人誌アーカイブや動画ファイルをスマートに分類・整理し、ショートカットキーひとつでランダム鑑賞できるWindows専用オールインワンユーティリティです。

単一の実行可能ファイル（`RandomMediaOpener.exe`）としてポータブルに動作し、大容量外付けドライブでも0.01秒で立ち上がる高速キャッシュと、安全なファイル整理アルゴリズムを備えています。

---

## 2. 主な機能

### 🎲 モジュール ①: スマートランダムランチャー
* **ワンクリック / グローバルショートカットキーによるランダム起動**:
  * アプリが最小化されていても、ショートカットキー（デフォルト：マンガ **`F8`**、動画 **`F7`**）で即座にランダム再生します。
  * ショートカットキーは設定からF1〜F12へ自由に変更可能です。
* **単一プレイヤータスク連携 (Single-Instance Integration)**:
  * PotPlayerの起動時に `/current` オプションを付与し、新しいウィンドウが次々に開くのを防ぎ、既存の再生画面でスムーズに切り替えます。
  * BandiView、Honeyview（蜜蜂ビューアー）などの主要漫画ビューアーを自動検出します。
* **大容量ドライブ対応 0.01秒高速キャッシュ (`media_cache.json`)**:
  * 数万〜数十万ファイルが存在する大容量ドライブ（`E:/` など）でも、インデックスキャッシュにより次回以降0.01秒で即時起動します。
* **システム保護フォルダの自動スキップ**:
  * `$RECYCLE.BIN` や `System Volume Information` などのWindows保護フォルダを自動的に除外して安全に探索します。
* **履歴機能**:
  * 最近再生した30件の履歴を保持し、ダブルクリックでの再実行やフォルダ展開が可能です。

### 📁 モジュール ②: 作家/サークル/シリーズ自動整理ツール
* **位置認識型カッコパーサー (Positional Bracket Tokenizer)**:
  * ファイル名前方の1〜2番目のカッコ位置を解析し、後方の原作名タグ（`(Fate/Grand Order)` 等）や言語タグ（`[中国翻訳]`、`[Korean]` 等）を作家名と誤認しません。
* **イベント・プラットフォームタグの自動除去**:
  * コミケなどのイベント名（`[C100]`, `[Comic Market 98]`, `[例大祭]` 等）や支援サイトタグ（`[FANBOX]`, `[Fantia]` 等）を自動スキップし、正確なサークル・作家名を特定します。
* **一般連載漫画の巻数・数字除去とシリーズ統合**:
  * 作家表記のない一般コミックス（`恐怖学校01.zip`, `HyperPolice02.zip`, `エイリアン9 03巻.zip` 等）の巻数表記をスマートに除去し、ひとつのシリーズフォルダに統合整理します（`エイリアン9` のような固有タイトル番号は保持）。
* **重複判定と安全なゴミ箱移動 (Deduplication & Safety)**:
  * 連番ダウンロードファイル（`(1)`, `(2)`）や更新日時（`mtime`）を比較し、最新版を残して旧バージョンは **Windows Shell APIを通じて安全にゴミ箱へ移動** します（完全削除は行いません）。

### 🛡️ v2.7 新機能: 安全警告システム & 取り消し（復旧）ツール
1. **`[Auto]` フォルダ自動作成のデフォルトOFF化**:
   * タイトルのみの短編ファイルが不要な個別フォルダに散らばるのを防ぐため、初期設定をOFF（無効）に設定。無効時は一致フォルダのないファイルはその場に安全にスキップ・保持されます。
2. **2重安全警告システム**:
   * **第1警告**: `[Auto] フォルダ自動作成` チェックボックスをONにした瞬間に警告ポップアップを表示し、タイトルのみのファイルの事前手動整理を案内。
   * **第2警告**: `[Auto]` が有効な状態で `[ ▶ 自動整理を開始 ]` をクリックした際に最終確認ダイアログを表示。
3. **取り消し復旧ツール: `[ ↩ サブフォルダのファイルを親フォルダへ戻す (取り消し) ]`**:
   * 誤って作成されたサブフォルダ内のファイルをワンクリックで親フォルダへ取り出し、空になったフォルダを自動削除します。
   * 同名ファイルが存在する場合は `_1`, `_2` の連番を付与し、ファイルの消失を100%防ぎます。
   * 既存フォルダの誤解体を防止するため、実行前に明確な注意警告ダイアログを表示します。

---

## 3. 使い方

1. **起動**:
   * インストール不要の **`RandomMediaOpener.exe`** をダブルクリックして起動します。
   * 右上の言語メニューからいつでも `한국어`, `English`, `日本語` を切り替えられます。
2. **ランチャー タブ**:
   * マンガおよび動画フォルダ、使用するビューアー・プレイヤーのパスを設定します。
   * **`F8`**（マンガ）または **`F7`**（動画）を押してランダム再生します。
3. **自動整理 タブ**:
   * **整理対象フォルダ**（ダウンロードフォルダ）と **基準保管フォルダ**（既存ライブラリ）を指定します。
   * オプション（自動作成、重複更新）を確認し、**`[ ▶ 自動整理を開始 ]`** をクリックします。
4. **サブフォルダ内容物の取り出し (取り消し)**:
   * 意図せずフォルダが細分化された場合、**`[ ↩ サブフォルダのファイルを親フォルダへ戻す (取り消し) ]`** をクリックして対象親フォルダを選択するだけで元の状態に戻せます。

---

## 4. 開発・ビルド環境 (Development & Build)
* **Language**: Python 3.10+
* **GUI Framework**: Tkinter (ttk)
* **Binary Packaging**: PyInstaller 6.x
```bash
# Pythonソースからの直接実行
python subculture_media_manager.py

# 単一EXEファイルのビルド
pyinstaller --distpath . RandomMediaOpener.spec --noconfirm
```

---

## 5. ライセンス (License)
This project is licensed under the **MIT License**.
Copyright (c) 2026 dedexperiment1
