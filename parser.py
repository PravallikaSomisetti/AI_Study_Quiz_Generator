import json

def parse_llm_json(raw_text: str) -> list:
    """
    Cleans up, normalizes, and validates the incoming JSON data structure from the LLM.
    """
    try:
        # Edge cleaning if markdown leaks through despite instructions
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.split("```json")[1]
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("```", 1)[0]
        clean_text = clean_text.strip()
        
        data = json.loads(clean_text)
        if "quiz" in data:
            return data["quiz"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("JSON does not contain an accessible quiz array list structure.")
    except Exception as e:
        raise ValueError(f"Failed parsing LLM payload to valid Quiz Dict array: {str(e)}")