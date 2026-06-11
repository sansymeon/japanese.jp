/* =====================================================
   DIFFERENT STROKES – STABLE FINAL VERSION
   ===================================================== */

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* ===== Timing ===== */

const INTRO_HOLD = 4000;
const INTRO_FADE = 800;
const PRE_DRAW_PAUSE = 200;
const POST_STROKE_BUFFER = 400;
const EMOJI_HOLD = 5500;
const EMOJI_FADE = 800;

/* =====================================================
   STROKES
   ===================================================== */

function prepareKanjiStrokes() {
  const svg = document.querySelector('.stroke-order svg');
  if (!svg) return null;

  const strokes = svg.querySelectorAll('path');
  if (!strokes.length) return null;

  strokes.forEach(stroke => {
    const length = stroke.getTotalLength();
    stroke.style.stroke = "#e00000";
    stroke.style.strokeDasharray = length;
    stroke.style.strokeDashoffset = length;
    stroke.style.transition = "none";
  });

  svg.getBoundingClientRect();
  return strokes;
}

function animateKanjiStrokes(strokes) {
  if (!strokes) return 2000;

  const DRAW = 750;
  const GAP = 950;

  strokes.forEach(stroke => {
    stroke.style.transition =
      `stroke-dashoffset ${DRAW}ms ease-out, stroke 300ms ease`;
  });

  strokes.forEach((stroke, i) => {
    setTimeout(() => {
      stroke.style.strokeDashoffset = 0;

      setTimeout(() => {
        stroke.style.stroke = "#000";
      }, DRAW - 120);

    }, i * GAP);
  });

  return strokes.length * GAP;
}
/* =====================================================
   MAIN FLOW (SAFE VERSION)
   ===================================================== */
async function fadeSequence() {
  const intro = document.getElementById('intro');
  const stroke = document.querySelector('.stroke-order');
  const kanjiDisplay = document.querySelector('.kanji-display');
  const emoji = document.getElementById('emoji-block');
  const closing = document.getElementById('closing');

  /* ===== CLEAN START ===== */

  if (kanjiDisplay) kanjiDisplay.style.opacity = 1;
  if (stroke) stroke.style.opacity = 0;

  emoji?.classList.remove('visible', 'fade-out');
  closing?.classList.remove('visible', 'fade-out');

  /* ===== INTRO ===== */

  intro?.classList.add('visible');
  await delay(INTRO_HOLD);

  intro?.classList.add('fade-out');
  await delay(INTRO_FADE);

  /* ===== KANJI FADE OUT ===== */

  if (kanjiDisplay) {
    kanjiDisplay.style.transition = "opacity 0.5s ease-out";
    kanjiDisplay.style.opacity = 0;
  }

  await delay(500);
  await delay(150);

  /* ===== STROKES BEGIN ===== */

  if (stroke) stroke.style.opacity = 1;

  let duration = 2000; // fallback

  try {
    const strokes = prepareKanjiStrokes();

    if (strokes && strokes.length) {
      await delay(PRE_DRAW_PAUSE);
      duration = animateKanjiStrokes(strokes);
    }
  } catch (e) {
    console.warn("Stroke animation skipped:", e);
  }

  await delay(duration + POST_STROKE_BUFFER);

  /* ===== STROKES OUT ===== */

  if (stroke) {
    stroke.style.transition = "opacity 0.6s ease";
    stroke.style.opacity = 0;
  }

  await delay(EMOJI_FADE);

  /* ===== FINAL ===== */

  emoji?.classList.add('visible');

  await delay(EMOJI_HOLD);

  emoji?.classList.add('fade-out');
  await delay(EMOJI_FADE);

  /* ===== CLOSING ===== */

  closing?.classList.add('visible');
}


/* =====================================================
   INIT
   ===================================================== */

function formatSignatureLine() {
  const sig = document.querySelector('.signature');
  if (!sig || sig.dataset.formatted) return;

  sig.dataset.formatted = '1';
  sig.innerHTML = 'Drawn by One. <span class="signature-part2">Remembered by Many.</span>';
}

window.addEventListener('load', async () => {
  const washi = document.getElementById('washi-bg');
  const page = document.querySelector('.page');

  formatSignatureLine();

  const loopBtn = document.getElementById("loop-btn");

if (loopBtn) {
  loopBtn.addEventListener("click", () => location.reload());
  loopBtn.addEventListener("touchstart", () => location.reload());
}

  washi?.classList.add('visible');
  await delay(400);

  page?.classList.add('visible');

  await fadeSequence();
});