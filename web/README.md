# Antiject Web Application 🛡️

Official interactive web playground, 3-layer prompt-injection visualizer, benchmark explorer, and documentation site for **Antiject** (Hacktoberfest 2026 × Integral University).

---

## 1. Quickstart & Local Setup

### Prerequisites
- Node.js 18+ (tested on Node v24.16.0)
- npm 9+

### Installation
```bash
# Clone the repository
git clone https://github.com/mustafasidd05-collab/Antiject.git
cd Antiject/web

# Install dependencies
npm install

# Start local dev server
npm run dev
```

### Production Build & Preview
```bash
# Typecheck & build static bundle
npm run build

# Preview production build locally
npm run preview
```

---

## 2. Scripts Reference

| Script | Command | Description |
|---|---|---|
| `dev` | `vite` | Start local Vite development server with HMR |
| `build` | `tsc -b && vite build` | Type-check and generate production bundle in `dist/` |
| `lint` | `oxlint` | Fast linter checking for code style and bugs |
| `test` | `vitest run` | Run unit tests across Layer 1 regex, L2 judge, and L3 policy logic |
| `preview` | `vite preview` | Run production preview server at `http://localhost:4173/` |

---

## 3. Architecture & Components

- **`src/antijectCore.ts`**: Pure client-side TypeScript port of the core Antiject security engine:
  - Layer 1: Unicode zero-width detector (`\u200B`, `\uFEFF`, RTL overrides), hidden HTML comment scanner (`<!-- ... -->`), and multilingual regex patterns (English, Hindi Devanagari, Hinglish).
  - Layer 2: Gemma AI Judge simulation with semantic classification and quote extraction.
  - Layer 3: Decision Engine, delimiter tag escaper (`escapeUntrustedDelimiters`), defensive wrapping (`wrapUntrustedData`), and tamper-evident audit receipt generator (`generateAuditReceipt`).
- **`src/benchmarkData.ts`**: Empirical 40-sample benchmark dataset (20 attacks, 20 benign hard negatives) and comparative pipeline performance metrics.
- **`src/App.tsx`**: Main interactive application layout featuring Hero, Preset Attack Sandbox, Live Comparison (Unprotected vs Protected Agent), 3-Layer Deep Dive, and Benchmark Explorer.
- **`src/index.css`**: Cybersecurity HUD design system with dark obsidian palettes, glowing neon accents, and WCAG 2.2 AA compliant focus states.

---

## 4. Deployment Targets

### Vercel Deployment
```bash
npx vercel --prod
```
Configured via `vercel.json` with security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`).

### Netlify Deployment
```bash
npx netlify deploy --prod --dir=dist
```
Configured via `netlify.toml` with publish directory set to `dist` and security headers enabled.

---

## 5. Security & Environment

- **Zero Client Secrets:** The interactive playground runs client-side zero-latency detection without requiring visitors to provide Gemini API keys.
- **Security Headers:** Strict Content Security Policies, clickjacking protection (`DENY`), and MIME-type nosniffing.
