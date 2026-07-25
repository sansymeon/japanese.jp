"""Shared Party Kanji timing and visual defaults (JSON-driven engine config)."""

from __future__ import annotations

# Calm museum pacing — slower fades, generous holds (especially closing humour).
PARTY_TIMING: dict[str, int] = {
    # Shock — giant → challenge → handoff
    "partyShockKanjiRevealMs": 450,
    "partyShockChallengeDelayMs": 3400,
    "partyShockChallengeRevealMs": 1300,
    "partyShockHoldAfterChallengeMs": 2200,
    "partyShockFadeMs": 900,
    # Reveal — burst → staggered components → equation
    "partyRevealFadeInMs": 700,
    "partyRevealBurstMs": 700,
    "partyComponentStaggerMs": 2400,
    "partyComponentArriveMs": 750,
    "partyEquationDelayMs": 3600,
    "partyEquationRevealMs": 800,
    "partyEquationHoldMs": 5200,
    "partyRevealFadeMs": 900,
    # Final — reward glow + component pulse
    "partyFinalFadeInMs": 1800,
    "partyFinalHoldMs": 2800,
    "partyComponentPulseFadeInMs": 800,
    "partyComponentPulseHoldMs": 2800,
    "partyFinalFadeOutMs": 1100,
    # Closing humour → end card → (gold crest via bookends)
    "partyClosingFadeInMs": 800,
    "partyClosingHoldMs": 6500,
    "partyClosingFadeMs": 900,
    "partyEndCardFadeInMs": 800,
    "partyEndCardHoldMs": 5500,
    "partyEndCardFadeMs": 1000,
    # Quiet crest coda (bookends.closing)
    "closingBlackBeforeMs": 600,
    "closingRevealMs": 3600,
    "closingHoldMs": 3200,
    "closingExhaleMs": 4200,
    "closingSilenceHoldMs": 0,
    "closingBlackAfterMs": 900,
    "closingFadeToBlackMs": 4200,
    "exhibitTransitionMs": 0,
    "exhibitBlackHoldMs": 0,
    "blackHoldMs": 0,
}

PARTY_VISUAL: dict[str, object] = {
    "componentReveal": "burst",  # burst | slide
    "componentGlow": False,
    "componentBounce": True,
    "finalGlow": False,
    "componentPulseOpacity": 0.18,
    "showReadingInReveal": False,
    "showTrivia": False,
    "showPlaylistSubtitle": True,
}

DEFAULT_CLOSING_MESSAGE = "Big kanji are just little kanji having a party."

SERIES_TAGLINE = "Learn this before your next party."
