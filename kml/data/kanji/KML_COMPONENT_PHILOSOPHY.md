# Component Philosophy

KML component breakdowns are designed for **recognition and learning**, not for
historical or linguistic analysis.

Our goal is to help learners quickly recognize kanji by reusing the largest
familiar components available.

## Priority order

1. **Use an existing kanji or previously learned component whenever possible.**

   - 膜 → 月 + 莫
   - 認 → 言 + 忍

2. **Otherwise use the largest familiar subcomponents.**

   - 合 → 人 + 一 + 口
   - 春 → 三 + 人 + 月
   - 先 → 午 + 儿

3. **Only decompose into individual strokes when no meaningful reusable
   components exist.**

## Notes

Historical or etymological decompositions are not the objective unless they also
improve recognition.

When multiple analyses are possible, prefer the one that an average learner would
naturally perceive and that best supports future kanji recognition.

## Related

- Layout rules (H/V only): `KML_COMPONENT_STYLE_PHASE1.md`
- Canonical source (reviewed lesson HTML): `KML_COMPONENT_SOURCE_POLICY.md`
