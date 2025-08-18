"""Observability and tracing configuration using Langfuse."""

import os

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

# Global Langfuse instance
_langfuse_instance: Langfuse | None = None


def get_langfuse_instance() -> Langfuse | None:
    """Get the global Langfuse instance."""
    global _langfuse_instance

    if _langfuse_instance is None:
        # Initialize Langfuse if environment variables are present
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST")

        if public_key and secret_key:
            try:
                _langfuse_instance = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host,
                )
                print(f"✅ Langfuse initialized successfully (host: {host})")
            except Exception as e:
                print(f"⚠️  Failed to initialize Langfuse: {e}")
                _langfuse_instance = None
        else:
            print("ℹ️  Langfuse not configured (missing LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY)")

    return _langfuse_instance


def get_langfuse_callback():
    """Get the Langfuse callback handler for LangChain integration."""
    langfuse = get_langfuse_instance()
    if langfuse:
        return CallbackHandler()
    return None


def is_langfuse_enabled() -> bool:
    """Check if Langfuse is properly configured and enabled."""
    return get_langfuse_instance() is not None


def create_trace(name: str, user_id: str | None = None, session_id: str | None = None, **metadata):
    """Create a new Langfuse trace - simplified for Langfuse 3.x compatibility."""
    # For now, we'll rely mainly on the callback handler for automatic tracing
    # Manual trace creation API has changed in Langfuse 3.x
    if is_langfuse_enabled():
        print(f"🔍 Starting traced workflow: {name} (session: {session_id})")
    return {"name": name, "session_id": session_id, "user_id": user_id, "metadata": metadata}


def flush_langfuse():
    """Flush any pending Langfuse events."""
    langfuse = get_langfuse_instance()
    if langfuse:
        langfuse.flush()
