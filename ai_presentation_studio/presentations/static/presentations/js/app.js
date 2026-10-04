const form = document.querySelector('#generator-form');

if (form) {
  const paletteInput = form.querySelector('#id_color_preset');
  const paletteCards = [...form.querySelectorAll('.palette-card')];
  const customBox = form.querySelector('#custom-colors');
  const selectedLabel = form.querySelector('#selected-palette-label');

  const bgInput = form.querySelector('#id_background_color');
  const accentInput = form.querySelector('#id_accent_color');
  const textInput = form.querySelector('#id_text_color');
  const preview = form.querySelector('#custom-preview');

  const syncCustomPreview = () => {
    if (!bgInput || !accentInput || !textInput || !preview) return;
    preview.style.setProperty('--custom-bg', bgInput.value);
    preview.style.setProperty('--custom-accent', accentInput.value);
    preview.style.setProperty('--custom-text', textInput.value);
    document.querySelector('#bg-hex').textContent = bgInput.value.toUpperCase();
    document.querySelector('#accent-hex').textContent = accentInput.value.toUpperCase();
    document.querySelector('#text-hex').textContent = textInput.value.toUpperCase();
  };

  const activatePalette = (card) => {
    paletteCards.forEach(item => item.classList.toggle('active', item === card));
    paletteInput.value = card.dataset.palette;
    selectedLabel.textContent = card.dataset.label;
    const isCustom = card.dataset.palette === 'custom';
    customBox.hidden = !isCustom;

    // When Custom is first opened, start from the swatch shown on the card.
    if (isCustom) {
      if (card.dataset.bg) bgInput.value = card.dataset.bg;
      if (card.dataset.accent) accentInput.value = card.dataset.accent;
      if (card.dataset.text) textInput.value = card.dataset.text;
      syncCustomPreview();
    }
  };

  paletteCards.forEach(card => card.addEventListener('click', () => activatePalette(card)));
  [bgInput, accentInput, textInput].forEach(input => input && input.addEventListener('input', syncCustomPreview));

  // Preserve server-side selected value after validation errors.
  const initial = paletteCards.find(card => card.dataset.palette === paletteInput.value) || paletteCards[0];
  if (initial) activatePalette(initial);

  form.addEventListener('submit', () => {
    const btn = form.querySelector('.generate');
    btn.disabled = true;
    btn.innerHTML = '<span>✦</span> Generating presentation…';
  });
}
