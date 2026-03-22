# HMN Mental Pasienter — Design System v2
> Updated after homepage v10. Use this document for ALL pages going forward.
> Previous design system (v1) is superseded by this document entirely.

---

## The Concept
**"Private friend group portal with dark gaming energy and a fake Norwegian health portal leaking through the cracks."**

Premium dark gaming UI (think Valorant launcher, Riot client) as the base.
Norwegian bureaucratic chaos as the personality layer on top.
Every page should feel like a real product that happens to be run by 6 idiots from Trondheim.

---

## Fonts

Load these in `index.html` or global CSS — never use system fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Barlow:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500&display=swap" rel="stylesheet">
```

| Role | Font | Usage |
|---|---|---|
| Display / headings | `Barlow Condensed` | H1, H2, section titles, labels, badges, buttons, nav brand |
| Body / UI text | `Barlow` | Body copy, descriptions, nav links, card text |
| Utility / small | `DM Sans` | General UI, meta text, captions |

**Font weights used:**
- Barlow Condensed: 600, 700, 800, 900
- Barlow: 400, 500, 600 (italic 400 for quotes)
- DM Sans: 400, 500

**Never use:** Inter, Roboto, Arial, system-ui, or any weight not listed above.

---

## Color Palette

### CSS Variables — add to global `:root`

```css
:root {
  /* ── Backgrounds ── */
  --hmn-bg:        #080c12;   /* Page background — deepest dark */
  --hmn-bg2:       #0b1018;   /* Slightly lighter bg for sections */
  --hmn-surface:   #0f1720;   /* Cards, panels, raised surfaces */
  --hmn-surface2:  #131e28;   /* Hovered surfaces, inner panels */

  /* ── Borders ── */
  --hmn-border:    rgba(255,255,255,0.07);   /* Default border on all cards/panels */
  --hmn-border2:   rgba(255,255,255,0.11);   /* Slightly brighter border, hover states */

  /* ── Text ── */
  --hmn-text:      #b8ccd8;   /* Default body text */
  --hmn-muted:     #3d5668;   /* Muted text, metadata, labels */
  --hmn-bright:    #eaf2ff;   /* Headings, important values, white-ish */

  /* ── Accent Colors ── */
  --hmn-red:       #c8102e;   /* Primary action, brand, danger */
  --hmn-red2:      #e8304a;   /* Brighter red for glows, hover states */
  --hmn-cyan:      #00b8d0;   /* Secondary accent, links, info */
  --hmn-cyan2:     #30d8f0;   /* Brighter cyan for gradients */
  --hmn-gold:      #d89820;   /* Warning, events, Thomas-related */
  --hmn-green:     #28b860;   /* Online, success, live indicators */
  --hmn-purple:    #7050d8;   /* Decorative, subtle bg glows only */

  /* ── Platform Colors (gaming section only) ── */
  --hmn-steam:     #1b9fd4;
  --hmn-xbox:      #107c10;
  --hmn-bnet:      #148eff;
  --hmn-discord:   #5865f2;

  /* ── Semantic Shortcuts ── */
  --hmn-danger:    var(--hmn-red2);
  --hmn-warning:   var(--hmn-gold);
  --hmn-success:   var(--hmn-green);
  --hmn-info:      var(--hmn-cyan);

  /* ── Radius ── */
  --hmn-radius-sm: 4px;    /* Badges, small pills, sharp elements */
  --hmn-radius-md: 6px;    /* Buttons */
  --hmn-radius-lg: 10px;   /* Cards, panels */
  --hmn-radius-xl: 12px;   /* Large panels, hero cards */
}
```

---

## Where Each Color Is Used

### Backgrounds
| Surface | Variable | Notes |
|---|---|---|
| Page background | `--hmn-bg` | `#080c12` — always the base |
| Alternate section bg | `--hmn-bg2` | Very subtle variation |
| All cards and panels | `--hmn-surface` | `#0f1720` |
| Hovered/inner panels | `--hmn-surface2` | `#131e28` |
| Nav background | `--hmn-bg` + `rgba(8,12,18,0.9)` | With `backdrop-filter:blur(24px)` |
| Driftsmelding bar | `rgba(200,16,46,0.06)` | Tinted red, not solid |
| Hero section | Radial gradients on `--hmn-bg` | See hero pattern below |

### Borders
| Context | Variable |
|---|---|
| All card/panel borders | `--hmn-border` (`rgba(255,255,255,0.07)`) |
| Hover/featured borders | `--hmn-border2` (`rgba(255,255,255,0.11)`) |
| Driftsmelding border | `rgba(200,16,46,0.15)` |
| Melding featured top border | `rgba(0,184,208,0.16)` |

### Text
| Context | Variable | Notes |
|---|---|---|
| Body text | `--hmn-text` | `#b8ccd8` |
| Muted labels, meta | `--hmn-muted` | `#3d5668` |
| Headings, values | `--hmn-bright` | `#eaf2ff` |
| Red values (danger) | `--hmn-red2` | Krenkethet, warnings |
| Cyan values (info) | `--hmn-cyan` | Counts, links, online |
| Gold values (warning) | `--hmn-gold` | Events, kaffe, Thomas |
| Green values (success) | `--hmn-green` | Online dots, diagnose: stabil |
| Text on --hmn-red bg | `white` | Always white on red |
| On dark surface text | `--hmn-bright` for titles, `--hmn-muted` for labels | |

---

## Component Rules

### Nav
```css
/* Wrapper */
position: sticky; top: 0; z-index: 40;
background: rgba(8,12,18,0.9);
backdrop-filter: blur(24px);
border-bottom: 1px solid var(--hmn-border);
height: 64px;

/* Cyan line under nav */
.nav-wrap::after {
  content: '';
  position: absolute; bottom: -1px; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,184,208,0.2) 40%, rgba(0,184,208,0.2) 60%, transparent);
}

/* Brand name */
font-family: 'Barlow Condensed', sans-serif;
font-size: 18–19px; font-weight: 800;
text-transform: uppercase; letter-spacing: 0.05em;
color: var(--hmn-bright);

/* Brand logo mark */
width: 38px; height: 38px; border-radius: 9px;
background: linear-gradient(145deg, var(--hmn-red), #7a0e1e);
box-shadow: 0 0 16px rgba(200,16,46,0.3);

/* Nav links */
font-family: 'Barlow', sans-serif;
font-size: 13px; font-weight: 500;
color: var(--hmn-muted);
padding: 7px 12px; border-radius: 6px;

/* Active nav link */
color: var(--hmn-cyan);

/* Hover nav link */
color: var(--hmn-text); background: rgba(255,255,255,0.05);

/* Forum link — ALWAYS */
text-decoration: line-through;
color: #182430;
pointer-events: none;
```

### Driftsmelding Bar
```css
background: rgba(200,16,46,0.06);
border-bottom: 1px solid rgba(200,16,46,0.15);
padding: 6px 2rem;

/* Pulsing dot */
width: 6px; height: 6px;
background: var(--hmn-red2);
border-radius: 50%;
box-shadow: 0 0 7px var(--hmn-red2);
animation: blink 2s infinite;

/* Tag */
font-family: 'Barlow Condensed', sans-serif;
font-size: 10px; letter-spacing: 0.14em; font-weight: 700;
color: var(--hmn-red2); text-transform: uppercase;

/* Text */
font-size: 11px; color: rgba(255,255,255,0.2);
```

### Buttons
```css
/* All buttons */
display: inline-flex; align-items: center; gap: 7px;
padding: 9px 20px; border-radius: 6px;
font-size: 13px; font-weight: 600;
font-family: 'Barlow', sans-serif;
cursor: pointer; border: none;
transition: all 0.18s;

/* Primary — red */
.btn-red {
  background: linear-gradient(145deg, var(--hmn-red), #8a0e1e);
  color: white;
  box-shadow: 0 4px 16px rgba(200,16,46,0.28);
}
.btn-red:hover {
  box-shadow: 0 6px 24px rgba(200,16,46,0.42);
  transform: translateY(-1px);
}

/* Ghost — transparent */
.btn-ghost {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--hmn-border2);
  color: var(--hmn-text);
}
.btn-ghost:hover {
  background: rgba(255,255,255,0.08);
  transform: translateY(-1px);
}

/* Never use BankID, never add text-transform:uppercase to ghost buttons */
```

### Cards / Panels
```css
/* Standard card */
background: rgba(255,255,255,0.028);
border: 1px solid var(--hmn-border2);
border-radius: var(--hmn-radius-lg); /* 10px */
overflow: hidden;
transition: border-color 0.2s;

/* Card hover */
border-color: rgba(255,255,255,0.15);

/* Card header bar (inside card) */
padding: 11–13px 16–18px;
border-bottom: 1px solid var(--hmn-border);
background: rgba(255,255,255,0.02);

/* Card header title */
font-family: 'Barlow Condensed', sans-serif;
font-size: 13px; font-weight: 800;
color: var(--hmn-bright);
letter-spacing: 0.08em; text-transform: uppercase;

/* Inner row dividers */
border-bottom: 1px solid var(--hmn-border);

/* Left accent hover effect (update list items) */
position: relative; overflow: hidden;
::before — left: 0; top: 0; bottom: 0; width: 2px;
background: transparent → var(--hmn-cyan) on hover;
```

### Section Headers
```css
display: flex; align-items: center; gap: 14px;
margin-bottom: 20px;

/* Title */
font-family: 'Barlow Condensed', sans-serif;
font-size: 18px; font-weight: 800;
color: var(--hmn-bright);
letter-spacing: 0.08em; text-transform: uppercase;

/* Cyan word inside title */
color: var(--hmn-cyan); /* wrap second word in <em> with font-style:normal */

/* Divider line */
flex: 1; height: 1px;
background: linear-gradient(90deg, var(--hmn-border2), transparent);

/* Optional tag */
font-size: 10px; color: var(--hmn-muted);
padding: 3px 9px; border-radius: 4px;
background: rgba(255,255,255,0.04);
border: 1px solid var(--hmn-border);
```

### Badges / Status Pills
```css
/* All badges */
font-family: 'Barlow Condensed', sans-serif;
font-size: 9px; font-weight: 700;
letter-spacing: 0.07em; text-transform: uppercase;
padding: 4px 10px; border-radius: 4px;
white-space: nowrap;

/* Gold — events, required attendance */
background: rgba(216,152,32,0.12);
color: var(--hmn-gold);
border: 1px solid rgba(216,152,32,0.22);

/* Red — Thomas blame, danger */
background: rgba(200,16,46,0.12);
color: var(--hmn-red2);
border: 1px solid rgba(200,16,46,0.22);

/* Cyan — info, login prompts */
background: rgba(0,184,208,0.08);
color: var(--hmn-cyan);
border: 1px solid rgba(0,184,208,0.18);

/* Green — online, success */
background: rgba(40,184,96,0.1);
color: var(--hmn-green);
border: 1px solid rgba(40,184,96,0.2);
```

### Live Dot (online indicator)
```css
width: 6–7px; height: 6–7px;
border-radius: 50%;
background: var(--hmn-green);
box-shadow: 0 0 7–9px var(--hmn-green);
animation: blink 2–2.5s infinite;

@keyframes blink {
  0%, 100% { opacity: 1 }
  50%       { opacity: 0.2 }
}
```

### Hero Section
```css
/* Background layers */
background:
  radial-gradient(ellipse 80% 60% at 72% 45%, rgba(0,184,208,0.05), transparent 60%),
  radial-gradient(ellipse 45% 55% at 8% 75%,  rgba(200,16,46,0.07), transparent 55%),
  radial-gradient(ellipse 50% 35% at 88% 88%, rgba(112,80,216,0.05), transparent 50%),
  linear-gradient(180deg, #050910 0%, var(--hmn-bg) 100%);

/* Grid overlay */
background-image:
  linear-gradient(rgba(0,184,208,0.022) 1px, transparent 1px),
  linear-gradient(90deg, rgba(0,184,208,0.022) 1px, transparent 1px);
background-size: 52px 52px;
mask-image: linear-gradient(155deg, rgba(0,0,0,0.45) 0%, transparent 50%);

/* H1 style */
font-family: 'Barlow Condensed', sans-serif;
font-size: clamp(4.4rem, 7.8vw, 8.4rem);
font-weight: 900; line-height: 0.88;
text-transform: uppercase;

/* Gradient word (cyan) */
background: linear-gradient(92deg, var(--hmn-cyan) 0%, var(--hmn-cyan2) 50%, rgba(160,240,255,0.9) 100%);
-webkit-background-clip: text; background-clip: text; color: transparent;

/* Dim subtitle line */
color: rgba(255,255,255,0.1);
font-size: 0.52em; letter-spacing: 0.1em; margin-top: 6px;
```

### Ticker / Systemfeed
```css
background: rgba(0,0,0,0.3);
border-bottom: 1px solid var(--hmn-border);
padding: 10px 0; overflow: hidden;

/* Fade edges */
::before, ::after — gradient fade left/right using var(--hmn-bg)

/* Label */
font-family: 'Barlow Condensed', sans-serif;
font-size: 10px; letter-spacing: 0.16em; font-weight: 700;
color: var(--hmn-cyan); text-transform: uppercase;

/* Scrolling text */
color: rgba(255,255,255,0.16); font-size: 11px;
animation: ticker Xs linear infinite;

/* Highlighted words */
color: rgba(255,255,255,0.42);

@keyframes ticker {
  0%   { transform: translateX(0) }
  100% { transform: translateX(-50%) }
}
/* Content must be duplicated for seamless loop */
```

### Footer
```css
background: rgba(0,0,0,0.35);
border-top: 1px solid var(--hmn-border);
padding: 16px 0;
font-size: 11px;
color: rgba(255,255,255,0.1);
font-family: 'DM Sans', sans-serif;
display: flex; justify-content: space-between;
```

### Scroll Reveal
```css
/* Default hidden state */
.reveal {
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
/* Triggered by IntersectionObserver adding .in class */
.reveal.in {
  opacity: 1;
  transform: none;
}
```

```js
const obs = new IntersectionObserver(els => {
  els.forEach(el => { if (el.isIntersecting) el.target.classList.add('in'); });
}, { threshold: 0.08 });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
```

---

## Page Layout Template

```
Driftsmelding bar
Nav (sticky)
─────────────────
Hero
  Left: Title + desc + CTA + pills
  Right: Status panel (Pasientstatus)
─────────────────
Systemfeed ticker
─────────────────
Main content (--hmn-bg background, padding 52px 0 72px)
  Bedriftsmeldinger (featured + update list)
  Kommende hendelser + Helsejournal
  Fra gjengen (Født i kaos + Discord)
  Historisk øyeblikk
  Login CTA
─────────────────
Footer
```

Max content width: `1120px`, centered, `2.5rem` side padding.

---

## Gaming Section (profile page only)

Platform colors are **only used in the gaming stats section** of the profile page — never bleed into the main site palette.

```css
--hmn-steam:   #1b9fd4;   /* Steam blue */
--hmn-xbox:    #107c10;   /* Xbox green */
--hmn-bnet:    #148eff;   /* Battle.net blue */
--hmn-discord: #5865f2;   /* Discord purple */
```

Platform badge pattern:
```css
/* Steam example */
background: rgba(27,159,212,0.12);
color: #4ab8e8;
border: 1px solid rgba(27,159,212,0.25);
border-radius: 4px;
font-family: 'Barlow Condensed', sans-serif;
font-size: 9px; font-weight: 700; text-transform: uppercase;
```

---

## The Writing Rules (copy guidelines for agents)

These apply to ALL user-facing text across the entire site:

1. **§ references** — fake legal paragraphs on rules. e.g. `§ 2.1`, `§ 7.7 garanterer ingenting`
2. **Thomas har skylda** — any failure, warning or unresolved issue is Thomas's fault
3. **Health portal leaking through** — occasional clinical language for absurd things. "Eksistensielt stressnivå: Forhøyet", "Diagnose: Stabil, for nå"
4. **Never sound like AI** — no "robust", "seamless", "leverage", "cutting-edge". Write like a real person, slightly tired, slightly unhinged
5. **Forum is always dead** — strikethrough in nav, referenced in ticker, never linked
6. **GDPR-compliant*** — the asterisk appears in footer, never explained
7. **Ref numbers** — `HMN-XXX-000` format for official-looking things
8. **Driftsmelding** — always present, always about the forum, always says "Forventet retur: Aldri"
9. **"Logg inn" not "BankID"** — never reference BankID, Vipps or any real Norwegian auth service
10. **Pasientstatus not System Status** — the hero panel uses health terminology

---

## What NOT To Do

- Never hardcode hex values — always use CSS variables
- Never use `//` prefixes on labels — that was v7, it's gone
- Never use `text-transform: uppercase` on ghost buttons
- Never show Fitte Points on the homepage
- Never reference BankID
- Never use Inter, Roboto, Arial or system fonts
- Never add rounded corners larger than `--hmn-radius-xl` (12px)
- Never use white or light backgrounds anywhere
- Never add drop shadows — use `box-shadow` with rgba only for glow effects
- Never use emoji in section headers or nav — only in content cards where they already exist
