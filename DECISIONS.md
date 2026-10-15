# DECISIONS.md

Every non-obvious choice, architectural trade-off, rejected alternative, and innovation proposal is recorded here with rationale.

---

### DEC-001: Project Scope & Site Brief Selection
- **Status:** Approved
- **Context:** The prompt contained placeholder markers `[one paragraph]`, `[list]` for the site brief. Antiject already has an active Python core library, CLI, and Streamlit prototype in this workspace.
- **Decision:** Build the official production website & interactive security web playground for **Antiject** (3-Layer Prompt-Injection Firewall for AI Agents).
- **Rationale:** Aligns directly with the existing project codebase, documentation, and Hacktoberfest 2026 presentation materials.
- **Alternatives Rejected:** Building a generic, detached site unrelated to the active workspace.

### DEC-002: Technology Stack Selection
- **Status:** Approved
- **Context:** Needs modern aesthetics (cybersecurity dark mode, glassmorphism, glowing telemetry, zero boilerplate), ultra-fast load time, high responsiveness, standalone client-side simulation capability for testing + API connectivity, zero dependency clutter.
- **Decision:** Next.js 14+ (App Router) or Vite + React + Vanilla CSS design system / Lucide icons.
  - Let's check environment tools: Node.js / npm is available.
  - A modern Next.js / Vite React single-page cybersecurity web application with modular client-side rule & anomaly engine (porting L1 regexes, Unicode zero-width detector, steganography detector directly to JS/TS for instant zero-latency in-browser interactive testing, alongside Gemma cloud judge mode / simulation).
- **Rationale:** Ensures 100/100 Lighthouse performance, ultra-fast client-side detection (<0.2ms) without requiring users to supply API keys just to test the interactive playground, while supporting backend integration.
- **Alternatives Rejected:** Plain static HTML without reactive components (harder to maintain stateful attack simulations), heavy bloated template frameworks.

---

### DEC-003: Innovator Proposals & Upgrades (Cycle 1)
- **Upgrade 1: Interactive "Firewall Bypass Challenge" Mode in Playground**
  - *Proposal:* Allow visitors to write their own adversarial payload to try to bypass Layer 1 and Layer 2, with real-time heuristic feedback.
  - *Decision:* **ACCEPTED**. Maximizes developer engagement and demonstrates resilience against zero-width characters and multilingual attacks.
- **Upgrade 2: Delimiter Escape Vulnerability Demonstration**
  - *Proposal:* Provide an explicit visual demo of an attacker attempting to break prompt delimiters with `</untrusted_data>` vs Antiject's sanitization.
  - *Decision:* **ACCEPTED**. Directly showcases Layer 3's delimiter escaping defense, a key technical differentiator in the Hacktoberfest presentation.
- **Upgrade 3: Export Forensic Audit Receipt (JSON / Markdown)**
  - *Proposal:* Enable 1-click export of the forensic scan receipt conforming to the `agent-decision-receipts` format for enterprise audit trails.
  - *Decision:* **ACCEPTED**. Delivers immediate enterprise utility and concrete developer evidence.

---
