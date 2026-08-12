const pptxgen = require("pptxgenjs");

const P = {
  indigo: "1B2A4A",
  ink:    "0F1A2E",
  cream:  "F2EFE9",
  paper:  "FFFFFF",
  terra:  "C1553A",
  sage:   "6E8F8A",
  grey:   "5A6472",
  light:  "9AA3B0",
  card:   "E8E4DA",
};

const HEAD = "Cambria";
const BODY = "Calibri";
const MONO = "Courier New";

const W = 13.3, H = 7.5, M = 0.65;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Kyros";
pres.title = "LOOM - Cross-Portfolio Sourcing Intelligence";

const sh = () => ({ type: "outer", color: "1B2A4A", blur: 12, offset: 3, angle: 90, opacity: 0.12 });

// dark slide
function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: P.indigo };
  return s;
}
function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: P.paper };
  return s;
}

function title(s, text, opts = {}) {
  s.addText(text, {
    x: M, y: opts.y || 0.5, w: W - M * 2, h: 0.85,
    fontFace: HEAD, fontSize: opts.size || 38, bold: true,
    color: opts.color || P.indigo, align: "left", margin: 0,
  });
}

function kicker(s, text, color) {
  s.addText(text.toUpperCase(), {
    x: M, y: 0.28, w: W - M * 2, h: 0.3,
    fontFace: BODY, fontSize: 11, bold: true, charSpacing: 2.2,
    color: color || P.terra, align: "left", margin: 0,
  });
}

function numCircle(s, n, x, y, color) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.42, h: 0.42, fill: { color: color || P.terra }, line: { width: 0 },
  });
  s.addText(String(n), {
    x, y, w: 0.42, h: 0.42, fontFace: BODY, fontSize: 15, bold: true,
    color: "FFFFFF", align: "center", valign: "middle", margin: 0,
  });
}

function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: fill || P.cream }, line: { width: 0 }, shadow: sh(),
  });
}

/* ============================ 1  TITLE ============================ */
{
  const s = darkSlide();
  s.addText("LOOM", {
    x: M, y: 1.9, w: 7.5, h: 1.5, fontFace: HEAD, fontSize: 96, bold: true,
    color: P.paper, margin: 0, charSpacing: 4,
  });
  s.addText("A cross-portfolio sourcing intelligence layer", {
    x: M, y: 3.35, w: 8.2, h: 0.5, fontFace: BODY, fontSize: 22, color: P.card, margin: 0,
  });
  s.addText("30x the buying power.  1x the negotiating leverage.", {
    x: M, y: 4.0, w: 8.6, h: 0.5, fontFace: HEAD, fontSize: 21, italic: true,
    color: P.terra, margin: 0,
  });
  s.addText("Think9 AI & Intelligence Challenge   ·   Track 2: Cross-Portfolio Supply Chain & Sourcing", {
    x: M, y: 6.5, w: 10, h: 0.35, fontFace: BODY, fontSize: 12, color: P.light, margin: 0,
  });

  card(s, 9.05, 1.9, 3.6, 2.0, P.ink);
  s.addText("“AI will redefine agility for business — making paths to growth speedy and seamless.”", {
    x: 9.35, y: 2.15, w: 3.0, h: 1.1, fontFace: HEAD, fontSize: 14, italic: true,
    color: P.card, margin: 0, valign: "top",
  });
  s.addText("Think9, Principles", {
    x: 9.35, y: 3.4, w: 3.0, h: 0.3, fontFace: BODY, fontSize: 10.5,
    color: P.sage, bold: true, margin: 0,
  });
  s.addNotes("Open on their own stated principle. The framing is agility and speed, not cost cutting - which is why the north-star metric is cycle time.");
}

/* ============================ 2  WHY NOW ============================ */
{
  const s = lightSlide();
  kicker(s, "Why now");
  title(s, "Packaging costs are spiking this quarter");

  card(s, M, 1.75, 5.5, 2.75, P.indigo);
  s.addText("15–25%", {
    x: M + 0.4, y: 2.15, w: 4.7, h: 1.3, fontFace: HEAD, fontSize: 76, bold: true,
    color: P.terra, margin: 0,
  });
  s.addText("increase in packaging input costs, 2026", {
    x: M + 0.4, y: 3.5, w: 4.7, h: 0.9, fontFace: BODY, fontSize: 16,
    color: P.card, margin: 0,
  });

  const pts = [
    ["Crude-linked inputs", "up 20–25% against pre-conflict levels"],
    ["FMCG packaging specifically", "up 15–20%"],
    ["D2C margins", "squeezed simultaneously on raw materials, packaging, logistics and manufacturing"],
  ];
  let y = 1.85;
  pts.forEach(([h, d], i) => {
    numCircle(s, i + 1, 6.5, y, P.terra);
    s.addText(h, {
      x: 7.15, y: y - 0.03, w: 5.4, h: 0.32, fontFace: BODY, fontSize: 15, bold: true,
      color: P.indigo, margin: 0,
    });
    s.addText(d, {
      x: 7.15, y: y + 0.3, w: 5.4, h: 0.62, fontFace: BODY, fontSize: 13.5,
      color: P.grey, margin: 0,
    });
    y += 1.12;
  });

  s.addText("This is margin defence against a dated, live shock — not a theoretical efficiency gain.", {
    x: M, y: 5.45, w: W - M * 2, h: 0.4, fontFace: HEAD, fontSize: 17, italic: true,
    color: P.indigo, margin: 0,
  });
  s.addText("Sources: Packaging South Asia; Inc42, “Boxed In: The War Shock For D2C”", {
    x: M, y: 6.2, w: 9, h: 0.3, fontFace: BODY, fontSize: 10, color: P.light, margin: 0,
  });
}

/* ============================ 3  BOTTLENECK ============================ */
{
  const s = lightSlide();
  kicker(s, "The bottleneck");
  title(s, "Scale that exists on paper, not in the room");

  s.addText("Each brand sources independently. That is the correct thing for each brand to do.", {
    x: M, y: 1.6, w: 11.6, h: 0.35, fontFace: BODY, fontSize: 15.5, color: P.grey, margin: 0,
  });

  card(s, M, 2.25, 5.6, 1.5, P.cream);
  s.addText("30x", { x: M + 0.35, y: 2.45, w: 1.5, h: 0.9, fontFace: HEAD, fontSize: 46, bold: true, color: P.sage, margin: 0 });
  s.addText("the buying power of any single brand", { x: M + 2.0, y: 2.6, w: 3.4, h: 0.7, fontFace: BODY, fontSize: 14, color: P.indigo, margin: 0, valign: "middle" });

  card(s, M, 3.95, 5.6, 1.5, P.cream);
  s.addText("1x", { x: M + 0.35, y: 4.15, w: 1.5, h: 0.9, fontFace: HEAD, fontSize: 46, bold: true, color: P.terra, margin: 0 });
  s.addText("the negotiating leverage at the table", { x: M + 2.0, y: 4.3, w: 3.4, h: 0.7, fontFace: BODY, fontSize: 14, color: P.indigo, margin: 0, valign: "middle" });

  card(s, 6.75, 2.25, 5.9, 3.2, P.indigo);
  s.addText("Because at the moment a brand negotiates, nobody in the building can see what the other brands pay for the same physical object.", {
    x: 7.15, y: 2.6, w: 5.1, h: 1.6, fontFace: HEAD, fontSize: 20, color: P.paper, margin: 0, valign: "top",
  });
  s.addText("Not a discipline problem. Not solved by a shared spreadsheet. And it gets monotonically worse as the portfolio grows.", {
    x: 7.15, y: 4.35, w: 5.1, h: 0.9, fontFace: BODY, fontSize: 13.5, color: P.card, margin: 0,
  });

  s.addText("Built at 11 brands. Designed for 30+.", {
    x: M, y: 5.9, w: 11.6, h: 0.4, fontFace: HEAD, fontSize: 17, italic: true, color: P.terra, margin: 0,
  });
  s.addNotes("Do not correct their 30+ figure. Frame it as designing ahead of the growth curve.");
}

/* ============================ 4  FIVE NAMES  (hero) ============================ */
{
  const s = lightSlide();
  kicker(s, "The hard problem");
  title(s, "One bottle. Five names.");

  const names = [
    ["50ml Amber Glass Bottle, 20mm neck", "Neude  ·  PDF"],
    ["Amber Boston Round 50 ML (20/400)", "Beauty by Bie  ·  PDF"],
    ["GB-AMB-50-20N", "Panchamrit  ·  WhatsApp"],
    ["Glass bottle - amber - 50cc - neck 20mm - w/o cap", "Neude  ·  email"],
    ["एम्बर ग्लास बॉटल 50ml 20mm", "Goodbug  ·  WhatsApp"],
  ];
  let y = 1.65;
  names.forEach(([n, src]) => {
    card(s, M, y, 7.4, 0.72, P.cream);
    s.addText(n, {
      x: M + 0.3, y: y + 0.06, w: 5.3, h: 0.34, fontFace: MONO, fontSize: 12.5,
      color: P.indigo, margin: 0,
    });
    s.addText(src, {
      x: M + 0.3, y: y + 0.4, w: 5.3, h: 0.26, fontFace: BODY, fontSize: 10.5,
      color: P.grey, margin: 0,
    });
    y += 0.85;
  });

  card(s, 8.5, 1.65, 4.15, 3.95, P.indigo);
  s.addText("ONE PHYSICAL OBJECT", {
    x: 8.8, y: 2.0, w: 3.55, h: 0.3, fontFace: BODY, fontSize: 11, bold: true,
    charSpacing: 1.5, color: P.sage, margin: 0,
  });
  s.addText("You cannot combine orders for things you cannot prove are the same thing.", {
    x: 8.8, y: 2.5, w: 3.55, h: 1.5, fontFace: HEAD, fontSize: 19, color: P.paper, margin: 0, valign: "top",
  });
  s.addText("So the bottleneck is not price comparison. It is SKU identity resolution — and that is what a script cannot do and a model against a spec graph can.", {
    x: 8.8, y: 4.1, w: 3.55, h: 1.3, fontFace: BODY, fontSize: 12.5, color: P.card, margin: 0,
  });

  s.addText("Nobody wrote these to be inconsistent. They arrived from four vendors across PDF, email and WhatsApp.", {
    x: M, y: 6.0, w: 11.6, h: 0.4, fontFace: BODY, fontSize: 14, italic: true, color: P.grey, margin: 0,
  });
  s.addNotes("This is the money slide. Land it slowly. Everything downstream depends on resolving identity first.");
}

/* ============================ 5  WHY AI ============================ */
{
  const s = lightSlide();
  kicker(s, "Earning the AI");
  title(s, "Why not a script, and why not a hire");

  const cols = [
    ["Could a script do it?", "No.", "There is no fixed input schema. ~200 vendors, each with their own quote layout, new ones onboarding constantly. Any regex-based parser is obsolete within a quarter."],
    ["Could a team do it?", "Too slow.", "3–4 FTE of tedious, error-prone work — and quotes expire in 15–30 days. Value exists only inside that window. A human queue introduces exactly the latency that destroys it."],
    ["Why agentic?", "It is a loop.", "Low-confidence extraction must trigger a clarifying action. Resolution must decide match-or-create against growing state. Detection runs continuously as quotes arrive and lapse."],
  ];
  cols.forEach(([q, a, d], i) => {
    const x = M + i * 4.05;
    card(s, x, 1.75, 3.75, 3.35, P.cream);
    s.addText(q, {
      x: x + 0.3, y: 2.0, w: 3.15, h: 0.35, fontFace: BODY, fontSize: 13, bold: true,
      color: P.grey, margin: 0,
    });
    s.addText(a, {
      x: x + 0.3, y: 2.4, w: 3.15, h: 0.6, fontFace: HEAD, fontSize: 30, bold: true,
      color: P.terra, margin: 0,
    });
    s.addText(d, {
      x: x + 0.3, y: 3.15, w: 3.15, h: 2.3, fontFace: BODY, fontSize: 13,
      color: P.indigo, margin: 0, valign: "top",
    });
  });

  s.addText("Perceive → reason → act → observe, against persistent state. That is an agent, not a transform.", {
    x: M, y: 5.45, w: 11.6, h: 0.4, fontFace: HEAD, fontSize: 17, italic: true, color: P.indigo, margin: 0,
  });
}

/* ============================ 6  MOQ PENALTY ============================ */
{
  const s = lightSlide();
  kicker(s, "The money");
  title(s, "A surcharge we pay only because we order apart", { size: 34 });

  card(s, M, 1.7, 12.0, 1.05, P.indigo);
  s.addText("“Suppliers may accept 500 units if buyers agree to pay 20–30% more per unit.”", {
    x: M + 0.4, y: 1.85, w: 10.0, h: 0.4, fontFace: HEAD, fontSize: 19, italic: true,
    color: P.paper, margin: 0,
  });
  s.addText("Industry reporting on 2026 packaging procurement", {
    x: M + 0.4, y: 2.28, w: 8, h: 0.3, fontFace: BODY, fontSize: 11, color: P.sage, margin: 0,
  });

  card(s, M, 3.05, 5.85, 1.95, P.cream);
  s.addText("Ordering separately", { x: M + 0.35, y: 3.25, w: 5.1, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: P.grey, margin: 0 });
  s.addText("4 ×", { x: M + 0.35, y: 3.6, w: 1.6, h: 0.85, fontFace: HEAD, fontSize: 48, bold: true, color: P.terra, margin: 0 });
  s.addText("Four brands, each below MOQ, each paying the sub-MOQ premium — four separate times.", {
    x: M + 1.85, y: 3.65, w: 3.6, h: 1.2, fontFace: BODY, fontSize: 13, color: P.indigo, margin: 0, valign: "top",
  });

  card(s, 6.8, 3.05, 5.85, 1.95, P.cream);
  s.addText("Ordering together", { x: 7.15, y: 3.25, w: 5.1, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: P.grey, margin: 0 });
  s.addText("0 ×", { x: 7.15, y: 3.6, w: 1.6, h: 0.85, fontFace: HEAD, fontSize: 48, bold: true, color: P.sage, margin: 0 });
  s.addText("One consolidated order clears the MOQ. The premium does not apply at all.", {
    x: 8.65, y: 3.65, w: 3.6, h: 1.2, fontFace: BODY, fontSize: 13, color: P.indigo, margin: 0, valign: "top",
  });

  s.addText("The saving is not “we negotiated harder.” It is “we stopped paying a surcharge that existed only because we ordered separately.”", {
    x: M, y: 5.35, w: 11.9, h: 0.8, fontFace: HEAD, fontSize: 19, color: P.indigo, margin: 0,
  });
  s.addText("Arithmetic, not skill — which is why it is defensible. Negotiating leverage is upside on top.", {
    x: M, y: 6.15, w: 11.9, h: 0.35, fontFace: BODY, fontSize: 13, italic: true, color: P.grey, margin: 0,
  });
  s.addNotes("Know this cold. It is the claim the whole pitch rests on.");
}

/* ============================ 7  ARCHITECTURE ============================ */
{
  const s = lightSlide();
  kicker(s, "System architecture");
  title(s, "Six layers, three human gates");

  const layers = [
    ["L0", "INGEST", "Email, WhatsApp, file drop, ERP export — stored immutably with provenance", ""],
    ["L1", "EXTRACTION", "Line items with per-field confidence and source-span citation. Never infers a missing value", "confidence routing"],
    ["L2", "RESOLUTION", "Line item → canonical SKU. Attribute normalization, tolerance rules, fuzzy fallback", "GATE 1"],
    ["L3", "SPEC GRAPH", "Canonical SKUs, vendors keyed on GSTIN, brands, price history, procurement mode", ""],
    ["L4", "OPPORTUNITY", "Five always-on detectors: bundling, price outlier, concentration, lead-time drift, expiry", ""],
    ["L5", "BRIEF", "The negotiation packet a human takes into the call, with reasoning shown", ""],
    ["L6", "DECISION", "Category manager approves. Outcome writes back — the graph learns", "GATES 2 & 3"],
  ];
  let y = 1.6;
  layers.forEach(([id, name, desc, gate]) => {
    card(s, M, y, 11.9, 0.66, gate ? P.card : P.cream);
    s.addText(id, {
      x: M + 0.28, y: y + 0.15, w: 0.6, h: 0.36, fontFace: MONO, fontSize: 14, bold: true,
      color: P.terra, margin: 0,
    });
    s.addText(name, {
      x: M + 0.95, y: y + 0.15, w: 1.85, h: 0.36, fontFace: BODY, fontSize: 13.5, bold: true,
      color: P.indigo, margin: 0,
    });
    s.addText(desc, {
      x: M + 2.85, y: y + 0.16, w: 7.0, h: 0.36, fontFace: BODY, fontSize: 12,
      color: P.grey, margin: 0,
    });
    if (gate) {
      s.addText(gate.toUpperCase(), {
        x: M + 9.9, y: y + 0.17, w: 1.85, h: 0.32, fontFace: BODY, fontSize: 10, bold: true,
        color: P.terra, align: "right", margin: 0, charSpacing: 0.8,
      });
    }
    y += 0.74;
  });

  s.addText("The agent never commits spend and never contacts a vendor.", {
    x: M, y: 6.85, w: 11.9, h: 0.35, fontFace: HEAD, fontSize: 15, italic: true, color: P.indigo, margin: 0,
  });
}

/* ============================ 8  COMPOUNDING ============================ */
{
  const s = lightSlide();
  kicker(s, "Why it must be central");
  title(s, "Value that compounds instead of adding up");

  card(s, M, 1.8, 5.75, 2.0, P.cream);
  s.addText("Most AI proposals", { x: M + 0.35, y: 2.0, w: 5.0, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: P.grey, margin: 0 });
  s.addText("Linear", { x: M + 0.35, y: 2.32, w: 5.0, h: 0.5, fontFace: HEAD, fontSize: 27, bold: true, color: P.light, margin: 0 });
  s.addText("Help one team do one thing faster. Deploy to 30 brands, get 30 units of value, pay 30 units of cost.", {
    x: M + 0.35, y: 2.9, w: 5.0, h: 0.75, fontFace: BODY, fontSize: 13, color: P.indigo, margin: 0,
  });

  card(s, M, 4.0, 5.75, 2.35, P.indigo);
  s.addText("LOOM", { x: M + 0.35, y: 4.2, w: 5.0, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: P.sage, margin: 0 });
  s.addText("Superlinear", { x: M + 0.35, y: 4.52, w: 5.0, h: 0.5, fontFace: HEAD, fontSize: 27, bold: true, color: P.terra, margin: 0 });
  s.addText("Every quote any brand receives makes the graph denser — which makes every future negotiation across all other brands better informed.", {
    x: M + 0.35, y: 5.1, w: 5.0, h: 1.0, fontFace: BODY, fontSize: 13, color: P.card, margin: 0,
  });

  card(s, 6.95, 1.8, 5.7, 4.55, P.cream);
  s.addText("The next brand starts at portfolio-best", {
    x: 7.3, y: 2.15, w: 5.0, h: 0.7, fontFace: HEAD, fontSize: 23, bold: true, color: P.indigo, margin: 0,
  });
  const bullets = [
    "Brand 12 does not negotiate up from scratch — it inherits portfolio-best pricing, qualified vendors and known lead times on day one.",
    "Think9 grows partly by acquisition. An acquired brand arrives with its own vendor list and its own naming conventions — canonical resolution is exactly the tool that absorbs it.",
    "This only works if the system sits at the centre. Which is what “centralized intelligence layer” asks for.",
  ];
  let by = 3.1;
  bullets.forEach((b) => {
    s.addShape(pres.ShapeType.ellipse, { x: 7.32, y: by + 0.1, w: 0.12, h: 0.12, fill: { color: P.terra }, line: { width: 0 } });
    s.addText(b, { x: 7.62, y: by, w: 4.7, h: 1.0, fontFace: BODY, fontSize: 13, color: P.indigo, margin: 0, valign: "top" });
    by += 1.1;
  });
  s.addNotes("This is the closing argument for centrality. The acquisition angle is specific to Think9 - they bought Whoppl and have been in talks with a dozen D2C brands.");
}

/* ============================ 9  HITL ============================ */
{
  const s = lightSlide();
  kicker(s, "Human-in-the-loop");
  title(s, "Three gates, placed where errors cost most");

  const gates = [
    ["1", "Canonical creation", "L2", "Graph pollution. A wrong merge silently corrupts every downstream recommendation and is hard to detect afterwards.", "Sourcing analyst"],
    ["2", "Spend recommendation", "L6", "Committing money on a machine judgment. The agent proposes consolidation; a human authorises it.", "Category manager"],
    ["3", "Vendor communication", "L6", "Reputational and negotiating-position damage. The agent drafts; a human sends.", "Category manager"],
  ];
  let y = 1.7;
  gates.forEach(([n, name, layer, why, who]) => {
    card(s, M, y, 8.4, 1.28, P.cream);
    numCircle(s, n, M + 0.35, y + 0.42);
    s.addText(name, { x: M + 1.0, y: y + 0.22, w: 4.0, h: 0.32, fontFace: BODY, fontSize: 15, bold: true, color: P.indigo, margin: 0 });
    s.addText(layer, { x: M + 5.0, y: y + 0.24, w: 0.7, h: 0.28, fontFace: MONO, fontSize: 12, bold: true, color: P.terra, margin: 0 });
    s.addText(why, { x: M + 1.0, y: y + 0.58, w: 6.9, h: 0.58, fontFace: BODY, fontSize: 12.5, color: P.grey, margin: 0 });
    s.addText(who, { x: M + 5.85, y: y + 0.22, w: 2.3, h: 0.3, fontFace: BODY, fontSize: 11, italic: true, color: P.sage, align: "right", margin: 0 });
    y += 1.42;
  });

  card(s, 9.4, 1.7, 3.25, 4.26, P.indigo);
  s.addText("Confidence routing", {
    x: 9.7, y: 1.95, w: 2.7, h: 0.35, fontFace: BODY, fontSize: 13.5, bold: true, color: P.sage, margin: 0,
  });
  const routes = [["≥ 0.90", "auto-advance"], ["0.60 – 0.90", "human review"], ["< 0.60", "reject to human"]];
  let ry = 2.5;
  routes.forEach(([r, a]) => {
    s.addText(r, { x: 9.7, y: ry, w: 2.7, h: 0.3, fontFace: MONO, fontSize: 14, bold: true, color: P.terra, margin: 0 });
    s.addText(a, { x: 9.7, y: ry + 0.3, w: 2.7, h: 0.3, fontFace: BODY, fontSize: 12.5, color: P.card, margin: 0 });
    ry += 0.82;
  });
  s.addText("Human effort scales with ambiguity, not with volume.", {
    x: 9.7, y: 5.1, w: 2.7, h: 0.7, fontFace: BODY, fontSize: 12, italic: true, color: P.card, margin: 0,
  });

  s.addText("Full autonomy here would be a design error, not a feature.", {
    x: M, y: 6.2, w: 11.9, h: 0.35, fontFace: HEAD, fontSize: 16, italic: true, color: P.indigo, margin: 0,
  });
}

/* ============================ 10  PROTOTYPE: INPUT ============================ */
{
  const s = lightSlide();
  kicker(s, "Proof of concept");
  title(s, "It runs. No API key, 1.8 seconds.");

  const stats = [["12", "vendor artifacts"], ["27", "line items"], ["8", "canonical SKUs"], ["5", "Think9 brands"]];
  stats.forEach(([n, l], i) => {
    const x = M + i * 3.06;
    card(s, x, 1.7, 2.8, 1.35, P.cream);
    s.addText(n, { x: x + 0.25, y: 1.83, w: 2.3, h: 0.65, fontFace: HEAD, fontSize: 38, bold: true, color: P.terra, margin: 0 });
    s.addText(l, { x: x + 0.25, y: 2.5, w: 2.3, h: 0.32, fontFace: BODY, fontSize: 12.5, color: P.indigo, margin: 0 });
  });

  card(s, M, 3.25, 5.9, 2.35, P.indigo);
  s.addText("Deliberately incompatible formats", {
    x: M + 0.35, y: 3.5, w: 5.2, h: 0.32, fontFace: BODY, fontSize: 13, bold: true, color: P.sage, margin: 0,
  });
  const fmts = "3 PDF letterheads  ·  3 CSVs with mutually contradictory column schemas  ·  2 email bodies with prices in prose  ·  3 WhatsApp transcripts including Hinglish and Devanagari  ·  1 Excel with merged cells";
  s.addText(fmts, {
    x: M + 0.35, y: 3.9, w: 5.2, h: 1.6, fontFace: BODY, fontSize: 13, color: P.card, margin: 0, valign: "top",
  });

  card(s, 6.95, 3.25, 5.7, 2.75, P.cream);
  s.addText("Real, not scaffolded", {
    x: 7.3, y: 3.5, w: 5.0, h: 0.32, fontFace: BODY, fontSize: 13, bold: true, color: P.grey, margin: 0,
  });
  const real = [
    "Resolution cascade and the contradiction rule",
    "Five detectors computing from a live SQLite graph",
    "Every rupee figure derived, none asserted",
  ];
  let ry2 = 3.9;
  real.forEach((r) => {
    s.addShape(pres.ShapeType.ellipse, { x: 7.32, y: ry2 + 0.09, w: 0.12, h: 0.12, fill: { color: P.terra }, line: { width: 0 } });
    s.addText(r, { x: 7.62, y: ry2, w: 4.7, h: 0.35, fontFace: BODY, fontSize: 13, color: P.indigo, margin: 0 });
    ry2 += 0.45;
  });
  s.addText("The normalizer was written before the quote data existed and has not been tuned against it.", {
    x: 7.3, y: 5.3, w: 5.0, h: 0.55, fontFace: BODY, fontSize: 12, italic: true, color: P.grey, margin: 0,
  });

  s.addText("python run_demo.py", {
    x: M, y: 6.35, w: 5, h: 0.4, fontFace: MONO, fontSize: 15, bold: true, color: P.indigo, margin: 0,
  });
}

/* ============================ 11  PROTOTYPE: OUTPUT (hero) ============================ */
{
  const s = lightSlide();
  kicker(s, "Proof of concept — output");
  title(s, "Five names resolved. One bundle. A rupee figure.");

  card(s, M, 1.65, 7.35, 2.15, P.cream);
  s.addText("GLS-AMB-050-20", { x: M + 0.35, y: 1.85, w: 3.4, h: 0.35, fontFace: MONO, fontSize: 15, bold: true, color: P.terra, margin: 0 });
  s.addText("50ml amber glass bottle, 20mm neck", { x: M + 0.35, y: 2.2, w: 6.5, h: 0.3, fontFace: BODY, fontSize: 12.5, color: P.grey, margin: 0 });
  const rows = [
    ["Neude", "800", "Rs 20.75"], ["Beauty by Bie", "600", "Rs 21.50"],
    ["Panchamrit", "450", "Rs 22.50"], ["Goodbug", "700", "Rs 22.80"],
  ];
  rows.forEach(([b, q, p], i) => {
    const x = M + 0.35 + i * 1.72;
    s.addText(b, { x, y: 2.62, w: 1.65, h: 0.26, fontFace: BODY, fontSize: 11, color: P.indigo, margin: 0 });
    s.addText(q, { x, y: 2.88, w: 1.65, h: 0.3, fontFace: HEAD, fontSize: 17, bold: true, color: P.indigo, margin: 0 });
    s.addText(p, { x, y: 3.2, w: 1.65, h: 0.26, fontFace: MONO, fontSize: 10.5, color: P.grey, margin: 0 });
  });
  s.addText("2,550 units of requirement  vs  MOQ 2,500  →  clears", {
    x: M + 0.35, y: 3.48, w: 6.6, h: 0.28, fontFace: BODY, fontSize: 12.5, bold: true, color: P.sage, margin: 0,
  });

  card(s, 8.5, 1.65, 4.15, 2.15, P.indigo);
  s.addText("Rs 13,255", { x: 8.8, y: 1.95, w: 3.6, h: 0.7, fontFace: HEAD, fontSize: 40, bold: true, color: P.terra, margin: 0 });
  s.addText("saved on this SKU by consolidating four brands into one order", {
    x: 8.8, y: 2.7, w: 3.55, h: 0.9, fontFace: BODY, fontSize: 13, color: P.card, margin: 0,
  });

  card(s, M, 4.0, 7.35, 2.0, P.cream);
  s.addText("The refusal matters as much as the match", {
    x: M + 0.35, y: 4.2, w: 6.6, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: P.indigo, margin: 0,
  });
  s.addText("A 48ml bottle scored 85% description similarity against the 50ml canonical — exactly the fuzzy-match threshold. A text-based matcher merges them. LOOM refuses: volume 48 ≠ 50, both stated.",
    { x: M + 0.35, y: 4.55, w: 6.6, h: 0.95, fontFace: BODY, fontSize: 12.5, color: P.grey, margin: 0, valign: "top" });
  s.addText("Had it merged, it would have added 1,000 phantom units to the bundle above.",
    { x: M + 0.35, y: 5.5, w: 6.6, h: 0.32, fontFace: BODY, fontSize: 12, italic: true, color: P.terra, margin: 0 });

  card(s, 8.5, 4.0, 4.15, 2.0, P.cream);
  s.addText("Rs 31,672.60", { x: 8.8, y: 4.2, w: 3.6, h: 0.55, fontFace: HEAD, fontSize: 29, bold: true, color: P.indigo, margin: 0 });
  s.addText("total identified across six audited findings, from 12 quotes", {
    x: 8.8, y: 4.78, w: 3.55, h: 0.55, fontFace: BODY, fontSize: 12, color: P.grey, margin: 0,
  });
  s.addText("23 / 27 resolved  (85%)\n4 held for human review", {
    x: 8.8, y: 5.38, w: 3.55, h: 0.55, fontFace: BODY, fontSize: 12.5, bold: true, color: P.sage, margin: 0,
  });

  s.addText("Risk findings are excluded from the total — they quantify exposure against spend already counted, not new money.", {
    x: M, y: 6.25, w: 11.9, h: 0.35, fontFace: BODY, fontSize: 12, italic: true, color: P.grey, margin: 0,
  });
  s.addNotes("85% coverage with four visible holds is the credible number. A resolver that catches everything reads as a demo.");
}

/* ============================ 12  ROADMAP ============================ */
{
  const s = lightSlide();
  kicker(s, "Implementation");
  title(s, "Thirty days to a banked saving");

  s.addText("Scoped to packaging only — highest cross-brand overlap, substantial spend, and no regulatory sign-off to slow the loop.", {
    x: M, y: 1.55, w: 11.9, h: 0.35, fontFace: BODY, fontSize: 14, color: P.grey, margin: 0,
  });

  const phases = [
    ["Days 1–7", "Ingest & extraction", "Live for packaging. Seed ~150 canonical SKUs from the top 3 brands by spend.", "Extraction F1 ≥ 0.90"],
    ["Days 8–15", "Resolution & graph", "Backfill 90 days of history via GST e-invoice records. GSTIN as vendor key.", "80% of spend resolved"],
    ["Days 16–23", "First real negotiation", "Opportunity agent live. Run one consolidated negotiation end to end.", "One banked rupee saving"],
    ["Days 24–30", "Gates & measurement", "Human-gate console, alerting, instrumentation. Publish the baseline.", "Cycle time, before / after"],
  ];
  phases.forEach(([d, t, desc, exit], i) => {
    const x = M + i * 3.06;
    card(s, x, 2.1, 2.8, 3.5, i === 2 ? P.indigo : P.cream);
    const on = i === 2;
    s.addText(d, { x: x + 0.25, y: 2.3, w: 2.3, h: 0.3, fontFace: BODY, fontSize: 11.5, bold: true, color: on ? P.sage : P.terra, margin: 0 });
    s.addText(t, { x: x + 0.25, y: 2.62, w: 2.3, h: 0.65, fontFace: HEAD, fontSize: 17, bold: true, color: on ? P.paper : P.indigo, margin: 0 });
    s.addText(desc, { x: x + 0.25, y: 3.35, w: 2.3, h: 1.3, fontFace: BODY, fontSize: 12, color: on ? P.card : P.grey, margin: 0, valign: "top" });
    s.addText("EXIT", { x: x + 0.25, y: 4.72, w: 2.3, h: 0.22, fontFace: BODY, fontSize: 9, bold: true, charSpacing: 1, color: on ? P.sage : P.light, margin: 0 });
    s.addText(exit, { x: x + 0.25, y: 4.96, w: 2.3, h: 0.5, fontFace: BODY, fontSize: 11.5, bold: true, color: on ? P.terra : P.indigo, margin: 0 });
  });

  s.addText("A system that banks one real saving in month one earns the right to expand to ingredients, logistics and services. One that produces a dashboard does not.", {
    x: M, y: 5.85, w: 11.9, h: 0.6, fontFace: HEAD, fontSize: 16, italic: true, color: P.indigo, margin: 0,
  });
  s.addNotes("Position this inside the Office of Optimisation - it delivers that unit's first supply-chain case study.");
}

/* ============================ 13  STACK ============================ */
{
  const s = lightSlide();
  kicker(s, "Stack");
  title(s, "Boring on purpose");

  const stack = [
    ["Extraction", "Claude vision, OCR fallback", "Removes the brittle OCR-to-parse chain for photographed quotes"],
    ["Orchestration", "Temporal, not LangGraph", "Negotiations span days and must survive restarts. Durability beats graph ergonomics"],
    ["Storage", "Postgres + pgvector, not Neo4j", "At this volume the graph is small; recursive CTEs handle the traversals"],
    ["Serving", "FastAPI + Streamlit console", "The human gates must exist by day 30. Streamlit builds in days"],
  ];
  let y = 1.7;
  stack.forEach(([a, b, c]) => {
    card(s, M, y, 7.85, 0.92, P.cream);
    s.addText(a, { x: M + 0.3, y: y + 0.14, w: 1.75, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true, color: P.grey, margin: 0 });
    s.addText(b, { x: M + 2.05, y: y + 0.12, w: 5.5, h: 0.32, fontFace: BODY, fontSize: 14, bold: true, color: P.indigo, margin: 0 });
    s.addText(c, { x: M + 2.05, y: y + 0.46, w: 5.5, h: 0.36, fontFace: BODY, fontSize: 11.5, color: P.grey, margin: 0 });
    y += 1.02;
  });

  card(s, 8.95, 1.7, 3.7, 3.9, P.indigo);
  s.addText("Scale sanity check", { x: 9.25, y: 1.95, w: 3.1, h: 0.32, fontFace: BODY, fontSize: 13, bold: true, color: P.sage, margin: 0 });
  s.addText("24,000", { x: 9.25, y: 2.4, w: 3.1, h: 0.55, fontFace: HEAD, fontSize: 34, bold: true, color: P.terra, margin: 0 });
  s.addText("quote line-items per year. About 100 a working day.", { x: 9.25, y: 3.0, w: 3.1, h: 0.6, fontFace: BODY, fontSize: 12.5, color: P.card, margin: 0 });
  s.addText("~$500", { x: 9.25, y: 3.75, w: 3.1, h: 0.55, fontFace: HEAD, fontSize: 34, bold: true, color: P.terra, margin: 0 });
  s.addText("a year in inference cost, against a savings target in crores.", { x: 9.25, y: 4.35, w: 3.1, h: 0.6, fontFace: BODY, fontSize: 12.5, color: P.card, margin: 0 });
  s.addText("A small-data problem wearing a big-data costume.", { x: 9.25, y: 5.05, w: 3.1, h: 0.45, fontFace: BODY, fontSize: 12, italic: true, color: P.sage, margin: 0 });

  s.addText("No Kafka. No Spark. No vector database. Refusing infrastructure the scale does not justify is itself a design decision.", {
    x: M, y: 6.0, w: 11.9, h: 0.4, fontFace: HEAD, fontSize: 16, italic: true, color: P.indigo, margin: 0,
  });
}

/* ============================ 14  WHAT WOULD MAKE ME WRONG ============================ */
{
  const s = darkSlide();
  kicker(s, "Failure modes", P.sage);
  title(s, "What would make me wrong", { color: P.paper });

  const risks = [
    ["Wrong canonical merge", "Two different SKUs unified, and every recommendation built on a false equivalence.", "Gate 1. All merges reversible with audit trail. Precision weighted above recall."],
    ["Contract manufacturers buy the packaging", "If the co-packer procures, the brand isn't buying it and there is nothing to bundle.", "Every brand-SKU edge carries procurement mode. Direct-buy bundles; CM-embedded gets rate-benchmarked."],
    ["Vendors learn we bundle", "Base quotes inflate in anticipation of consolidated volume.", "Do not disclose portfolio volume until commit. Maintain and use BATNA vendors."],
    ["Over-consolidation", "Single-sourcing a bundled SKU creates a new portfolio-level supply risk.", "Concentration is a first-class alert, surfaced alongside every saving."],
  ];
  let y = 1.55;
  risks.forEach(([r, c, m]) => {
    s.addShape(pres.ShapeType.roundRect, {
      x: M, y, w: 11.9, h: 0.98, rectRadius: 0.06, fill: { color: P.ink }, line: { width: 0 },
    });
    s.addText(r, { x: M + 0.32, y: y + 0.14, w: 3.5, h: 0.7, fontFace: BODY, fontSize: 13.5, bold: true, color: P.terra, margin: 0, valign: "top" });
    s.addText(c, { x: M + 3.95, y: y + 0.14, w: 3.5, h: 0.75, fontFace: BODY, fontSize: 11.5, color: P.light, margin: 0, valign: "top" });
    s.addText(m, { x: M + 7.6, y: y + 0.14, w: 3.95, h: 0.75, fontFace: BODY, fontSize: 11.5, color: P.card, margin: 0, valign: "top" });
    y += 1.1;
  });

  s.addText("An architecture that has not enumerated its failure modes has not been designed.", {
    x: M, y: 6.25, w: 11.9, h: 0.4, fontFace: HEAD, fontSize: 17, italic: true, color: P.sage, margin: 0,
  });
}

pres.writeFile({ fileName: "/tmp/deck/LOOM_Think9.pptx" }).then(() => console.log("written"));
