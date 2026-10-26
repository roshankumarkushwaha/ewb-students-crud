"""Optional local Ollama assistant. It never executes model-generated SQL."""
import json
import urllib.error
import urllib.request

from app.crud import export_students


class OllamaUnavailableError(Exception):
    pass

def ask_ollama(question: str, model: str = "llama3.2:1b"):
    records = export_students()
    context = [{
        "id": r["id"], "name": r["name"], "date_of_birth": r["date_of_birth"],
        "email": r["email"], "phone": r["phone"], "course": r["course"],
        "enrollment_date": r["enrollment_date"]
    } for r in records[:200]]
    prompt = (
        "Answer only from this student data JSON. If data does not support an answer, say so. "
        "Do not change records or execute SQL. Be concise.\n\n"
        f"DATA:\n{json.dumps(context, ensure_ascii=False)}\n\nQUESTION: {question}"
    )
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.1}}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OllamaUnavailableError(
            "Ollama is unavailable at 127.0.0.1:11434. Start Ollama and pull the selected model."
        ) from exc
    return {"question": question, "answer": result.get("response", "").strip(), "model": model}
