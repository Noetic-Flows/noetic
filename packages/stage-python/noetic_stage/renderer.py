from typing import Any, Dict, List, Union
from .schema import Component, Binding, Text, Button, Column, Row, Container, ForEach, Conditional, Intent, RenderEvent
from .bindings import resolve_pointer
from noetic_knowledge import WorldState

try:
    from fastui import components as c
    from fastui.events import PageEvent, GoToEvent
except ImportError:
    c = None
    PageEvent = None
    GoToEvent = None

class Renderer:
    def render(self, intent: Intent) -> RenderEvent:
        if intent.type == "display_message":
            return RenderEvent(
                type="ui_card",
                payload={
                    "component": "MessageCard",
                    "content": intent.content.get("text", "")
                }
            )
        return RenderEvent(type="unknown", payload={})

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

        # Enrich context: Map entities by 'name' attribute for easier binding
        if "entities" in context:
            # We must be careful not to mutate the original context if it's shared
            entities = context["entities"]
            enriched_entities = entities.copy()
            for eid, entity in entities.items():
                if isinstance(entity, dict) and "attributes" in entity:
                    name = entity["attributes"].get("name")
                    if name:
                        enriched_entities[name] = entity
            
            # Create a shallow copy of context with enriched entities
            context = context.copy()
            context["entities"] = enriched_entities

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
            action_id = self._resolve(node.action_id, context)
            on_click = GoToEvent(url=f"/?event={action_id}") if GoToEvent else None
            return c.Button(text=str(text), on_click=on_click)
            
        elif isinstance(node, Column):
            children = [self._visit(child, context) for child in node.children]
            return c.Div(components=children, class_name="flex flex-col")
            
        elif isinstance(node, Row):
            children = [self._visit(child, context) for child in node.children]
            return c.Div(components=children, class_name="flex flex-row")
            
        elif isinstance(node, ForEach):
            items = self._resolve(node.items, context)
            if isinstance(items, dict):
                # Use a list of unique values to avoid duplicates from name-aliasing
                seen_ids = set()
                unique_items = []
                for val in items.values():
                    if isinstance(val, dict) and "id" in val:
                        oid = str(val["id"])
                        if oid not in seen_ids:
                            seen_ids.add(oid)
                            unique_items.append(val)
                    else:
                        unique_items.append(val)
                items = unique_items
            if not isinstance(items, list):
                items = []
            
            children = []
            for item in items:
                child_context = context.copy()
                child_context[node.var] = item
                children.append(self._visit(node.template, child_context))
            
            return c.Div(components=children, class_name="flex flex-col")
        
        elif isinstance(node, Conditional):
            condition = self._resolve(node.condition, context)
            # Evaluate truthiness
            if condition:
                return self._visit(node.true_child, context)
            elif node.false_child:
                return self._visit(node.false_child, context)
            else:
                return c.Div(components=[]) # Empty div

        return c.Text(text=f"Unknown Component: {node.type}")
