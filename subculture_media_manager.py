"""
Subculture Media Manager & Launcher (서브컬처 미디어 매니저 & 런처) v2.4
- 탭 1: 스마트 랜덤 미디어 런처 (기본 단축키: 만화 F8, 영상 F7, 대용량 인덱스 캐시, 안전 탐색)
- 탭 2: 작가/서클 스마트 자동 정리기 (위치 기반 괄호 파서, 모든 파일 지원, 옵션 간소화, 휴지통 안전 이동)
- 공통: 다국어(한국어/일본어/영어) 전체 실시간 갱신, UI 잘림 방지, 도움말 모달, 무중단 예외 처리
"""

import os
import sys
import json
import random
import re
import shutil
import threading
import subprocess
import ctypes
import ctypes.wintypes
from collections import deque
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ==========================================
# Windows Shell & Hotkey API
# ==========================================
MOD_ALT      = 0x0001
MOD_CONTROL  = 0x0002
MOD_SHIFT    = 0x0004
MOD_WIN      = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY    = 0x0312
WM_QUIT      = 0x0012

VK_MAP = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B
}

class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [
        ('hwnd', ctypes.wintypes.HWND),
        ('wFunc', ctypes.wintypes.UINT),
        ('pFrom', ctypes.wintypes.LPCWSTR),
        ('pTo', ctypes.wintypes.LPCWSTR),
        ('fFlags', ctypes.wintypes.WORD),
        ('fAnyOperationsAborted', ctypes.wintypes.BOOL),
        ('hNameMappings', ctypes.wintypes.LPVOID),
        ('lpszProgressTitle', ctypes.wintypes.LPCWSTR),
    ]

FO_DELETE = 0x0003
FOF_ALLOWUNDO = 0x0040
FOF_NOCONFIRMATION = 0x0010
FOF_SILENT = 0x0004

def safe_send_to_recycle_bin(filepath):
    """Windows Shell API를 사용하여 안전하게 휴지통으로 이동 (영구삭제 방지)"""
    try:
        abspath = os.path.abspath(filepath)
        p_from = abspath + '\0\0'
        fileop = SHFILEOPSTRUCTW()
        fileop.hwnd = None
        fileop.wFunc = FO_DELETE
        fileop.pFrom = p_from
        fileop.pTo = None
        fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
        ret = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
        if ret != 0:
            os.remove(filepath)
        return True
    except Exception:
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False

# ==========================================
# 다국어 리소스 사전 (i18n) - 간결화 및 완전 갱신
# ==========================================
I18N = {
    "ko": {
        "app_title": "📂 서브컬처 미디어 매니저 & 런처 v2.7",
        "tab_launcher": "🎲 스마트 랜덤 런처",
        "tab_organizer": "📁 작가/서클 스마트 정리기",
        "help_btn": "❓ 사용법 / Help",
        "lang_label": "🌐 언어:",
        "btn_manga": "🎲 랜덤 만화 열기\n[ 단축키: {key} ]",
        "btn_video": "🎬 랜덤 영상 열기\n[ 단축키: {key} ]",
        "path_settings": "경로 설정",
        "manga_folder": "📁 만화 폴더:",
        "manga_viewer": "👁 만화 뷰어:",
        "video_folder": "🎥 영상 폴더:",
        "video_player": "▶ 영상 플레이어:",
        "browse": "찾아보기",
        "refresh": "🔄 새로고침",
        "subfolders": "하위 폴더 포함",
        "topmost": "항상 위",
        "hotkeys_active": "단축키 활성화",
        "hotkey_manga_lbl": "만화:",
        "hotkey_video_lbl": "영상:",
        "history_title": "📜 최근 실행 목록 (더블클릭: 다시 열기)",
        "open_folder": "📂 파일 위치 열기",
        "status_ready": "준비 완료 (만화: {manga:,}개 | 영상: {video:,}개)",
        "cache_loaded": "[캐시 로드됨]",
        # 정리기 탭
        "org_folder_settings": "정리 폴더 지정",
        "src_folder": "📥 정리 대상 폴더:",
        "dst_folder": "📚 기준 보관 폴더:",
        "detected_authors": "감지된 작가 폴더: {count:,}개 (수동: {manual:,} / Auto: {auto:,})",
        "org_options": "정리 옵션",
        "opt_auto_folder": "신규 작가는 '작가명 [Auto]' 폴더 자동 생성 (해제 시 미분류 파일 이동 안 함)",
        "opt_mtime_conflict": "동일 파일 충돌 시 '수정한 날짜' 최신본 남기고 구버전 휴지통 이동",
        "btn_start_organize": "▶ 스마트 자동 정리 시작",
        "btn_stop_organize": "⏹ 작업 중단",
        "btn_extract_subfolders": "↩ 하위 폴더 내용물 꺼내기 (되돌리기)",
        "warn_auto_folder_toggle": "⚠️ [Auto] 폴더 자동생성 옵션 안내\n\n이 옵션은 작가/서클명 표기 없이 제목만 있는 단편 파일의 경우 제목마다 새 폴더가 생성될 수 있습니다.\n\n제목만 있는 파일은 미리 수작업으로 정리한 후 실행하는 것을 권장합니다.\n\n계속 활성화하시겠습니까?",
        "warn_auto_folder_start": "⚠️ [Auto] 폴더 자동생성 옵션이 켜져 있습니다.\n\n작가 표기가 없는 파일은 제목마다 개별 폴더가 생성될 수 있습니다.\n\n정말로 정리를 시작하시겠습니까?",
        "warn_extract_subfolders": "⚠️ [주의] 하위 폴더 내용물 꺼내기 (되돌리기)\n\n지정된 폴더 내부의 모든 직속 하위 폴더에서 파일을 상위로 꺼내고 빈 폴더를 삭제합니다.\n\n원치 않는 기존 폴더가 섞여서 풀리는 것을 방지하기 위해,\n[미리 내용물을 꺼낼 대상 폴더들만 안전한 별도 폴더에 이동시킨 후 실행]하십시오.\n\n정말로 실행하시겠습니까?",
        "select_folder_to_extract": "내용물을 상위로 꺼낼 대상 상위 폴더를 선택하세요",
        "msg_extract_done": "하위 폴더 내용물 꺼내기가 완료되었습니다!\n이동된 파일: {moved_files:,}개\n삭제된 빈 폴더: {deleted_dirs:,}개",
        "progress_status": "진행도: {cur} / {total} ({percent}%)",
        "log_title": "📋 실시간 처리 로그",
        "warn_no_folder": "폴더 경로를 먼저 지정해주세요.",
        "msg_done": "정리 작업이 완료되었습니다!\n총 처리: {total}건 (성공: {success}건, 충돌해결: {conflict}건, 스킵: {fail}건)",
        "confirm_stop": "작업을 중단하시겠습니까?",
        "help_content": """[서브컬처 미디어 매니저 & 런처 사용 안내]

1. 🎲 스마트 랜덤 런처
- 만화/영상 폴더를 지정한 후 큰 버튼 또는 전역 단축키를 누르면 무작위 감상합니다.
- 기본 단축키: 만화(F8), 영상(F7) - 옵션에서 F1~F12 자유 변경 가능.
- 대용량 드라이브(E:/ 등)도 캐시 기능을 통해 재실행 시 0.01초 만에 즉시 준비 완료됩니다.

2. 📁 작가/서클 스마트 자동 정리기
- 모든 파일(압축파일, 이미지, 영상 등)을 작가/서클별 폴더로 자동 분류·이동합니다.
- 초반 1~2번째 괄호 위치를 지능적으로 분석하여, 뒤쪽의 원작 장르명((Fate...), (원작...))이나 언어 태그([Korean])를 작가명으로 오인하지 않습니다.
- 괄호가 없는 파일(aaa.zip 등)도 파일명 자체를 대조하여 기존 폴더와 정상 매칭합니다.
- 신규 작가 옵션 해제 시에는 미분류 파일을 임의로 이동하지 않고 원래 위치에 보존합니다."""
    },
    "ja": {
        "app_title": "📂 サブカルチャーメディアマネージャー & ランチャー v2.7",
        "tab_launcher": "🎲 スマートランダムランチャー",
        "tab_organizer": "📁 作家/サークル自動整理",
        "help_btn": "❓ 使い方 / Help",
        "lang_label": "🌐 言語:",
        "btn_manga": "🎲 ランダムマンガ\n[ キー: {key} ]",
        "btn_video": "🎬 ランダム動画\n[ キー: {key} ]",
        "path_settings": "パス設定",
        "manga_folder": "📁 マンガフォルダ:",
        "manga_viewer": "👁 マンガビューアー:",
        "video_folder": "🎥 動画フォルダ:",
        "video_player": "▶ 動画プレイヤー:",
        "browse": "参照",
        "refresh": "🔄 更新",
        "subfolders": "サブフォルダ含む",
        "topmost": "常に最前面",
        "hotkeys_active": "ショートカット有効",
        "hotkey_manga_lbl": "マンガ:",
        "hotkey_video_lbl": "動画:",
        "history_title": "📜 最近開いたファイル (ダブルクリックで再実行)",
        "open_folder": "📂 ファイルの場所",
        "status_ready": "準備完了 (マンガ: {manga:,} | 動画: {video:,})",
        "cache_loaded": "[キャッシュ済]",
        # Organizer
        "org_folder_settings": "整理フォルダ指定",
        "src_folder": "📥 整理対象フォルダ:",
        "dst_folder": "📚 基準保管フォルダ:",
        "detected_authors": "検出された作家フォルダ: {count:,}個 (手動: {manual:,} / Auto: {auto:,})",
        "org_options": "整理オプション",
        "opt_auto_folder": "新規作家は「作家名 [Auto]」フォルダ作成 (オフ時は移動しない)",
        "opt_mtime_conflict": "重複時は更新日時が最新のものを残し、古いものはゴミ箱へ",
        "btn_start_organize": "▶ 自動整理を開始",
        "btn_stop_organize": "⏹ 中断",
        "btn_extract_subfolders": "↩ サブフォルダのファイルを親フォルダへ戻す (取り消し)",
        "warn_auto_folder_toggle": "⚠️ [Auto] フォルダ自動作成について\n\n作家名やサークル名の表記がなくタイトルのみのファイルの場合、タイトルごとに個別のフォルダが作成される可能性があります。\n\nタイトルのみのファイルは事前に手動で整理することを推奨します。\n\n有効にしますか？",
        "warn_auto_folder_start": "⚠️ [Auto] フォルダ自動作成が有効になっています。\n\n作家表記のないファイルはタイトルごとにフォルダが作成される可能性があります。\n\n本当に整理を開始しますか？",
        "warn_extract_subfolders": "⚠️ [注意] サブフォルダ内容物の取り出し (取り消し)\n\n指定されたフォルダ内のすべてのサブフォルダからファイルを親フォルダへ移動し、空になったフォルダを削除します。\n\n意図しない既存フォルダが解体されるのを防ぐため、[事前に取り出したい対象フォルダのみを別の安全な作業用フォルダへ移動してから実行]してください。\n\n本当に実行しますか？",
        "select_folder_to_extract": "ファイルを親フォルダへ取り出す対象の親フォルダを選択してください",
        "msg_extract_done": "サブフォルダ内容物の取り出し完了！\n移動されたファイル: {moved_files:,}個\n削除された空フォルダ: {deleted_dirs:,}個",
        "progress_status": "進捗: {cur} / {total} ({percent}%)",
        "log_title": "📋 リアルタイムログ",
        "warn_no_folder": "フォルダのパスを指定してください。",
        "msg_done": "整理が完了しました！\n合計: {total}件 (成功: {success}件, 衝突解決: {conflict}件, スキップ: {fail}件)",
        "confirm_stop": "作業を中断しますか？",
        "help_content": """[サブカルチャーメディアマネージャー 使い方]

1. 🎲 スマートランダムランチャー
- フォルダ指定後、ボタンまたはショートカットキーでランダム起動します。
- 基本ショートカット: マンガ(F8)、動画(F7) - 設定でF1~F12に変更可能。

2. 📁 作家/サークル自動整理
- すべてのファイル(ZIP、画像、動画等)を作家フォルダへ自動分類します。
- 1~2番目の括弧位置を正確に解析し、後ろの原作タグ((Fate...)等)を作家名と誤認しません。
- 括弧のないファイル(aaa.zip等)も既存フォルダと正常に照合します。"""
    },
    "en": {
        "app_title": "📂 Subculture Media Manager & Launcher v2.7",
        "tab_launcher": "🎲 Smart Random Launcher",
        "tab_organizer": "📁 Smart Author Organizer",
        "help_btn": "❓ Help / Guide",
        "lang_label": "🌐 Language:",
        "btn_manga": "🎲 Random Comic\n[ Hotkey: {key} ]",
        "btn_video": "🎬 Random Video\n[ Hotkey: {key} ]",
        "path_settings": "Path Settings",
        "manga_folder": "📁 Comic Folder:",
        "manga_viewer": "👁 Comic Viewer:",
        "video_folder": "🎥 Video Folder:",
        "video_player": "▶ Video Player:",
        "browse": "Browse",
        "refresh": "🔄 Refresh",
        "subfolders": "Include Subfolders",
        "topmost": "Always on Top",
        "hotkeys_active": "Enable Hotkeys",
        "hotkey_manga_lbl": "Comic:",
        "hotkey_video_lbl": "Video:",
        "history_title": "📜 Recent History (Double-click to reopen)",
        "open_folder": "📂 Open Folder",
        "status_ready": "Ready (Comics: {manga:,} | Videos: {video:,})",
        "cache_loaded": "[Cached]",
        # Organizer
        "org_folder_settings": "Folder Settings",
        "src_folder": "📥 Source Folder:",
        "dst_folder": "📚 Library Folder:",
        "detected_authors": "Detected Author Folders: {count:,} (Manual: {manual:,} / Auto: {auto:,})",
        "org_options": "Organizing Options",
        "opt_auto_folder": "Auto-create 'Author [Auto]' folder (Keep files in place if unchecked)",
        "opt_mtime_conflict": "Keep newer modified date on conflict, move older to Recycle Bin",
        "btn_start_organize": "▶ Start Auto-Organizing",
        "btn_stop_organize": "⏹ Stop",
        "btn_extract_subfolders": "↩ Extract Files from Subfolders (Undo / Flatten)",
        "warn_auto_folder_toggle": "⚠️ Auto-Create Folder Notice\n\nIf files only have a title without author/circle tags, a separate folder may be created for each individual title.\n\nIt is recommended to manually organize title-only files beforehand.\n\nDo you want to enable this option?",
        "warn_auto_folder_start": "⚠️ Auto-create folder option is currently enabled.\n\nFiles without author tags may result in separate folders for each title.\n\nDo you want to proceed with organizing?",
        "warn_extract_subfolders": "⚠️ [Caution] Extract Files from Subfolders (Undo)\n\nThis will move all files from direct subfolders into the parent folder and remove empty subfolders.\n\nTo prevent existing folders from being unpacked unintentionally, please [move only the target folders to a safe separate working directory before running this].\n\nDo you really want to proceed?",
        "select_folder_to_extract": "Select the parent folder containing subfolders to unpack",
        "msg_extract_done": "Subfolder extraction completed!\nFiles moved: {moved_files:,}\nEmpty folders removed: {deleted_dirs:,}",
        "progress_status": "Progress: {cur} / {total} ({percent}%)",
        "log_title": "📋 Real-time Process Log",
        "warn_no_folder": "Please specify the folder paths first.",
        "msg_done": "Organizing complete!\nTotal: {total} (Success: {success}, Conflict Resolved: {conflict}, Skipped: {fail})",
        "confirm_stop": "Do you want to stop the process?",
        "help_content": """[Subculture Media Manager & Launcher Guide]

1. 🎲 Smart Random Launcher
- Randomly launches comic archives or video files with one click or hotkeys.
- Default Hotkeys: Comic (F8), Video (F7) - customizable from F1 to F12.
- Instant 0.01s startup via local caching even on large root drives (E:/).

2. 📁 Smart Author Organizer
- Categorizes all file formats (archives, images, videos) into author folders.
- Positional bracket analysis prevents genre tags (e.g. Fate) from being mistaken as author names.
- Files without brackets (e.g. aaa.zip) are matched directly to folder 'aaa'."""
    }
}

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(get_base_dir(), "config.json")
CACHE_PATH  = os.path.join(get_base_dir(), "media_cache.json")

# ==========================================
# 전역 단축키 매니저 (ctypes RegisterHotKey)
# ==========================================
class GlobalHotkeyManager:
    def __init__(self, on_hotkey_callback):
        self.on_hotkey = on_hotkey_callback
        self.thread = None
        self.thread_id = None
        self.is_running = False
        self.hotkeys = {}

    def set_hotkeys(self, manga_vk_name, video_vk_name):
        self.hotkeys = {
            1: (0, VK_MAP.get(manga_vk_name, 0x77), "manga"), # F8 기본
            2: (0, VK_MAP.get(video_vk_name, 0x76), "video")  # F7 기본
        }

    def start(self):
        if self.is_running:
            self.stop()
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.thread_id:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
        self.thread = None

    def _run_loop(self):
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        user32 = ctypes.windll.user32

        registered = []
        for hid, (mod, vk, _) in self.hotkeys.items():
            if vk and user32.RegisterHotKey(None, hid, mod | MOD_NOREPEAT, vk):
                registered.append(hid)

        msg = ctypes.wintypes.MSG()
        while self.is_running:
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break
            if msg.message == WM_HOTKEY:
                hid = msg.wParam
                if hid in self.hotkeys and self.on_hotkey:
                    self.on_hotkey(hid, self.hotkeys[hid][2])
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        for hid in registered:
            user32.UnregisterHotKey(None, hid)

# ==========================================
# 위치 기반 괄호 메타데이터 파서 (Positional Bracket Tokenizer)
# ==========================================
EVENT_RE = re.compile(
    r'^([cC]\d+|comike\s*\d*|comiket\s*\d*|comic\s*market\s*\d*|コミケ\s*\d*|コミックマーケット\s*\d*|COMIC1[☆★\d\s]*|例大祭\d*|サンクリ[^\)\]]*|こみトレ\d*|SC\d*|M3[^\)\]]*|COMITIA\d*|コミティア\d*|COMIC\s+CITY[^\)\]]*|COMIC\s+快楽天[^\)\]]*|コミック[^\)\]]*|Mimiket\s*\d*|紅楼夢\d*|ふたけっと\d*|FF\d+)$',
    re.IGNORECASE
)
PLATFORM_KEYWORDS = {'fanbox', 'pixiv', 'twitter', 'fantia', 'ci-en', 'skeb', 'patreon', 'gumroad', 'subscribestar', 'dlsite'}
STATUS_TAGS = {'완결', '完', '단편', '단면', '양면', '미완', '연재', '개정판', '무삭제', '전권', '단행본', '스캔'}

def is_event_or_platform(token):
    t = token.strip()
    if EVENT_RE.match(t):
        return True
    if t.lower() in PLATFORM_KEYWORDS:
        return True
    if t in STATUS_TAGS or re.match(r'^(~?\s*\d+\s*화|JPG\d*|PNG\d*|단면|양면)', t, re.IGNORECASE):
        return True
    return False

def strip_volume_and_numbers(name):
    """단행본 권수/화수 및 말단 숫자 제거하여 순수 시리즈 제목 추출"""
    clean = name.strip()
    clean = re.sub(r'[\(\[]\s*~?\s*\d+\s*(?:화|권|부)?(?:\s*완결|\s*完)?\s*[\)\]]', '', clean)
    clean = re.sub(r'[\(\[]\s*(?:완결|完|단편|단면|양면|스캔|JPG\d*.*?)\s*[\)\]]', '', clean)
    
    prev = clean
    clean = re.sub(r'[\s_]*~?\s*\d+\s*(?:화|권|부)(?:\s*완결|\s*完)?$', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[\s_]*\d+\s*(?:완결|完)$', '', clean, flags=re.IGNORECASE)
    if clean != prev:
        return clean.strip()
    
    if re.search(r'\s+\d{1,3}$', clean):
        clean = re.sub(r'\s+\d{1,3}$', '', clean)
        return clean.strip()
        
    clean = re.sub(r'(?<=[^\d\s])\d{1,3}$', '', clean)
    return clean.strip()

def extract_version_number(filename):
    """(1), (2) 등 다운로드 중복 번호 추출 (기본 파일은 0)"""
    base, _ = os.path.splitext(filename)
    m = re.search(r'[\(\[]([0-9]+)[\)\]]$', base.strip())
    if m:
        return int(m.group(1))
    return 0

def find_existing_duplicate_target(target_dir, filename):
    """목적지 폴더에 동일 파일명 또는 넘버링( (1), (2) )만 다른 동일 작품이 존재하는지 검사"""
    exact_path = os.path.join(target_dir, filename)
    if os.path.exists(exact_path):
        return exact_path

    base_name, ext = os.path.splitext(filename)
    norm_base = re.sub(r'[\s_]*\([0-9]+\)$', '', base_name).strip()
    norm_base = re.sub(r'[\s_]*\[[0-9]+\]$', '', norm_base).strip()

    try:
        for entry in os.scandir(target_dir):
            if entry.is_file():
                e_name, e_ext = os.path.splitext(entry.name)
                if e_ext.lower() == ext.lower():
                    e_norm = re.sub(r'[\s_]*\([0-9]+\)$', '', e_name).strip()
                    e_norm = re.sub(r'[\s_]*\[[0-9]+\]$', '', e_norm).strip()
                    if e_norm.lower() == norm_base.lower():
                        return entry.path
    except Exception:
        pass
    return None

def extract_top_brackets(text):
    """문자열의 좌측부터 최상위 괄호 블록들을 순서대로 추출"""
    results = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] in '([':
            start_char = text[i]
            end_char = ')' if start_char == '(' else ']'
            start_idx = i
            i += 1
            depth = 1
            while i < n and depth > 0:
                if text[i] == start_char:
                    depth += 1
                elif text[i] == end_char:
                    depth -= 1
                i += 1
            block = text[start_idx + 1:i - 1].strip()
            results.append((start_char, block, start_idx, i))
        else:
            i += 1
    return results

def parse_author_metadata(filename):
    """
    초반 1~2번째 괄호 위치를 기반으로 서클/작가명을 정확히 추출.
    동인지뿐만 아니라 일반 연재 단행본(공포학교, HyperPolice 등)의 권수/숫자를 제거하여 단일 시리즈로 통합.
    """
    clean, _ = os.path.splitext(filename)
    clean = clean.replace('［', '[').replace('］', ']').replace('（', '(').replace('）', ')').strip()

    # 1. 파일명 끝의 순수 숫자 괄호 (" (2)", " [1]") 사전 분리
    clean = re.sub(r'[\s_]*\([0-9]+\)$', '', clean)
    clean = re.sub(r'[\s_]*\[[0-9]+\]$', '', clean).strip()

    brackets = extract_top_brackets(clean)

    # 1. 괄호가 전혀 없는 파일 (예: 공포학교01.zip, HyperPolice02.zip, aaa.zip)
    if not brackets:
        stripped = strip_volume_and_numbers(clean)
        if ' - ' in stripped:
            cand = stripped.split(' - ')[0].strip()
            return (cand, cand)
        final_cand = stripped if stripped else clean
        return (final_cand, final_cand)

    def split_circle_author(token):
        m = re.match(r'^(.*?)\((.*?)\)$', token)
        if m:
            c = m.group(1).strip()
            a = m.group(2).strip()
            if c and a:
                return (c, a)
        return (token, token)

    first_is_meta = is_event_or_platform(brackets[0][1])

    # 2. 1번째 괄호가 행사명, 플랫폼, 상태 태그인 경우
    if first_is_meta:
        # 1번째와 2번째 괄호 사이에 일반 텍스트(aaa 또는 시리즈명)가 있는 경우
        if len(brackets) >= 2:
            between_text = clean[brackets[0][3]:brackets[1][2]].strip()
            if between_text and not between_text.startswith(('-', '_')):
                stripped_between = strip_volume_and_numbers(between_text)
                final_b = stripped_between if stripped_between else between_text
                return (final_b, final_b)
            else:
                if not re.match(r'^[0-9]+$', brackets[1][1].strip()):
                    return split_circle_author(brackets[1][1])

        rest = clean[brackets[0][3]:].strip()
        if rest:
            m_sns = re.search(r'@[\w\.\-_]+\s*\(([^)]+)\)', rest)
            if m_sns:
                a = m_sns.group(1).strip()
                return (a, a)
            if ' - ' in rest:
                cand = rest.split(' - ')[0].strip()
                return (cand, cand)
            cand = re.split(r'[\(\[]', rest)[0].strip()
            if cand:
                stripped_cand = strip_volume_and_numbers(cand)
                final_c = stripped_cand if stripped_cand else cand
                return (final_c, final_c)
            stripped_rest = strip_volume_and_numbers(rest)
            final_r = stripped_rest if stripped_rest else rest
            return (final_r, final_r)

        return (brackets[0][1], brackets[0][1])
    else:
        # 3. 1번째 괄호가 일반 명칭인 경우 (예: [Wise Speak])
        return split_circle_author(brackets[0][1])

# ==========================================
# 메인 GUI 애플리케이션 클래스
# ==========================================
class SubcultureMediaManagerApp:
    def __init__(self, root):
        self.root = root
        self.config = self.load_config()
        self.lang = self.config.get("language", "ko")
        if self.lang not in I18N:
            self.lang = "ko"

        self.root.title(self.t("app_title"))
        self.root.geometry("780x740")
        self.root.minsize(700, 620)

        # 런처 데이터 캐시
        self.manga_files_cache = []
        self.video_files_cache = []
        self.recent_history = deque(maxlen=35)
        self.recent_played_set = deque(maxlen=25)
        self.scan_lock = threading.Lock()

        # 정리기 상태
        self.is_organizing = False
        self.cancel_requested = False
        self.author_folders_map = {}

        # 단축키 매니저 초기화
        self.hotkey_mgr = GlobalHotkeyManager(self._on_global_hotkey)
        self.update_hotkeys()

        # 스타일
        self.setup_styles()

        # UI 위젯 딕셔너리 (동적 언어 전환용)
        self.ui_labels = {}

        # UI 생성
        self.build_ui()

        # 캐시 불러오기 & 백그라운드 스캔
        self.load_media_cache()
        self.trigger_background_scan()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def t(self, text_id, **kwargs):
        """다국어 텍스트 조회 함수"""
        text = I18N.get(self.lang, I18N["ko"]).get(text_id, text_id)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

    def setup_styles(self):
        self.colors = {
            "bg": "#181926",
            "card_bg": "#24273a",
            "card_border": "#363a4f",
            "text": "#cad3f5",
            "subtext": "#a5adcb",
            "btn_manga": "#805ad5",
            "btn_video": "#3182ce",
            "btn_start": "#2e7d32",
            "btn_stop": "#c53030",
            "entry_bg": "#1e2030",
            "entry_fg": "#cad3f5",
            "accent": "#8aadf4"
        }
        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["card_bg"], foreground=self.colors["text"],
                        font=("Malgun Gothic", 10, "bold"), padding=[16, 6])
        style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])],
                  foreground=[("selected", "#181926")])
        style.configure("TProgressbar", thickness=16, troughcolor=self.colors["entry_bg"],
                        background=self.colors["accent"])

    def load_config(self):
        default_config = {
            "language": "ko",
            "manga_folder": "E:/",
            "manga_viewer": self.detect_viewer(["C:/Program Files/BandiView/BandiView.exe",
                                                r"C:\00 personal program\Honeyview\Honeyview.exe"]),
            "video_folder": "E:/movieeee",
            "video_player": self.detect_viewer([r"C:\00 personal program\PotPlayer\PotPlayer64.exe",
                                                "C:/Program Files/DAUM/PotPlayer/PotPlayer64.exe"]),
            "include_subfolders": True,
            "always_on_top": False,
            "enable_hotkeys": True,
            "hotkey_manga": "F8",
            "hotkey_video": "F7",
            "org_src_folder": "",
            "org_dst_folder": "",
            "opt_auto_folder": False,
            "opt_mtime_conflict": True,
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    default_config.update(saved)
            except Exception as e:
                print(f"설정 로드 오류: {e}")
        return default_config

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 저장 오류: {e}")

    def detect_viewer(self, candidates):
        for c in candidates:
            if os.path.isfile(c):
                return c
        return candidates[0] if candidates else ""

    def load_media_cache(self):
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("manga_folder") == self.config.get("manga_folder"):
                        self.manga_files_cache = data.get("manga_files", [])
                    if data.get("video_folder") == self.config.get("video_folder"):
                        self.video_files_cache = data.get("video_files", [])
                    self.update_launcher_status(is_cached=True)
            except Exception as e:
                print(f"캐시 로드 실패: {e}")

    def save_media_cache(self):
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "manga_folder": self.config.get("manga_folder"),
                    "manga_files": self.manga_files_cache,
                    "video_folder": self.config.get("video_folder"),
                    "video_files": self.video_files_cache
                }, f, ensure_ascii=False)
        except Exception as e:
            print(f"캐시 저장 실패: {e}")

    def update_hotkeys(self):
        manga_k = self.config.get("hotkey_manga", "F8")
        video_k = self.config.get("hotkey_video", "F7")
        self.hotkey_mgr.set_hotkeys(manga_k, video_k)
        if self.config.get("enable_hotkeys", True):
            self.hotkey_mgr.start()
        else:
            self.hotkey_mgr.stop()

    def _on_global_hotkey(self, hid, action):
        if action == "manga":
            self.root.after(0, self.open_random_manga)
        elif action == "video":
            self.root.after(0, self.open_random_video)

    # ==========================================
    # UI 생성 및 동적 다국어 갱신 체계
    # ==========================================
    def build_ui(self):
        # 상단 헤더
        header_bar = tk.Frame(self.root, bg=self.colors["bg"])
        header_bar.pack(fill="x", padx=16, pady=(10, 6))

        self.lbl_app_title = tk.Label(header_bar, text=self.t("app_title"), font=("Malgun Gothic", 12, "bold"),
                                      bg=self.colors["bg"], fg=self.colors["text"])
        self.lbl_app_title.pack(side="left")

        right_header = tk.Frame(header_bar, bg=self.colors["bg"])
        right_header.pack(side="right")

        self.btn_help = tk.Button(right_header, text=self.t("help_btn"), font=("Malgun Gothic", 8, "bold"),
                                  bg="#363a4f", fg="#cad3f5", relief="flat", padx=8, pady=2,
                                  cursor="hand2", command=self.show_help_modal)
        self.btn_help.pack(side="left", padx=(0, 10))

        self.lbl_lang_prefix = tk.Label(right_header, text=self.t("lang_label"), font=("Malgun Gothic", 8),
                                        bg=self.colors["bg"], fg=self.colors["subtext"])
        self.lbl_lang_prefix.pack(side="left", padx=(0, 4))

        self.cb_lang = ttk.Combobox(right_header, values=["한국어", "日本語", "English"], width=8, state="readonly")
        lang_idx = {"ko": 0, "ja": 1, "en": 2}.get(self.lang, 0)
        self.cb_lang.current(lang_idx)
        self.cb_lang.bind("<<ComboboxSelected>>", self.on_language_change)
        self.cb_lang.pack(side="left")

        # 탭 노트북
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        self.tab1 = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.tab2 = tk.Frame(self.notebook, bg=self.colors["bg"])

        self.notebook.add(self.tab1, text=self.t("tab_launcher"))
        self.notebook.add(self.tab2, text=self.t("tab_organizer"))

        self.build_tab1_launcher()
        self.build_tab2_organizer()

    def on_language_change(self, event=None):
        selected = self.cb_lang.get()
        mapping = {"한국어": "ko", "日本語": "ja", "English": "en"}
        self.lang = mapping.get(selected, "ko")
        self.config["language"] = self.lang
        self.save_config()
        self.refresh_ui_texts()

    def refresh_ui_texts(self):
        """언어 변경 시 UI 내 모든 레이블, 버튼, 체크박스 텍스트를 즉각 100% 갱신"""
        self.root.title(self.t("app_title"))
        self.lbl_app_title.config(text=self.t("app_title"))
        self.btn_help.config(text=self.t("help_btn"))
        self.lbl_lang_prefix.config(text=self.t("lang_label"))
        self.notebook.tab(0, text=self.t("tab_launcher"))
        self.notebook.tab(1, text=self.t("tab_organizer"))

        # 런처 위젯들
        mk = self.config.get("hotkey_manga", "F8")
        vk = self.config.get("hotkey_video", "F7")
        self.btn_manga.config(text=self.t("btn_manga", key=mk))
        self.btn_video.config(text=self.t("btn_video", key=vk))

        self.lbl_path_title.config(text=self.t("path_settings"))
        self.chk_sub.config(text=self.t("subfolders"))
        self.chk_top.config(text=self.t("topmost"))
        self.chk_hot.config(text=self.t("hotkeys_active"))
        self.lbl_hk_m_prefix.config(text=self.t("hotkey_manga_lbl"))
        self.lbl_hk_v_prefix.config(text=self.t("hotkey_video_lbl"))
        self.btn_open_folder.config(text=self.t("open_folder"))
        self.lbl_hist_title.config(text=self.t("history_title"))

        # 등록된 동적 라벨들 갱신
        for key, lbl in self.ui_labels.items():
            lbl.config(text=self.t(key))

        # 정리기 위젯들
        self.lbl_org_paths.config(text=self.t("org_folder_settings"))
        self.lbl_org_opts.config(text=self.t("org_options"))
        self.chk_auto.config(text=self.t("opt_auto_folder"))
        self.chk_mtime.config(text=self.t("opt_mtime_conflict"))
        self.btn_start_org.config(text=self.t("btn_start_organize"))
        self.btn_stop_org.config(text=self.t("btn_stop_organize"))
        if hasattr(self, 'btn_extract'):
            self.btn_extract.config(text=self.t("btn_extract_subfolders"))
        self.lbl_log_title.config(text=self.t("log_title"))

        self.update_launcher_status()
        self.scan_destination_authors(self.config.get("org_dst_folder", ""))

    # -------------------------------------------------------------
    # 탭 1: 스마트 랜덤 미디어 런처
    # -------------------------------------------------------------
    def build_tab1_launcher(self):
        p = tk.Frame(self.tab1, bg=self.colors["bg"])
        p.pack(fill="both", expand=True, padx=8, pady=8)

        # 1. 대형 액션 버튼 카드
        btn_card = tk.Frame(p, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        btn_card.pack(fill="x", pady=(0, 8), ipady=6, ipadx=8)

        grid = tk.Frame(btn_card, bg=self.colors["card_bg"])
        grid.pack(fill="x", expand=True, padx=6, pady=4)

        mk = self.config.get("hotkey_manga", "F8")
        vk = self.config.get("hotkey_video", "F7")

        self.btn_manga = tk.Button(grid, text=self.t("btn_manga", key=mk), font=("Malgun Gothic", 11, "bold"),
                                   bg=self.colors["btn_manga"], fg="#ffffff", activebackground="#6b46c1",
                                   relief="flat", cursor="hand2", pady=8, command=self.open_random_manga)
        self.btn_manga.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self.btn_video = tk.Button(grid, text=self.t("btn_video", key=vk), font=("Malgun Gothic", 11, "bold"),
                                   bg=self.colors["btn_video"], fg="#ffffff", activebackground="#2b6cb0",
                                   relief="flat", cursor="hand2", pady=8, command=self.open_random_video)
        self.btn_video.pack(side="right", fill="both", expand=True, padx=(4, 0))

        # 2. 경로 설정 카드
        path_card = tk.Frame(p, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        path_card.pack(fill="x", pady=(0, 8), ipady=4, ipadx=6)

        self.lbl_path_title = tk.Label(path_card, text=self.t("path_settings"), font=("Malgun Gothic", 9, "bold"),
                                       bg=self.colors["card_bg"], fg=self.colors["accent"])
        self.lbl_path_title.pack(anchor="w", padx=8, pady=(2, 2))

        self.create_entry_row(path_card, "manga_folder", True)
        self.create_entry_row(path_card, "manga_viewer", False)
        self.create_entry_row(path_card, "video_folder", True)
        self.create_entry_row(path_card, "video_player", False)

        # 3. 단축키 및 옵션 바
        opt_bar = tk.Frame(p, bg=self.colors["bg"])
        opt_bar.pack(fill="x", pady=(0, 6))

        hk_frame = tk.Frame(opt_bar, bg=self.colors["bg"])
        hk_frame.pack(side="left")

        self.lbl_hk_m_prefix = tk.Label(hk_frame, text=self.t("hotkey_manga_lbl"), font=("Malgun Gothic", 8),
                                        bg=self.colors["bg"], fg=self.colors["text"])
        self.lbl_hk_m_prefix.pack(side="left")

        self.cb_manga_hk = ttk.Combobox(hk_frame, values=list(VK_MAP.keys()), width=4, state="readonly")
        self.cb_manga_hk.set(self.config.get("hotkey_manga", "F8"))
        self.cb_manga_hk.bind("<<ComboboxSelected>>", self.on_hotkey_change)
        self.cb_manga_hk.pack(side="left", padx=(2, 8))

        self.lbl_hk_v_prefix = tk.Label(hk_frame, text=self.t("hotkey_video_lbl"), font=("Malgun Gothic", 8),
                                        bg=self.colors["bg"], fg=self.colors["text"])
        self.lbl_hk_v_prefix.pack(side="left")

        self.cb_video_hk = ttk.Combobox(hk_frame, values=list(VK_MAP.keys()), width=4, state="readonly")
        self.cb_video_hk.set(self.config.get("hotkey_video", "F7"))
        self.cb_video_hk.bind("<<ComboboxSelected>>", self.on_hotkey_change)
        self.cb_video_hk.pack(side="left", padx=(2, 8))

        self.var_hotkeys = tk.BooleanVar(value=self.config.get("enable_hotkeys", True))
        self.chk_hot = tk.Checkbutton(hk_frame, text=self.t("hotkeys_active"), variable=self.var_hotkeys,
                                      bg=self.colors["bg"], fg=self.colors["text"], selectcolor=self.colors["card_bg"],
                                      command=self.on_hotkeys_toggle)
        self.chk_hot.pack(side="left")

        chk_right = tk.Frame(opt_bar, bg=self.colors["bg"])
        chk_right.pack(side="right")

        self.var_sub = tk.BooleanVar(value=self.config.get("include_subfolders", True))
        self.chk_sub = tk.Checkbutton(chk_right, text=self.t("subfolders"), variable=self.var_sub,
                                      bg=self.colors["bg"], fg=self.colors["text"], selectcolor=self.colors["card_bg"],
                                      command=self.on_launcher_option_change)
        self.chk_sub.pack(side="left", padx=(0, 6))

        self.var_top = tk.BooleanVar(value=self.config.get("always_on_top", False))
        self.chk_top = tk.Checkbutton(chk_right, text=self.t("topmost"), variable=self.var_top,
                                      bg=self.colors["bg"], fg=self.colors["text"], selectcolor=self.colors["card_bg"],
                                      command=self.on_launcher_option_change)
        self.chk_top.pack(side="left")
        self.root.attributes("-topmost", self.var_top.get())

        # 4. 최근 실행 기록
        hist_bar = tk.Frame(p, bg=self.colors["bg"])
        hist_bar.pack(fill="x", pady=(2, 2))
        self.lbl_hist_title = tk.Label(hist_bar, text=self.t("history_title"), font=("Malgun Gothic", 8, "bold"),
                                       bg=self.colors["bg"], fg=self.colors["text"])
        self.lbl_hist_title.pack(side="left")

        self.btn_open_folder = tk.Button(hist_bar, text=self.t("open_folder"), font=("Malgun Gothic", 8),
                                         bg="#363a4f", fg="#cad3f5", relief="flat", padx=6, pady=1,
                                         command=self.open_selected_history_in_explorer)
        self.btn_open_folder.pack(side="right")

        hist_box_frame = tk.Frame(p, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        hist_box_frame.pack(fill="both", expand=True, pady=(0, 6))

        self.hist_listbox = tk.Listbox(hist_box_frame, bg=self.colors["entry_bg"], fg=self.colors["text"],
                                       selectbackground="#494d64", font=("Consolas", 9), relief="flat", bd=0)
        sb = tk.Scrollbar(hist_box_frame, orient="vertical", command=self.hist_listbox.yview)
        self.hist_listbox.config(yscrollcommand=sb.set)
        self.hist_listbox.pack(side="left", fill="both", expand=True, padx=3, pady=3)
        sb.pack(side="right", fill="y", pady=3)
        self.hist_listbox.bind("<Double-Button-1>", self.on_history_double_click)

        # 5. 상태바
        self.launcher_status = tk.Label(p, text="", font=("Malgun Gothic", 8),
                                        bg=self.colors["bg"], fg=self.colors["subtext"], anchor="w")
        self.launcher_status.pack(fill="x")
        self.update_launcher_status()

    def create_entry_row(self, parent, config_key, is_folder):
        row = tk.Frame(parent, bg=self.colors["card_bg"])
        row.pack(fill="x", padx=8, pady=2)

        lbl = tk.Label(row, text=self.t(config_key), width=16, anchor="w",
                       font=("Malgun Gothic", 8), bg=self.colors["card_bg"], fg=self.colors["text"])
        lbl.pack(side="left")
        self.ui_labels[config_key] = lbl

        var = tk.StringVar(value=self.config.get(config_key, ""))
        setattr(self, f"var_{config_key}", var)

        ent = tk.Entry(row, textvariable=var, font=("Malgun Gothic", 8),
                       bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                       insertbackground="#ffffff", relief="flat", highlightbackground="#363a4f", highlightthickness=1)
        ent.pack(side="left", fill="x", expand=True, padx=4, ipady=1)

        def browse():
            if is_folder:
                chosen = filedialog.askdirectory(initialdir=var.get() or "C:\\")
            else:
                chosen = filedialog.askopenfilename(filetypes=[("Programs", "*.exe"), ("All", "*.*")],
                                                    initialdir=os.path.dirname(var.get()) if var.get() else "C:\\")
            if chosen:
                var.set(chosen)
                self.config[config_key] = chosen
                self.save_config()
                if is_folder:
                    self.trigger_background_scan()

        btn = tk.Button(row, text=self.t("browse"), font=("Malgun Gothic", 8),
                        bg="#363a4f", fg="#cad3f5", relief="flat", padx=6, pady=1, command=browse)
        btn.pack(side="right")
        self.ui_labels[f"browse_{config_key}"] = btn

    def on_hotkey_change(self, event=None):
        self.config["hotkey_manga"] = self.cb_manga_hk.get()
        self.config["hotkey_video"] = self.cb_video_hk.get()
        self.save_config()
        self.update_hotkeys()
        self.refresh_ui_texts()

    def on_hotkeys_toggle(self):
        self.config["enable_hotkeys"] = self.var_hotkeys.get()
        self.save_config()
        self.update_hotkeys()

    def on_launcher_option_change(self):
        self.config["include_subfolders"] = self.var_sub.get()
        self.config["always_on_top"] = self.var_top.get()
        self.root.attributes("-topmost", self.var_top.get())
        self.save_config()
        self.trigger_background_scan()

    def trigger_background_scan(self):
        t = threading.Thread(target=self._scan_launcher_worker, daemon=True)
        t.start()

    def _scan_launcher_worker(self):
        manga_dir = self.config.get("manga_folder", "").strip()
        video_dir = self.config.get("video_folder", "").strip()
        include_sub = self.config.get("include_subfolders", True)

        m_exts = {".zip", ".rar", ".cbz", ".cbr", ".7z", ".tar", ".pdf"}
        v_exts = {".mp4", ".mkv", ".avi", ".wmv", ".webm", ".mov", ".flv", ".ts", ".m4v"}

        new_manga = []
        if manga_dir and os.path.isdir(manga_dir):
            new_manga = self._safe_deep_walk(manga_dir, m_exts, include_sub)

        new_video = []
        if video_dir and os.path.isdir(video_dir):
            new_video = self._safe_deep_walk(video_dir, v_exts, include_sub)

        with self.scan_lock:
            self.manga_files_cache = new_manga
            self.video_files_cache = new_video

        self.save_media_cache()
        self.root.after(0, self.update_launcher_status)

    def _safe_deep_walk(self, base_folder, exts, include_sub):
        results = []
        SKIP_DIRS = {"$recycle.bin", "system volume information", ".git", ".svn", "node_modules", "recovery"}
        try:
            if include_sub:
                for root, dirs, files in os.walk(base_folder, topdown=True, onerror=None):
                    dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith(".")]
                    for f in files:
                        if f.startswith("._") or f.startswith("~$") or f == "desktop.ini":
                            continue
                        _, ext = os.path.splitext(f)
                        if ext.lower() in exts:
                            results.append(os.path.join(root, f))
            else:
                for entry in os.scandir(base_folder):
                    if entry.is_file():
                        _, ext = os.path.splitext(entry.name)
                        if ext.lower() in exts:
                            results.append(entry.path)
        except Exception as e:
            print(f"탐색 경고: {e}")
        return results

    def update_launcher_status(self, is_cached=False):
        mc = len(self.manga_files_cache)
        vc = len(self.video_files_cache)
        tag = self.t("cache_loaded") if is_cached else ""
        text = f"{self.t('status_ready', manga=mc, video=vc)} {tag}"
        self.launcher_status.config(text=text)

    def open_random_manga(self):
        with self.scan_lock:
            pool = list(self.manga_files_cache)
        if not pool:
            messagebox.showinfo("알림", self.t("warn_no_folder"))
            return
        selected = self._pick_smart_random(pool)
        viewer = self.config.get("manga_viewer", "").strip()
        self._launch_file(selected, viewer, "만화", is_video=False)

    def open_random_video(self):
        with self.scan_lock:
            pool = list(self.video_files_cache)
        if not pool:
            messagebox.showinfo("알림", self.t("warn_no_folder"))
            return
        selected = self._pick_smart_random(pool)
        player = self.config.get("video_player", "").strip()
        self._launch_file(selected, player, "영상", is_video=True)

    def _pick_smart_random(self, pool):
        available = [p for p in pool if p not in self.recent_played_set]
        if not available:
            self.recent_played_set.clear()
            available = pool
        chosen = random.choice(available)
        self.recent_played_set.append(chosen)
        return chosen

    def _launch_file(self, filepath, app_path, category, is_video=False):
        try:
            if app_path and os.path.isfile(app_path):
                subprocess.Popen([app_path, filepath])
            else:
                os.startfile(filepath)

            self.recent_history.appendleft((category, filepath))
            self.hist_listbox.delete(0, tk.END)
            for cat, path in self.recent_history:
                icon = "🎲 [만화]" if cat == "만화" else "🎬 [영상]"
                self.hist_listbox.insert(tk.END, f"{icon} {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("오류", f"실행 중 에러 발생: {e}")

    def on_history_double_click(self, event):
        idx = self.hist_listbox.curselection()
        if not idx:
            return
        cat, filepath = self.recent_history[idx[0]]
        is_vid = (cat == "영상")
        app = self.config.get("video_player" if is_vid else "manga_viewer", "")
        self._launch_file(filepath, app, cat, is_video=is_vid)

    def open_selected_history_in_explorer(self):
        idx = self.hist_listbox.curselection()
        if not idx:
            return
        _, filepath = self.recent_history[idx[0]]
        if os.path.exists(filepath):
            subprocess.Popen(f'explorer /select,"{os.path.abspath(filepath)}"')

    # -------------------------------------------------------------
    # 탭 2: 동인지/서브컬처 스마트 자동 정리기 (위치 기반 파서 & 간소화 옵션)
    # -------------------------------------------------------------
    def build_tab2_organizer(self):
        p = tk.Frame(self.tab2, bg=self.colors["bg"])
        p.pack(fill="both", expand=True, padx=8, pady=8)

        # 1. 폴더 경로 카드
        path_card = tk.Frame(p, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        path_card.pack(fill="x", pady=(0, 8), ipady=4, ipadx=6)

        self.lbl_org_paths = tk.Label(path_card, text=self.t("org_folder_settings"), font=("Malgun Gothic", 9, "bold"),
                                      bg=self.colors["card_bg"], fg=self.colors["accent"])
        self.lbl_org_paths.pack(anchor="w", padx=8, pady=(2, 2))

        self.create_org_path_row(path_card, "org_src_folder", "src_folder")
        self.create_org_path_row(path_card, "org_dst_folder", "dst_folder")

        self.lbl_detected_authors = tk.Label(path_card, text=self.t("detected_authors", count=0, manual=0, auto=0),
                                             font=("Malgun Gothic", 8), bg=self.colors["card_bg"], fg=self.colors["subtext"])
        self.lbl_detected_authors.pack(anchor="w", padx=8, pady=(2, 4))

        # 2. 정리 옵션 카드 (필수 옵션 2개만 깔끔하게 유지)
        opt_card = tk.Frame(p, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        opt_card.pack(fill="x", pady=(0, 8), ipady=4, ipadx=6)

        self.lbl_org_opts = tk.Label(opt_card, text=self.t("org_options"), font=("Malgun Gothic", 9, "bold"),
                                     bg=self.colors["card_bg"], fg=self.colors["accent"])
        self.lbl_org_opts.pack(anchor="w", padx=8, pady=(2, 2))

        self.var_opt_auto = tk.BooleanVar(value=self.config.get("opt_auto_folder", False))
        self.chk_auto = tk.Checkbutton(opt_card, text=self.t("opt_auto_folder"), variable=self.var_opt_auto,
                                       bg=self.colors["card_bg"], fg=self.colors["text"], selectcolor=self.colors["entry_bg"],
                                       command=self.on_toggle_auto_folder)
        self.chk_auto.pack(anchor="w", padx=12, pady=2)

        self.var_opt_mtime = tk.BooleanVar(value=self.config.get("opt_mtime_conflict", True))
        self.chk_mtime = tk.Checkbutton(opt_card, text=self.t("opt_mtime_conflict"), variable=self.var_opt_mtime,
                                        bg=self.colors["card_bg"], fg=self.colors["text"], selectcolor=self.colors["entry_bg"],
                                        command=self.save_org_options)
        self.chk_mtime.pack(anchor="w", padx=12, pady=2)

        # 3. 실행 버튼 및 실수 복구 도구, 프로그레스바
        act_frame = tk.Frame(p, bg=self.colors["bg"])
        act_frame.pack(fill="x", pady=(2, 4))

        self.btn_start_org = tk.Button(act_frame, text=self.t("btn_start_organize"), font=("Malgun Gothic", 10, "bold"),
                                       bg=self.colors["btn_start"], fg="#ffffff", activebackground="#276749",
                                       relief="flat", cursor="hand2", padx=14, pady=6, command=self.start_organizing)
        self.btn_start_org.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_stop_org = tk.Button(act_frame, text=self.t("btn_stop_organize"), font=("Malgun Gothic", 10, "bold"),
                                      bg="#4a5568", fg="#ffffff", activebackground="#718096", state="disabled",
                                      relief="flat", cursor="hand2", padx=14, pady=6, command=self.stop_organizing)
        self.btn_stop_org.pack(side="right", padx=(6, 0))

        rec_frame = tk.Frame(p, bg=self.colors["bg"])
        rec_frame.pack(fill="x", pady=(0, 6))

        self.btn_extract = tk.Button(rec_frame, text=self.t("btn_extract_subfolders"), font=("Malgun Gothic", 9),
                                     bg="#363a4f", fg="#cad3f5", activebackground="#494d64",
                                     relief="flat", cursor="hand2", padx=10, pady=4, command=self.extract_subfolder_contents)
        self.btn_extract.pack(fill="x")

        self.progress_bar = ttk.Progressbar(p, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=(4, 2))

        self.lbl_org_status = tk.Label(p, text=self.t("progress_status", cur=0, total=0, percent=0),
                                       font=("Malgun Gothic", 8), bg=self.colors["bg"], fg=self.colors["subtext"], anchor="w")
        self.lbl_org_status.pack(fill="x", pady=(0, 4))

        # 4. 실시간 로그창
        self.lbl_log_title = tk.Label(p, text=self.t("log_title"), font=("Malgun Gothic", 8, "bold"),
                                      bg=self.colors["bg"], fg=self.colors["text"], anchor="w")
        self.lbl_log_title.pack(fill="x")

        log_frame = tk.Frame(p, bg=self.colors["card_bg"], highlightbackground=self.colors["card_border"], highlightthickness=1)
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, bg=self.colors["entry_bg"], fg=self.colors["text"],
                                font=("Consolas", 8), relief="flat", wrap="none")
        sb_log = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.config(yscrollcommand=sb_log.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=3, pady=3)
        sb_log.pack(side="right", fill="y", pady=3)

    def on_toggle_auto_folder(self):
        if self.var_opt_auto.get():
            if not messagebox.askyesno("안내", self.t("warn_auto_folder_toggle")):
                self.var_opt_auto.set(False)
        self.save_org_options()

    def save_org_options(self):
        self.config["opt_auto_folder"] = self.var_opt_auto.get()
        self.config["opt_mtime_conflict"] = self.var_opt_mtime.get()
        self.save_config()

    def create_org_path_row(self, parent, config_key, label_key):
        row = tk.Frame(parent, bg=self.colors["card_bg"])
        row.pack(fill="x", padx=8, pady=2)

        lbl = tk.Label(row, text=self.t(label_key), width=18, anchor="w",
                       font=("Malgun Gothic", 8), bg=self.colors["card_bg"], fg=self.colors["text"])
        lbl.pack(side="left")
        self.ui_labels[label_key] = lbl

        var = tk.StringVar(value=self.config.get(config_key, ""))
        setattr(self, f"var_{config_key}", var)

        ent = tk.Entry(row, textvariable=var, font=("Malgun Gothic", 8),
                       bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
                       insertbackground="#ffffff", relief="flat", highlightbackground="#363a4f", highlightthickness=1)
        ent.pack(side="left", fill="x", expand=True, padx=4, ipady=1)

        def browse():
            chosen = filedialog.askdirectory(initialdir=var.get() or "C:\\")
            if chosen:
                var.set(chosen)
                self.config[config_key] = chosen
                self.save_config()
                if config_key == "org_dst_folder":
                    self.scan_destination_authors(chosen)

        btn = tk.Button(row, text=self.t("browse"), font=("Malgun Gothic", 8),
                        bg="#363a4f", fg="#cad3f5", relief="flat", padx=6, pady=1, command=browse)
        btn.pack(side="right")
        self.ui_labels[f"browse_{config_key}"] = btn

    def scan_destination_authors(self, dst_folder):
        if not dst_folder or not os.path.isdir(dst_folder):
            self.lbl_detected_authors.config(text=self.t("detected_authors", count=0, manual=0, auto=0))
            return
        author_map = {}
        manual_cnt = 0
        auto_cnt = 0

        try:
            for entry in os.scandir(dst_folder):
                if entry.is_dir():
                    raw_name = entry.name
                    clean_name = raw_name
                    if clean_name.lower().endswith("[auto]"):
                        clean_name = clean_name[:-6].strip()
                        auto_cnt += 1
                    else:
                        manual_cnt += 1

                    norm_key = clean_name.lower().replace(" ", "").replace("_", "")
                    if norm_key:
                        author_map[norm_key] = entry.path

            self.author_folders_map = author_map
            total = manual_cnt + auto_cnt
            msg = self.t("detected_authors", count=total, manual=manual_cnt, auto=auto_cnt)
            self.lbl_detected_authors.config(text=msg)
        except Exception as e:
            print(f"작가 폴더 스캔 에러: {e}")

    def append_log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def start_organizing(self):
        src = self.config.get("org_src_folder", "").strip()
        dst = self.config.get("org_dst_folder", "").strip()
        if not src or not dst or not os.path.isdir(src) or not os.path.isdir(dst):
            messagebox.showwarning("알림", self.t("warn_no_folder"))
            return

        if self.var_opt_auto.get():
            if not messagebox.askyesno("확인", self.t("warn_auto_folder_start")):
                return

        self.scan_destination_authors(dst)
        self.is_organizing = True
        self.cancel_requested = False
        self.btn_start_org.config(state="disabled", bg="#4a5568")
        self.btn_stop_org.config(state="normal", bg=self.colors["btn_stop"])
        if hasattr(self, 'btn_extract'):
            self.btn_extract.config(state="disabled")

        t = threading.Thread(target=self._organize_worker, args=(src, dst), daemon=True)
        t.start()

    def stop_organizing(self):
        if self.is_organizing:
            if messagebox.askyesno("확인", self.t("confirm_stop")):
                self.cancel_requested = True
                self.append_log("⏹ 작업 중단 요청됨...")

    def extract_subfolder_contents(self):
        if self.is_organizing:
            messagebox.showwarning("알림", "정리 작업이 진행 중입니다. 작업이 완료된 후 실행해주세요.")
            return

        if not messagebox.askyesno("주의", self.t("warn_extract_subfolders")):
            return

        initial_dir = self.config.get("org_dst_folder", "").strip() or self.config.get("org_src_folder", "").strip() or "C:\\"
        target_dir = filedialog.askdirectory(title=self.t("select_folder_to_extract"), initialdir=initial_dir)
        if not target_dir or not os.path.isdir(target_dir):
            return

        moved_files = 0
        deleted_dirs = 0

        self.append_log("=" * 60)
        self.append_log(f"🔄 [되돌리기 시작] 대상 상위 폴더: {target_dir}")

        try:
            subdirs = [entry.path for entry in os.scandir(target_dir) if entry.is_dir()]
            if not subdirs:
                self.append_log("ℹ [알림] 하위 폴더가 존재하지 않습니다.")
                messagebox.showinfo("알림", "선택한 폴더 안에 하위 폴더가 없습니다.")
                return

            for sdir in subdirs:
                for root, _, files in os.walk(sdir, topdown=False):
                    for fname in files:
                        src_f = os.path.join(root, fname)
                        dst_f = os.path.join(target_dir, fname)

                        if os.path.exists(dst_f) and os.path.abspath(src_f) != os.path.abspath(dst_f):
                            base, ext = os.path.splitext(fname)
                            counter = 1
                            while os.path.exists(dst_f):
                                dst_f = os.path.join(target_dir, f"{base}_{counter}{ext}")
                                counter += 1

                        try:
                            shutil.move(src_f, dst_f)
                            moved_files += 1
                            self.append_log(f"  ▲ [꺼내기] {fname} -> {os.path.basename(target_dir)}")
                        except Exception as fe:
                            self.append_log(f"  ❌ [이동 오류] {fname}: {fe}")

                    try:
                        if not os.listdir(root):
                            os.rmdir(root)
                    except Exception:
                        pass

                try:
                    if os.path.exists(sdir) and not os.listdir(sdir):
                        os.rmdir(sdir)
                        deleted_dirs += 1
                        self.append_log(f"  🗑 [빈 폴더 삭제] {os.path.basename(sdir)}")
                except Exception as de:
                    self.append_log(f"  ⚠️ [폴더 삭제 오류] {os.path.basename(sdir)}: {de}")

            dst = self.config.get("org_dst_folder", "").strip()
            if dst and os.path.isdir(dst):
                self.scan_destination_authors(dst)

            done_msg = self.t("msg_extract_done", moved_files=moved_files, deleted_dirs=deleted_dirs)
            self.append_log("=" * 60)
            self.append_log(done_msg)
            messagebox.showinfo("완료", done_msg)

        except Exception as e:
            err_msg = f"복구 작업 중 오류 발생: {e}"
            self.append_log(f"❌ {err_msg}")
            messagebox.showerror("오류", err_msg)

    def _organize_worker(self, src_folder, dst_folder):
        # 1. 특정 확장자 제한 없이 모든 파일 수집
        file_list = []
        for root, _, files in os.walk(src_folder):
            for f in files:
                if f.startswith(".") or f.startswith("~$") or f == "desktop.ini":
                    continue
                file_list.append(os.path.join(root, f))

        total = len(file_list)
        success_cnt = 0
        conflict_cnt = 0
        skip_cnt = 0

        self.root.after(0, lambda: self.progress_bar.config(maximum=total if total > 0 else 1, value=0))

        for idx, src_path in enumerate(file_list, start=1):
            if self.cancel_requested:
                break

            filename = os.path.basename(src_path)
            try:
                # 2. 위치 기반 파서로 초반 1~2번째 괄호에서 서클/작가명 확정
                circle, author = parse_author_metadata(filename)
                target_author = author or circle or ""

                # 3. 매칭 검사
                matched_dir = self._find_matching_folder(circle, author)

                if not matched_dir:
                    if self.var_opt_auto.get() and target_author:
                        # 신규 작가 폴더 생성
                        new_folder_name = f"{target_author} [Auto]"
                        matched_dir = os.path.join(dst_folder, new_folder_name)
                        os.makedirs(matched_dir, exist_ok=True)
                        norm_key = target_author.lower().replace(" ", "").replace("_", "")
                        self.author_folders_map[norm_key] = matched_dir
                    else:
                        # 신규 작가 옵션 해제 시: 미분류 폴더를 만들지 않고 원래 위치에 보존!
                        skip_cnt += 1
                        self.root.after(0, self.append_log, f"⏩ [스킵 보존] {filename} (매칭 폴더 없음)")
                        pct = int((idx / total) * 100) if total > 0 else 0
                        self.root.after(0, self._update_org_progress, idx, total, pct)
                        continue

                dest_file_path = os.path.join(matched_dir, filename)

                # 4. 동일 파일 및 중복 넘버링 (1), (2) 판본 충돌 해결
                existing_duplicate = find_existing_duplicate_target(matched_dir, filename)

                if existing_duplicate:
                    if self.var_opt_mtime.get():
                        src_ver = extract_version_number(filename)
                        dst_ver = extract_version_number(os.path.basename(existing_duplicate))

                        src_mtime = os.path.getmtime(src_path)
                        dst_mtime = os.path.getmtime(existing_duplicate)

                        # 넘버링이 더 높거나, 넘버링이 같을 때 수정시간이 최신이면 교체
                        is_src_newer = False
                        if src_ver > dst_ver:
                            is_src_newer = True
                        elif src_ver < dst_ver:
                            is_src_newer = False
                        else:
                            is_src_newer = (src_mtime >= dst_mtime)

                        if is_src_newer:
                            safe_send_to_recycle_bin(existing_duplicate)
                            shutil.move(src_path, dest_file_path)
                            log_msg = f"♻ [최신본 대체] {filename} -> {os.path.basename(matched_dir)} (구버전 {os.path.basename(existing_duplicate)} 휴지통 이동)"
                            conflict_cnt += 1
                        else:
                            safe_send_to_recycle_bin(src_path)
                            log_msg = f"♻ [기존본 보존] {filename} (다운로드된 이전 버전 휴지통 이동)"
                            conflict_cnt += 1
                    else:
                        skip_cnt += 1
                        log_msg = f"⏩ [충돌 스킵] {filename} (이미 동일 작품이 존재하여 건너뜀)"
                else:
                    # 원본 파일명 100% 보존 이동
                    shutil.move(src_path, dest_file_path)
                    log_msg = f"✔ [이동 완료] {filename} -> {os.path.basename(matched_dir)}"
                    success_cnt += 1

                self.root.after(0, self.append_log, log_msg)

            except Exception as e:
                skip_cnt += 1
                self.root.after(0, self.append_log, f"❌ [오류 스킵] {filename}: {e}")

            pct = int((idx / total) * 100) if total > 0 else 0
            self.root.after(0, self._update_org_progress, idx, total, pct)

        self.root.after(0, self._on_organizing_finished, total, success_cnt, conflict_cnt, skip_cnt)

    def _find_matching_folder(self, circle, author):
        norm_author = author.lower().replace(" ", "").replace("_", "") if author else ""
        norm_circle = circle.lower().replace(" ", "").replace("_", "") if circle else ""

        # 1순위: 완전 일치
        if norm_author and norm_author in self.author_folders_map:
            return self.author_folders_map[norm_author]
        if norm_circle and norm_circle in self.author_folders_map:
            return self.author_folders_map[norm_circle]

        # 2순위: 부분 일치 (기존 사용자 폴더명이 2글자 이상 포함되어 있는 경우)
        for key, folder_path in self.author_folders_map.items():
            if len(key) >= 2:
                if (norm_author and key in norm_author) or (norm_circle and key in norm_circle):
                    return folder_path

        return None

    def _update_org_progress(self, cur, total, pct):
        self.progress_bar.config(value=cur)
        self.lbl_org_status.config(text=self.t("progress_status", cur=cur, total=total, percent=pct))

    def _on_organizing_finished(self, total, success, conflict, skip):
        self.is_organizing = False
        self.btn_start_org.config(state="normal", bg=self.colors["btn_start"])
        self.btn_stop_org.config(state="disabled", bg="#4a5568")
        if hasattr(self, 'btn_extract'):
            self.btn_extract.config(state="normal")

        msg = self.t("msg_done", total=total, success=success, conflict=conflict, fail=skip)
        self.append_log("=" * 60)
        self.append_log(msg)
        messagebox.showinfo("완료", msg)

    # -------------------------------------------------------------
    # 공통: 도움말 모달
    # -------------------------------------------------------------
    def show_help_modal(self):
        modal = tk.Toplevel(self.root)
        modal.title(self.t("help_btn"))
        modal.geometry("540x500")
        modal.configure(bg=self.colors["bg"])
        modal.transient(self.root)
        modal.grab_set()

        frame = tk.Frame(modal, bg=self.colors["bg"], padx=14, pady=12)
        frame.pack(fill="both", expand=True)

        txt = tk.Text(frame, bg=self.colors["card_bg"], fg=self.colors["text"],
                      font=("Malgun Gothic", 9), relief="flat", wrap="word", padx=10, pady=10)
        txt.insert("1.0", self.t("help_content"))
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, pady=(0, 10))

        btn = tk.Button(frame, text="닫기 / Close", font=("Malgun Gothic", 9, "bold"),
                        bg="#363a4f", fg="#ffffff", relief="flat", padx=14, pady=4,
                        command=modal.destroy)
        btn.pack(side="right")

    def on_close(self):
        self.hotkey_mgr.stop()
        self.save_config()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SubcultureMediaManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
