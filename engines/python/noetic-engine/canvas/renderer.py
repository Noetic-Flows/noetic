from typing import Any, Dict, List, Union
from .schema import Component, Binding, Text, Button, Column, Row, Container, ForEach
from .bindings import resolve_pointer
from noetic_engine.knowledge import WorldState

try:
    from fastui import components as c
    from fastui.events import BackEvent
except ImportError:
    c = None
    BackEvent = None

class CanvasRenderer:
    def __init__(self):
        pass

    def render(self, root: Component, context: Dict[str, Any]) -> Any:
        """
        Recursively transforms the A2UI Component tree into a FastUI component tree,
        resolving bindings against the provided context (merged state).
        """
        if c is None:
            return {"error": "FastUI not installed"}

        return self._visit(root, context)

    def _resolve(self, value: Union[str, Binding, Any], context: Dict[str, Any]) -> Any:
        if isinstance(value, Binding):
            return resolve_pointer(context, value.bind, value.fallback)
        if isinstance(value, dict) and "bind" in value:
            return resolve_pointer(context, value["bind"], value.get("fallback"))
        return value

    def _visit(self, node: Component, context: Dict[str, Any]) -> Any:
        if isinstance(node, Text):
            content = self._resolve(node.content, context)
            return c.Text(text=str(content))
            
        elif isinstance(node, Button):
            text = self._resolve(node.label, context)
            on_click = BackEvent(type=node.action_id) if BackEvent else None
            return c.Button(text=str(text), on_click=on_click)
            
        elif isinstance(node, Column):
            children = [self._visit(child, context) for child in node.children]
            return c.Div(components=children, class_name="flex flex-col")
            
        elif isinstance(node, Row):
            children = [self._visit(child, context) for child in node.children]
            return c.Div(components=children, class_name="flex flex-row")
            
        elif isinstance(node, ForEach):
            items = self._resolve(node.items, context)
            if not isinstance(items, list):
                items = []
            
            children = []
            for item in items:
                child_context = context.copy()
                child_context[node.var] = item
                children.append(self._visit(node.template, child_context))
            
            return c.Div(components=children, class_name="flex flex-col")

        return c.Text(text=f"Unknown Component: {node.type}")
