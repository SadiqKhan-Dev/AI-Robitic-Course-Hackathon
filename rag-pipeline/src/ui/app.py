"""Streamlit UI for RAG Agent - AI Robotics Book Assistant."""
import streamlit as st
import sys
from pathlib import Path

# Add rag-pipeline to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.agents.rag_agent import get_rag_agent
from src.services.qdrant_service import get_qdrant_service


def load_config():
    """Load UI configuration."""
    import yaml
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)["ui"]


def display_sources(sources):
    """Display source information."""
    if sources:
        with st.expander(f"Sources ({len(sources)} found)", expanded=False):
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Unknown")
                url = source.get("url", "")
                score = source.get("score", 0)

                col1, col2 = st.columns([3, 1])
                with col1:
                    if url:
                        st.markdown(f"**{i}. [{title}]({url})**")
                    else:
                        st.markdown(f"**{i}. {title}**")
                with col2:
                    st.caption(f"Relevance: {score:.2f}")


def main():
    """Main Streamlit application."""
    config = load_config()

    st.set_page_config(
        page_title=config["title"],
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main-header { text-align: center; padding: 1rem 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {config['title']}</h1>
        <p>{config['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = get_rag_agent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.agent_ready = False
            st.session_state.agent_error = str(e)

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This AI assistant answers questions about the **Humanoid AI Book** using:
        - **Qdrant** Vector Database
        - **Sentence Transformers** Embeddings
        - **Google Gemini** LLM
        """)
        st.divider()

        st.header("Collection Info")
        try:
            qdrant = get_qdrant_service()
            info = qdrant.get_collection_info()
            st.write(f"Status: {info['status']}")
            st.write(f"Documents: {info['points_count']}")
        except Exception as e:
            st.error(f"Could not fetch collection info: {e}")

        st.divider()
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    # Main chat area
    if not st.session_state.get("agent_ready", False):
        st.error("Agent not ready. Please check your configuration.")
        if st.session_state.get("agent_error"):
            st.error(f"Error: {st.session_state['agent_error']}")
        return

    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                display_sources(message["sources"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the AI Robotics Book..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base and generating response..."):
                try:
                    response = st.session_state.agent.generate_response(prompt)
                    st.markdown(response["answer"])
                    display_sources(response["sources"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response["sources"],
                    })
                except Exception as e:
                    st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
