# offline_translator.py
import torch
from transformers import MarianTokenizer, MarianMTModel
import re

# Models will be loaded lazily when translate_offline is called.
# This prevents module import from trying to download models (which requires network)
# immediately and allows the program to run in online-only mode without offline models.

# Module-level variables for models (initialized when needed)
en_vi_tokenizer = None
en_vi_model = None
ja_en_tokenizer = None
ja_en_model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_models_loaded = False

def _load_models(local_cache_dir: str = None, progress_callback=None) -> bool:
    """
    Load models from pre-trained sources. If local_cache_dir is provided, it will try to
    load from that local path first. Returns True if successful, False otherwise.
    """
    global en_vi_tokenizer, en_vi_model, ja_en_tokenizer, ja_en_model, _models_loaded
    if _models_loaded:
        return True

    try:
        # Optionally allow specifying local model directories via environment variable
        import os
        en_vi_name = os.environ.get('OFFLINE_MODEL_EN_VI', 'Helsinki-NLP/opus-mt-en-vi')
        ja_en_name = os.environ.get('OFFLINE_MODEL_JA_EN', 'Helsinki-NLP/opus-mt-ja-en')
        if local_cache_dir:
            # if local_cache_dir is a folder containing the two models under subfolders
            en_vi_src = os.path.join(local_cache_dir, 'en-vi')
            ja_en_src = os.path.join(local_cache_dir, 'ja-en')
        else:
            en_vi_src = en_vi_name
            ja_en_src = ja_en_name

        if progress_callback:
            progress_callback("Đang tải mô hình EN→VI... (lazy)")
        else:
            print("Đang tải mô hình EN→VI... (lazy)")
        en_vi_tokenizer = MarianTokenizer.from_pretrained(en_vi_src)
        en_vi_model = MarianMTModel.from_pretrained(en_vi_src)
        en_vi_model.to(device)

        if progress_callback:
            progress_callback("Đang tải mô hình JA→EN... (lazy)")
        else:
            print("Đang tải mô hình JA→EN... (lazy)")
        ja_en_tokenizer = MarianTokenizer.from_pretrained(ja_en_src)
        ja_en_model = MarianMTModel.from_pretrained(ja_en_src)
        ja_en_model.to(device)

        _models_loaded = True
        return True
    except Exception as e:
        # Loading failed (network or models missing); print message and return False
        if progress_callback:
            progress_callback(f"Warning: Không thể tải mô hình offline: {e}")
        else:
            print(f"Warning: Không thể tải mô hình offline: {e}")
        print("Bạn có thể:")
        print("  - Chạy một lần với mạng để tải mô hình (cách nhanh nhất)")
        print("  - Hoặc tải thủ công bằng huggingface-cli và đặt biến môi trường OFFLINE_MODELS_PATH")
        _models_loaded = False
        return False

def download_models(local_cache_dir: str = None) -> bool:
    """
    Public helper: attempt to download/load the offline models now.
    Returns True if models are successfully loaded, False otherwise.
    """
    return _load_models(local_cache_dir, progress_callback=None)

def download_models_with_progress(local_cache_dir: str = None, progress_callback=None) -> bool:
    return _load_models(local_cache_dir, progress_callback=progress_callback)

def is_models_ready() -> bool:
    """Return True if models are already loaded or cached."""
    global _models_loaded
    if _models_loaded:
        return True
    # Otherwise, check environment-defined cache or default Hugging Face cache
    import os
    local_cache = os.environ.get('OFFLINE_MODELS_PATH')
    if local_cache:
        en_vi_dir = os.path.join(local_cache, 'en-vi')
        ja_en_dir = os.path.join(local_cache, 'ja-en')
        if os.path.isdir(en_vi_dir) and os.path.isdir(ja_en_dir):
            return True
    # Check default HF cache location
    hf_cache = os.environ.get('TRANSFORMERS_CACHE') or os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'transformers')
    try:
        if os.path.isdir(hf_cache):
            items = os.listdir(hf_cache)
            # Look for folder names containing model ids
            has_en_vi = any('opus-mt-en-vi' in p or 'en-vi' in p for p in items)
            has_ja_en = any('opus-mt-ja-en' in p or 'ja-en' in p for p in items)
            if has_en_vi and has_ja_en:
                return True
    except Exception:
        pass
    return False

# --------------------------------------------------------------
# Hàm cleaner text
# --------------------------------------------------------------
def clean_text(text: str) -> str:
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text

# --------------------------------------------------------------
# Tách câu để dịch chính xác hơn
# --------------------------------------------------------------
def split_sentences(text: str):
    # chia theo dấu chấm, ?, ! hoặc khoảng trắng lớn
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [p.strip() for p in parts if p.strip()]

# --------------------------------------------------------------
# Ngôn ngữ detection đơn giản
# --------------------------------------------------------------
def guess_language(text: str) -> str:
    # Nếu có nhiều ký tự tiếng Nhật → chọn ja
    japanese_chars = re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]', text)
    if len(japanese_chars) > 3:
        return "ja"

    # Nếu chủ yếu là chữ cái Latin → en
    latin_chars = re.findall(r'[A-Za-z]', text)
    if len(latin_chars) > 3:
        return "en"

    return "en"  # fallback

# --------------------------------------------------------------
# Dịch EN → VI
# --------------------------------------------------------------
def translate_en_vi(text: str) -> str:
    sentences = split_sentences(text)
    translated = []

    for s in sentences:
        batch = en_vi_tokenizer(s, return_tensors="pt", padding=True)
        # Move tensors in batch to device
        batch = {k: v.to(device) for k, v in batch.items()}
        gen = en_vi_model.generate(**batch, max_length=256)
        out = en_vi_tokenizer.decode(gen[0], skip_special_tokens=True)
        translated.append(out)

    return " ".join(translated)

# --------------------------------------------------------------
# Dịch JA → VI (JA → EN → VI)
# --------------------------------------------------------------
def translate_ja_vi(text: str) -> str:
    sentences = split_sentences(text)
    translated = []

    for s in sentences:
        # Step 1: JA → EN
        batch_ja = ja_en_tokenizer(s, return_tensors="pt", padding=True)
        batch_ja = {k: v.to(device) for k, v in batch_ja.items()}
        gen_ja = ja_en_model.generate(**batch_ja, max_length=256)
        en_text = ja_en_tokenizer.decode(gen_ja[0], skip_special_tokens=True)

        # Step 2: EN → VI
        vi_text = translate_en_vi(en_text)
        translated.append(vi_text)

    return " ".join(translated)

# --------------------------------------------------------------
# Hàm chính: auto detect + chọn mô hình offline
# --------------------------------------------------------------
def translate_offline(text: str, src=None, dest="vi") -> str:
    if not text.strip():
        return ""

    text = clean_text(text)

    if src is None:
        src = guess_language(text)

    # Chỉ dịch sang tiếng Việt
    if dest != "vi":
        raise ValueError("Offline translator currently only supports dest='vi'.")

    # Ensure models are loaded; try to load from environment local cache if specified
    from os import environ
    local_cache = environ.get('OFFLINE_MODELS_PATH')
    if not _models_loaded:
        ok = _load_models(local_cache_dir=local_cache)
        if not ok:
            raise RuntimeError("Offline models not available - cannot translate offline.")

    if src == "en":
        return translate_en_vi(text)
    elif src == "ja":
        return translate_ja_vi(text)
    else:
        # fallback: coi như tiếng Anh
        return translate_en_vi(text)



