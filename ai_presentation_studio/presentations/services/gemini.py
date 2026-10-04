import json
import os
from typing import Literal

from pydantic import BaseModel, Field


SlideType = Literal[
    "title",
    "content",
    "content_image",
    "comparison",
    "cards",
    "stats",
    "steps",
    "quote",
    "ending",
]


class Slide(BaseModel):
    type: SlideType = "content"
    title: str
    subtitle: str = ""
    content: list[str] = Field(default_factory=list)
    image_query: str = ""
    left_title: str = ""
    left_text: str = ""
    right_title: str = ""
    right_text: str = ""
    stat_value: str = ""
    stat_label: str = ""


class PresentationSchema(BaseModel):
    title: str
    description: str = ""
    slides: list[Slide]


def ai_status() -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    demo_enabled = os.getenv("PRESENTATION_DEMO_MODE", "false").strip().lower() in {
        "1", "true", "yes", "on"
    }
    return {
        "ready": bool(api_key),
        "demo": (not api_key) and demo_enabled,
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
    }


def _demo(prompt: str, slide_count: int, language: str) -> dict:
    """Explicit demo mode only. Never used silently when the API key is missing."""
    topic = prompt.strip().split("\n")[0][:70] or "AI Presentation"
    slides = [
        {"type": "title", "title": topic, "subtitle": "Demo mode: AI API ulanmagan"},
        {
            "type": "content_image",
            "title": f"{topic}: mavzuga kirish",
            "content": [
                "Bu slayd demo rejimida generatsiya qilindi",
                "Haqiqiy kontent uchun GEMINI_API_KEY ishlashi kerak",
                "API ulangach prompt asosida yangi matn yaratiladi",
            ],
            "image_query": topic,
        },
        {
            "type": "comparison",
            "title": "Demo va AI rejimi",
            "left_title": "Demo",
            "left_text": "Oldindan tayyorlangan namuna strukturasi",
            "right_title": "AI",
            "right_text": "Prompt mavzusidan yangi va kontekstual slaydlar",
        },
        {"type": "cards", "title": "Tizim imkoniyatlari", "content": ["Kontent", "Dizayn", "PPTX"]},
        {"type": "steps", "title": "Ishlash jarayoni", "content": ["Prompt", "Gemini", "Layout", "PPTX"]},
        {"type": "stats", "title": "Natija", "stat_value": "1 → PPTX", "stat_label": "Bitta promptdan tahrirlanadigan PowerPoint"},
        {"type": "quote", "title": "Muhim", "content": ["Demo rejimi haqiqiy AI javobi emas."]},
        {"type": "content", "title": "API ulangach", "content": ["Mavzuga mos sarlavhalar", "Real misollar", "Turli layoutlar"]},
        {"type": "ending", "title": "Demo yakunlandi", "subtitle": "Gemini API'ni ulang va qayta generatsiya qiling."},
    ]
    if slide_count <= len(slides):
        slides = slides[:slide_count]
        slides[-1] = {
            "type": "ending",
            "title": "Demo yakunlandi",
            "subtitle": "Gemini API'ni ulang va qayta generatsiya qiling.",
        }
    else:
        while len(slides) < slide_count:
            slides.insert(
                -1,
                {
                    "type": "content",
                    "title": f"{topic}: qo‘shimcha demo slayd",
                    "content": ["Bu demo kontent", "AI API ulangach almashtiriladi"],
                },
            )
    return {"title": topic, "description": f"Demo mode · {language}", "slides": slides[:slide_count]}


def _extract_data(response) -> dict:
    # New google-genai versions can expose parsed structured output directly.
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, PresentationSchema):
        return parsed.model_dump()
    if isinstance(parsed, dict):
        return PresentationSchema.model_validate(parsed).model_dump()

    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Gemini bo‘sh javob qaytardi.")

    # Defensive cleanup for older SDK/model combinations that wrap JSON in fences.
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].lstrip()

    return PresentationSchema.model_validate(json.loads(text)).model_dump()


def generate_presentation(
    prompt: str,
    slide_count: int = 10,
    language: str = "uz",
    theme: str = "emerald",
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
    demo_enabled = os.getenv("PRESENTATION_DEMO_MODE", "false").strip().lower() in {
        "1", "true", "yes", "on"
    }

    if not api_key:
        if demo_enabled:
            return _demo(prompt, slide_count, language)
        raise RuntimeError(
            "GEMINI_API_KEY topilmadi. .env yoki config/.env ichiga haqiqiy Gemini API key kiriting. "
            "Demo kerak bo‘lsa PRESENTATION_DEMO_MODE=true yozing."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    instruction = f"""
You are a senior presentation strategist, researcher and slide copywriter.
Create a COMPLETE professional presentation based only on the user's requested topic.
Language: {language}.
Selected visual theme: {theme}.
Required slide count: exactly {slide_count}.

USER REQUEST:
{prompt}

CONTENT RULES:
- Every slide must directly relate to the user's topic. Never return generic filler such as
  "main idea", "three principles", "before/after" unless those labels genuinely fit the topic.
- First understand the topic, then build a logical narrative: opening -> core facts/ideas -> examples -> conclusion.
- One clear idea per slide; avoid repeating the same point on multiple slides.
- Use concrete names, dates, places, examples, processes or numbers when the topic supports them.
- If the user asks about a historical person/topic, include biography/context, major milestones,
  important works/actions, influence/legacy and a useful conclusion instead of prompt-engineering examples.
- Keep slide copy presentation-friendly: normally 2-5 concise bullets, not paragraphs.
- Do not invent exact statistics, dates or quotations when uncertain. Prefer a non-quantified factual statement.
- A quote slide must contain a real short quote only when you are confident it is authentic; otherwise use another layout.

LAYOUT RULES:
- Slide 1: type='title'. Slide {slide_count}: type='ending'.
- Use varied layouts based on the content, not randomly.
- content_image: use it for people, places, objects, events, architecture or other strongly visual subjects.
- image_query: concise ENGLISH web-photo search phrase with subject + context; never generic words like 'image'.
- comparison: fill left_title/left_text/right_title/right_text with meaningful contrasted concepts.
- stats: only use when there is a meaningful trustworthy number/metric; fill stat_value/stat_label.
- cards: content should contain 3 short distinct ideas.
- steps: content should contain 3-5 ordered steps/timeline stages.
- ending: concise conclusion or takeaway, not a generic 'ready' message.

OUTPUT RULES:
- Exactly {slide_count} slides.
- Return valid structured output only.
"""

    data = None
    last_error = None
    current_instruction = instruction
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=model,
                contents=current_instruction,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PresentationSchema,
                    temperature=0.55 if attempt == 0 else 0.35,
                ),
            )
            candidate = _extract_data(response)
            count = len(candidate.get("slides", []))
            if count == slide_count:
                data = candidate
                break
            last_error = RuntimeError(
                f"Gemini {slide_count} ta slayd o‘rniga {count} ta slayd qaytardi."
            )
            current_instruction = instruction + f"\nIMPORTANT RETRY: Your previous output had {count} slides. Return EXACTLY {slide_count} slides this time."
        except Exception as exc:
            last_error = exc

    if data is None:
        raise RuntimeError(f"Gemini generatsiyasi muvaffaqiyatsiz: {last_error}") from last_error

    slides = data.get("slides", [])

    if slides and slides[0].get("type") != "title":
        slides[0]["type"] = "title"
    if slides and slides[-1].get("type") != "ending":
        slides[-1]["type"] = "ending"

    return data
