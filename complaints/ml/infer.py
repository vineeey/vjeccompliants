from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple

from django.conf import settings

from ..models import CategoryDepartmentMapping, Complaint


@dataclass
class ModelBundle:
    model: any
    vectorizer: any
    version: str


def _load_model_bundle() -> Optional[ModelBundle]:
    """Load trained model if available; otherwise return None for rule-based fallback."""
    try:
        import joblib
    except Exception:
        return None

    base = os.path.join(settings.BASE_DIR, "complaints", "models_storage")
    model_path = os.path.join(base, "category_model.joblib")
    vec_path = os.path.join(base, "tfidf_vectorizer.joblib")
    meta_path = os.path.join(base, "model_version.txt")

    if os.path.exists(model_path) and os.path.exists(vec_path):
        try:
            model = joblib.load(model_path)
            vectorizer = joblib.load(vec_path)
            version = open(meta_path, "r", encoding="utf-8").read().strip() if os.path.exists(meta_path) else "unknown"
            return ModelBundle(model=model, vectorizer=vectorizer, version=version)
        except Exception:
            return None
    return None


_MODEL_BUNDLE = _load_model_bundle()


def predict_category(text: str) -> Tuple[str, float, str]:
    """
    Predict category from text.
    Returns (category, confidence, model_version).
    """
    text = (text or "").strip()
    if not text:
        return "other", 0.0, _MODEL_BUNDLE.version if _MODEL_BUNDLE else "rule-0.1"

    # If model is available, use it
    if _MODEL_BUNDLE:
        try:
            X = _MODEL_BUNDLE.vectorizer.transform([text])
            proba = _MODEL_BUNDLE.model.predict_proba(X)[0]
            idx = proba.argmax()
            label = _MODEL_BUNDLE.model.classes_[idx]
            conf = float(proba[idx])
            return str(label), conf, _MODEL_BUNDLE.version
        except Exception:
            pass  # fallback to rules

    # Rule-based fallback: simple keyword mapping
    rules = {
        "infrastructure": ["room", "classroom", "lab", "electric", "fan", "leak", "repair", "broken", "toilet", "water"],
        "academics": ["exam", "assignment", "grade", "lecture", "teacher", "professor", "syllabus", "course"],
        "administration": ["admission", "fee", "certificate", "office", "scholarship", "registration", "document"],
        "finance": ["payment", "refund", "fees", "bill", "receipt"],
        "discipline": ["harassment", "bully", "fight", "cheat", "discipline", "ragging"],
        "hostel": ["hostel", "mess", "food", "dining", "warden"],
        "transport": ["bus", "transport", "shuttle", "driver", "route"],
    }
    lower = text.lower()
    for label, keywords in rules.items():
        if any(k in lower for k in keywords):
            return label, 0.6, "rule-0.1"
    return "other", 0.5, "rule-0.1"


def predict_priority(text: str) -> str:
    """Rule-based priority: high if urgent/safety, medium for time-sensitive, else low."""
    lower = (text or "").lower()
    high_tokens = ["urgent", "immediately", "asap", "danger", "harassment", "safety", "medical", "fire", "threat"]
    medium_tokens = ["soon", "delay", "late", "problem persists", "repeated"]
    if any(t in lower for t in high_tokens):
        return "high"
    if any(t in lower for t in medium_tokens):
        return "medium"
    return "low"


def summarize_text(text: str) -> str:
    """
    Extractive summary:
    - Try gensim.summarization.summarize (if available)
    - Fallback to first 40 words
    """
    text = (text or "").strip()
    if not text:
        return ""
    # 1) Try transformers summarization if available
    try:
        from transformers import pipeline  # type: ignore
        nlp = pipeline("summarization")
        out = nlp(text, max_length=60, min_length=15, do_sample=False)
        if out and isinstance(out, list) and out[0].get("summary_text"):
            return out[0]["summary_text"].strip()
    except Exception:
        pass
    # 2) Try gensim summarization if available
    try:
        from gensim.summarization.summarizer import summarize  # type: ignore
        summ = summarize(text, word_count=40)
        if summ:
            return summ
    except Exception:
        pass
    words = text.split()
    return " ".join(words[:40]) + ("..." if len(words) > 40 else "")


def process_audio(file_path: str) -> Optional[str]:
    """Transcribe audio using faster-whisper or openai-whisper if available.
    Returns transcript text, or None if transcription isn't available.
    """
    if not file_path or not os.path.exists(file_path):
        return None
    # Try faster-whisper first
    try:
        from faster_whisper import WhisperModel  # type: ignore
        model = WhisperModel("base", device="auto")
        segments, info = model.transcribe(file_path, beam_size=1)
        text = " ".join(seg.text for seg in segments if getattr(seg, "text", None))
        return text.strip() or None
    except Exception:
        pass
    # Fallback to openai-whisper (whisper)
    try:
        import whisper  # type: ignore
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        text = (result or {}).get("text")
        return (text or "").strip() or None
    except Exception:
        pass
    return None


def infer_enrich_complaint(instance: Complaint) -> bool:
    """
    Derive category, priority, summary, model_version, confidence from description.
    Also map department from category via CategoryDepartmentMapping if available.
    Returns True if any field changed.
    """
    changed = False
    cat, conf, version = predict_category(instance.description)
    pri = predict_priority(instance.description)
    summ = summarize_text(instance.description)

    if not instance.category:
        instance.category = cat
        changed = True
    if not instance.priority:
        instance.priority = pri
        changed = True
    if not instance.summary:
        instance.summary = summ
        changed = True
    if not instance.model_version:
        instance.model_version = version
        changed = True
    if not instance.confidence:
        instance.confidence = conf
        changed = True

    # Department mapping: category → department
    if not instance.department and instance.category:
        mapping = CategoryDepartmentMapping.objects.filter(category__iexact=instance.category).first()
        if mapping:
            instance.department = mapping.department
            changed = True

    return changed