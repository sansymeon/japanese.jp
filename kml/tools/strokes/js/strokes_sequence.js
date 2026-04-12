/* =====================================================
   DIFFERENT STROKES – SEQUENCE ENGINE (IMAGE-BASED CLEAN)
   ===================================================== */

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* ===== Timing ===== */

const INTRO_HOLD = 3500;
const INTRO_FADE = 800;
const PRE_DRAW_PAUSE = 250;
const POST_STROKE_BUFFER = 500;
const EMOJI_HOLD = 3000;
const EMOJI_FADE = 1000;
const CLOSING_DELAY = 500;

/* =====================================================
   STROKE ENGINE
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

  svg.getBoundingClientRect(); // force layout

  return strokes;
}

function animateKanjiStrokes(strokes) {
  if (!strokes || !strokes.length) return 2000;

  const DRAW_TIME = 700;
  const RED_HOLD = 120;
  const BLACK_HOLD = 80;
  const GAP = DRAW_TIME + RED_HOLD + BLACK_HOLD;

  strokes.forEach(stroke => {
    stroke.style.transition =
      `stroke-dashoffset ${DRAW_TIME}ms ease-out, stroke 400ms ease`;
  });

  strokes.forEach((stroke, i) => {
    setTimeout(() => {
      stroke.style.strokeDashoffset = 0;

      setTimeout(() => {
        stroke.style.stroke = "#000";
      }, DRAW_TIME + RED_HOLD - 100);

    }, i * GAP);
  });

  return strokes.length * GAP;
}

/* =====================================================
   MAIN FLOW
   ===================================================== */

async function fadeSequence() {
  const intro = document.getElementById('intro');
  const kanji = document.querySelector('.stroke-order');
  const emoji = document.getElementById('emoji-block');
  const closing = document.getElementById('closing');

  /* ===== CLEAN START ===== */

  if (kanji) kanji.style.opacity = 0;

  if (emoji) {
    emoji.style.opacity = "";
    emoji.classList.remove('visible', 'fade-out');
  }

  if (closing) {
    closing.style.opacity = "";
    closing.classList.remove('visible', 'fade-out');
  }

  /* ===== INTRO ===== */

  intro?.classList.add('visible');
  await delay(INTRO_HOLD);

  intro?.classList.add('fade-out');
  await delay(INTRO_FADE);

  /* ===== STROKES ===== */

  const strokes = prepareKanjiStrokes();

  if (kanji) {
    kanji.classList.remove('fade-out');
    kanji.style.opacity = 1;
  }

  await delay(PRE_DRAW_PAUSE);

  const strokeDuration = animateKanjiStrokes(strokes);
  await delay(strokeDuration + POST_STROKE_BUFFER);

  /* ===== HIDE STROKES ===== */

  kanji?.classList.add('fade-out');
  await delay(EMOJI_FADE);

  /* ===== FINAL (KANJI + STAMP) ===== */

  if (emoji) {
    emoji.classList.remove('fade-out');
    emoji.classList.add('visible');

    /* ---- Kanji image animation ---- */
    const finalKanji = emoji.querySelector('.final-kanji');
    if (finalKanji) {
      finalKanji.style.opacity = 0;
      finalKanji.style.transform = "translateY(6px)";

      requestAnimationFrame(() => {
        finalKanji.style.transition =
          "opacity 0.6s ease, transform 0.6s ease";
        finalKanji.style.opacity = 1;
        finalKanji.style.transform = "translateY(0)";
      });
    }

    /* ---- Stamp animation ---- */
    const stamp = emoji.querySelector('.stamp');
    if (stamp) {
      stamp.style.opacity = 0;
      stamp.style.transform = "translate(6px, 6px) scale(0.8)";

      setTimeout(() => {
        stamp.style.transition = "all 0.4s ease-out";
        stamp.style.opacity = 0.85;
        stamp.style.transform = "translate(0, 0) scale(1)";
      }, 400);
    }

    /* ---- Keyword fade-in ---- */
    const keyword = emoji.querySelector('.emoji-keyword');
    if (keyword) {
      keyword.style.opacity = 0;

      requestAnimationFrame(() => {
        keyword.style.transition = "opacity 0.8s ease";
        keyword.style.opacity = 1;
      });
    }

    /* remove intro completely */
    intro?.remove();
  }

  await delay(EMOJI_HOLD);

  emoji?.classList.add('fade-out');
  await delay(EMOJI_FADE);

  /* ===== CLOSING ===== */

  await delay(CLOSING_DELAY);

  if (closing) {
    closing.classList.remove('fade-out');
    closing.classList.add('visible');
  }
}

/* =====================================================
   INIT
   ===================================================== */

window.addEventListener('load', async () => {
  const kanji = document.querySelector('.stroke-order');
  const washi = document.getElementById('washi-bg');
  const page = document.querySelector('.page');

  if (kanji) kanji.style.opacity = 0;

  document.getElementById("loop-btn")?.addEventListener("click", () => {
    location.reload();
  });

  washi?.classList.add('visible');
  await delay(600);

  page?.classList.add('visible');

  await fadeSequence();
});