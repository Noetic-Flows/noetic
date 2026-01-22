from typing import Any, Dict
import jsonpointer

def resolve_pointer(data: Dict[str, Any], pointer: str, fallback: Any = None) -> Any:
    """
    Resolves a JSON Pointer against a data dictionary.
    Safe wrapper around jsonpointer.
    """
    if not pointer.startswith("/"):
        pointer = "/" + pointer
        
    try:
        return jsonpointer.resolve_pointer(data, pointer, default=fallback)
    except Exception:
        return fallback
