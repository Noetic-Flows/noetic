from __future__ import annotations
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field

class Intent(BaseModel):
    type: str
    content: Dict[str, Any]

class RenderEvent(BaseModel):
    type: str
    payload: Dict[str, Any]

# A2UI Schema

class Component(BaseModel):
    type: str
    id: Optional[str] = None
    style: Optional[Dict[str, Any]] = None

class Binding(BaseModel):
    bind: str # JSON Pointer
    fallback: Optional[Any] = None

class Text(Component):
    type: Literal["Text"] = "Text"
    content: Union[str, Binding]

class Button(Component):
    type: Literal["Button"] = "Button"
    label: Union[str, Binding]
    action_id: Union[str, Binding]

AnyComponent = Union["Column", "Row", "Text", "Button", "ForEach", "Component"]

class Container(Component):
    children: List[AnyComponent]

class Column(Container):
    type: Literal["Column"] = "Column"

class Row(Container):
    type: Literal["Row"] = "Row"

class ForEach(Component):
    type: Literal["ForEach"] = "ForEach"
    items: Union[List[Any], Binding]
    template: AnyComponent # The template to render for each item
    var: str = "item" # The variable name to expose in the child scope

class Conditional(Component):
    type: Literal["Conditional"] = "Conditional"
    condition: Union[bool, Binding]
    true_child: AnyComponent
    false_child: Optional[AnyComponent] = None

AnyComponent = Union["Column", "Row", "Text", "Button", "ForEach", "Conditional", "Component"]

class Container(Component):
    children: List[AnyComponent]

class Column(Container):
    type: Literal["Column"] = "Column"

class Row(Container):
    type: Literal["Row"] = "Row"

# Update forward refs
Column.model_rebuild()
Row.model_rebuild()
ForEach.model_rebuild()
Conditional.model_rebuild()

def parse_component(data: Dict[str, Any]) -> AnyComponent:
    """
    Parses a component dictionary into the appropriate A2UI subclass.
    """
    ctype = data.get("type")
    if ctype == "Column":
        return Column(**data)
    if ctype == "Row":
        return Row(**data)
    if ctype == "Text":
        return Text(**data)
    if ctype == "Button":
        return Button(**data)
    if ctype == "ForEach":
        return ForEach(**data)
    if ctype == "Conditional":
        return Conditional(**data)
    
    return Component(**data)


class Binding(BaseModel):
    bind: str # JSON Pointer
    fallback: Optional[Any] = None

class Text(Component):
    type: Literal["Text"] = "Text"
    content: Union[str, Binding]

class Button(Component):
    type: Literal["Button"] = "Button"
    label: Union[str, Binding]
    action_id: Union[str, Binding]

AnyComponent = Union["Column", "Row", "Text", "Button", "ForEach", "Component"]

class Container(Component):
    children: List[AnyComponent]

class Column(Container):
    type: Literal["Column"] = "Column"

class Row(Container):
    type: Literal["Row"] = "Row"

class ForEach(Component):
    type: Literal["ForEach"] = "ForEach"
    items: Union[List[Any], Binding]
    template: AnyComponent # The template to render for each item
    var: str = "item" # The variable name to expose in the child scope

class Conditional(Component):
    type: Literal["Conditional"] = "Conditional"
    condition: Union[bool, Binding]
    true_child: AnyComponent
    false_child: Optional[AnyComponent] = None

AnyComponent = Union["Column", "Row", "Text", "Button", "ForEach", "Conditional", "Component"]

class Container(Component):
    children: List[AnyComponent]

class Column(Container):
    type: Literal["Column"] = "Column"

class Row(Container):
    type: Literal["Row"] = "Row"

# Update forward refs
Column.model_rebuild()
Row.model_rebuild()
ForEach.model_rebuild()
Conditional.model_rebuild()

def parse_component(data: Dict[str, Any]) -> AnyComponent:
    """
    Parses a component dictionary into the appropriate A2UI subclass.
    """
    ctype = data.get("type")
    if ctype == "Column":
        return Column(**data)
    if ctype == "Row":
        return Row(**data)
    if ctype == "Text":
        return Text(**data)
    if ctype == "Button":
        return Button(**data)
    if ctype == "ForEach":
        return ForEach(**data)
    if ctype == "Conditional":
        return Conditional(**data)
    
    return Component(**data)
