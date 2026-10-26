# Fred's Adventure

Fred's Adventure is an independent, optional entertainment layer. It could eventually connect with Frega. It is not a replacement for the Frega platform, and it does not assume how Frega is built.

The visitor meets Fred and Fredette in a short phone game. Paddy's team keeps every official decision: merchants, discounts, payments, and whether a future connection is worth making.

This folder is a private demonstration for Paddy and the Bangalore development team. The intended address, after an approved deploy, is:

`https://sansymeon.jp/freds-adventure/`

That address is unlisted. It is not linked from the main website, and it is not in a sitemap. The page sends `noindex`. An unlisted address is not access protection. Anyone who is given the link can open it. There is no password on this prototype. Path-specific Basic Authentication would have required a Netlify plan upgrade, and that upgrade is not part of this demonstration.

Nothing here is a decision about Frega's architecture. Commercial arrangements, and any future integration, remain with Paddy and his team.

## What the visitor sees

A lightweight mobile game. One main action on each screen. Large buttons. No account, no payment, and no explanation of merchant rules.

Fred and Fredette are the two mascots. Their drawings are the ones already in the prototype. Only the names have changed.

Three places are playable:

- Crownbridge — Royal Adventure. A fictional British town.
- Yufuin — The Daimyo's Journey. A real place, with fictional demonstration rewards.
- Yanagawa — The Canal Adventure. A real place, with fictional demonstration rewards.

The path is: choose England or Japan, stay with that country's adventures, tap a demonstration seal, see a fictional parking discount, then open a separate mystery. England leads to Crownbridge. Japan offers Yufuin and Yanagawa. After a reward, Continue Exploring stays in the current adventure, and Return to Adventures stays in the same country. Changing country is a separate, deliberate step. Saved rewards are kept. Some mysteries invite the visitor into the Photo Studio. **My Parking Pass** brings the saved discount back.

## Division of responsibilities

**Fred's Adventure**

- Characters and stories
- QR-triggered game discoveries
- Five-frame scorecards
- Chapter progression
- Completed-adventure archives
- Entertainment and souvenir certificates

**Frega**

- Official QR verification
- Merchant relationships
- Parking discounts and other commercial rewards
- Transactions and payments
- Redemption and eligibility
- Any future integration decisions

In this prototype the parking discount is a fiction used to show the hand-off. Fred's Adventure draws the certificate. It does not decide that a real discount exists.

## What is implemented

Working in the browser, on this device only:

- A country choice, saved in this browser, then only that country's adventures. The mascots and the seal button. The seal is not a camera scan.
- A fictional parking discount saved on every successful demonstration scan, then a separate mystery.
- The same discount shown two ways: a plain proof, and a themed souvenir certificate. In Crownbridge the certificate uses `images/parking_certificate.jpg`. The words and QR printed inside that picture are samples. The saved code, and a real QR made from that code, are shown separately.
- **My Parking Pass** after the first successful scan. It survives navigation and refresh. Opening it does not create a new code. A later scan replaces it. **Show at Parking** is the plain proof. The pass stores a place id and a reference code in `localStorage` under `freds-adventure-pass-v1`. A pass saved by the earlier name of this demo is copied across once.
- Mystery reveals. The prize is separate from the parking proof.
- Photo Studio for an adult portrait style. The visitor's own photo is shown unchanged. The Royal Sisters and Royal Gentlemen pictures are finished examples. Live image generation is not connected.
- Child Mode: an object photo only. No child face. Three sample cards show a mascot with an item. The uploaded object is not painted into those cards.
- A magical-item surprise: an ordinary object photo, then one of two finished examples, Dragon Puppy or the puzzle cube. The collection remembers which example was found. It does not store the photograph.
- The Crownbridge Adventure Scorecard: five frames, two filled with original illustrations, three empty, reading **2 of 5 discoveries**. A quiet line says that five discoveries can open another chapter. Scans do not fill the frames.

The QR on a saved pass is produced by `js/qr.js` (byte mode, error correction M). It encodes the saved reference. The seal in the viewfinder is decorative.

## What is simulated

The Demo desk is a labeled simulation of merchant settings. It is not a login and it does not speak to a Frega account. Visitors are not meant to configure it. Hiding the Demo button, and bringing it back with five taps on the title, only keeps the simulation out of the way.

The desk can preview three ways a mystery might be shared later:

- Everyone Wins
- Prize by Chance (10%, 20%, or 50%). A miss still keeps the parking proof.
- Guaranteed Gift + Lucky Bonus

It can also preview a prize cap, start and end dates, an on/off switch, and one reward per scan, per day, or per promotion. These rules affect only the mystery. They live in this browser. A visitor cannot change the odds.

## What is proposed

Not built. Described so the team can see the intended shape.

- Real QR scanning.
- Counting discoveries and filling scorecard frames from play.
- Opening the next chapter after five discoveries.
- Archiving a completed chapter, while still letting the visitor open saved souvenirs and any reward reference they were given.
- Accounts, guardian accounts, and merchant accounts.
- A real prize inventory, eligibility service, or server-side draw.
- Live transformation of a visitor's photograph.

### Five frames, then the next chapter

Each chapter would offer five discoveries. A discovery is a find inside the game, separate from any official Frega reward. The scorecard is that chapter: filled frames for what was found, empty frames for what remains.

After five discoveries, the intended game would unlock the next chapter and archive the finished one. An archived chapter would stay available to look at, and would stop accepting new discoveries. Saved rewards from that chapter would remain retrievable. Today, retrieval means **My Parking Pass**. Nothing in the prototype counts frames, opens a second chapter, or writes an archive.

The Crownbridge screen is a picture of that scorecard, fixed at 2 of 5. Open it from **Adventure Scorecard** on the Crownbridge parking screen or the Crownbridge reward screen, or at `#/scorecard/crownbridge`.

### One engine, many places

The same sequence already runs in three settings. Stories, prizes, studio styles, and certificate wording come from the place list in `js/adventure.js`. A later chapter could be another town, a festival, or another culture, without changing the official reward system.

### A QR code that could serve both

Today the visitor taps a drawn seal. A future scan could, if Frega chooses, do two things at once: the official operation Frega already uses that code for, and an optional invitation into a discovery.

How a code is structured, signed, and checked is Frega's decision. This prototype does not assume a payload, a signature, or a scanner stack. The game must not treat a copied page as permission to create an official reward.

Possible later connections, none of which are assumed:

- Frega tells the adventure that a visit is eligible, and the adventure shows the story.
- Frega issues the official reward. The adventure only displays the reference Frega returns.
- A discovery id is reported back if Frega wants game progress stored with the visitor.
- An image provider is called from a server Frega controls, under a privacy policy a guardian can accept.

Any of those can be declined. The adventure can also remain a separate review page, as it is now.

## Security and official rewards

Anything a visitor can spend, redeem, or show to staff has to be checked by a system the visitor cannot edit. This browser is not that system. `localStorage` is fine for a demonstration and is not a record of a real discount.

A production reward would need, at least, a server that decides eligibility and stores the decision, a reference the game can show but cannot silently replace, and a check at the point of use. Those checks belong to Frega. No secret belongs in this front-end source.

## What Fred's Adventure Does NOT Do

The prototype does not handle payments, merchant accounts, actual discount validation, parking transactions, or official Frega business operations.

It also does not:

- replace the Frega platform, or write into a Frega database
- scan real QR codes, or decide what a live Frega code means
- validate a discount with a gate, a booth, or a member of staff
- take money, issue a refund, or talk to a payment provider
- create merchant logins or visitor accounts
- count discoveries, unlock a chapter, or archive one
- store child photographs, or transform a photograph with a live model
- claim endorsement by the British Royal Family, or by the real businesses of Yufuin and Yanagawa
- protect the page. The address is only unlisted.

All real-world commercial decisions, and any future integration, remain with Paddy and his team.

## Fictional Crownbridge

Crownbridge is an invented British town with a playful royal family, original illustrations, and humorous proclamations. The King of Crownbridge is a character in that story.

The royal family in the Crownbridge story is fictional. It is not the British Royal Family, and nothing in the prototype is endorsed by them. That note is on the destination screen and on the scorecard.

Yufuin and Yanagawa remain real Japanese destinations. Their rewards, merchants, and studio scenes in this demo are fictional.

## Source and deployment

```
freds-adventure/
  index.html       page, header, pass dialog, merchant dialog
  css/adventure.css
  js/adventure.js  the demonstration
  js/qr.js         QR encoder for saved codes
  images/          example pictures and the Royal Carriage certificate
  README.md        this file
```

Paths inside the page are relative (`css/`, `js/`, `images/`), so the folder can be served at `/freds-adventure/`.

`netlify.toml` in the site root sets no build command and no publish directory. Publishing stays with the directory chosen in the Netlify UI. This prototype does not add a build step, a redirect, a sitemap entry, or a link from the main site. Do not enable site-wide password protection in the Netlify UI for this demo. That control would lock the rest of sansymeon.jp, including the Japanese lessons.

Local preview, from the site root:

```
python3 -m http.server 8877 --bind 127.0.0.1
```

Open `http://127.0.0.1:8877/freds-adventure/`.

The page is marked `noindex`. It contains no production credentials and no customer data. Every offer is marked DEMO — NOT REDEEMABLE.

## Implemented, simulated, or proposed

| Piece | In this prototype |
| --- | --- |
| Choose England, then Crownbridge; or Japan, then Yufuin or Yanagawa | Implemented. The country is remembered in this browser. |
| Fred and Fredette | Implemented. Existing drawings, new names. |
| Tap the demonstration seal | Implemented. The seal is a button. |
| Save a fictional parking discount on that tap | Implemented, in this browser |
| Plain proof and themed certificate, same code | Implemented |
| Royal Carriage artwork | Implemented for Crownbridge. The art's own code and QR are samples. |
| My Parking Pass, including refresh | Implemented in this browser |
| Real QR for the saved code | Implemented in `js/qr.js` |
| Mystery reveal after parking | Implemented |
| Crownbridge scorecard, 2 of 5 frames | Visual sample only. Not tied to scans. |
| Next chapter after five discoveries | Proposed. Not built. |
| Archive of a completed chapter | Proposed. Not built. |
| Everyone Wins, Prize by Chance, Guaranteed Gift + Lucky Bonus | Simulated in the Demo desk |
| Prize cap, dates, on/off, once per scan, day, or promotion | Simulated in this browser |
| Photo Studio and example transformations | Implemented. No live transformation. |
| Child Mode and magical-item examples | Implemented. Photographs are not stored. |
| A QR code used by both the game and Frega | Proposed. The method is Frega's decision. |
| Payments, validation, parking transactions, Frega operations | Not built. Out of scope. |
