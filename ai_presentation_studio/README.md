# PresentAI Studio

Prompt asosida **haqiqiy AI kontentli PowerPoint prezentatsiya** yaratadigan Django loyiha.

## Stack
- Django
- Gemini API (`google-genai`)
- `python-pptx`
- Pexels image search (optional)
- HTML/CSS/JS

## Muhim tuzatish
Oldingi build `config/.env` ichiga API key yozgan, lekin `settings.py` faqat loyiha rootidagi `.env` faylini o'qigan. Natijada `GEMINI_API_KEY` topilmay, sayt generic demo slaydlarni qaytarayotgan edi.

Yangi versiya:
- root `.env` ni o'qiydi;
- eski `config/.env` ni fallback sifatida ham o'qiydi;
- API key yo'q bo'lsa, demo kontentni yashirincha bermaydi;
- demo faqat `PRESENTATION_DEMO_MODE=true` bo'lsa ishlaydi;
- Gemini prompt mavzusiga bevosita bog'langan slaydlar yaratadi;
- `content_image` slaydlari browser previewda ham rasm ko'rsatadi (Pexels key bo'lsa).

## O'rnatish

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
python manage.py migrate
python manage.py runserver
```

Brauzer: `http://127.0.0.1:8000/`

## `.env`

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash-lite
PRESENTATION_DEMO_MODE=false
PEXELS_API_KEY=YOUR_PEXELS_API_KEY
```

## Flow

```text
User prompt
   ↓
Gemini structured output
   ↓
PresentationSchema
   ↓
Browser slide preview (+ optional Pexels images)
   ↓
python-pptx layout engine
   ↓
Editable PPTX
```

## Asosiy fayllar
- `presentations/services/gemini.py` — Gemini va structured output
- `presentations/services/images.py` — Pexels image search
- `presentations/services/pptx_builder.py` — PowerPoint layout engine
- `presentations/views.py` — web flow
- `presentations/templates/presentations/preview.html` — rich slide preview

## Xavfsizlik
`.env.example` ichiga haqiqiy API key qo'ymang. Agar API key Git/zip orqali tarqalgan bo'lsa, uni provider panelidan rotate qilish tavsiya etiladi.
