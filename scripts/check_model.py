#!/usr/bin/env python3
"""
Model Discovery and Verification Script for PromptShield.
Queries Google GenAI API to discover available Gemma models and verify connectivity.
"""

import os
import sys
from dotenv import load_dotenv

# Load any .env present
load_dotenv()

def get_api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def check_models():
    api_key = get_api_key()
    print("=" * 60)
    print("PromptShield Model Discovery & Verification")
    print("=" * 60)
    
    if not api_key:
        print("\n[!] No GEMINI_API_KEY or GOOGLE_API_KEY found.")
        print("    -> PromptShield will run in 'MockJudge (Local Simulation - No API Key)' mode.")
        print("    -> To connect to live Gemma models:")
        print("       1. Copy .env.example to .env: copy .env.example .env")
        print("       2. Add your Google AI Studio API key in .env")
        print("       3. Re-run: python scripts/check_model.py\n")
        return {
            "status": "offline",
            "active_model": "MockJudge",
            "label": "MockJudge (Local Simulation - No API Key)",
            "available_gemma_models": [],
        }

    print(f"\n[*] API Key detected: {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}")
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except ImportError:
        print("\n[!] 'google-genai' package is not installed. Run: pip install -e .")
        return {
            "status": "missing_dependency",
            "active_model": "MockJudge",
            "label": "MockJudge (Missing google-genai dependency)",
            "available_gemma_models": [],
        }
    except Exception as e:
        print(f"\n[!] Failed to initialize Google GenAI client: {e}")
        return {
            "status": "client_error",
            "active_model": "MockJudge",
            "label": f"MockJudge (Client init error: {e})",
            "available_gemma_models": [],
        }

    print("[*] Fetching available models via client.models.list()...")
    gemma_models = []
    gemini_models = []
    
    try:
        for model in client.models.list():
            name = getattr(model, "name", str(model))
            # Clean model name prefix if present (e.g. 'models/gemma-2-9b-it' -> 'gemma-2-9b-it')
            clean_name = name.replace("models/", "")
            
            if "gemma" in clean_name.lower():
                gemma_models.append(clean_name)
            elif "gemini" in clean_name.lower() and "flash" in clean_name.lower():
                gemini_models.append(clean_name)
    except Exception as e:
        print(f"[!] Error listing models: {e}")
        # Proceed with fallback test
    
    print("\n--- Discovered Gemma Models ---")
    if gemma_models:
        for m in gemma_models:
            print(f"  [+] {m}")
    else:
        print("  [-] No dedicated Gemma models directly listed in current endpoint tier.")

    print("\n--- Available Fast Fallback Models ---")
    for m in gemini_models[:5]:
        print(f"  [*] {m}")

    # Determine recommended model
    # Prefer explicitly set PROMPTSHIELD_MODEL if valid
    env_override = os.environ.get("PROMPTSHIELD_MODEL")
    active_model = None
    model_label = None

    if env_override and (env_override in gemma_models or env_override in gemini_models):
        active_model = env_override
        model_label = f"{env_override} (User override)"
    elif any("gemma-4" in m for m in gemma_models):
        active_model = next(m for m in gemma_models if "gemma-4" in m)
        model_label = f"{active_model} (Gemma 4 Native)"
    elif any("gemma-2" in m for m in gemma_models):
        active_model = next(m for m in gemma_models if "gemma-2" in m)
        model_label = f"{active_model} (Gemma 2 Open Weights)"
    elif gemma_models:
        active_model = gemma_models[0]
        model_label = f"{active_model} (Gemma Open Weights)"
    elif any("gemini-2.5-flash" in m for m in gemini_models):
        active_model = "gemini-2.5-flash"
        model_label = "gemini-2.5-flash (Gemma-Judge Fallback)"
    elif any("gemini-1.5-flash" in m for m in gemini_models):
        active_model = "gemini-1.5-flash"
        model_label = "gemini-1.5-flash (Gemma-Judge Fallback)"
    else:
        active_model = "gemma-2-9b-it"
        model_label = "gemma-2-9b-it (Default Candidate)"

    print(f"\n[+] Selected Active Model: {active_model}")
    print(f"[+] Display Label: {model_label}")

    # Live connectivity test
    print(f"\n[*] Running live verification probe on '{active_model}'...")
    try:
        response = client.models.generate_content(
            model=active_model,
            contents='Test ping: Reply strictly with JSON: {"status": "ok"}'
        )
        print(f"[+] Live Response received: {response.text.strip()}")
        is_live = True
    except Exception as e:
        print(f"[!] Live probe failed: {e}")
        is_live = False
        model_label += " [Probe Failed - Check Quota/Access]"

    return {
        "status": "online" if is_live else "probe_failed",
        "active_model": active_model,
        "label": model_label,
        "available_gemma_models": gemma_models,
        "available_fallbacks": gemini_models[:5],
    }

if __name__ == "__main__":
    result = check_models()
    print("\n" + "=" * 60)
    print(f"Summary: {result['label']}")
    print("=" * 60)
