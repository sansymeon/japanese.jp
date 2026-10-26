/* Fred's Adventure prototype.
   Fictional rewards only. No network, accounts, payments, or merchant calls.
   Mascots are placeholder drawings. Swap mascotSvg() when original art arrives. */

(function () {
  "use strict";

  const LOCATIONS = {
    crownbridge: {
      id: "crownbridge",
      where: "England",
      name: "Crownbridge",
      adventure: "Royal Adventure",
      line: "A fictional castle town. Parking is saved, then a royal surprise.",
      sealTitle: "A mark on the high street",
      sealHint: "The scan always saves parking. The mystery afterwards can change.",
      relicName: "A royal decree",
      relicHint: "Fred and Fredette kept this aside. Wax, ribbon, and a surprise.",
      object: "decree",
      parking: {
        title: "Parking saved",
        story: "A demonstration discount on Crownbridge parking.",
        detail: "20% off one fictional stay at the castle car park. Every scan saves you money.",
        merchant: "Crownbridge Castle Parking",
        offer: "20% off parking",
        certificate: {
          privilege: "Royal Carriage Privilege",
          name: "Royal Carriage Discount Certificate",
          decree: "By Royal Decree",
          grant: "Your carriage discount has been granted.",
        },
      },
      studio: [
        { id: "king", group: "Become Royalty", label: "King", scene: "royalty", blurb: "Crown, royal clothing, and the castle behind you." },
        { id: "queen", group: "Become Royalty", label: "Queen", scene: "royalty", blurb: "A crown, a gown, and the palace light." },
        { id: "prince", group: "Become Royalty", label: "Prince", scene: "royalty", blurb: "A younger crown, and the same castle." },
        { id: "princess", group: "Become Royalty", label: "Princess", scene: "royalty", blurb: "A tiara, and bunting on the battlements." },
        { id: "motoring", group: "Vintage Motoring", label: "At the wheel", scene: "motoring", blurb: "Period clothing, the driver's seat, and a scenic road." },
      ],
      rewards: [
        {
          tier: "portrait",
          weight: 24,
          title: "You've won a Fred Portrait!",
          story: "Congratulations! The studio door is open.",
          detail: "Choose to become royalty, or sit at the wheel of a vintage motorcar. If the souvenir is for a child, Child Mode uses a photo of an object, not a face. This invitation has no cash value. A real portrait service is not connected yet.",
          merchant: "Fred's Photo Studio",
          ribbon: "A studio invitation",
        },
        {
          tier: "cafe",
          weight: 22,
          title: "The Tea Room Bows",
          story: "A cream tea is waiting on the high street.",
          detail: "A demonstrated pot of tea and a warm bun. The tea room is as fictional as the town.",
          merchant: "Banner Tea Room",
          ribbon: "A neighbourly treat",
        },
        {
          tier: "attraction",
          weight: 20,
          title: "The Castle Gate Opens",
          story: "The castle has kept you a place on the walls.",
          detail: "A demonstrated wander along the battlements, with the high street below.",
          merchant: "Crownbridge Castle Walk",
          ribbon: "An invitation nearby",
        },
        {
          tier: "humorous",
          weight: 18,
          title: "The Bunting Decree",
          story: "By royal whim, you are Honorary Keeper of the Bunting.",
          detail: "A fictional honour. It will not pay for parking, tea, or anything else.",
          merchant: "The Town Crier",
          ribbon: "A humorous decree",
        },
        {
          tier: "consolation",
          weight: 16,
          title: "A Royal Wave",
          story: "The King of Crownbridge is judging the sponge cakes. Please accept an imaginary sticker.",
          detail: "The parking discount still stands. This extra prize is only a joke.",
          merchant: "The Castle Ravens",
          ribbon: "A small consolation",
        },
      ],
    },
    yufuin: {
      id: "yufuin",
      where: "Japan",
      name: "Yufuin",
      adventure: "The Daimyo's Journey",
      line: "Steam and cedars, after the parking is saved.",
      sealTitle: "A mark by the lake road",
      sealHint: "The scan always saves parking. The scroll afterwards can change.",
      relicName: "The Daimyo's scroll",
      relicHint: "Fred and Fredette kept the cord tied. Nothing has been unrolled.",
      object: "scroll",
      parking: {
        title: "Parking saved",
        story: "A demonstration discount on Yufuin parking.",
        detail: "20% off one fictional stay beside the lake road. Every scan saves you money.",
        merchant: "Yufuin Lake Road Parking",
        offer: "20% off parking",
        certificate: {
          privilege: "Lantern Road Privilege",
          name: "The Daimyo's Discount Writ",
          decree: "By the Journey's Seal",
          grant: "Your lake-road discount has been granted.",
        },
      },
      studio: [
        { id: "daimyo", group: "The Daimyo's Journey", label: "Daimyo portrait", scene: "daimyo", blurb: "Formal robes, a crest, and the steam of the hills." },
        { id: "rickshaw", group: "The Daimyo's Journey", label: "Rickshaw portrait", scene: "rickshaw", blurb: "A seat in a lantern-lit rickshaw, with your face still recognisable." },
      ],
      rewards: [
        {
          tier: "portrait",
          weight: 28,
          title: "You've won a Fred Portrait!",
          story: "Congratulations! The studio door is open.",
          detail: "Choose a daimyo portrait or a rickshaw portrait. If the souvenir is for a child, Child Mode uses a photo of an object, not a face. This invitation has no cash value. A real portrait service is not connected yet.",
          merchant: "Fred's Photo Studio",
          ribbon: "A studio invitation",
        },
        {
          tier: "cafe",
          weight: 26,
          title: "Steam, Then a Cup",
          story: "The tea house has poured something warm in your name.",
          detail: "A demonstrated coffee or roast-tea set. The tea house is fictional.",
          merchant: "Cedar Kettle Tea House",
          ribbon: "A neighbourly treat",
        },
        {
          tier: "attraction",
          weight: 24,
          title: "The Flower Corridor",
          story: "The mountain path is open, and it saved you a stroll.",
          detail: "A demonstrated wander through the seasonal flowers.",
          merchant: "The Seasonal Flower Path",
          ribbon: "An invitation nearby",
        },
        {
          tier: "humorous",
          weight: 22,
          title: "Deputy Lantern",
          story: "The daimyo sneezed and appointed you Deputy Lantern.",
          detail: "A ceremonial joke. The parking discount was the practical part.",
          merchant: "The Procession",
          ribbon: "A humorous privilege",
        },
      ],
    },
    yanagawa: {
      id: "yanagawa",
      where: "Japan",
      name: "Yanagawa",
      adventure: "The Canal Adventure",
      line: "Willows and lanterns, after the parking is saved.",
      sealTitle: "A mark at the landing",
      sealHint: "The scan always saves parking. The gift afterwards can change.",
      relicName: "A canal-kingdom gift",
      relicHint: "Fred and Fredette kept the ribbon tied.",
      object: "gift",
      parking: {
        title: "Parking saved",
        story: "A demonstration discount on Yanagawa parking.",
        detail: "20% off one fictional stay at the landing. Every scan saves you money.",
        merchant: "Yanagawa Landing Parking",
        offer: "20% off parking",
        certificate: {
          privilege: "Canal Landing Privilege",
          name: "Canal Discount Certificate",
          decree: "By the Landing's Seal",
          grant: "Your landing discount has been granted.",
        },
      },
      studio: [
        { id: "historical", group: "The Canal Adventure", label: "Historical portrait", scene: "historical", blurb: "A formal riverside portrait, with your features kept recognisable." },
        { id: "boat", group: "The Canal Adventure", label: "Canal boat portrait", scene: "boat", blurb: "A seat in a willow boat, lanterns on the water." },
      ],
      rewards: [
        {
          tier: "portrait",
          weight: 28,
          title: "You've won a Fred Portrait!",
          story: "Congratulations! The studio door is open.",
          detail: "Choose a historical portrait or a seat in a canal boat. If the souvenir is for a child, Child Mode uses a photo of an object, not a face. This invitation has no cash value. A real portrait service is not connected yet.",
          merchant: "Fred's Photo Studio",
          ribbon: "A studio invitation",
        },
        {
          tier: "cafe",
          weight: 26,
          title: "The Tea Boat",
          story: "A riverside coffee, where the lanterns meet the water.",
          detail: "A demonstrated cup on the canal bank. The café is fictional.",
          merchant: "Canal Bank Coffee",
          ribbon: "A neighbourly treat",
        },
        {
          tier: "attraction",
          weight: 24,
          title: "The Lantern Cruise",
          story: "An evening seat has drifted your way.",
          detail: "A demonstrated place on the lantern cruise. Bring a quiet voice.",
          merchant: "Canal Kingdom Cruises",
          ribbon: "An invitation nearby",
        },
        {
          tier: "humorous",
          weight: 22,
          title: "Admiral of the Ducks",
          story: "The canal kingdom promotes you, with immediate effect and no boat.",
          detail: "The ducks are not included. Your parking discount was already saved.",
          merchant: "The Resident Ducks",
          ribbon: "A humorous reward",
        },
      ],
    },
  };

  const THEME = {
    welcome: "#fff4e6",
    crownbridge: "#d5e2f6",
    yufuin: "#d7e4cf",
    yanagawa: "#b7e4dc",
  };

  const SCARF = {
    welcome: "#c53622",
    crownbridge: "#1e3a7a",
    yufuin: "#b8432f",
    yanagawa: "#0e6a66",
  };

  const DESK_KEY = "freds-adventure-desk-v2";
  const VISIT_KEY = "freds-adventure-visit-v2";
  const PASS_KEY = "freds-adventure-pass-v1";
  const COUNTRY_KEY = "freds-adventure-country-v1";
  const MAGIC_KEY = "freds-adventure-magic-v1";
  const MAGIC_KINDS = {
    puppy: {
      title: "Dragon Puppy",
      story: "An ordinary stuffed puppy grew wings, a scarf, and a castle of its own.",
    },
    cube: {
      title: "The Enchanted Cube",
      story: "An ordinary puzzle cube woke up beside a little dragon.",
    },
  };
  const MERCHANT_KEY = "freds-adventure-merchant-v1";
  const CLAIMS_KEY = "freds-adventure-claims-v1";

  const screenEl = document.getElementById("screen");
  const backBtn = document.getElementById("nav-back");
  const soundBtn = document.getElementById("sound-btn");
  const demoOpen = document.getElementById("demo-open");
  const demoDialog = document.getElementById("demo-dialog");
  const demoBody = document.getElementById("demo-body");
  const passBtn = document.getElementById("pass-open");
  const passDialog = document.getElementById("pass-dialog");
  const passBody = document.getElementById("pass-body");
  const live = document.getElementById("live");
  const themeMeta = document.querySelector('meta[name="theme-color"]');

  const state = {
    screen: "welcome",
    locationId: null,
    country: null,
    phase: "scan",
    reward: null,
    coupon: null,
    parkingCoupon: null,
    pass: null,
    passView: "certificate",
    merchant: {},
    claims: {},
    photoUrl: null,
    photoName: "",
    transformId: null,
    studioGuest: null,
    childStep: "intro",
    childConcept: null,
    magicStep: "intro",
    magicKind: null,
    magicId: null,
    magicFresh: false,
    collection: [],
    faceCheck: null,
    busy: false,
    sound: true,
    mode: "random",
    weights: {},
    deskVisible: true,
    history: [],
    booted: false,
  };

  let openTimer = 0;
  let photoToken = 0;
  let wordmarkTaps = [];
  let audioCtx = null;
  let generation = 1;

  function defaultWeights(id) {
    const weights = {};
    LOCATIONS[id].rewards.forEach(function (reward) {
      weights[reward.tier] = reward.weight;
    });
    return weights;
  }

  function freshDesk() {
    const weights = {};
    Object.keys(LOCATIONS).forEach(function (id) {
      weights[id] = defaultWeights(id);
    });
    return { sound: true, mode: "random", weights: weights, deskVisible: true };
  }

  function loadDesk() {
    const fresh = freshDesk();
    try {
      const saved = JSON.parse(localStorage.getItem(DESK_KEY) || "null");
      if (!saved) return fresh;
      fresh.sound = saved.sound !== false;
      fresh.mode = saved.mode || "random";
      fresh.deskVisible = saved.deskVisible !== false;
      Object.keys(LOCATIONS).forEach(function (id) {
        const incoming = saved.weights && saved.weights[id];
        if (!incoming) return;
        LOCATIONS[id].rewards.forEach(function (reward) {
          const n = Number(incoming[reward.tier]);
          if (Number.isFinite(n) && n >= 0) fresh.weights[id][reward.tier] = n;
        });
      });
    } catch (err) {
      return fresh;
    }
    return fresh;
  }

  function saveDesk() {
    localStorage.setItem(DESK_KEY, JSON.stringify({
      sound: state.sound,
      mode: state.mode,
      weights: state.weights,
      deskVisible: state.deskVisible,
    }));
  }

  function saveVisit() {
    sessionStorage.setItem(VISIT_KEY, JSON.stringify({
      screen: state.screen,
      locationId: state.locationId,
      reward: state.reward,
      coupon: state.coupon,
      parkingCoupon: state.parkingCoupon,
      history: state.history.slice(0, 6),
    }));
  }

  function loadVisit() {
    try {
      return JSON.parse(sessionStorage.getItem(VISIT_KEY) || "null");
    } catch (err) {
      return null;
    }
  }

  function loadPass() {
    try {
      if (!localStorage.getItem(PASS_KEY)) {
        const earlier = localStorage.getItem("frega-adventure-pass-v1");
        if (earlier) localStorage.setItem(PASS_KEY, earlier);
      }
      const raw = JSON.parse(localStorage.getItem(PASS_KEY) || "null");
      if (!raw || !LOCATIONS[raw.locationId]) return null;
      const code = String(raw.code || "");
      if (!/^DEMO-[A-Z]{2}-[A-Z0-9]{4}$/.test(code)) return null;
      return { locationId: raw.locationId, code: code };
    } catch (err) {
      return null;
    }
  }

  function savePass(pass) {
    localStorage.setItem(PASS_KEY, JSON.stringify({
      locationId: pass.locationId,
      code: pass.code,
    }));
  }

  function todayKey() {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return now.getFullYear() + "-" + month + "-" + day;
  }

  function defaultOffer(id) {
    const loc = LOCATIONS[id];
    const reward = rewardByTier(loc, "cafe");
    const gift = rewardByTier(loc, "humorous");
    const bonus = rewardByTier(loc, "portrait");
    return {
      merchantName: reward.merchant,
      rewardTier: reward.tier,
      rewardTitle: reward.title,
      rewardDetail: reward.detail,
      giftTier: gift.tier,
      giftTitle: gift.title,
      giftDetail: gift.detail,
      bonusTier: bonus.tier,
      bonusTitle: bonus.title,
      bonusDetail: bonus.detail,
      mode: "gift",
      probability: 50,
      maxPrizes: 40,
      awarded: 0,
      frequency: "visit",
      start: "",
      end: "",
      enabled: true,
    };
  }

  function loadMerchant() {
    const all = {};
    Object.keys(LOCATIONS).forEach(function (id) { all[id] = defaultOffer(id); });
    try {
      const saved = JSON.parse(localStorage.getItem(MERCHANT_KEY) || "null");
      if (!saved) return all;
      Object.keys(LOCATIONS).forEach(function (id) {
        const item = saved[id];
        if (!item) return;
        const offer = all[id];
        ["merchantName", "rewardTitle", "rewardDetail", "giftTitle", "giftDetail", "bonusTitle", "bonusDetail"].forEach(function (key) {
          if (typeof item[key] === "string") offer[key] = item[key].slice(0, 280);
        });
        ["start", "end"].forEach(function (key) {
          if (typeof item[key] === "string" && /^\d{4}-\d{2}-\d{2}$/.test(item[key])) offer[key] = item[key];
        });
        ["rewardTier", "giftTier", "bonusTier"].forEach(function (key) {
          if (LOCATIONS[id].rewards.some(function (reward) { return reward.tier === item[key]; })) offer[key] = item[key];
        });
        if (item.mode === "everyone" || item.mode === "chance" || item.mode === "gift") offer.mode = item.mode;
        if ([10, 20, 50].indexOf(Number(item.probability)) !== -1) offer.probability = Number(item.probability);
        const maxPrizes = Number(item.maxPrizes);
        if (Number.isFinite(maxPrizes) && maxPrizes >= 0 && maxPrizes <= 9999) offer.maxPrizes = Math.round(maxPrizes);
        const awarded = Number(item.awarded);
        if (Number.isFinite(awarded) && awarded >= 0 && awarded <= 99999) offer.awarded = Math.round(awarded);
        if (item.frequency === "visit" || item.frequency === "day" || item.frequency === "promotion") offer.frequency = item.frequency;
        offer.enabled = item.enabled !== false;
      });
    } catch (err) {
      return all;
    }
    return all;
  }

  function saveMerchant() {
    localStorage.setItem(MERCHANT_KEY, JSON.stringify(state.merchant));
  }

  function loadClaims() {
    try {
      const saved = JSON.parse(localStorage.getItem(CLAIMS_KEY) || "null");
      return saved && typeof saved === "object" ? saved : {};
    } catch (err) {
      return {};
    }
  }

  function saveClaims() {
    localStorage.setItem(CLAIMS_KEY, JSON.stringify(state.claims));
  }

  function offerOf(loc) {
    return state.merchant[loc.id] || defaultOffer(loc.id);
  }

  function promotionOpen(offer) {
    if (!offer.enabled) return false;
    if (offer.start && offer.end && offer.end < offer.start) return false;
    const today = todayKey();
    if (offer.start && today < offer.start) return false;
    if (offer.end && today > offer.end) return false;
    return true;
  }

  function alreadyClaimed(locId, offer) {
    const claim = state.claims[locId];
    if (!claim || offer.frequency === "visit") return false;
    if (offer.frequency === "day") return claim.day === todayKey();
    return !!claim.promotion;
  }

  function markClaim(locId, offer) {
    if (offer.frequency === "visit") return;
    if (!state.claims[locId]) state.claims[locId] = {};
    if (offer.frequency === "day") state.claims[locId].day = todayKey();
    if (offer.frequency === "promotion") state.claims[locId].promotion = true;
    saveClaims();
  }

  function giveLimitedPrize(locId, offer) {
    offer.awarded += 1;
    saveMerchant();
    markClaim(locId, offer);
  }

  function authoredStory(loc, tier, title, fallback) {
    const found = loc.rewards.find(function (reward) {
      return reward.tier === tier && reward.title === title;
    });
    return found ? found.story : fallback;
  }

  function merchantPrize(loc, offer, tierKey, titleKey, detailKey) {
    const tier = offer[tierKey];
    const title = offer[titleKey] || "A small surprise";
    return {
      tier: tier,
      title: title,
      story: authoredStory(loc, tier, title, "Something from " + (offer.merchantName || "a nearby place") + "."),
      detail: offer[detailKey] || "",
      merchant: offer.merchantName || "A nearby place",
      ribbon: "A surprise",
    };
  }

  function quietReward(offer, fields) {
    return {
      tier: "none",
      title: fields.title,
      story: fields.story,
      detail: fields.detail,
      merchant: offer.merchantName || "",
      ribbon: "Parking still saved",
      kind: fields.kind,
    };
  }

  function resolveVisit(loc) {
    const offer = offerOf(loc);
    if (!promotionOpen(offer)) {
      return quietReward(offer, {
        kind: "closed",
        title: "The town is quiet",
        story: "There is no extra gift right now.",
        detail: "The adventure is still here.",
      });
    }
    if (alreadyClaimed(loc.id, offer)) {
      return quietReward(offer, {
        kind: "already",
        title: "That gift is already yours",
        story: offer.frequency === "promotion" ? "This promotion has already given you its reward." : "You already received today's gift.",
        detail: "Another one is not added.",
      });
    }
    if (offer.mode === "everyone" || offer.mode === "chance") {
      if (offer.awarded >= offer.maxPrizes) {
        return quietReward(offer, {
          kind: "spent",
          title: "Those extra prizes are gone",
          story: "Every one of them has been given out.",
          detail: "The adventure is still here.",
        });
      }
      if (offer.mode === "chance" && Math.random() * 100 >= offer.probability) {
        return quietReward(offer, {
          kind: "miss",
          title: "The mascots kept their secret",
          story: "No extra prize this time.",
          detail: "You can try the adventure again.",
        });
      }
      giveLimitedPrize(loc.id, offer);
      const prize = merchantPrize(loc, offer, "rewardTier", "rewardTitle", "rewardDetail");
      prize.kind = "prize";
      prize.ribbon = offer.mode === "everyone" ? "For you" : "A lucky find";
      return prize;
    }
    const gift = merchantPrize(loc, offer, "giftTier", "giftTitle", "giftDetail");
    const lucky = offer.awarded < offer.maxPrizes && Math.random() * 100 < offer.probability;
    if (lucky) {
      giveLimitedPrize(loc.id, offer);
      const bonus = merchantPrize(loc, offer, "bonusTier", "bonusTitle", "bonusDetail");
      bonus.kind = "both";
      bonus.ribbon = "A gift, and a lucky extra";
      bonus.alsoTitle = gift.title;
      bonus.alsoDetail = gift.detail;
      bonus.alsoTier = gift.tier;
      return bonus;
    }
    markClaim(loc.id, offer);
    gift.kind = "gift";
    gift.ribbon = "A gift for you";
    return gift;
  }

  function rewardOpensStudio(reward) {
    return !!(reward && (reward.tier === "portrait" || reward.alsoTier === "portrait"));
  }

  function esc(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch];
    });
  }

  function currentPlace() {
    return LOCATIONS[state.locationId] || null;
  }

  function countryOf(loc) {
    return loc && loc.where === "England" ? "england" : "japan";
  }

  function loadCountry() {
    const value = localStorage.getItem(COUNTRY_KEY);
    return value === "england" || value === "japan" ? value : null;
  }

  function saveCountry(id) {
    state.country = id;
    localStorage.setItem(COUNTRY_KEY, id);
  }

  function countryName() {
    return state.country === "japan" ? "Japan" : "England";
  }

  function placesInCountry() {
    return Object.keys(LOCATIONS).filter(function (id) {
      return countryOf(LOCATIONS[id]) === state.country;
    });
  }

  function world() {
    if (state.screen === "choose" && state.country === "england") return "crownbridge";
    if (state.screen === "choose" && state.country === "japan") return "yufuin";
    if (state.screen === "welcome" || state.screen === "country" || state.screen === "choose" || !state.locationId) return "welcome";
    return state.locationId;
  }

  function rewardByTier(loc, tier) {
    return loc.rewards.find(function (reward) { return reward.tier === tier; }) || loc.rewards[0];
  }

  function hashString(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i += 1) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function qrSvg(seed) {
    const n = 21;
    let h = hashString(seed);
    let cells = "";
    for (let y = 0; y < n; y += 1) {
      for (let x = 0; x < n; x += 1) {
        const finder = finderOn(x, y, n);
        h = (Math.imul(h, 1664525) + 1013904223) >>> 0;
        const on = finder === null ? (h % 3 !== 0) : finder;
        if (on) cells += '<rect x="' + x + '" y="' + y + '" width="1" height="1"/>';
      }
    }
    return '<svg class="coupon-qr" viewBox="0 0 21 21" aria-hidden="true">' + cells + "</svg>";
  }

  function finderOn(x, y, n) {
    const boxes = [[0, 0], [n - 7, 0], [0, n - 7]];
    for (let i = 0; i < boxes.length; i += 1) {
      const x0 = boxes[i][0];
      const y0 = boxes[i][1];
      if (x < x0 || y < y0 || x >= x0 + 7 || y >= y0 + 7) continue;
      const lx = x - x0;
      const ly = y - y0;
      const border = lx === 0 || ly === 0 || lx === 6 || ly === 6;
      const core = lx >= 2 && lx <= 4 && ly >= 2 && ly <= 4;
      return border || core;
    }
    return null;
  }

  function couponFor(id) {
    const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    const prefix = { crownbridge: "CB", yufuin: "YF", yanagawa: "YG" }[id] || "FG";
    let body = "";
    for (let i = 0; i < 4; i += 1) {
      body += alphabet[Math.floor(Math.random() * alphabet.length)];
    }
    return "DEMO-" + prefix + "-" + body;
  }

  function rollReward(loc) {
    if (state.mode !== "random" && loc.rewards.some(function (reward) { return reward.tier === state.mode; })) {
      return rewardByTier(loc, state.mode);
    }
    const weights = state.weights[loc.id] || defaultWeights(loc.id);
    const entries = loc.rewards.map(function (reward) {
      return { reward: reward, w: Math.max(0, Number(weights[reward.tier]) || 0) };
    });
    let total = entries.reduce(function (sum, entry) { return sum + entry.w; }, 0);
    if (total <= 0) return loc.rewards[Math.floor(Math.random() * loc.rewards.length)];
    let cursor = Math.random() * total;
    for (let i = 0; i < entries.length; i += 1) {
      cursor -= entries[i].w;
      if (cursor < 0) return entries[i].reward;
    }
    return entries[entries.length - 1].reward;
  }

  function rememberPull(loc, reward) {
    state.history.unshift({
      location: loc.name,
      title: reward.title,
      tier: reward.tier,
    });
    state.history = state.history.slice(0, 6);
  }

  function clearPhoto() {
    photoToken += 1;
    if (state.photoUrl) URL.revokeObjectURL(state.photoUrl);
    state.photoUrl = null;
    state.photoName = "";
    state.faceCheck = null;
  }

  function resetStudioPath() {
    state.studioGuest = null;
    state.childStep = "intro";
    state.childConcept = null;
    state.magicStep = "intro";
    state.magicKind = null;
    state.magicId = null;
    state.magicFresh = false;
    state.faceCheck = null;
  }

  function loadMagic() {
    try {
      const raw = JSON.parse(localStorage.getItem(MAGIC_KEY) || "[]");
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (item) {
        return item && MAGIC_KINDS[item.kind] && typeof item.id === "string" && LOCATIONS[item.locationId];
      }).slice(0, 24);
    } catch (err) {
      return [];
    }
  }

  function saveMagic(list) {
    state.collection = list.slice(0, 24);
    localStorage.setItem(MAGIC_KEY, JSON.stringify(state.collection.map(function (item) {
      return { id: item.id, kind: item.kind, locationId: item.locationId };
    })));
  }

  function studioChoice(loc) {
    const list = loc.studio || [];
    return list.find(function (item) { return item.id === state.transformId; }) || list[0] || null;
  }

  function exampleSvg(scene) {
    const royal = {
      king: "royalty",
      queen: "royalty",
      prince: "royalty",
      princess: "royalty",
    };
    const scenes = {
      royalty: '<rect width="320" height="180" fill="#1e3a7a"/><path d="M0 130 L40 70 L80 110 L120 40 L160 110 L200 60 L240 120 L320 80 V180 H0Z" fill="#c6a56a"/><path d="M70 180 V100 H130 V180" fill="#f4e7c8"/><circle cx="100" cy="78" r="16" fill="#f6c9a0"/><path d="M84 70 L92 52 L100 66 L108 48 L116 70" fill="#e2b033"/>',
      motoring: '<rect width="320" height="180" fill="#8ec6ea"/><path d="M0 128 Q80 96 160 128 T320 118 V180 H0Z" fill="#7d9a62"/><path d="M36 136 Q96 86 168 126 L214 126 Q236 96 278 126 L292 138 Z" fill="#9e2d22"/><circle cx="88" cy="142" r="18" fill="#241c16"/><circle cx="236" cy="142" r="18" fill="#241c16"/><circle cx="88" cy="142" r="7" fill="#d9d3c7"/><circle cx="236" cy="142" r="7" fill="#d9d3c7"/><path d="M118 118 H214 V138 H118Z" fill="#d7e7f2"/><circle cx="156" cy="108" r="18" fill="#f6c9a0"/><path d="M140 104 H172 L164 86 H148Z" fill="#1e3a7a"/><circle cx="168" cy="128" r="10" fill="none" stroke="#241c16" stroke-width="3"/><path d="M168 118 V138 M158 128 H178" stroke="#241c16" stroke-width="2"/>',
      daimyo: '<rect width="320" height="180" fill="#d7e4cf"/><path d="M0 150 L70 70 L140 130 L210 50 L320 140 V180 H0Z" fill="#2f5d45"/><rect x="126" y="78" width="68" height="102" fill="#b8432f"/><circle cx="160" cy="70" r="16" fill="#f6c9a0"/><path d="M144 62 H176 L168 40 H152Z" fill="#241c16"/>',
      rickshaw: '<rect width="320" height="180" fill="#f7f1e6"/><path d="M0 140 H320 V180 H0Z" fill="#c6a56a"/><circle cx="78" cy="140" r="22" fill="#241c16"/><circle cx="210" cy="140" r="22" fill="#241c16"/><path d="M70 132 H230 L210 78 H110 Z" fill="#b8432f"/><circle cx="168" cy="70" r="14" fill="#f6c9a0"/><path d="M40 90 H120" stroke="#241c16" stroke-width="6"/>',
      historical: '<rect width="320" height="180" fill="#e7f3ef"/><path d="M20 180 Q40 40 70 180" fill="#2f6b4f"/><rect x="120" y="36" width="90" height="120" fill="#f4efe4" stroke="#241c16" stroke-width="3"/><circle cx="165" cy="78" r="16" fill="#f6c9a0"/><path d="M132 150 Q165 110 198 150 V156 H132Z" fill="#0e6a66"/>',
      boat: '<rect width="320" height="180" fill="#d7f1ec"/><path d="M0 110 H320 V180 H0Z" fill="#0e6a66"/><path d="M70 118 Q160 150 250 118 L230 138 H90Z" fill="#f4e2c0"/><path d="M150 118 V62" stroke="#241c16" stroke-width="4"/><circle cx="168" cy="78" r="14" fill="#f6c9a0"/><path d="M30 70 Q50 20 70 90" fill="#2f6b4f"/>',
    };
    return (
      '<svg class="example-art" viewBox="0 0 320 180" aria-hidden="true">' +
      (scenes[scene] || scenes[royal[scene]] || scenes.royalty) +
      "</svg>"
    );
  }

  function childConcepts(loc) {
    const local = {
      crownbridge: {
        blurb: "The mascot takes the item to the castle, in a royal, vintage British scene.",
        scene: "local-crownbridge",
      },
      yufuin: {
        blurb: "The mascot carries the item on the daimyo road, between the steam and a rickshaw.",
        scene: "local-yufuin",
      },
      yanagawa: {
        blurb: "The mascot brings the item onto a lantern boat along the canal.",
        scene: "local-yanagawa",
      },
    }[loc.id] || {
      blurb: "The mascot uses the item in this destination.",
      scene: "local-crownbridge",
    };
    return [
      {
        id: "wear",
        title: "Mascot Wear",
        blurb: "Fred or Fredette simply wears or carries the item.",
        scene: "wear",
      },
      {
        id: "local",
        title: "Local Adventure Version",
        blurb: local.blurb,
        scene: local.scene,
      },
      {
        id: "fantasy",
        title: "Special Fantasy Version",
        blurb: "A more magical, celebratory version of the mascot, still using the item.",
        scene: "fantasy",
      },
    ];
  }

  function childConceptArt(scene) {
    const mascot = '<circle cx="168" cy="104" r="28" fill="#f6b26b"/><ellipse cx="150" cy="78" rx="8" ry="12" fill="#f6b26b"/><ellipse cx="186" cy="78" rx="8" ry="12" fill="#f6b26b"/><circle cx="158" cy="100" r="3" fill="#241c16"/><circle cx="178" cy="100" r="3" fill="#241c16"/><path d="M160 112 Q168 118 176 112" fill="none" stroke="#241c16" stroke-width="2"/>';
    const item = '<path d="M154 76 H182 L174 60 H162 Z" fill="#c53622"/><path d="M146 74 H190 L186 82 H150 Z" fill="#9e2d22"/>';
    const scenes = {
      wear: '<rect width="320" height="180" fill="#fff6ea"/>' + mascot + item,
      "local-crownbridge": '<rect width="320" height="180" fill="#1e3a7a"/><path d="M0 140 L50 80 L90 120 L140 50 L190 120 L240 70 L320 130 V180 H0Z" fill="#c6a56a"/>' + mascot + item,
      "local-yufuin": '<rect width="320" height="180" fill="#d7e4cf"/><path d="M0 150 L80 70 L150 130 L230 60 L320 140 V180 H0Z" fill="#2f5d45"/>' + mascot + item,
      "local-yanagawa": '<rect width="320" height="180" fill="#d7f1ec"/><path d="M0 120 H320 V180 H0Z" fill="#0e6a66"/><path d="M70 124 Q160 156 250 124 L230 146 H90Z" fill="#f4e2c0"/>' + mascot + item,
      fantasy: '<rect width="320" height="180" fill="#2a2148"/><circle cx="46" cy="36" r="3" fill="#fff6ea"/><circle cx="90" cy="58" r="2" fill="#e2b033"/><circle cx="250" cy="40" r="3" fill="#fff6ea"/><circle cx="280" cy="78" r="2" fill="#f29ab0"/>' + mascot + item + '<path d="M200 70 L206 84 L220 90 L206 96 L200 110 L194 96 L180 90 L194 84 Z" fill="#e2b033"/>',
    };
    return (
      '<svg class="example-art" viewBox="0 0 320 180" aria-hidden="true">' +
      (scenes[scene] || scenes.wear) +
      "</svg>"
    );
  }

  function trustNotes() {
    return (
      '<ul class="trust">' +
        "<li>Child Mode uses object photos only.</li>" +
        "<li>No child face is needed.</li>" +
        "<li>Photos are used only for this experience.</li>" +
        "<li>Remove photo at any time.</li>" +
      "</ul>"
    );
  }

  function objectPreview(alt) {
    if (!state.photoUrl) return "";
    return (
      '<img class="photo-preview photo-object" alt="' + esc(alt) + '" src="' + esc(state.photoUrl) + '">' +
      '<p class="quiet">' + esc(state.photoName || "Selected photo") + "</p>" +
      '<button type="button" class="cta cta-secondary" data-action="remove-photo">Remove photo</button>'
    );
  }

  function photoPicker(label, capture, cameraLabel) {
    return (
      '<div class="studio-actions">' +
        '<button type="button" class="cta cta-primary" data-action="pick-photo" data-capture="">' + label + "</button>" +
        '<button type="button" class="cta cta-secondary" data-action="pick-photo" data-capture="' + capture + '">' + cameraLabel + "</button>" +
      "</div>" +
      '<input id="photo-input" class="sr-only" type="file" accept="image/*" aria-label="' + esc(label) + '">'
    );
  }

  function mascotSvg(who, place) {
    const getta = who === "getta";
    const body = getta ? "#f29ab0" : "#f6b26b";
    const deep = getta ? "#e57f98" : "#e8944a";
    const belly = getta ? "#fff0f4" : "#fff6ea";
    const inner = getta ? "#ffd0dc" : "#f7c9a8";
    const scarf = SCARF[place] || SCARF.welcome;
    const bow = getta
      ? '<g><ellipse cx="156" cy="78" rx="16" ry="11" fill="#c53622"/><ellipse cx="178" cy="78" rx="16" ry="11" fill="#c53622"/><circle cx="166" cy="78" r="6" fill="#e2b033"/></g>'
      : "";
    return (
      '<svg class="mascot' + (getta ? " mascot-getta" : "") + '" viewBox="0 0 220 240" aria-hidden="true">' +
        '<ellipse cx="110" cy="226" rx="52" ry="8" fill="rgba(36,28,22,.13)"/>' +
        '<ellipse cx="78" cy="210" rx="22" ry="12" fill="#2b2118"/>' +
        '<ellipse cx="142" cy="210" rx="22" ry="12" fill="#2b2118"/>' +
        '<ellipse cx="78" cy="206" rx="20" ry="10" fill="' + inner + '"/>' +
        '<ellipse cx="142" cy="206" rx="20" ry="10" fill="' + inner + '"/>' +
        '<ellipse cx="46" cy="42" rx="18" ry="24" fill="#2b2118"/>' +
        '<ellipse cx="174" cy="42" rx="18" ry="24" fill="#2b2118"/>' +
        '<ellipse cx="46" cy="40" rx="15" ry="21" fill="' + body + '"/>' +
        '<ellipse cx="174" cy="40" rx="15" ry="21" fill="' + body + '"/>' +
        '<ellipse cx="46" cy="44" rx="7" ry="12" fill="' + inner + '"/>' +
        '<ellipse cx="174" cy="44" rx="7" ry="12" fill="' + inner + '"/>' +
        '<circle cx="114" cy="122" r="82" fill="#2b2118"/>' +
        '<circle cx="110" cy="118" r="82" fill="' + body + '"/>' +
        '<ellipse cx="42" cy="150" rx="20" ry="16" fill="' + deep + '"/>' +
        '<ellipse cx="178" cy="150" rx="20" ry="16" fill="' + deep + '"/>' +
        '<ellipse cx="110" cy="150" rx="46" ry="38" fill="' + belly + '"/>' +
        '<ellipse cx="68" cy="132" rx="14" ry="9" fill="#f28b82" opacity=".75"/>' +
        '<ellipse cx="152" cy="132" rx="14" ry="9" fill="#f28b82" opacity=".75"/>' +
        '<ellipse cx="86" cy="112" rx="10" ry="13" fill="#241c16"/>' +
        '<ellipse cx="134" cy="112" rx="10" ry="13" fill="#241c16"/>' +
        '<ellipse cx="89" cy="107" rx="3.5" ry="4.5" fill="#fff"/>' +
        '<ellipse cx="137" cy="107" rx="3.5" ry="4.5" fill="#fff"/>' +
        '<path d="M96 136 Q110 152 124 136" fill="none" stroke="#241c16" stroke-width="4" stroke-linecap="round"/>' +
        '<path d="M58 146 Q110 190 164 146 Q148 168 110 170 Q72 168 58 146" fill="' + scarf + '"/>' +
        bow +
      "</svg>"
    );
  }

  function cast(place, compact) {
    return (
      '<div class="cast' + (compact ? " cast-compact" : "") + '">' +
        '<figure class="bob">' + mascotSvg("kun", place) +
          (compact ? "" : "<figcaption>Fred</figcaption>") +
        "</figure>" +
        '<figure class="bob bob-late">' + mascotSvg("getta", place) +
          (compact ? "" : "<figcaption>Fredette</figcaption>") +
        "</figure>" +
      "</div>"
    );
  }

  function relicSvg(kind) {
    if (kind === "scroll") {
      return (
        '<svg class="relic" viewBox="0 0 220 250" aria-hidden="true">' +
          '<rect x="48" y="28" width="124" height="188" rx="10" fill="#f4e6cf" stroke="#241c16" stroke-width="4"/>' +
          '<rect x="36" y="22" width="22" height="200" rx="11" fill="#e7d3ae" stroke="#241c16" stroke-width="4"/>' +
          '<rect x="162" y="22" width="22" height="200" rx="11" fill="#e7d3ae" stroke="#241c16" stroke-width="4"/>' +
          '<path d="M70 78 h80 M70 100 h80 M70 122 h64" stroke="#c4b08a" stroke-width="4" stroke-linecap="round"/>' +
          '<path d="M78 168 Q110 150 142 168" fill="none" stroke="#b8432f" stroke-width="6" stroke-linecap="round"/>' +
          '<circle cx="110" cy="166" r="7" fill="#e2b033" stroke="#241c16" stroke-width="3"/>' +
        "</svg>"
      );
    }
    if (kind === "gift") {
      return (
        '<svg class="relic" viewBox="0 0 220 250" aria-hidden="true">' +
          '<rect x="40" y="92" width="140" height="120" rx="12" fill="#0e6a66" stroke="#241c16" stroke-width="4"/>' +
          '<rect x="96" y="92" width="28" height="120" fill="#e2b033"/>' +
          '<rect x="40" y="132" width="140" height="24" fill="#e2b033"/>' +
          '<rect x="36" y="78" width="148" height="24" rx="6" fill="#127e78" stroke="#241c16" stroke-width="4"/>' +
          '<path d="M110 80 C80 40 40 70 78 92" fill="none" stroke="#e2b033" stroke-width="10" stroke-linecap="round"/>' +
          '<path d="M110 80 C140 40 180 70 142 92" fill="none" stroke="#e2b033" stroke-width="10" stroke-linecap="round"/>' +
          '<circle cx="110" cy="82" r="8" fill="#fff6ea" stroke="#241c16" stroke-width="3"/>' +
        "</svg>"
      );
    }
    return (
      '<svg class="relic" viewBox="0 0 220 250" aria-hidden="true">' +
        '<path d="M38 30 h144 v168 l-16 22 -16 -16 -16 22 -16 -16 -16 22 -16 -16 -16 22 -16 -22 z" fill="#f6e7c8" stroke="#241c16" stroke-width="4"/>' +
        '<path d="M62 68 h96 M62 92 h96 M62 116 h72" stroke="#d9c4a0" stroke-width="4" stroke-linecap="round"/>' +
        '<circle cx="110" cy="162" r="26" fill="#c53622" stroke="#241c16" stroke-width="4"/>' +
        '<path d="M110 148 l4 10 h10 l-8 6 3 10 -9 -6 -9 6 3 -10 -8 -6 h10 z" fill="#e2b033"/>' +
      "</svg>"
    );
  }

  function relicButton(loc, opening) {
    return (
      '<button type="button" class="relic-btn' + (opening ? " opening" : " arrive") + '" data-action="open">' +
        '<span class="halves" aria-hidden="true"><i class="half half-top"></i><i class="half half-bottom"></i></span>' +
        relicSvg(loc.object) +
        '<i class="spark s1"></i><i class="spark s2"></i><i class="spark s3"></i><i class="spark s4"></i>' +
        '<span class="sr-only">Open the surprise</span>' +
      "</button>"
    );
  }

  function confetti() {
    const colors = ["#c53622", "#e2b033", "#7ec8e3", "#f29ab0", "#fffaf3", "#2f5d45"];
    let html = "";
    for (let i = 0; i < 16; i += 1) {
      const style = "--x:" + Math.round(Math.random() * 100) + "%;--d:" + (Math.random() * 0.8).toFixed(2) +
        "s;--r:" + Math.round(Math.random() * 80 - 40) + "deg;--c:" + colors[i % colors.length] +
        ";--dur:" + (2.6 + Math.random() * 1.8).toFixed(2) + "s";
      html += '<i class="confetti" style="' + style + '"></i>';
    }
    return html;
  }

  function placeArt(id) {
    if (id === "crownbridge") {
      return '<div class="place-art art-crownbridge" aria-hidden="true"><i class="art-sun"></i><i class="castle"></i><i class="street"></i></div>';
    }
    if (id === "yufuin") {
      return '<div class="place-art art-yufuin" aria-hidden="true"><i class="art-sun"></i><i class="steam"></i><i class="hill"></i></div>';
    }
    return '<div class="place-art art-yanagawa" aria-hidden="true"><i class="art-moon"></i><i class="boat"></i><i class="wave"></i></div>';
  }

  function viewWelcome() {
    return (
      '<section class="view">' +
        '<div class="sky">' +
          '<i class="sun" aria-hidden="true"></i><i class="cloud" aria-hidden="true"></i>' +
          cast("welcome") +
        "</div>" +
        '<div class="sheet">' +
          '<p class="kicker">Optional entertainment</p>' +
          "<h1>Welcome to Fred's Adventure</h1>" +
          '<p class="lede">Every scan saves you money. Every scan brings a surprise. And sometimes, you become royalty.</p>' +
          '<p class="quiet">The parking discount stays easy to find. The adventure is the extra. Every offer is fictional.</p>' +
          (state.country
            ? '<p class="quiet">Continuing in ' + countryName() + '.</p>' +
              '<button type="button" class="text-btn change-country" data-action="change-country">Change Country</button>'
            : "") +
        "</div>" +
        '<div class="dock">' +
          '<button type="button" class="cta cta-primary" data-action="begin">Begin Your Adventure!</button>' +
        "</div>" +
      "</section>"
    );
  }

  function viewCountry() {
    return (
      '<section class="view">' +
        '<div class="sky sky-short sky-choose">' + cast("welcome", true) + "</div>" +
        '<div class="sheet">' +
          '<p class="kicker">A local adventure</p>' +
          "<h1>Choose a country</h1>" +
          '<p class="lede">Stay with one country. Its towns remain yours to explore.</p>' +
          '<div class="country-list">' +
            '<button type="button" class="country country-england" data-action="country" data-country="england">' +
              "<strong>England</strong>" +
              "<span>Crownbridge, a fictional royal town.</span>" +
            "</button>" +
            '<button type="button" class="country country-japan" data-action="country" data-country="japan">' +
              "<strong>Japan</strong>" +
              "<span>Yufuin and Yanagawa.</span>" +
            "</button>" +
          "</div>" +
          '<p class="quiet">Saved rewards stay with you if you change country later.</p>' +
        "</div>" +
      "</section>"
    );
  }

  function viewChoose() {
    const england = state.country !== "japan";
    const cards = placesInCountry().map(function (id) {
      const loc = LOCATIONS[id];
      return (
        '<button type="button" class="place" data-action="enter" data-location="' + loc.id + '">' +
          placeArt(loc.id) +
          '<span class="place-copy">' +
            '<span class="place-where">' + esc(loc.where) + "</span>" +
            '<span class="place-name">' + esc(loc.name) + "</span>" +
            '<span class="place-adventure">' + esc(loc.adventure) + "</span>" +
            '<span class="place-line">' + esc(loc.line) + "</span>" +
          "</span>" +
        "</button>"
      );
    }).join("");
    return (
      '<section class="view">' +
        '<div class="sky sky-short sky-choose">' + cast(england ? "crownbridge" : "yufuin", true) + "</div>" +
        '<div class="sheet">' +
          '<p class="kicker">' + (england ? "England" : "Japan") + "</p>" +
          "<h1>" + (england ? "Crownbridge" : "Choose your adventure") + "</h1>" +
          '<p class="lede">' + (england
            ? "Crownbridge is an invented British town. Every merchant and reward is a demonstration."
            : "Yufuin and Yanagawa are real places. Every merchant and reward is a demonstration.") + "</p>" +
          '<div class="place-list">' + cards + "</div>" +
          (england
            ? '<p class="quiet">The royal family in the Crownbridge story is fictional. It is not the British Royal Family, and nothing here is endorsed by them.</p>'
            : "") +
          '<button type="button" class="text-btn change-country" data-action="change-country">Change Country</button>' +
        "</div>" +
      "</section>"
    );
  }

  function viewDiscover() {
    const loc = currentPlace();
    return (
        '<section class="view">' +
          '<div class="sky">' +
            '<button type="button" class="viewfinder" data-action="scan">' +
              '<span class="finder-frame">' +
                '<i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>' +
                qrSvg("freds-seal-" + loc.id) +
                '<span class="seal-demo">DEMO</span>' +
                '<span class="scanline"></span>' +
              "</span>" +
              '<span class="sr-only">Scan the demonstration seal</span>' +
            "</button>" +
          "</div>" +
          '<div class="sheet">' +
            '<p class="kicker">' + esc(loc.adventure) + "</p>" +
            "<h1>" + esc(loc.sealTitle) + "</h1>" +
            '<p class="lede">' + esc(loc.sealHint) + "</p>" +
          "</div>" +
          '<div class="dock">' +
            '<button type="button" class="cta cta-primary" data-action="scan"' + (state.busy ? " disabled" : "") + ">" +
              (state.busy ? "Reading the seal…" : "Scan the seal") +
            "</button>" +
          "</div>" +
        "</section>"
    );
  }

  function proofCode(coupon) {
    if (!coupon) return "";
    return (
      '<div class="code-row">' +
        '<div class="code-qr">' + FredQR.svg(coupon) + "</div>" +
        "<div>" +
          '<p class="code-label">Reference code</p>' +
          '<p class="code-value">' + esc(coupon) + "</p>" +
        "</div>" +
      "</div>"
    );
  }

  function sealSvg() {
    return (
      '<svg class="seal" viewBox="0 0 64 64" aria-hidden="true">' +
        '<circle cx="32" cy="32" r="28" fill="#8d1c2c"/>' +
        '<circle cx="32" cy="32" r="22" fill="none" stroke="#e2b033" stroke-width="2"/>' +
        '<path d="M18 40 L26 24 H30 L32 30 L34 24 H38 L46 40 H40 L38 34 H26 L24 40 Z" fill="#e2b033"/>' +
      "</svg>"
    );
  }

  function adventureCertificate(loc, parking, code) {
    const cert = parking.certificate;
    const art = loc.id === "crownbridge"
      ? '<img class="cert-art" src="images/parking_certificate.jpg" width="1448" height="1086" alt="Illustrated Royal Carriage Discount Certificate. The code and QR printed in the picture are samples.">' +
        '<p class="quiet">The picture is an illustration. The code and QR printed on it are samples.</p>'
      : sealSvg() +
        '<p class="cert-ribbon">' + esc(cert.decree) + "</p>" +
        "<h2>" + esc(cert.privilege) + "</h2>" +
        '<p class="cert-name">' + esc(cert.name) + "</p>" +
        '<p class="story">' + esc(cert.grant) + "</p>";
    return (
      '<article class="certificate">' +
        '<p class="compare-kicker">Fred\'s Adventure</p>' +
        (loc.id === "crownbridge"
          ? '<p class="cert-ribbon">' + esc(cert.decree) + "</p><h2>" + esc(cert.privilege) + "</h2>"
          : "") +
        art +
        '<div class="saved-pass">' +
          '<p class="compare-kicker">Your saved pass</p>' +
          '<p class="merchant">' + esc(parking.merchant) + "</p>" +
          '<p class="proof-offer">' + esc(parking.offer) + "</p>" +
          proofCode(code) +
          '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
        "</div>" +
      "</article>"
    );
  }

  function viewParking() {
    const pass = state.pass;
    const loc = pass ? LOCATIONS[pass.locationId] : currentPlace();
    if (!pass || !loc) {
      return (
        '<section class="view">' +
          '<div class="sky sky-park">' + cast(loc ? loc.id : "welcome", true) + "</div>" +
          '<div class="sheet sheet-park">' +
            "<h1>Parking discount</h1>" +
            '<p class="lede">Scan the seal to save a demonstration parking discount.</p>' +
          "</div>" +
          '<div class="dock">' +
            '<button type="button" class="cta cta-primary" data-action="begin">' + (state.country ? "Return to Adventures" : "Choose a country") + "</button>" +
          "</div>" +
        "</section>"
      );
    }
    const parking = loc.parking;
    const code = pass.code;
    return (
      '<section class="view">' +
        '<div class="sheet sheet-park">' +
          '<p class="kicker">Parking saved</p>' +
          "<h1>Your parking reward</h1>" +
          '<p class="lede">A plain proof shows the practical record. Fred\'s Adventure gives the same discount through a themed certificate.</p>' +
          '<div class="compare">' +
            adventureCertificate(loc, parking, code) +
            '<article class="proof">' +
              '<p class="compare-kicker">Plain proof</p>' +
              "<h2>Parking Discount Saved</h2>" +
              '<p class="proof-sub">Proof of Discount</p>' +
              '<p class="merchant">' + esc(parking.merchant) + "</p>" +
              '<p class="proof-offer">' + esc(parking.offer) + "</p>" +
              '<p class="proof-same quiet">Same reference code as the certificate.</p>' +
              proofCode(code) +
              '<p class="quiet">Demonstration only. Not a real parking voucher.</p>' +
            "</article>" +
          "</div>" +
          '<p class="quiet">Same discount. Same code. The story does not change the proof. It stays in My Parking Pass.</p>' +
          (loc.id === "crownbridge"
            ? '<button type="button" class="text-btn score-link" data-action="scorecard">Adventure Scorecard</button>'
            : "") +
        "</div>" +
        '<div class="dock">' +
          '<button type="button" class="cta cta-primary" data-action="mystery">Open the mystery reward</button>' +
        "</div>" +
      "</section>"
    );
  }

  function passMarkup(view) {
    const pass = state.pass;
    const loc = LOCATIONS[pass.locationId];
    const parking = loc.parking;
    const cert = parking.certificate;
    const code = pass.code;
    if (loc.id === "crownbridge") {
      return (
        '<div class="pass-scroll">' +
          '<article class="certificate pass-royal">' +
            '<img class="cert-art" src="images/parking_certificate.jpg" width="1448" height="1086" alt="Illustrated Royal Carriage Discount Certificate. The code and QR printed in the picture are samples.">' +
            '<p class="quiet">The picture is an illustration. The code and QR printed on it are samples.</p>' +
            '<div class="saved-pass">' +
              '<p class="compare-kicker">Your saved pass</p>' +
              '<p class="merchant">' + esc(parking.merchant) + "</p>" +
              '<p class="proof-offer">' + esc(parking.offer) + "</p>" +
              proofCode(code) +
              '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
            "</div>" +
          "</article>" +
        "</div>"
      );
    }
    if (view === "proof") {
      return (
        '<div class="pass-scroll">' +
          '<p class="quiet">Fictional demonstration. Not a real parking voucher.</p>' +
          '<article class="booth">' +
            '<p class="compare-kicker">Show at Parking</p>' +
            "<h3>Proof of Discount</h3>" +
            '<p class="booth-offer">' + esc(parking.offer) + "</p>" +
            '<p class="merchant">' + esc(parking.merchant) + "</p>" +
            '<p>' + esc(loc.name) + ", " + esc(loc.where) + "</p>" +
            '<div class="code-qr">' + FredQR.svg(code) + "</div>" +
            '<p class="code-label">Reference code</p>' +
            '<p class="booth-code">' + esc(code) + "</p>" +
            '<p class="quiet">Demonstration only. Not a real parking voucher.</p>' +
            '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
          "</article>" +
        "</div>" +
        '<button type="button" class="cta cta-secondary" data-pass="certificate">' +
          (loc.id === "crownbridge" ? "Royal Carriage Certificate" : "Adventure certificate") +
        "</button>"
      );
    }
    const art = loc.id === "crownbridge"
      ? '<img class="cert-art" src="images/parking_certificate.jpg" width="1448" height="1086" alt="Illustrated Royal Carriage Discount Certificate. The code and QR printed in the picture are samples.">' +
        '<p class="quiet">The picture is an illustration. The code and QR printed on it are samples. Your saved code is below.</p>'
      : '<p class="cert-ribbon">' + esc(cert.decree) + "</p>" +
        "<h3>" + esc(cert.privilege) + "</h3>" +
        '<p class="cert-name">' + esc(cert.name) + "</p>" +
        '<p class="story">' + esc(cert.grant) + "</p>";
    return (
      '<div class="pass-scroll">' +
        '<p class="quiet">Fictional demonstration. Not a real parking voucher. Opening this pass does not create a new code.</p>' +
        '<article class="certificate">' +
          '<p class="compare-kicker">Fred\'s Adventure</p>' +
          (loc.id === "crownbridge" ? '<p class="cert-ribbon">' + esc(cert.decree) + "</p><h3>" + esc(cert.name) + "</h3>" : "") +
          art +
          '<div class="saved-pass">' +
            '<p class="compare-kicker">Your saved pass</p>' +
            '<p class="merchant">' + esc(parking.merchant) + "</p>" +
            '<p class="proof-offer">' + esc(parking.offer) + "</p>" +
            '<p class="quiet">' + esc(loc.name) + ", " + esc(loc.where) + "</p>" +
            proofCode(code) +
            '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
          "</div>" +
        "</article>" +
      "</div>" +
      '<button type="button" class="cta cta-primary" data-pass="proof">Show at Parking</button>'
    );
  }

  function showPass(view) {
    if (!state.pass) return;
    closeDesk();
    state.passView = view || "certificate";
    passBody.innerHTML = passMarkup(state.passView);
    if (!passDialog.open) passDialog.showModal();
    passBtn.setAttribute("aria-expanded", "true");
    live.textContent = state.passView === "proof"
      ? "Show at Parking. Proof of discount. Demonstration only. Not a real parking voucher. " + state.pass.code
      : "Parking certificate. Demonstration only. Not a real parking voucher. " + state.pass.code;
  }

  function closePass() {
    if (passDialog.open) passDialog.close();
    if (passBtn) passBtn.setAttribute("aria-expanded", "false");
  }

  function viewMystery() {
    const loc = currentPlace();
    const opening = state.phase === "opening";
    return (
      '<section class="view">' +
        '<div class="sky sky-mystery">' +
          '<div class="cast cast-peek">' +
            '<figure class="bob">' + mascotSvg("kun", loc.id) + "</figure>" +
            '<figure class="bob bob-late">' + mascotSvg("getta", loc.id) + "</figure>" +
          "</div>" +
          relicButton(loc, opening) +
        "</div>" +
        '<div class="sheet">' +
          '<p class="kicker">Mystery reward</p>' +
          "<h1>" + esc(loc.relicName) + "</h1>" +
          '<p class="lede">' + (opening ? "Something is about to slip free." : esc(loc.relicHint)) + "</p>" +
        "</div>" +
        '<div class="dock">' +
          '<button type="button" class="cta cta-primary" data-action="open"' + (opening ? " disabled" : "") + ">" +
            (opening ? "Opening…" : "Tap to reveal") +
          "</button>" +
        "</div>" +
      "</section>"
    );
  }

  function viewReward() {
    const loc = currentPlace();
    const reward = state.reward;
    const rarityClass = reward.tier === "portrait" ? " rare" : reward.tier === "consolation" || reward.tier === "humorous" ? " consolation" : "";
    const won = reward.tier !== "none";
    const studio = rewardOpensStudio(reward);
    const dock = studio
      ? '<div class="dock"><button type="button" class="cta cta-primary" data-action="studio">Enter the Photo Studio</button></div>'
      : '<div class="dock"><button type="button" class="cta cta-primary" data-action="again">Continue Exploring</button></div>';
    const more = (studio
      ? '<button type="button" class="cta cta-secondary" data-action="again">Continue Exploring</button>'
      : "") +
      '<button type="button" class="cta cta-secondary" data-action="adventures">Return to Adventures</button>' +
      (loc.id === "crownbridge"
        ? '<button type="button" class="text-btn score-link" data-action="scorecard">Adventure Scorecard</button>'
        : "");
    const also = reward.alsoTitle
      ? '<p class="lede">Also for you: ' + esc(reward.alsoTitle) + ". " + esc(reward.alsoDetail || "") + "</p>"
      : "";
    const coupon = won && state.coupon
      ? '<hr class="perforation"><div class="code-row"><div class="code-qr">' + FredQR.svg(state.coupon) + "</div><div>" +
        '<p class="code-label">Mystery coupon</p><p class="code-value">' + esc(state.coupon) + "</p>" +
        '<p class="quiet">Demonstration only. Not redeemable.</p></div></div>'
      : "";
    return (
      '<section class="view">' +
        '<div class="sky sky-short">' + (won ? confetti() : cast(loc.id, true)) + "</div>" +
        '<div class="sheet">' +
          '<article class="ticket' + (reward.tier === "portrait" ? " ticket-portrait" : "") + '">' +
            '<div class="ticket-mascots">' + mascotSvg("kun", loc.id) + mascotSvg("getta", loc.id) + "</div>" +
            '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span>' +
              '<span class="rarity' + rarityClass + '">' + esc(reward.ribbon) + "</span></p>" +
            "<h1>" + esc(reward.title) + "</h1>" +
            '<p class="story">' + esc(reward.story) + "</p>" +
            '<p class="lede">' + esc(reward.detail) + "</p>" +
            also +
            '<div class="meta-block">' +
              (reward.merchant && reward.tier !== "none" ? '<p class="merchant">' + esc(reward.merchant) + "</p>" : "") +
              '<p class="quiet">' + esc(loc.name) + ", " + esc(loc.where) + "</p>" +
            "</div>" +
            coupon +
            '<p class="quiet">' + (state.pass
              ? "Your parking discount is saved. Open My Parking Pass whenever you need it."
              : "The parking discount is separate from this prize.") + "</p>" +
          "</article>" +
          more +
        "</div>" +
        dock +
      "</section>"
    );
  }

  function scoreFrame(found, index, title, detail, art) {
    return (
      '<li class="score-frame' + (found ? " is-found" : "") + '">' +
        '<span class="score-index">' + index + "</span>" +
        (found ? art : "") +
        "<strong>" + title + "</strong>" +
        "<span>" + detail + "</span>" +
      "</li>"
    );
  }

  function viewScorecard() {
    const castle = '<svg class="score-art" viewBox="0 0 160 72" aria-hidden="true"><rect width="160" height="72" fill="#1e3a7a"/><path d="M8 58 L28 28 H40 L48 40 L58 22 H70 L80 44 L96 18 H108 L120 40 H132 L152 58 V72 H8Z" fill="#c6a56a"/><path d="M64 72 V40 H96 V72" fill="#f4e7c8"/><path d="M18 22 H34 L30 14 H22Z" fill="#8d1c2c"/><circle cx="26" cy="12" r="3" fill="#e2b033"/></svg>';
    const carriage = '<svg class="score-art" viewBox="0 0 160 72" aria-hidden="true"><rect width="160" height="72" fill="#243e78"/><circle cx="48" cy="54" r="10" fill="#e2b033"/><circle cx="112" cy="54" r="10" fill="#e2b033"/><path d="M36 48 H124 L112 28 H58 Z" fill="#8d1c2c"/><path d="M70 28 V16 H96 V28" fill="#f4e7c8"/><path d="M74 16 H92 L88 8 H78Z" fill="#e2b033"/></svg>';
    return (
      '<section class="view">' +
        '<div class="sheet sheet-score">' +
          '<p class="kicker">Royal Adventure</p>' +
          "<h1>Adventure Scorecard</h1>" +
          '<p class="score-count">2 of 5 discoveries</p>' +
          '<p class="quiet score-next">Five discoveries can open another chapter.</p>' +
          '<ol class="score-frames">' +
            scoreFrame(true, "1", "The Castle Gate", "Bunting on the battlements.", castle) +
            scoreFrame(true, "2", "The Royal Carriage", "A privilege granted in the high street.", carriage) +
            scoreFrame(false, "3", "Still to discover", "An empty frame.") +
            scoreFrame(false, "4", "Still to discover", "An empty frame.") +
            scoreFrame(false, "5", "Still to discover", "An empty frame.") +
          "</ol>" +
          '<p class="quiet">A sample scorecard. Discoveries are not counted from scans yet.</p>' +
          '<p class="quiet">Crownbridge and its royal family are fictional. This story is not the British Royal Family, and it is not endorsed by them.</p>' +
        "</div>" +
        '<div class="dock">' +
          '<button type="button" class="cta cta-primary" data-action="scorecard-back">Back to the adventure</button>' +
        "</div>" +
      "</section>"
    );
  }

  function viewStudio() {
    if (state.studioGuest === "child") return viewChildStudio();
    if (state.studioGuest === "magic") return viewMagic();
    if (state.studioGuest === "adult") return viewAdultStudio();
    return viewStudioGate();
  }

  function viewStudioGate() {
    const loc = currentPlace();
    return (
      '<section class="view">' +
        '<div class="sky sky-short sky-gate">' + cast(loc.id, true) + "</div>" +
        '<div class="sheet studio">' +
          '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
          "<h1>Fred's Photo Studio</h1>" +
          '<p class="story">Who is this souvenir for?</p>' +
          '<p class="lede">Children personalize the mascots with their objects, not with their faces.</p>' +
          '<button type="button" class="choice" data-action="guest" data-guest="adult">' +
            "<strong>For me</strong>" +
            "<span>A grown-up portrait style. Your own photograph is shown unchanged, because portrait generation is not connected.</span>" +
          "</button>" +
          '<button type="button" class="choice" data-action="guest" data-guest="child">' +
            "<strong>For a child</strong>" +
            "<span>Child Mode. Photograph a hat, scarf, toy, shoes, or bag. The mascot wears it. No child face is needed.</span>" +
          "</button>" +
          '<button type="button" class="choice" data-action="guest" data-guest="magic">' +
            "<strong>A magical item</strong>" +
            "<span>Photograph something ordinary. It becomes a surprise for a child's collection. The child does not choose what it becomes. No child face is needed.</span>" +
          "</button>" +
          (state.collection.length
            ? '<button type="button" class="cta cta-secondary" data-action="magic-collection">My magical collection</button>'
            : "") +
          trustNotes() +
        "</div>" +
      "</section>"
    );
  }

  function viewAdultStudio() {
    const loc = currentPlace();
    const choice = studioChoice(loc);
    const groups = [];
    loc.studio.forEach(function (item) {
      let group = groups.find(function (entry) { return entry.name === item.group; });
      if (!group) {
        group = { name: item.group, items: [] };
        groups.push(group);
      }
      group.items.push(item);
    });
    const choices = groups.map(function (group) {
      return (
        '<fieldset class="studio-group">' +
          "<legend>" + esc(group.name) + "</legend>" +
          group.items.map(function (item) {
            const pressed = choice && choice.id === item.id;
            return (
              '<button type="button" class="choice" data-action="transform" data-style="' + esc(item.id) + '" aria-pressed="' + (pressed ? "true" : "false") + '">' +
                "<strong>" + esc(item.label) + "</strong>" +
                "<span>" + esc(item.blurb) + "</span>" +
              "</button>"
            );
          }).join("") +
        "</fieldset>"
      );
    }).join("");
    const photo = state.photoUrl
      ? '<img class="photo-preview" alt="Your selected photograph, shown unchanged" src="' + esc(state.photoUrl) + '">' +
        '<p class="quiet">' + esc(state.photoName || "Selected photo") + "</p>" +
        '<button type="button" class="cta cta-secondary" data-action="remove-photo">Remove photo</button>'
      : '<div class="photo-empty"><p>No photo yet. It will stay on this device.</p></div>';
    const royal = choice && ["king", "queen", "prince", "princess"].indexOf(choice.id) !== -1;
    const example = royal
      ? royalGallery()
      : '<figure class="example-card">' +
          '<figcaption><span class="demo-flag">EXAMPLE</span> Intended result, not your photo</figcaption>' +
          exampleSvg(choice ? choice.id : "king") +
          '<p class="quiet">Live AI transformation is not connected. Your photograph is shown unchanged.</p>' +
        "</figure>";
    return (
      '<section class="view">' +
        '<div class="sky sky-short">' + cast(loc.id, true) + "</div>" +
        '<div class="sheet studio">' +
          '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
          "<h1>Fred's Photo Studio</h1>" +
          (royal ? "" : '<p class="lede">Your photograph stays on this device. It is not transformed.</p>') +
          (royal ? example : "") +
          "<h2>Your photograph</h2>" +
          photo +
          '<input id="photo-input" class="sr-only" type="file" accept="image/*" aria-label="Choose a photograph from this device">' +
          '<p class="quiet">The photograph stays in this browser tab. It is not uploaded or stored. Remove it at any time. A refresh clears it.</p>' +
          "<h2>Style</h2>" +
          choices +
          (royal ? "" : example) +
          '<button type="button" class="text-btn switch-mode" data-action="guest" data-guest="child">This souvenir is for a child</button>' +
          '<button type="button" class="cta cta-secondary" data-action="again">Continue Exploring</button>' +
        "</div>" +
        '<div class="dock dock-pair">' +
          '<button type="button" class="cta cta-primary" data-action="pick-photo" data-capture="">Choose a photo</button>' +
          '<button type="button" class="cta cta-secondary" data-action="pick-photo" data-capture="user">Take a selfie</button>' +
        "</div>" +
      "</section>"
    );
  }

  function royalGallery() {
    return (
      '<section class="showpiece" aria-label="Example AI Transformation">' +
        '<p class="show-label">Example AI Transformation</p>' +
        "<h2>The Royal Sisters</h2>" +
        '<div class="wipe">' +
          '<img class="wipe-after" src="images/royal_sisters_after.jpeg" alt="The Royal Sisters, after the royal transformation" width="1448" height="1086">' +
          '<img class="wipe-before" src="images/sisters_before.jpeg" alt="The Royal Sisters, before" width="1536" height="1152">' +
          '<input class="wipe-range" type="range" min="0" max="100" value="56" aria-label="Compare the Royal Sisters. Left is before, right is after.">' +
        "</div>" +
        '<p class="wipe-caption"><span>Before</span><span>Drag</span><span>After</span></p>' +
        '<p class="show-label">Example AI Transformation</p>' +
        "<h2>The Royal Gentlemen</h2>" +
        "<figure class=\"single\">" +
          '<img src="images/Gentlemen%20to%20Royal%20Servants.jpg" alt="The Royal Gentlemen demonstration photograph" width="1448" height="1086">' +
        "</figure>" +
        '<p class="quiet">These examples were created separately. Live AI transformation is not connected yet.</p>' +
      "</section>"
    );
  }

  function magicExample(kind) {
    if (kind === "cube") {
      return (
        '<figure class="single">' +
          '<img src="images/rubics_cube.jpg" alt="A puzzle cube shown beside its magical transformation" width="1672" height="941">' +
        "</figure>"
      );
    }
    return (
      '<div class="wipe wipe-portrait">' +
        '<img class="wipe-after" src="images/puppy_dragon.jpg" alt="The stuffed puppy after a magical dragon transformation" width="1122" height="1402">' +
        '<img class="wipe-before" src="images/puppy_before.jpeg" alt="A stuffed puppy, before" width="1152" height="1536">' +
        '<input class="wipe-range" type="range" min="0" max="100" value="18" aria-label="Compare the example puppy. Left is before, right is after.">' +
      "</div>" +
      '<p class="wipe-caption"><span>Before</span><span>Drag</span><span>After</span></p>'
    );
  }

  function magicThumb(kind) {
    if (kind === "cube") {
      return '<img src="images/rubics_cube.jpg" alt="" width="1672" height="941">';
    }
    return '<img src="images/puppy_dragon.jpg" alt="" width="1122" height="1402">';
  }

  function viewMagic() {
    const step = state.magicStep;
    let body = "";
    let dock = "";
    if (step === "collection") {
      body = magicCollection();
      dock = '<div class="dock"><button type="button" class="cta cta-primary" data-action="magic-again">Photograph another item</button></div>';
    } else if (step === "result" && MAGIC_KINDS[state.magicKind]) {
      body = magicResult();
      dock = '<div class="dock"><button type="button" class="cta cta-primary" data-action="magic-collection">See my collection</button></div>';
    } else if (step === "reveal") {
      body = magicReveal();
      dock = '<div class="dock"><button type="button" class="cta cta-primary" data-action="magic-reveal"' + (state.busy ? " disabled" : "") + ">" +
        (state.busy ? "The magic is stirring…" : "Reveal the magic") + "</button></div>";
    } else if (step === "review" || step === "rejected") {
      body = childReview();
    } else {
      body = magicIntro();
      dock = '<div class="dock dock-pair">' +
        '<button type="button" class="cta cta-primary" data-action="pick-photo" data-capture="environment">Take a photo of an item</button>' +
        '<button type="button" class="cta cta-secondary" data-action="pick-photo" data-capture="">Choose a photo of an item</button>' +
      "</div>";
    }
    return (
      '<section class="view">' +
        '<div class="sky sky-short">' + cast(currentPlace().id, true) + "</div>" +
        '<div class="sheet studio">' +
          '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
          '<p class="kicker">Magical item</p>' +
          body +
          '<button type="button" class="text-btn switch-mode" data-action="guest" data-guest="gate">Choose a different souvenir</button>' +
        "</div>" +
        dock +
      "</section>"
    );
  }

  function magicIntro() {
    return (
      "<h1>Photograph something ordinary</h1>" +
      '<p class="story">A toy, a puzzle, a hat, a bag. You will not know what it becomes.</p>' +
      '<p class="lede">Photograph the item, not a person. The surprise is an example. Your photograph is not transformed.</p>' +
      magicTrust() +
      '<input id="photo-input" class="sr-only" type="file" accept="image/*" aria-label="Choose a photo of an item">' +
      '<p class="quiet">The rear camera is used for an item. This is not a selfie. The photograph is not uploaded or stored.</p>'
    );
  }

  function magicTrust() {
    return (
      '<ul class="trust">' +
        "<li>This adventure uses object photos only.</li>" +
        "<li>No child face is needed.</li>" +
        "<li>The photograph stays on this device for this visit only.</li>" +
        "<li>The collection remembers the surprise. It does not keep the photograph.</li>" +
        "<li>Remove photo at any time.</li>" +
      "</ul>"
    );
  }

  function magicReveal() {
    const photo = state.photoUrl
      ? objectPreview("Your object photograph, shown unchanged")
      : "";
    return (
      "<h1>What will it become?</h1>" +
      '<p class="story">The item is about to change. Nobody has chosen the result.</p>' +
      photo +
      magicTrust()
    );
  }

  function magicResult() {
    const kind = MAGIC_KINDS[state.magicKind];
    const loc = currentPlace();
    const photo = state.magicFresh && state.photoUrl
      ? '<h2>Your object</h2>' + objectPreview("Your object photograph, shown unchanged")
      : "";
    return (
      "<h1>" + esc(kind.title) + "</h1>" +
      '<p class="story">' + esc(kind.story) + "</p>" +
      '<p class="lede">' + esc(loc.name) + " kept this surprise.</p>" +
      photo +
      '<section class="showpiece" aria-label="Example magical transformation">' +
        '<p class="show-label">Example transformation</p>' +
        magicExample(state.magicKind) +
        '<p class="quiet">This example was created separately. Your photograph is not in this picture. Live AI transformation is not connected.</p>' +
      "</section>" +
      '<p class="quiet">Saved in this browser’s collection. The photograph itself was not saved.</p>' +
      '<button type="button" class="cta cta-secondary" data-action="magic-drop" data-id="' + esc(state.magicId) + '">Remove this from my collection</button>' +
      '<button type="button" class="cta cta-secondary" data-action="magic-again">Photograph another item</button>'
    );
  }

  function magicCollection() {
    if (!state.collection.length) {
      return (
        "<h1>My magical collection</h1>" +
        '<p class="lede">Nothing is here yet. Photograph an ordinary item and the first surprise will be kept on this device.</p>' +
        '<p class="quiet">The collection does not store photographs.</p>'
      );
    }
    const cards = state.collection.map(function (item) {
      const kind = MAGIC_KINDS[item.kind];
      const loc = LOCATIONS[item.locationId];
      return (
        '<button type="button" class="magic-card" data-action="magic-open" data-id="' + esc(item.id) + '">' +
          magicThumb(item.kind) +
          "<span><strong>" + esc(kind.title) + "</strong>" +
          "<span>" + esc(loc.name) + "</span>" +
          '<span class="quiet">Example. Your photograph is not in this picture.</span></span>' +
        "</button>"
      );
    }).join("");
    return (
      "<h1>My magical collection</h1>" +
      '<p class="lede">Each card is a surprise this browser remembers. The photographs were not saved.</p>' +
      '<div class="magic-list">' + cards + "</div>"
    );
  }

  function viewChildStudio() {
    const loc = currentPlace();
    const step = state.childStep;
    let body = "";
    if (step === "review" || step === "rejected") body = childReview();
    else if (step === "concepts") body = childConceptsView(loc);
    else if (step === "souvenir") body = childSouvenir(loc);
    else body = childIntro();
    return (
      '<section class="view">' +
        '<div class="sky sky-short">' + cast(loc.id, true) + "</div>" +
        '<div class="sheet studio">' +
          '<p><span class="demo-flag">DEMO — NOT REDEEMABLE</span></p>' +
          '<p class="kicker">Child Mode</p>' +
          body +
          '<button type="button" class="text-btn switch-mode" data-action="guest" data-guest="adult">This portrait is for me instead</button>' +
        "</div>" +
      "</section>"
    );
  }

  function childIntro() {
    const photo = state.photoUrl
      ? objectPreview("Your object photograph, shown unchanged")
      : '<div class="photo-empty"><p>No photo yet. It stays on this device, and only for this experience.</p></div>';
    return (
      "<h1>Photograph an item</h1>" +
      '<p class="story">In Child Mode, please photograph an item, not a person.</p>' +
      '<p class="lede">Examples: hat, scarf, toy, shoes, bag.</p>' +
      trustNotes() +
      photo +
      photoPicker("Choose a photo of an item", "environment", "Take a photo of an item") +
      '<p class="quiet">The rear camera is used for an item. This is not a selfie. The photograph is not uploaded or stored.</p>'
    );
  }

  function childReview() {
    const magical = state.studioGuest === "magic";
    const rejected = state.childStep === "rejected" || state.magicStep === "rejected" || state.faceCheck === "face";
    const label = magical ? "This magical adventure" : "Child Mode";
    let status = "";
    if (state.faceCheck === "pending") {
      status = '<div class="check-panel"><p class="story">Checking the photograph.</p><p class="lede">Looking for a face with this browser. A fuller person check is a future feature.</p></div>';
    } else if (state.faceCheck === "face") {
      status = '<div class="reject-panel"><p class="story">Let\'s use a different photo.</p><p class="lede">This browser found a face, so this photo cannot be used. ' + label + ' accepts object photos only. Photograph a hat, scarf, toy, shoes, bag, umbrella, or something similar.</p></div>';
    } else if (rejected) {
      status = '<div class="reject-panel"><p class="story">Let\'s use a different photo.</p><p class="lede">' + label + ' accepts object photos only. No child face is needed. You marked this photo as a person. Automatic person detection is still a future feature, so this demonstration is asking you instead of deciding for you.</p></div>';
    } else if (state.faceCheck === "clear") {
      status = '<div class="check-panel"><p class="story">No face was found.</p><p class="lede">This browser did not find a face. It still cannot tell whether a person is in the photo. That fuller check is a future feature. Please confirm this is an item.</p></div>';
    } else {
      status = '<div class="check-panel"><p class="story">Automatic detection is not running.</p><p class="lede">Face and person detection is a future feature. It is not available in this browser yet. For this demonstration, say what the photo shows. Nothing is uploaded.</p></div>';
    }
    const actions = rejected || state.faceCheck === "face"
      ? photoPicker("Choose a different item", "environment", "Take a photo of an item")
      : (
        state.faceCheck === "pending"
          ? ""
          : '<div class="studio-actions">' +
              '<button type="button" class="cta cta-primary" data-action="object-ok">This photo is an object only</button>' +
              '<button type="button" class="cta cta-secondary" data-action="object-person">This photo shows a person</button>' +
            "</div>" +
            photoPicker("Choose a different photo", "environment", "Take a photo of an item")
      );
    return (
      "<h1>" + (rejected || state.faceCheck === "face" ? "Object photos only" : "Check the photograph") + "</h1>" +
      objectPreview("Your selected object photograph, shown unchanged") +
      status +
      (magical ? magicTrust() : trustNotes()) +
      actions
    );
  }

  function childConceptsView(loc) {
    const cards = childConcepts(loc).map(function (concept) {
      return (
        '<button type="button" class="concept" data-action="concept" data-concept="' + concept.id + '">' +
          '<span class="concept-flag">EXAMPLE</span>' +
          childConceptArt(concept.scene) +
          "<strong>" + esc(concept.title) + "</strong>" +
          "<span>" + esc(concept.blurb) + "</span>" +
          '<span class="quiet">Sample card. Your object is not in this picture.</span>' +
        "</button>"
      );
    }).join("");
    return (
      "<h1>Three ways to use the item</h1>" +
      '<p class="lede">Choose a favorite. Each card is a sample of the mascot with an item. Your photograph is not transformed.</p>' +
      objectPreview("Your object photograph, shown unchanged") +
      trustNotes() +
      '<div class="concepts">' + cards + "</div>"
    );
  }

  function childSouvenir(loc) {
    const concepts = childConcepts(loc);
    const chosen = concepts.find(function (concept) { return concept.id === state.childConcept; }) || concepts[0];
    return (
      "<h1>Your mascot souvenir</h1>" +
      '<p class="story">' + esc(chosen.title) + "</p>" +
      '<p class="lede">Children personalize the mascots with their objects, not with their faces.</p>' +
      '<figure class="example-card">' +
        '<figcaption><span class="demo-flag">EXAMPLE</span> Sample souvenir, not your photo</figcaption>' +
        childConceptArt(chosen.scene) +
        '<p class="lede">' + esc(chosen.blurb) + "</p>" +
        '<p class="quiet">Image generation is not connected. This illustration does not contain the uploaded object, and it does not contain a child.</p>' +
      "</figure>" +
      '<div class="object-row">' +
        (state.photoUrl
          ? '<img class="object-thumb photo-object" alt="Your object photograph, shown unchanged" src="' + esc(state.photoUrl) + '">'
          : "") +
        "<div><p><strong>Your object</strong></p><p class=\"quiet\">Shown exactly as selected. Photos are used only for this experience.</p></div>" +
      "</div>" +
      trustNotes() +
      '<button type="button" class="cta cta-secondary" data-action="child-concepts">See the other versions</button>' +
      '<button type="button" class="cta cta-secondary" data-action="remove-photo">Remove photo</button>'
    );
  }

  function announce() {
    const loc = currentPlace();
    if (state.screen === "welcome") live.textContent = "Welcome to Fred's Adventure.";
    else if (state.screen === "country") live.textContent = "Choose England or Japan. Saved rewards stay with you.";
    else if (state.screen === "choose") live.textContent = state.country === "japan"
      ? "Japan. Choose Yufuin or Yanagawa."
      : "England. Crownbridge is the royal adventure.";
    else if (state.screen === "discover") live.textContent = loc.name + ". Scan the demonstration seal.";
    else if (state.screen === "parking") live.textContent = state.pass
      ? "Parking discount saved. The same code is in My Parking Pass. Demonstration only. Not a real parking voucher. " + state.pass.code
      : "Scan the seal to save a demonstration parking discount.";
    else if (state.screen === "mystery") live.textContent = loc.relicName + ". Tap to reveal the mystery reward.";
    else if (state.screen === "reward" && state.reward) {
      live.textContent = state.reward.title + " " + state.reward.story + " Demonstration only. Not redeemable. " + state.coupon;
    } else if (state.screen === "scorecard") {
      live.textContent = "Adventure Scorecard. 2 of 5 discoveries. Crownbridge and its royal family are fictional.";
    } else if (state.screen === "studio" && state.studioGuest === "magic") {
      if (state.magicStep === "rejected" || state.faceCheck === "face") {
        live.textContent = "This magical adventure accepts object photos only. No child face is needed.";
      } else if (state.magicStep === "result" && MAGIC_KINDS[state.magicKind]) {
        live.textContent = MAGIC_KINDS[state.magicKind].title + ". Example transformation. Your photograph is not in this picture.";
      } else if (state.magicStep === "collection") {
        live.textContent = "My magical collection. The photographs were not saved.";
      } else if (state.magicStep === "reveal") {
        live.textContent = "What will it become? The surprise has not been chosen.";
      } else if (state.magicStep === "review") {
        live.textContent = "Check the photograph. This magical adventure uses object photos only.";
      } else {
        live.textContent = "Photograph an ordinary item. You will not know what it becomes. No child face is needed.";
      }
    } else if (state.screen === "studio" && state.studioGuest === "child") {
      if (state.childStep === "rejected" || state.faceCheck === "face") {
        live.textContent = "Child Mode accepts object photos only. No child face is needed.";
      } else if (state.childStep === "concepts") {
        live.textContent = "Three sample ideas. Your object is not in these pictures. Choose a favorite.";
      } else if (state.childStep === "souvenir") {
        live.textContent = "Mascot souvenir. Children personalize the mascots with their objects, not with their faces.";
      } else if (state.childStep === "review") {
        live.textContent = "Check the photograph. Child Mode uses object photos only.";
      } else {
        live.textContent = "Child Mode. Photograph an item, not a person. No child face is needed.";
      }
    } else if (state.screen === "studio") {
      live.textContent = state.studioGuest === "adult"
        ? "Fred's Photo Studio. Your photograph is not transformed. The portrait service is not connected."
        : "Who is this souvenir for? Child Mode uses an object photo, not a child's face.";
    }
  }

  function showingRoyalGallery() {
    if (state.screen !== "studio" || state.studioGuest !== "adult") return false;
    const loc = currentPlace();
    const choice = loc && studioChoice(loc);
    return !!(choice && ["king", "queen", "prince", "princess"].indexOf(choice.id) !== -1);
  }

  function render() {
    const place = world();
    document.body.dataset.world = place;
    document.body.dataset.desk = state.deskVisible ? "shown" : "hidden";
    document.body.dataset.gallery = showingRoyalGallery() ? "open" : "closed";
    document.body.dataset.compare = state.screen === "parking" ? "open" : "closed";
    if (themeMeta) themeMeta.setAttribute("content", THEME[place] || THEME.welcome);
    const titles = {
      welcome: "Fred's Adventure",
      country: "Choose a country · Fred's Adventure",
      choose: countryName() + " · Fred's Adventure",
      discover: (currentPlace() ? currentPlace().name + " · " : "") + "Fred's Adventure",
      parking: "Parking saved · Fred's Adventure",
      mystery: "Mystery reward · Fred's Adventure",
      reward: (state.reward ? state.reward.title + " · " : "") + "Fred's Adventure",
      scorecard: "Adventure Scorecard · Fred's Adventure",
      studio: state.studioGuest === "child"
        ? "Child Mode · Fred's Photo Studio"
        : state.studioGuest === "magic" ? "Magical item · Fred's Adventure" : "Fred's Photo Studio",
    };
    document.title = titles[state.screen] || "Fred's Adventure";
    backBtn.hidden = state.screen === "welcome";
    soundBtn.textContent = state.sound ? "Sound" : "Muted";
    soundBtn.setAttribute("aria-pressed", state.sound ? "true" : "false");
    soundBtn.setAttribute("aria-label", state.sound ? "Mute sound" : "Turn sound on");
    if (passBtn) {
      passBtn.hidden = !state.pass;
      passBtn.setAttribute("aria-expanded", passDialog && passDialog.open ? "true" : "false");
    }
    if (passDialog && passDialog.open && !state.pass) passDialog.close();

    const previous = screenEl.dataset.screen;
    const html = {
      welcome: viewWelcome,
      country: viewCountry,
      choose: viewChoose,
      discover: viewDiscover,
      parking: viewParking,
      mystery: viewMystery,
      reward: viewReward,
      scorecard: viewScorecard,
      studio: viewStudio,
    }[state.screen]();
    screenEl.innerHTML = html;
    screenEl.dataset.screen = state.screen;
    bindStudio();
    bindWipe();
    if (previous !== state.screen && !demoDialog.open) {
      screenEl.focus({ preventScroll: true });
    }
    announce();
    saveVisit();
  }

  function hashFor(screen, locationId) {
    if (screen === "country") return "#/country";
    if (screen === "choose") return "#/choose";
    if (screen === "discover" && locationId) return "#/discover/" + locationId;
    if (screen === "parking" && locationId) return "#/parking/" + locationId;
    if (screen === "mystery" && locationId) return "#/mystery/" + locationId;
    if (screen === "reward" && locationId) return "#/reward/" + locationId;
    if (screen === "studio" && locationId) return "#/studio/" + locationId;
    if (screen === "scorecard") return "#/scorecard/crownbridge";
    return "#/";
  }

  function entry() {
    return {
      freds: true,
      gen: generation,
      screen: state.screen,
      locationId: state.locationId,
      phase: state.screen === "mystery" ? state.phase : "scan",
      reward: state.reward,
      coupon: state.coupon,
      parkingCoupon: state.parkingCoupon,
    };
  }

  function applyEntry(item) {
    state.screen = item.screen || "welcome";
    state.locationId = item.locationId || null;
    state.phase = item.phase === "sealed" || item.phase === "opening" ? "sealed" : "scan";
    state.reward = item.reward || null;
    state.coupon = item.coupon || null;
    state.parkingCoupon = state.pass ? state.pass.code : (item.parkingCoupon || state.parkingCoupon || null);
    state.busy = false;
    if (state.screen === "choose" && !state.country) state.screen = "country";
    if (state.screen !== "welcome" && state.screen !== "country" && state.screen !== "choose" && !LOCATIONS[state.locationId]) {
      state.screen = state.country ? "choose" : "country";
      state.locationId = null;
    }
    if ((state.screen === "reward" || state.screen === "studio") && !state.reward) {
      state.screen = state.locationId ? "discover" : (state.country ? "choose" : "country");
    }
    if (state.screen === "studio" && !rewardOpensStudio(state.reward)) {
      state.screen = "reward";
    }
  }

  function go(screen, mode) {
    window.clearTimeout(openTimer);
    state.busy = false;
    state.screen = screen;
    if (screen === "discover" || screen === "parking") state.phase = "scan";
    if (screen === "mystery" && state.phase === "opening") state.phase = "sealed";
    if (screen === "welcome" || screen === "choose") {
      if (screen === "welcome") state.locationId = null;
    }
    const item = entry();
    const hash = hashFor(state.screen, state.locationId);
    if (mode === "replace") history.replaceState(item, "", hash);
    else history.pushState(item, "", hash);
    render();
  }

  function seedHistory(screen) {
    const sequence = ["welcome", "country", "choose", "discover", "parking", "mystery", "reward", "studio"];
    const end = Math.max(0, sequence.indexOf(screen));
    const trail = [];
    for (let i = 0; i <= end; i += 1) {
      const step = sequence[i];
      const needsPlace = step !== "welcome" && step !== "country" && step !== "choose";
      if (needsPlace && !state.locationId) break;
      if ((step === "reward" || step === "studio") && !state.reward) break;
      trail.push({
        screen: step,
        locationId: needsPlace ? state.locationId : null,
        reward: step === "reward" || step === "studio" ? state.reward : null,
        coupon: step === "reward" || step === "studio" ? state.coupon : null,
        parkingCoupon: state.pass ? state.pass.code : null,
        phase: step === "mystery" ? "sealed" : "scan",
      });
    }
    trail.forEach(function (item, index) {
      const snapshot = {
        freds: true,
        gen: generation,
        screen: item.screen,
        locationId: item.locationId,
        phase: item.phase,
        reward: item.reward,
        coupon: item.coupon,
        parkingCoupon: item.parkingCoupon,
      };
      const hash = hashFor(item.screen, item.locationId);
      if (index === 0) history.replaceState(snapshot, "", hash);
      else history.pushState(snapshot, "", hash);
    });
    const last = trail[trail.length - 1];
    state.screen = last.screen;
    state.locationId = last.locationId;
    state.reward = last.reward;
    state.coupon = last.coupon;
    state.parkingCoupon = state.pass ? state.pass.code : last.parkingCoupon;
    state.phase = last.phase || "scan";
  }

  function playTone(freq, when, duration, type, volume) {
    if (!state.sound) return;
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === "suspended") audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type || "triangle";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(volume, audioCtx.currentTime + when);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + when + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(audioCtx.currentTime + when);
      osc.stop(audioCtx.currentTime + when + duration);
    } catch (err) {
      state.sound = false;
    }
  }

  function playScan() {
    playTone(520, 0, 0.08, "square", 0.03);
    playTone(680, 0.09, 0.1, "square", 0.03);
  }

  function playParking() {
    playTone(494, 0, 0.12, "triangle", 0.045);
    playTone(659, 0.1, 0.16, "triangle", 0.04);
  }

  function playReveal(tier) {
    const notes = tier === "portrait" ? [523, 659, 784, 1046] : [392, 523, 659];
    notes.forEach(function (note, index) {
      playTone(note, index * 0.09, 0.28, "triangle", 0.06);
    });
  }

  function begin() {
    go(state.country ? "choose" : "country", "push");
  }

  function selectCountry(id) {
    if (id !== "england" && id !== "japan") return;
    saveCountry(id);
    state.locationId = null;
    go("choose", "push");
  }

  function enter(id) {
    const loc = LOCATIONS[id];
    if (!loc) return;
    if (state.country && countryOf(loc) !== state.country) return;
    clearPhoto();
    resetStudioPath();
    state.locationId = id;
    state.reward = null;
    state.coupon = null;
    state.transformId = null;
    state.phase = "scan";
    go("discover", "push");
  }

  function scan() {
    if (state.busy || state.screen !== "discover") return;
    const loc = currentPlace();
    if (!loc) return;
    state.busy = true;
    playScan();
    render();
    window.clearTimeout(openTimer);
    openTimer = window.setTimeout(function () {
      state.busy = false;
      state.pass = { locationId: loc.id, code: couponFor(loc.id) };
      savePass(state.pass);
      state.parkingCoupon = state.pass.code;
      state.reward = null;
      state.coupon = null;
      playParking();
      go("parking", "push");
    }, prefersReduced() ? 180 : 720);
  }

  function revealMagic() {
    if (state.busy || state.studioGuest !== "magic" || state.magicStep !== "reveal" || !state.photoUrl) return;
    const loc = currentPlace();
    if (!loc) return;
    state.busy = true;
    render();
    window.clearTimeout(openTimer);
    openTimer = window.setTimeout(function () {
      const kind = Math.random() < 0.5 ? "puppy" : "cube";
      const item = {
        id: "M" + Math.random().toString(36).slice(2, 8),
        kind: kind,
        locationId: loc.id,
      };
      saveMagic([item].concat(state.collection));
      state.magicKind = kind;
      state.magicId = item.id;
      state.magicFresh = true;
      state.magicStep = "result";
      state.busy = false;
      playTone(520, 0, 0.12, "triangle", 0.06);
      playTone(780, 0.14, 0.2, "triangle", 0.05);
      render();
    }, prefersReduced() ? 180 : 900);
  }

  function openRelic() {
    if (state.busy || state.screen !== "mystery" || state.phase === "opening") return;
    const loc = currentPlace();
    if (!loc) return;
    state.busy = true;
    state.phase = "opening";
    render();
    window.clearTimeout(openTimer);
    openTimer = window.setTimeout(function () {
      const reward = resolveVisit(loc);
      state.reward = reward;
      state.coupon = reward.tier === "none" ? null : couponFor(loc.id);
      state.busy = false;
      state.phase = "sealed";
      state.transformId = loc.studio && loc.studio[0] ? loc.studio[0].id : null;
      rememberPull(loc, reward);
      playReveal(reward.tier);
      go("reward", "push");
      paintDesk();
    }, prefersReduced() ? 180 : 1100);
  }

  function tryAgain() {
    clearPhoto();
    resetStudioPath();
    state.reward = null;
    state.coupon = null;
    state.transformId = null;
    state.phase = "scan";
    go("discover", "replace");
  }

  function prefersReduced() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function percentMap(weights, rewards) {
    const total = rewards.reduce(function (sum, reward) {
      return sum + Math.max(0, Number(weights[reward.tier]) || 0);
    }, 0);
    const map = {};
    rewards.forEach(function (reward) {
      const value = Math.max(0, Number(weights[reward.tier]) || 0);
      map[reward.tier] = total <= 0 ? Math.round(100 / rewards.length) : Math.round((value / total) * 100);
    });
    return map;
  }

  function deskLocationId() {
    const select = document.getElementById("desk-location");
    if (select && LOCATIONS[select.value]) return select.value;
    return state.locationId || "crownbridge";
  }

  function rewardOptions(loc, selected) {
    return loc.rewards.map(function (reward) {
      const label = reward.tier === "portrait" ? "Photo Studio — " + reward.title : reward.title;
      return '<option value="' + reward.tier + '"' + (reward.tier === selected ? " selected" : "") + ">" + esc(label) + "</option>";
    }).join("");
  }

  function merchantField(id) {
    const node = document.getElementById(id);
    return node ? node.value : "";
  }

  function updateMerchantBits() {
    const id = deskLocationId();
    const offer = state.merchant[id];
    const loc = LOCATIONS[id];
    if (!offer || !loc) return;
    const place = document.getElementById("merchant-place");
    if (place) place.textContent = loc.name + ", " + loc.where;
    const chance = offer.mode === "chance" || offer.mode === "gift";
    const gift = offer.mode === "gift";
    const probability = document.getElementById("merchant-probability-wrap");
    const rewardWrap = document.getElementById("merchant-reward-wrap");
    const giftWrap = document.getElementById("merchant-gift-wrap");
    const bonusWrap = document.getElementById("merchant-bonus-wrap");
    if (probability) probability.hidden = !chance;
    if (rewardWrap) rewardWrap.hidden = gift;
    if (giftWrap) giftWrap.hidden = !gift;
    if (bonusWrap) bonusWrap.hidden = !gift;
    const count = document.getElementById("merchant-count");
    if (count) count.textContent = "Prizes shared in this browser: " + offer.awarded + " of " + offer.maxPrizes + ".";
    const dates = document.getElementById("merchant-date-note");
    if (dates) dates.hidden = !(offer.start && offer.end && offer.end < offer.start);
    const list = document.getElementById("desk-pulls");
    if (list) {
      list.innerHTML = state.history.length
        ? state.history.map(function (pull) {
          return "<li><strong>" + esc(pull.title) + "</strong> <small>" + esc(pull.location) + "</small></li>";
        }).join("")
        : '<li class="quiet">No pulls yet this visit.</li>';
    }
    const hide = document.getElementById("desk-hide");
    if (hide) hide.checked = !state.deskVisible;
  }

  function fillMerchantForm() {
    if (!demoBody.dataset.ready) return;
    const id = deskLocationId();
    const offer = state.merchant[id] || defaultOffer(id);
    state.merchant[id] = offer;
    const loc = LOCATIONS[id];
    ["reward", "gift", "bonus"].forEach(function (slot) {
      const pick = document.getElementById("merchant-" + slot + "-pick");
      if (!pick) return;
      pick.innerHTML = rewardOptions(loc, offer[slot + "Tier"]);
      pick.value = offer[slot + "Tier"];
    });
    const values = {
      "merchant-name": offer.merchantName,
      "merchant-reward-title": offer.rewardTitle,
      "merchant-reward-detail": offer.rewardDetail,
      "merchant-gift-title": offer.giftTitle,
      "merchant-gift-detail": offer.giftDetail,
      "merchant-bonus-title": offer.bonusTitle,
      "merchant-bonus-detail": offer.bonusDetail,
      "merchant-max": String(offer.maxPrizes),
      "merchant-start": offer.start,
      "merchant-end": offer.end,
    };
    Object.keys(values).forEach(function (key) {
      const node = document.getElementById(key);
      if (node) node.value = values[key];
    });
    demoBody.querySelectorAll('input[name="merchant-mode"]').forEach(function (input) {
      input.checked = input.value === offer.mode;
    });
    const probability = document.getElementById("merchant-probability");
    if (probability) probability.value = String(offer.probability);
    const frequency = document.getElementById("merchant-frequency");
    if (frequency) frequency.value = offer.frequency;
    const enabled = document.getElementById("merchant-enabled");
    if (enabled) enabled.checked = offer.enabled !== false;
    updateMerchantBits();
  }

  function readMerchantForm() {
    const id = deskLocationId();
    const offer = state.merchant[id] || defaultOffer(id);
    const modeInput = demoBody.querySelector('input[name="merchant-mode"]:checked');
    offer.merchantName = merchantField("merchant-name").slice(0, 80);
    offer.rewardTitle = merchantField("merchant-reward-title").slice(0, 140);
    offer.rewardDetail = merchantField("merchant-reward-detail").slice(0, 280);
    offer.giftTitle = merchantField("merchant-gift-title").slice(0, 140);
    offer.giftDetail = merchantField("merchant-gift-detail").slice(0, 280);
    offer.bonusTitle = merchantField("merchant-bonus-title").slice(0, 140);
    offer.bonusDetail = merchantField("merchant-bonus-detail").slice(0, 280);
    offer.rewardTier = merchantField("merchant-reward-pick") || offer.rewardTier;
    offer.giftTier = merchantField("merchant-gift-pick") || offer.giftTier;
    offer.bonusTier = merchantField("merchant-bonus-pick") || offer.bonusTier;
    offer.mode = modeInput ? modeInput.value : offer.mode;
    const probability = Number(merchantField("merchant-probability"));
    if ([10, 20, 50].indexOf(probability) !== -1) offer.probability = probability;
    const maxPrizes = Number(merchantField("merchant-max"));
    if (Number.isFinite(maxPrizes)) offer.maxPrizes = Math.max(0, Math.min(9999, Math.round(maxPrizes)));
    const frequency = merchantField("merchant-frequency");
    if (frequency === "visit" || frequency === "day" || frequency === "promotion") offer.frequency = frequency;
    offer.start = merchantField("merchant-start");
    offer.end = merchantField("merchant-end");
    const enabled = document.getElementById("merchant-enabled");
    offer.enabled = !!(enabled && enabled.checked);
    state.merchant[id] = offer;
    saveMerchant();
    updateMerchantBits();
  }

  function applyPrepared(slot) {
    const id = deskLocationId();
    const loc = LOCATIONS[id];
    const offer = state.merchant[id] || defaultOffer(id);
    const tier = merchantField("merchant-" + slot + "-pick");
    const reward = rewardByTier(loc, tier);
    offer[slot + "Tier"] = reward.tier;
    offer[slot + "Title"] = reward.title;
    offer[slot + "Detail"] = reward.detail;
    state.merchant[id] = offer;
    const title = document.getElementById("merchant-" + slot + "-title");
    const detail = document.getElementById("merchant-" + slot + "-detail");
    if (title) title.value = reward.title;
    if (detail) detail.value = reward.detail;
    saveMerchant();
  }

  function paintDesk() {
    updateMerchantBits();
  }

  function buildDesk() {
    const options = Object.keys(LOCATIONS).map(function (id) {
      const loc = LOCATIONS[id];
      return '<option value="' + loc.id + '">' + esc(loc.name) + " — " + esc(loc.adventure) + "</option>";
    }).join("");
    demoBody.innerHTML =
      '<p class="quiet">This is a simulation of a merchant’s settings. It is not a login, and it does not control a live merchant account. Visitors do not see this panel. In a real service these rules would be checked on a server.</p>' +
      '<div class="desk-card">' +
        '<label class="field">Place<select id="desk-location">' + options + "</select></label>" +
        '<p class="quiet" id="merchant-place"></p>' +
        '<label class="field">Merchant name<input class="field-input" id="merchant-name" autocomplete="off" maxlength="80"></label>' +
        '<label class="checkline"><input type="checkbox" id="merchant-enabled"> Promotion enabled</label>' +
      "</div>" +
      '<div class="desk-card">' +
        "<h3>How rewards are shared</h3>" +
        '<label class="mode-pick"><input type="radio" name="merchant-mode" value="everyone"> <span>Everyone Wins. Every eligible scan receives the reward.</span></label>' +
        '<label class="mode-pick"><input type="radio" name="merchant-mode" value="chance"> <span>Prize by Chance. Only some scans receive the reward. Parking is kept either way.</span></label>' +
        '<label class="mode-pick"><input type="radio" name="merchant-mode" value="gift"> <span>Guaranteed Gift + Lucky Bonus. Everyone receives a small gift. Some also receive an extra prize.</span></label>' +
        '<div id="merchant-probability-wrap"><label class="field">Winning probability<select id="merchant-probability"><option value="10">10%</option><option value="20">20%</option><option value="50">50%</option></select></label></div>' +
      "</div>" +
      '<div class="desk-card" id="merchant-reward-wrap">' +
        "<h3>Reward</h3>" +
        '<label class="field">Prepared reward<select id="merchant-reward-pick"></select></label>' +
        '<label class="field">Title<input class="field-input" id="merchant-reward-title" autocomplete="off" maxlength="140"></label>' +
        '<label class="field">Description<textarea class="field-input" id="merchant-reward-detail" maxlength="280"></textarea></label>' +
      "</div>" +
      '<div class="desk-card" id="merchant-gift-wrap">' +
        "<h3>Guaranteed gift</h3>" +
        '<label class="field">Prepared gift<select id="merchant-gift-pick"></select></label>' +
        '<label class="field">Title<input class="field-input" id="merchant-gift-title" autocomplete="off" maxlength="140"></label>' +
        '<label class="field">Description<textarea class="field-input" id="merchant-gift-detail" maxlength="280"></textarea></label>' +
      "</div>" +
      '<div class="desk-card" id="merchant-bonus-wrap">' +
        "<h3>Lucky bonus</h3>" +
        '<label class="field">Prepared bonus<select id="merchant-bonus-pick"></select></label>' +
        '<label class="field">Title<input class="field-input" id="merchant-bonus-title" autocomplete="off" maxlength="140"></label>' +
        '<label class="field">Description<textarea class="field-input" id="merchant-bonus-detail" maxlength="280"></textarea></label>' +
      "</div>" +
      '<div class="desk-card">' +
        "<h3>Limits</h3>" +
        '<p class="quiet">These limits are stored only in this browser. They are a picture of future rules, not a live inventory.</p>' +
        '<label class="field">Maximum prizes<input class="field-input" id="merchant-max" type="number" min="0" max="9999"></label>' +
        '<p class="quiet" id="merchant-count"></p>' +
        '<label class="field">One reward<select id="merchant-frequency"><option value="visit">Each scan</option><option value="day">Once a day</option><option value="promotion">Once for this promotion</option></select></label>' +
        '<label class="field">Starts<input class="field-input" id="merchant-start" type="date"></label>' +
        '<label class="field">Ends<input class="field-input" id="merchant-end" type="date"></label>' +
        '<p class="quiet" id="merchant-date-note" hidden>The end date is before the start, so the promotion stays closed.</p>' +
        '<button type="button" class="cta cta-secondary" id="merchant-clear">Reset this promotion’s count</button>' +
      "</div>" +
      '<div class="desk-card">' +
        '<div class="desk-actions">' +
          '<button type="button" class="cta cta-primary" id="desk-play">Preview the adventure</button>' +
          '<button type="button" class="cta cta-secondary" id="desk-reward">Preview what a visitor receives</button>' +
          '<button type="button" class="cta cta-secondary" id="desk-studio">Open the Photo Studio</button>' +
        "</div>" +
        '<p class="quiet">The preview uses these rules, including the prize limit. It does not save a parking pass. The Photo Studio shortcut skips the promotion.</p>' +
      "</div>" +
      '<div class="desk-card">' +
        "<h3>Recent reveals</h3>" +
        '<ul class="pulls" id="desk-pulls"></ul>' +
      "</div>" +
      '<div class="desk-card">' +
        '<label class="checkline"><input type="checkbox" id="desk-hide"> Hide the Demo button</label>' +
        '<p class="quiet">Five taps on the title bring the desk back.</p>' +
        '<button type="button" class="cta cta-secondary" id="desk-welcome">Return to the welcome</button>' +
        '<button type="button" class="cta cta-secondary ghost-danger" id="desk-reset">Reset the demonstration</button>' +
      "</div>";
    demoBody.dataset.ready = "yes";

    document.getElementById("desk-location").addEventListener("change", fillMerchantForm);
    demoBody.addEventListener("input", function (event) {
      if (event.target.id === "desk-location") return;
      readMerchantForm();
    });
    demoBody.addEventListener("change", function (event) {
      const pick = event.target.closest("[id$='-pick']");
      if (!pick || pick.id.indexOf("merchant-") !== 0) return;
      const slot = pick.id.replace("merchant-", "").replace("-pick", "");
      if (slot === "reward" || slot === "gift" || slot === "bonus") applyPrepared(slot);
    });
    document.getElementById("merchant-clear").addEventListener("click", function () {
      const id = deskLocationId();
      if (state.merchant[id]) state.merchant[id].awarded = 0;
      delete state.claims[id];
      saveMerchant();
      saveClaims();
      updateMerchantBits();
    });
    document.getElementById("desk-hide").addEventListener("change", function (event) {
      state.deskVisible = !event.target.checked;
      saveDesk();
      render();
    });
    document.getElementById("desk-play").addEventListener("click", function () {
      closeDesk();
      enter(deskLocationId());
    });
    document.getElementById("desk-reward").addEventListener("click", function () {
      const id = deskLocationId();
      const loc = LOCATIONS[id];
      readMerchantForm();
      state.locationId = id;
      const reward = resolveVisit(loc);
      state.reward = reward;
      state.coupon = reward.tier === "none" ? null : couponFor(id);
      state.transformId = loc.studio && loc.studio[0] ? loc.studio[0].id : null;
      rememberPull(loc, reward);
      playReveal(reward.tier === "none" ? "consolation" : reward.tier);
      updateMerchantBits();
      closeDesk();
      go("reward", "push");
    });
    document.getElementById("desk-studio").addEventListener("click", function () {
      const id = deskLocationId();
      const loc = LOCATIONS[id];
      const reward = rewardByTier(loc, "portrait");
      state.locationId = id;
      state.reward = {
        tier: reward.tier,
        title: reward.title,
        story: reward.story,
        detail: reward.detail,
        merchant: reward.merchant,
        ribbon: reward.ribbon,
        kind: "prize",
      };
      state.coupon = couponFor(id);
      state.transformId = loc.studio && loc.studio[0] ? loc.studio[0].id : null;
      closeDesk();
      go("studio", "push");
    });
    document.getElementById("desk-welcome").addEventListener("click", function () {
      closeDesk();
      state.locationId = null;
      state.reward = null;
      state.coupon = null;
      go("welcome", "push");
    });
    document.getElementById("desk-reset").addEventListener("click", resetAll);
    fillMerchantForm();
  }


  function openDesk() {
    closePass();
    const select = document.getElementById("desk-location");
    if (select) select.value = state.locationId || select.value || "crownbridge";
    fillMerchantForm();
    if (!demoDialog.open) demoDialog.showModal();
  }

  function closeDesk() {
    if (demoDialog.open) demoDialog.close();
  }

  function resetAll() {
    window.clearTimeout(openTimer);
    const fresh = freshDesk();
    state.sound = fresh.sound;
    state.mode = fresh.mode;
    state.weights = fresh.weights;
    state.deskVisible = true;
    state.history = [];
    generation += 1;
    sessionStorage.setItem("freds-adventure-gen", String(generation));
    state.locationId = null;
    state.country = null;
    localStorage.removeItem(COUNTRY_KEY);
    clearPhoto();
    resetStudioPath();
    state.reward = null;
    state.coupon = null;
    state.pass = null;
    state.parkingCoupon = null;
    state.collection = [];
    state.merchant = {};
    state.claims = {};
    state.transformId = null;
    state.phase = "scan";
    state.busy = false;
    state.screen = "welcome";
    localStorage.removeItem(PASS_KEY);
    localStorage.removeItem(MAGIC_KEY);
    localStorage.removeItem(MERCHANT_KEY);
    localStorage.removeItem(CLAIMS_KEY);
    state.merchant = loadMerchant();
    state.claims = loadClaims();
    saveDesk();
    sessionStorage.removeItem(VISIT_KEY);
    seedHistory("welcome");
    closeDesk();
    closePass();
    render();
    fillMerchantForm();
  }

  function onScreenClick(event) {
    const target = event.target.closest("[data-action]");
    if (!target || state.busy && target.dataset.action !== "scan" && target.dataset.action !== "open") return;
    const action = target.dataset.action;
    if (action === "begin") begin();
    else if (action === "country") selectCountry(target.dataset.country);
    else if (action === "change-country") go("country", "push");
    else if (action === "adventures") go("choose", "push");
    else if (action === "enter") enter(target.dataset.location);
    else if (action === "scan") scan();
    else if (action === "mystery") {
      state.phase = "sealed";
      go("mystery", "push");
    } else if (action === "open") openRelic();
    else if (action === "again") tryAgain();
    else if (action === "scorecard") {
      state.locationId = "crownbridge";
      go("scorecard", "push");
    } else if (action === "scorecard-back") {
      if (history.length > 1) history.back();
      else go("discover", "replace");
    }
    else if (action === "studio") {
      const loc = currentPlace();
      clearPhoto();
      resetStudioPath();
      if (!state.transformId && loc && loc.studio[0]) state.transformId = loc.studio[0].id;
      go("studio", "push");
    } else if (action === "guest") {
      const asked = target.dataset.guest;
      const next = asked === "child" || asked === "magic" ? asked : asked === "gate" ? null : "adult";
      if (next !== state.studioGuest) clearPhoto();
      state.studioGuest = next;
      state.childStep = "intro";
      state.childConcept = null;
      state.magicStep = "intro";
      state.magicKind = null;
      state.magicId = null;
      state.magicFresh = false;
      render();
    } else if (action === "pick-photo") pickPhoto(target.dataset.capture);
    else if (action === "remove-photo") {
      clearPhoto();
      if (state.studioGuest === "child" || state.studioGuest === "magic") {
        state.childStep = "intro";
        state.childConcept = null;
        state.magicStep = "intro";
        state.magicKind = null;
        state.magicFresh = false;
      }
      render();
    } else if (action === "object-ok") {
      if (state.faceCheck === "pending" || state.faceCheck === "face" || !state.photoUrl) return;
      if (state.studioGuest === "magic") {
        state.magicStep = "reveal";
        state.magicKind = null;
        render();
        return;
      }
      state.childStep = "concepts";
      render();
    } else if (action === "object-person") {
      state.faceCheck = "person";
      state.childStep = "rejected";
      state.magicStep = "rejected";
      render();
    } else if (action === "magic-reveal") revealMagic();
    else if (action === "magic-collection") {
      clearPhoto();
      state.studioGuest = "magic";
      state.magicStep = "collection";
      state.magicFresh = false;
      render();
    } else if (action === "magic-again") {
      clearPhoto();
      state.studioGuest = "magic";
      state.magicStep = "intro";
      state.magicKind = null;
      state.magicId = null;
      state.magicFresh = false;
      render();
    } else if (action === "magic-open") {
      const found = state.collection.find(function (item) { return item.id === target.dataset.id; });
      if (!found) return;
      clearPhoto();
      state.magicKind = found.kind;
      state.magicId = found.id;
      state.magicFresh = false;
      state.magicStep = "result";
      render();
    } else if (action === "magic-drop") {
      saveMagic(state.collection.filter(function (item) { return item.id !== target.dataset.id; }));
      if (state.magicId === target.dataset.id) {
        state.magicId = null;
        state.magicKind = null;
        state.magicStep = "collection";
      }
      render();
    } else if (action === "concept") {
      state.childConcept = target.dataset.concept;
      state.childStep = "souvenir";
      render();
    } else if (action === "child-concepts") {
      state.childStep = "concepts";
      render();
    } else if (action === "transform") {
      state.transformId = target.dataset.style;
      render();
    }
  }

  function pickPhoto(capture) {
    const input = document.getElementById("photo-input");
    if (!input) return;
    if (capture) input.setAttribute("capture", capture);
    else input.removeAttribute("capture");
    input.click();
  }

  function bindWipe() {
    screenEl.querySelectorAll(".wipe").forEach(function (wipe) {
      const range = wipe.querySelector(".wipe-range");
      if (!range) return;
      const apply = function () {
        wipe.style.setProperty("--wipe", range.value + "%");
      };
      range.addEventListener("input", apply);
      apply();
    });
  }

  function bindStudio() {
    const input = document.getElementById("photo-input");
    if (!input) return;
    input.addEventListener("change", function () {
      const file = input.files && input.files[0];
      if (!file || file.type.indexOf("image/") !== 0) return;
      clearPhoto();
      state.photoUrl = URL.createObjectURL(file);
      state.photoName = file.name || "Selected photo";
      if (state.studioGuest !== "child" && state.studioGuest !== "magic") {
        render();
        return;
      }
      state.childStep = "review";
      state.magicStep = "review";
      state.childConcept = null;
      state.magicKind = null;
      state.magicFresh = false;
      if (typeof window.FaceDetector !== "function") {
        state.faceCheck = "unavailable";
        render();
        return;
      }
      state.faceCheck = "pending";
      const token = photoToken;
      render();
      window.setTimeout(function () {
        if (token !== photoToken || state.faceCheck !== "pending") return;
        state.faceCheck = "unavailable";
        render();
      }, 4000);
      detectFaces(state.photoUrl).then(function (result) {
        if (token !== photoToken || (state.studioGuest !== "child" && state.studioGuest !== "magic")) return;
        state.faceCheck = result.status;
        if (result.status === "face") {
          state.childStep = "rejected";
          state.magicStep = "rejected";
        }
        render();
      });
    });
  }

  function detectFaces(url) {
    return new Promise(function (resolve) {
      if (typeof window.FaceDetector !== "function") {
        resolve({ status: "unavailable" });
        return;
      }
      const img = new Image();
      img.onload = function () {
        try {
          const detector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 5 });
          detector.detect(img).then(function (faces) {
            resolve({ status: faces && faces.length ? "face" : "clear" });
          }).catch(function () {
            resolve({ status: "unavailable" });
          });
        } catch (err) {
          resolve({ status: "unavailable" });
        }
      };
      img.onerror = function () {
        resolve({ status: "unavailable" });
      };
      img.src = url;
    });
  }

  function bootFromStore() {
    const desk = loadDesk();
    state.sound = desk.sound;
    state.mode = desk.mode;
    state.weights = desk.weights;
    state.deskVisible = desk.deskVisible;
    const storedGen = Number(sessionStorage.getItem("freds-adventure-gen"));
    if (Number.isFinite(storedGen) && storedGen > 0) generation = storedGen;
    const visit = loadVisit();
    state.country = loadCountry();
    const parts = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
    let screen = "welcome";
    const placed = ["discover", "parking", "mystery", "reward", "studio"];
    if (parts[0] === "country") screen = "country";
    if (parts[0] === "choose") screen = state.country ? "choose" : "country";
    if (placed.indexOf(parts[0]) !== -1 && LOCATIONS[parts[1]]) {
      screen = parts[0];
      state.locationId = parts[1];
      const inferred = countryOf(LOCATIONS[parts[1]]);
      if (state.country !== inferred) saveCountry(inferred);
    }
    if (parts[0] === "scorecard") {
      screen = "scorecard";
      state.locationId = "crownbridge";
      if (state.country !== "england") saveCountry("england");
    }
    if (visit && visit.history) state.history = visit.history.slice(0, 6);
    state.merchant = loadMerchant();
    state.claims = loadClaims();
    state.pass = loadPass();
    state.collection = loadMagic();
    if (!state.pass && visit && visit.parkingCoupon && LOCATIONS[visit.locationId]) {
      const migrated = { locationId: visit.locationId, code: String(visit.parkingCoupon) };
      if (/^DEMO-[A-Z]{2}-[A-Z0-9]{4}$/.test(migrated.code)) {
        state.pass = migrated;
        savePass(state.pass);
      }
    }
    if (state.pass) state.parkingCoupon = state.pass.code;
    const place = currentPlace();
    if ((screen === "reward" || screen === "studio") && visit && visit.locationId === state.locationId && visit.reward) {
      state.reward = visit.reward;
      state.coupon = visit.coupon || null;
    }
    if ((screen === "reward" || screen === "studio") && !state.reward) {
      screen = state.locationId ? "discover" : "choose";
    }
    if (screen === "studio" && !rewardOpensStudio(state.reward)) screen = "reward";
    if (place && place.studio[0] && !state.transformId) state.transformId = place.studio[0].id;
    if (screen === "scorecard") {
      seedHistory("discover");
      go("scorecard", "push");
    } else {
      seedHistory(screen);
    }
    state.booted = true;
  }

  backBtn.addEventListener("click", function () {
    if (state.busy) return;
    if (state.screen === "studio" && state.studioGuest === "magic" && state.magicStep !== "intro") {
      if (state.magicStep === "collection") {
        clearPhoto();
        resetStudioPath();
      } else if (state.magicStep === "result") {
        state.magicStep = "collection";
        state.magicFresh = false;
      } else {
        state.magicStep = "intro";
        state.magicKind = null;
      }
      render();
      return;
    }
    if (state.screen === "studio" && state.studioGuest === "child" && state.childStep !== "intro") {
      if (state.childStep === "souvenir") state.childStep = "concepts";
      else if (state.childStep === "concepts") state.childStep = state.photoUrl ? "review" : "intro";
      else state.childStep = "intro";
      render();
      return;
    }
    if (state.screen === "studio" && state.studioGuest) {
      clearPhoto();
      resetStudioPath();
      render();
      return;
    }
    history.back();
  });
  soundBtn.addEventListener("click", function () {
    state.sound = !state.sound;
    saveDesk();
    if (state.sound) playTone(660, 0, 0.12, "triangle", 0.05);
    render();
  });
  demoOpen.addEventListener("click", openDesk);
  document.getElementById("demo-close").addEventListener("click", closeDesk);
  passBtn.addEventListener("click", function () { showPass("certificate"); });
  document.getElementById("pass-close").addEventListener("click", closePass);
  passDialog.addEventListener("click", function (event) {
    const target = event.target.closest("[data-pass]");
    if (!target) return;
    if (target.dataset.pass === "proof" || target.dataset.pass === "certificate") showPass(target.dataset.pass);
  });
  passDialog.addEventListener("close", function () {
    passBtn.setAttribute("aria-expanded", "false");
  });
  document.getElementById("wordmark").addEventListener("click", function () {
    if (state.deskVisible) return;
    const now = Date.now();
    wordmarkTaps = wordmarkTaps.filter(function (stamp) { return now - stamp < 4000; });
    wordmarkTaps.push(now);
    if (wordmarkTaps.length >= 5) {
      wordmarkTaps = [];
      state.deskVisible = true;
      saveDesk();
      render();
      openDesk();
    }
  });
  window.addEventListener("popstate", function (event) {
    window.clearTimeout(openTimer);
    const item = event.state;
    if (!item || !item.freds || item.gen !== generation) {
      state.screen = "welcome";
      state.locationId = null;
      clearPhoto();
      resetStudioPath();
      state.reward = null;
      state.coupon = null;
      state.pass = loadPass();
      state.collection = loadMagic();
      state.parkingCoupon = state.pass ? state.pass.code : null;
      state.transformId = null;
      state.phase = "scan";
      state.busy = false;
      history.replaceState(entry(), "", "#/");
    } else {
      applyEntry(item);
    }
    render();
  });
  screenEl.addEventListener("click", onScreenClick);

  bootFromStore();
  buildDesk();
  render();
})();
