async def generate_with_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error_message": "Gemini API key missing"
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1
                    }
                },
                timeout=30.0
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "response_text": data["candidates"][0]["content"]["parts"][0]["text"],
                "error_message": None
            }

        except httpx.HTTPStatusError as e:
            print("==== GEMINI ERROR RESPONSE BODY ====")
            print(e.response.text)
            print("====================================")

            return {
                "success": False,
                "error_message": f"Gemini HTTP {e.response.status_code}: {e.response.text}"
            }

        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }