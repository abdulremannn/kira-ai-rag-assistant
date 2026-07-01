"""Local CLI for quick testing (no server needed)."""
import logging

from app.config import settings
from app.service import RagService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def main():
    settings.validate()
    service = RagService()
    print(f"Ready — {len(service.retriever.docs)} KB docs loaded. Type 'exit' to quit.\n")

    session_id = "cli-local-session"
    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        result = service.ask(q, session_id=session_id)
        print(f"\nBot: {result['answer']}")
        if not result["refused"]:
            top = result["sources"][0]
            print(f"  (top match: {top['title']} — score {top['score']})")
        print()


if __name__ == "__main__":
    main()
