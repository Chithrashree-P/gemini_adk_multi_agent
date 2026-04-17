import os
import google.genai as genai
import time

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def call_llm(prompt):
    for i in range(3):  # retry 3 times
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"Retry {i+1} failed:", e)
            time.sleep(2)

    return "Fallback: Unable to generate"
