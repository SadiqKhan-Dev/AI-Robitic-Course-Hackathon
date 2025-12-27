"""Main entry point for RAG Pipeline."""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def run_cli():
    """Run CLI mode."""
    from src.agents.rag_agent import get_rag_agent

    agent = get_rag_agent()

    print("=" * 60)
    print("RAG Agent - AI Robotics Book Assistant")
    print("=" * 60)
    print("\nAsk me anything about the AI Robotics Book!")
    print("(Type 'quit' or 'exit' to stop)\n")

    while True:
        try:
            question = input("You: ").strip()
            if question.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break
            if not question:
                continue

            print("\nThinking...")
            response = agent.generate_response(question)

            print(f"\nAssistant: {response['answer']}")
            print(f"\n[Sourced from {len(response['sources'])} documents]")
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_streamlit():
    """Run Streamlit UI."""
    import streamlit
    streamlit.run("src.ui.app", main_script_path=str(Path(__file__).parent / "app.py"))


def run_api():
    """Run FastAPI server."""
    import uvicorn
    from src.api.server import app

    uvicorn.run(app, host="0.0.0.0", port=8000)


def check_status():
    """Check system status."""
    from src.services.qdrant_service import get_qdrant_service
    from src.services.embedding_service import get_embedding_service

    print("Checking RAG Pipeline Status...\n")

    # Check Qdrant
    print("1. Qdrant Vector Database:")
    try:
        qdrant = get_qdrant_service()
        info = qdrant.get_collection_info()
        print(f"   ✓ Connected")
        print(f"   ✓ Collection: {qdrant.collection_name}")
        print(f"   ✓ Documents: {info['points_count']}")
        print(f"   ✓ Status: {info['status']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Check Embedding Service
    print("\n2. Embedding Service:")
    try:
        embed = get_embedding_service()
        print(f"   ✓ Model: {embed.model_name}")
        print(f"   ✓ Dimension: {embed.dimension}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n3. Gemini LLM:")
    print("   ? Requires GEMINI_API_KEY in config.yaml")
    print("   Get your key from: https://aistudio.google.com/app/apikey")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RAG Pipeline CLI")
    parser.add_argument(
        "command",
        choices=["cli", "ui", "api", "status"],
        help="Command to run",
    )

    args = parser.parse_args()

    if args.command == "cli":
        run_cli()
    elif args.command == "ui":
        run_streamlit()
    elif args.command == "api":
        run_api()
    elif args.command == "status":
        check_status()


if __name__ == "__main__":
    main()
