"""
Lecture 11 — Airflow + Ollama: Open-Meteo weather JSON → structured JSON via LLM.

Open-Meteo: https://open-meteo.com/ (no API key)
Ollama API: POST /api/chat with format json when supported by your Ollama version.
"""

from __future__ import annotations

import json
import os
from datetime import timedelta, datetime
import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable


default_args = {
    "owner": "lecture11",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

DATA_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Data_pipeline", "data")
RAW_WEATHER_FILE = os.path.join(DATA_DIR, "raw_weather.json")
STRUCTURED_WEATHER_FILE = os.path.join(DATA_DIR, "structured_weather.json")


@dag(
    dag_id="weather_unstructured_to_structured_ollama",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lecture11", "ollama", "weather", "open-meteo"],
    default_args=default_args,
    doc_md=__doc__,
)
def weather_ollama_pipeline():
    
    # Create data directory at module level (runs when DAG is parsed)
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"📁 Data directory ready: {DATA_DIR}")
    
    @task
    def fetch_open_meteo_raw() -> str:
        """Download raw forecast JSON (string) — semi-structured source for the LLM."""
        import requests

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Europe/Paris",
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        raw_json_text = resp.text
        
        # Save raw data (overwrite existing file)
        try:
            raw_data = json.loads(raw_json_text)
            with open(RAW_WEATHER_FILE, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If not valid JSON, save as raw text
            with open(RAW_WEATHER_FILE, 'w', encoding='utf-8') as f:
                f.write(raw_json_text)
        
        print(f"📝 Raw data saved to: {RAW_WEATHER_FILE}")
        return raw_json_text

    @task
    def ollama_to_structured(raw_json_text: str) -> str:
        """
        Ask Ollama to emit ONE JSON object with a fixed schema.
        Set WEATHER_PIPELINES_MOCK_OLLAMA=1 to skip the HTTP call (tests / no GPU).
        """
        if os.environ.get("WEATHER_PIPELINES_MOCK_OLLAMA") == "1":
            return json.dumps(
                {
                    "city_label": "Paris (mock)",
                    "observation_date": "2024-01-15",
                    "temp_c_current": 12.0,
                    "temp_c_max": 14.0,
                    "temp_c_min": 8.0,
                    "conditions_short": "Mock: enable Ollama for real output.",
                    "precipitation_mm": 0.1,
                }
            )

        import requests

        base = Variable.get("ollama_base_url", default_var="http://127.0.0.1:11434").rstrip("/")
        model = Variable.get("ollama_model", default_var="llama3.2")

        # Enhanced prompt for better JSON compliance
        prompt = f"""Convert the following weather API JSON into ONE JSON object with exactly these keys:
"city_label" (string, human-readable place name for the coordinates),
"observation_date" (string, ISO date YYYY-MM-DD for the first daily forecast day if present, else today UTC),
"temp_c_current" (number or null),
"temp_c_max" (number or null),
"temp_c_min" (number or null),
"conditions_short" (string, max 160 characters, plain English summary of current conditions),
"precipitation_mm" (number or null, daily sum for that first day if present).

Rules:
- Temperatures are in Celsius.
- Use null if a value is missing.
- Output must be valid JSON only with no additional text, no markdown, no explanation.
- The JSON must be on a single line.
- Use the coordinates (48.8566, 2.3522) to determine city_label is "Paris, France".

RAW INPUT (Open-Meteo API response):
{raw_json_text}

Now output ONLY the JSON object, nothing else:"""

        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
        }
        
        try:
            resp = requests.post(f"{base}/api/chat", json=body, timeout=180)
            resp.raise_for_status()
            payload = resp.json()
            content = payload.get("message", {}).get("content")
            
            if not content:
                raise RuntimeError(f"Unexpected Ollama response: {payload!r}")
            
            # If content is already a dict, use it directly
            if isinstance(content, dict):
                return json.dumps(content)
            
            # Otherwise, parse the string content
            # Clean up any markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Validate JSON
            json.loads(content)
            return content
            
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Failed to connect to Ollama at {base}. Is Ollama running? Error: {e}")
        except Exception as e:
            raise RuntimeError(f"Ollama processing failed: {e}")

    @task
    def validate_and_emit(structured_json: str) -> dict:
        """Parse and ensure required keys exist (structured contract)."""
        obj = json.loads(structured_json)
        required = {
            "city_label",
            "observation_date",
            "temp_c_current",
            "temp_c_max",
            "temp_c_min",
            "conditions_short",
            "precipitation_mm",
        }
        missing = required - obj.keys()
        if missing:
            raise ValueError(f"Structured output missing keys: {sorted(missing)}")
        
        # Type validation
        if not isinstance(obj["city_label"], str):
            raise ValueError(f"city_label must be string, got {type(obj['city_label'])}")
        if not isinstance(obj["observation_date"], str):
            raise ValueError(f"observation_date must be string, got {type(obj['observation_date'])}")
        if not isinstance(obj["conditions_short"], str):
            raise ValueError(f"conditions_short must be string, got {type(obj['conditions_short'])}")
        
        print(f"✅ Validated structured weather data: {json.dumps(obj, indent=2)}")
        
        # Add metadata to the saved data
        output_data = {
            "metadata": {
                "timestamp_utc": datetime.now().isoformat(),
                "data_source": "open-meteo",
                "llm_model": Variable.get("ollama_model", default_var="llama3.2"),
                "version": "1.0"
            },
            "weather_data": obj
        }
        
        # Save structured data (overwrite existing file)
        with open(STRUCTURED_WEATHER_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Structured data saved to: {STRUCTURED_WEATHER_FILE}")
        print(f"📊 Weather summary: {obj['city_label']} - "
              f"Current: {obj['temp_c_current']}°C, "
              f"Range: {obj['temp_c_min']}°C to {obj['temp_c_max']}°C, "
              f"Precipitation: {obj['precipitation_mm']}mm")
        
        return obj

    # Define the task dependencies
    raw = fetch_open_meteo_raw()
    structured = ollama_to_structured(raw)
    validated = validate_and_emit(structured)


dag = weather_ollama_pipeline()