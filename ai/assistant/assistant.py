"""Public assistant entry point; implementation lives in service.py."""
from ai.assistant.service import process_question

__all__ = ["process_question"]

if __name__ == "__main__":
    import json
    for question in ("Which facility has the highest energy consumption?", "What are today's biggest problems?"):
        print(json.dumps(process_question(question), indent=2, default=str))
