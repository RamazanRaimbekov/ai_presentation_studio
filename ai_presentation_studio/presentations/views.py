import copy
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import PALETTE_OPTIONS, PresentationForm
from .services.gemini import ai_status, generate_presentation
from .services.images import search_pexels_image_url
from .services.pptx_builder import build_presentation, resolve_palette


def _custom_colors(cleaned_data):
    return {
        "background": cleaned_data.get("background_color", "#111111"),
        "accent": cleaned_data.get("accent_color", "#FF0000"),
        "text": cleaned_data.get("text_color", "#FFFFFF"),
    }


def _home_context(form=None):
    return {
        "form": form or PresentationForm(),
        "palettes": PALETTE_OPTIONS,
        "ai_status": ai_status(),
    }


def _add_preview_images(data: dict) -> dict:
    """Attach image URLs for browser preview without changing the AI schema."""
    enriched = copy.deepcopy(data)
    for slide in enriched.get("slides", []):
        if slide.get("type") == "content_image" and slide.get("image_query"):
            slide["preview_image_url"] = search_pexels_image_url(slide["image_query"])
    return enriched


def home(request):
    return render(request, "presentations/index.html", _home_context())


@require_POST
def generate(request):
    form = PresentationForm(request.POST)
    if not form.is_valid():
        return render(request, "presentations/index.html", _home_context(form))

    cd = form.cleaned_data
    palette = cd["color_preset"]
    custom_colors = _custom_colors(cd)

    try:
        data = generate_presentation(cd["prompt"], cd["slide_count"], cd["language"], palette)
    except Exception as exc:
        messages.error(request, f"AI xatosi: {exc}")
        return render(request, "presentations/index.html", _home_context(form))

    token = uuid.uuid4().hex
    request.session["presentation_data"] = data
    request.session["presentation_preview_data"] = _add_preview_images(data)
    request.session["presentation_palette"] = palette
    request.session["presentation_custom_colors"] = custom_colors
    request.session["presentation_token"] = token
    request.session["presentation_prompt"] = cd["prompt"]
    request.session["presentation_language"] = cd["language"]
    return redirect("presentations:preview")


def preview(request):
    data = request.session.get("presentation_preview_data") or request.session.get("presentation_data")
    if not data:
        return redirect("presentations:home")

    palette = request.session.get("presentation_palette", "red")
    custom_colors = request.session.get("presentation_custom_colors", {})
    colors = resolve_palette(palette, custom_colors)

    return render(
        request,
        "presentations/preview.html",
        {
            "presentation": data,
            "palette": palette,
            "colors": {key: f"#{value}" for key, value in colors.items()},
            "ai_status": ai_status(),
        },
    )


def download(request):
    data = request.session.get("presentation_data")
    token = request.session.get("presentation_token")
    if not data or not token:
        raise Http404("Presentation topilmadi")

    palette = request.session.get("presentation_palette", "red")
    custom_colors = request.session.get("presentation_custom_colors", {})
    path = Path(settings.MEDIA_ROOT) / f"presentation_{token}.pptx"
    build_presentation(data, path, palette, custom_colors)

    return FileResponse(
        open(path, "rb"),
        as_attachment=True,
        filename=f"{data.get('title', 'presentation')[:50]}.pptx",
    )


@require_POST
def regenerate(request):
    prompt = request.session.get("presentation_prompt")
    old = request.session.get("presentation_data")
    if not prompt or not old:
        return redirect("presentations:home")

    palette = request.session.get("presentation_palette", "red")
    language = request.session.get("presentation_language", "uz")
    try:
        data = generate_presentation(prompt, len(old.get("slides", [])) or 10, language, palette)
    except Exception as exc:
        messages.error(request, f"Qayta generatsiya xatosi: {exc}")
        return redirect("presentations:preview")

    request.session["presentation_data"] = data
    request.session["presentation_preview_data"] = _add_preview_images(data)
    request.session["presentation_token"] = uuid.uuid4().hex
    messages.success(request, "Prezentatsiya AI orqali qayta yaratildi. Tanlangan ranglar saqlandi.")
    return redirect("presentations:preview")
