"""Shared Party Kanji timing and visual defaults (JSON-driven engine config)."""

from __future__ import annotations

# Target ~36s episode at timingScale=1 (proof hold stays generous for confidence).
PARTY_TIMING: dict[str, int] = {
    # Shock — giant → challenge → handoff
    "partyShockKanjiRevealMs": 250,
    "partyShockChallengeDelayMs": 3000,
    "partyShockChallengeRevealMs": 350,
    "partyShockHoldAfterChallengeMs": 1650,
    "partyShockFadeMs": 400,
    # Reveal — burst → staggered components → equation
    "partyRevealFadeInMs": 350,
    "partyRevealBurstMs": 400,
    "partyComponentStaggerMs": 2000,
    "partyComponentArriveMs": 450,
    "partyEquationDelayMs": 3000,
    "partyEquationRevealMs": 400,
    "partyEquationHoldMs": 4000,
    "partyRevealFadeMs": 400,
    # Proof — stroke order (keep substantive)
    "partyProofFadeInMs": 400,
    "partyProofHoldMs": 8000,
    "partyProofFadeMs": 400,
    # Final — reward glow + component pulse
    "partyFinalFadeInMs": 1200,
    "partyFinalHoldMs": 1500,
    "partyComponentPulseFadeInMs": 500,
    "partyComponentPulseHoldMs": 2000,
    "partyFinalFadeOutMs": 600,
    # Closing line → end card
    "partyClosingFadeInMs": 350,
    "partyClosingHoldMs": 2500,
    "partyClosingFadeMs": 350,
    "partyEndCardFadeInMs": 350,
    "partyEndCardHoldMs": 1500,
    "partyEndCardFadeMs": 350,
    "exhibitTransitionMs": 0,
    "exhibitBlackHoldMs": 0,
    "blackHoldMs": 0,
}

PARTY_VISUAL: dict[str, object] = {
    "componentReveal": "burst",  # burst | slide
    "componentGlow": True,
    "componentBounce": True,
    "finalGlow": True,
    "componentPulseOpacity": 0.18,
    "showReadingInReveal": False,
    "showTrivia": False,
    "showPlaylistSubtitle": True,
}

DEFAULT_CLOSING_MESSAGE = "Big kanji are just little kanji having a party."

SERIES_TAGLINE = "Learn this before your next party."
