# PLAN.md: Antiject Production Website & Interactive Playground

## 1. Project Overview & Mission
- **Project:** Antiject (Prompt-Injection Firewall & Security Layer for Autonomous AI Agents)
- **Target Audience:** AI security engineers, LLM app developers, enterprise security architects, Hacktoberfest judges, and open-source contributors.
- **Primary Goal:** Provide a state-of-the-art, high-converting, educational, and interactive web experience showcasing Antiject's 3-Layer prompt injection defense. Allow visitors to test attacks in a live sandbox, inspect telemetry, compare unprotected vs protected agents, explore real 40-sample benchmarks, and integrate the library into their Python stack.
- **Deploy Target:** Production-ready web application deployable to Vercel, Netlify, or Cloudflare Pages with zero-config static/edge deployment.

---

## 2. Architecture & Tech Stack
- **Framework:** Vite + React + TypeScript / Vanilla CSS Design System
- **Design Language:** Modern Cybersecurity HUD / High-Tech Dark Theme
  - Color Palette: Obsidian Dark (`#0A0D14`, `#101624`), Cyber Cyan (`#00F0FF`), Neon Emerald (`#00FF9D`), Warning Amber (`#FFB800`), Threat Crimson (`#FF3B5C`), Soft Slate (`#94A3B8`).
  - Typography: Modern sans-serif (`Inter`, `JetBrains Mono` for code and telemetry).
  - Glassmorphism, cyber grid backdrop, glowing border animations, high-contrast accessible states.
- **Interactive Engine:**
  - Client-side Port of Layer 1 Scanner: Zero-width Unicode detector (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`, soft hyphens, RTL overrides), HTML comment detector (`<!-- ... -->`), and multilingual regex patterns (English, Hindi Devanagari, Hinglish Latin-script).
  - Layer 2 Gemma AI Judge Engine: Live simulation with full quote extraction and verification, with optional live API key connectivity.
  - Layer 3 Policy & Delimiter Sanitizer: Strict vs Balanced vs Lenient modes, delimiter escaping (`<untrusted_data>`), and verbatim quote redacting (`[REDACTED_BY_ANTIJECT]`).
  - Interactive Agent Simulator: Visual comparison of unprotected agent execution (tool-call compromise) vs protected agent execution (safe containment).

---

## 3. Page Structure & Features
1. **Header / Navbar:**
   - Brand logo with animated shield pulse
   - Navigation links: Playground, 3-Layer Defense, Benchmarks, Docs, Team
   - Live GitHub Star / Fork counter badge
   - "Launch Playground" Quick CTA
2. **Hero Section:**
   - Dynamic headline: "The 3-Layer Prompt-Injection Firewall for AI Agents"
   - Subtitle: "Neutralize indirect prompt injections, steganography, and multilingual jailbreaks before untrusted data reaches your LLM."
   - Quick Install Command: `pip install antiject` with instant copy feedback
   - Live threat detection counter / visual shield status
3. **Live Interactive Security Playground:**
   - Pre-loaded attack dataset:
     - Direct Prompt Override (OWASP LLM01 classic)
     - Invisible Zero-Width Unicode Steganography
     - Hidden HTML Comment Payload
     - Devanagari Hindi Injection ("पिछले निर्देश भूल जाओ...")
     - Hinglish Romanized Injection ("pichle instructions bhool jao...")
     - Delimiter Escape Attack (`</untrusted_data>`)
     - Benign Clean Article (Zero false positive test)
   - Real-time forensic breakdown:
     - L1 Scanner verdict, detected anomalies, rule hits, latency (<0.2ms)
     - L2 Gemma AI Judge intent classification, reasoning, and quote extraction
     - L3 Policy decision (ALLOW / SANITIZE / BLOCK), sanitized payload preview
   - **Interactive Firewall Bypass Challenge:** Test custom payloads against Antiject defenses with instant rule hit breakdown.
   - **Forensic Audit Receipt Export:** 1-click export of verifiable audit receipt (JSON / Markdown).
   - Live Agent Execution Comparison:
     - Unprotected Agent: Exploit triggered -> `send_email()` exfiltration
     - Protected Agent: Safe execution -> Threat neutralized, clean summary
4. **3-Layer Architecture Interactive Explorer:**
   - Step 1: Untrusted Ingestion (PDFs, Webhooks, Emails)
   - Step 2: Layer 1 Rule & Anomaly Scanner (~0.2ms)
   - Step 3: Layer 2 Gemma AI Judge (Chunked + Retried)
   - Step 4: Layer 3 Decision Engine & Delimiter Sanitizer
   - Interactive modal / card expanding each layer's inner workings
5. **Real-World Benchmark & Forensic Dashboard:**
   - 40-sample benchmark telemetry visualization (100% TPR, 100% TNR, 0% FPR)
   - Latency comparison chart (L1 0.18ms vs Cloud Guardrails 800ms)
   - Filterable benchmark test-case table with attack vectors and results
6. **Developer Integration & Quickstart:**
   - Interactive code tabs: Python Library, LangChain, LlamaIndex, Docker, FastAPI
   - Configuration parameters reference (`Policy`, `threshold`, `chunk_size`)
7. **Team & Hacktoberfest 2026 Credits:**
   - Team Trinity profile cards: Altamsh, Mohd Mustafa Siddiqui, Mohd Ayan Khan
   - Event badges: Hacktoberfest 2026, Integral University, DigitalOcean, DEV, MLH
8. **Footer & Compliance:**
   - MIT License, GitHub links, OWASP LLM Top 10 references, A11y & privacy commitments
9. **Custom 404 Error Page:**
   - Cyber-themed firewall intercept page with navigation recovery

---

## 4. Measurable Acceptance Criteria (Definition of Done)
1. **Feature Completeness:** All interactive sections functional; preset attacks trigger genuine forensic analysis; custom inputs work in real-time; code copy works; zero dead links.
2. **Build & Quality:** Clean build with 0 TypeScript/build errors, 0 console errors, clean linting.
3. **Responsiveness:** Flawless rendering at 375px (Mobile), 768px (Tablet), and 1440px (Desktop), verified with automated Playwright browser tests and saved screenshots in `/evidence`.
4. **Performance & Lighthouse:** 90+ on Performance, Accessibility, Best Practices, and SEO.
5. **Accessibility (a11y):** WCAG 2.2 AA compliant, full keyboard navigation, visible focus indicators, semantic landmarks, high contrast text.
6. **SEO & Sharing:** Meta tags, Open Graph, Twitter cards, favicon, robots.txt, sitemap.xml.
7. **Deployment:** Clean production build ready for static hosting over HTTPS with security headers.
