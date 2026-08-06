# Component system — later review notes

Items deferred from the Book 1 first-pass (Lessons 1–153). Do **not** change
these during routine rebuilds; revisit intentionally.

## Curriculum glyph verification

### L149 轁 (U+8F61)

- **Status:** deferred — no change now
- **Live HTML:** `data-kanji="轁"` (U+8F61), slug/keyword *tinkling bell*
- **Component structure (follows live HTML):** horizontal `車` + vertical `爫` / `臼`
- **Why review later:** Confirm this is the intended curriculum kanji and not a
  mistaken substitution. It is not joyō 轍 (U+8F4D). 鈴 (*small bell*) is already
  taught in Lesson 76. The component structure correctly tracks the HTML as
  source of truth until an editorial decision is made.

## Consistency phase (post first-pass)

Focus on consistency rather than redesign:

1. Every catalog component has a single canonical definition / label.
2. Every reused component references the same catalog entry throughout.
3. Final audit for duplicate or near-duplicate component definitions.
4. Rebuild derived data (ambient JSON, statistics, indexes) from finalized HTML.

See `KML_COMPONENT_CONSISTENCY_AUDIT.md` for the first audit snapshot.
