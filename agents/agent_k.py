from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from utils.llm import call_llm

def clean_json_response(response):
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return match.group(0)
    except:
        pass
    return response


# Get Rendered DOM using Playwright

# def get_page_dom(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()

#         try:
#             page.goto(url, timeout=60000)
#             page.wait_for_timeout(3000)
#             content = page.content()
#         except Exception as e:
#             print(f" Failed to load {url}: {e}")
#             content = ""
#         finally:
#             browser.close()

#         return content
def get_page_dom(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # FIX 1: Better loading strategy
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # FIX 2: Wait for actual page element instead of blind sleep
            page.wait_for_selector("body", timeout=10000)

            content = page.content()

        except Exception as e:
            print(f" Failed to load {url}: {e}")
            content = ""
        finally:
            browser.close()

        return content

# Extract Interactive Elements

def extract_interactive_elements(html):
    soup = BeautifulSoup(html, "html.parser")

    elements = []
    tags = ["input", "button", "a", "select", "textarea"]

    for tag in soup.find_all(tags):
        elem = {
            "tag": tag.name,
            "id": tag.get("id"),
            "name": tag.get("name"),
            "type": tag.get("type"),
            "placeholder": tag.get("placeholder"),
            "text": tag.text.strip() if tag.text else "",
            "class": tag.get("class"),
        }
        elements.append(elem)

    return elements

def build_locator_prompt(elements, scenario):
    return f"""
You are Agent K - Locator Extractor.

Scenario:
{json.dumps(scenario, indent=2)}

Available UI Elements:
{json.dumps(elements[:200], indent=2)}

Task:
Map each step to a reliable Playwright locator.

Rules:
- Prefer id
- Then name
- Then placeholder
- Then text
- Avoid brittle selectors
- Return STRICT JSON ONLY (no markdown, no explanation)

Format:
{{
  "id": "{scenario['id']}",
  "locators": [
    {{
      "step": "Enter username",
      "locator": "page.locator('#username')",
      "action": "fill"
    }}
  ]
}}
"""


# Main Agent K Function

def extract_locators(base_url, scenarios):
    print(" [Agent K] Extracting locators via web scraping...")

    results = []

    for scenario in scenarios:
        path = scenario.get("path", "")

        #  FIX: Handle wildcard paths
        if "*" in path:
            full_url = base_url
        else:
            full_url = base_url.rstrip("/") + path

        print(f"\n Processing: {scenario['id']} → {full_url}")

        html = get_page_dom(full_url)

        if not html:
            print(" No HTML content, skipping...")
            continue

        elements = extract_interactive_elements(html)

        if not elements:
            print(" No elements found, skipping...")
            continue

        prompt = build_locator_prompt(elements, scenario)

        response = call_llm(prompt)

        #  FIX: Clean JSON
        cleaned = clean_json_response(response)

        try:
            parsed = json.loads(cleaned)
            results.append(parsed)
        except Exception as e:
            print(" LLM parsing failed, skipping scenario:", e)

    return {
        "locators": results
    }