from __future__ import annotations
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field

# A2UI Schema

class Binding(BaseModel):
    bind: str # JSON Pointer
    fallback: Optional[Any] = None

class Component(BaseModel):
    type: str
    id: Optional[str] = None
    style: Optional[Dict[str, Any]] = None

class Container(Component):
    children: List[Union[Component, Any]] # Any for recursion

class Text(Component):
    type: Literal["Text"] = "Text"
    content: Union[str, Binding]

class Button(Component):
    type: Literal["Button"] = "Button"
    label: Union[str, Binding]
    action_id: str

class Column(Container):
    type: Literal["Column"] = "Column"

class Row(Container):
    type: Literal["Row"] = "Row"

class ForEach(Component):
    type: Literal["ForEach"] = "ForEach"
    items: Union[List[Any], Binding]
    template: Union[Component, Any] # The template to render for each item
    var: str = "item" # The variable name to expose in the child scope

# Update forward refs
Container.model_rebuild()
ForEach.model_rebuild()
