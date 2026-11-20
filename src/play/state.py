from typing_extensions import TypedDict
from typing import Annotated, Literal
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages] # Annotated[type, information that tells Langgraph what function to execute ádd_messages]
    corrections: Annotated[list, add_messages]
    session_evaluation: dict
    scene_info: dict
    goal_achieved: bool
    adventure_id: int
    scene_id: int
    student_id: int
