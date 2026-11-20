import datetime
import openai
from openai import OpenAI, APIConnectionError
from flask_login import current_user
from flask import session
import os
import json
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from typing import Literal
from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from src.play.state import State
from src.data_manager import DataManager as dm

api_key = os.environ.get("OPENAI_API_KEY")
MAX_CYCLE = 0

llm=init_chat_model(model="gpt-4.1-mini", temperature=0.4)


class MessageClassifier(BaseModel):
    action_to_take: Literal["continue", "finish"] = Field(
        ...,         # make this argument mandatory
        description="Classify if the goal of the conversation is achieved or not."
    )
    missing: str|None = Field(
        default=None, # make this argument optional
        description="What is currently missing in the conversation to achieve the goal?"
    )


class SessionEvaluationScheme(BaseModel):
    session_achievement: str = Field(
        ...,         # make this argument mandatory
        description="What did the student achieve in this session? E.g. what information did the student gain?"
    )

    estimated_CEFR_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = Field(
        ...,         # make this argument mandatory
        description="Classify the CEFR level of the student use of communication. Make an estimate as good as you can."
    )
    words_successfully_used: str|None = Field(
        default=None, # make this argument optional
        description="What words did the student use that were correct and part of the provided vocabulary. Separate the words via ';'"
    )
    phrases_successfully_used: str|None = Field(
        default=None, # make this argument optional
        description="What phrases did the student use that were grammatically correct. Separate phrases via ';'"
    )
    grammar_tips: str|None = Field(
        default=None, # make this argument optional
        description="What tips can you give the student to improve for a next session"
    )

graph_builder = StateGraph(State)


def actor_setup(scene_info):
    language = scene_info.get("target_language", "Portuguese")

    system_prompt = (
        "You are a language teacher, playing a role in an adventure. You stick to your role. Your task is to speak in the target language and force "
        "the student to speak in the target language. E.g. if the student says something in English and the target language is Italian, you should state that you don't understand in Italian. "
        "IMPORTANT INSTRUCTION: This conversation consists of many steps where a student says something, "
        "and you respond based only based on what the student says. Do not invent anything outside of the STEPS included below AND with what the student says or asks you."
        "BAD EXAMPLE: "
        "Student: 'Hello, how are things going?'"
        "You: 'May I ask you a question, by any chance, are you looking for a backpack that seems to have gone missing?" 
        "This is wrong as you started to talk about the backpack. This must be done by the student "
        "CORRECT EXAMPLE: "
        "You: 'Hello how are you'. "
        "Student: I am fine"
        "You: how can I help you?"
        "Student: I am looking for my backpack. I lost it. Did you find one?"
        "If the student uses a word that is not part of the target language, indicate you don't understand that specific word."
        "INFORMATION ABOUT YOUR CHARACTER: "
        f"Your name is {scene_info.get('persona',{'first_name': 'Unknown'}).get('first_name','unknown')} "
        f"{scene_info.get('persona',{'last_name': 'unknown'}).get('last_name','unknown')} "
        f"and you are a {scene_info.get('persona').get('role','no role')} and {scene_info['persona']['gender']}."
        f"Your character is:  {scene_info['persona'].get('description', 'friendly')}. You only speak in {language} and expect the "
        f"student to speak also in {language}. If the student does not, indicate you don't understand."
        f"The goal of the complete conversation is: {scene_info.get('goal','undefined')}."
        f" Important, your message is only one step in the whole conversation. Basically one of the many steps. "
        f" These are the steps you have to follow:\n "
        f"{scene_info.get('steps','not defined')}."
        "An example reply could simply : 'hello, how can I help you' (in the correct language)"
        )
    return system_prompt

def verification_prompt_definition(scene_info: dict) -> str:
    language = scene_info.get("target_language", "Portuguese")

    system_prompt = f"""
    You are a language corrector for the target language {language}. Your task is to correct the language of the phrase provided by the student. It is important to realize
    that the language is spoken, not written. Please take this in consideration when correcting.
    You are provided with the full conversation so far. IMPORTANT: You only evaluate and correct the last message HumanMessage in the conversation. 
    You do not evaluate any other message nor you invent a message to evaluate.
    Example in Portugues language:
    HumanMessage: 'Eu viu uma gato'
    Correction: 'Eu vi um gato'
    HumanMessage: 'Eu vi um gato'
    Correction: '✔'
    The same handling applies to other languages.
    """
    return system_prompt


def persona_actor(state:State):
    try:
        print_state("Persona_actor received state: \n:", state)

        response = llm.invoke(state["messages"])
        return {
            "messages" : [
                AIMessage(content=response.content, type="ai")
            ]
        }
    except (APIConnectionError, openai.BadRequestError) as e:
        return f"Agent not available: {e}"


def message_corrector(state:State):
    print_state(f"message_corrector received state: \n", state)
    background = []
    background.append(state['corrections'][0])
    for message in state['messages'][1:-1]:
        background.append(message)
    print("background: \n", background)
    try:
        response = llm.invoke(background)
        return {
            "corrections" : [
                AIMessage(content=response.content, type="ai")
            ]
        }
    except (APIConnectionError, openai.BadRequestError) as e:
        return None, None


def router(state:State):
    conversation = state["messages"][1:]
    goal = state["scene_info"].get("goal", "No goal defined")
    language = state["scene_info"].get("target_language", "Portuguese")
    cycle_counter = session['cycle_count']
    print(f"conversation so far: \n{conversation}")
    print(f"goal: {goal}")
    prompt = f"""
    You are evaluating a role-play between a language student and an actor playing a specific role where the actor should help 
    the student to achieve the goal of this conversation (see Goal definition below). The role play is in {language} language. Please analyze carefully the conversation
    and check if the goal of the conversation was achieved, ie. based upon the conversation in {language} you make a decision if the goal was achieved or not. 
    Based on the outcome you will decide the values of 2 fields
    Field 1: 'action_to_take' : 
        - 'finish': if the goal of the conversation is achieved
        - 'continue': if the goal of the conversation is not achieved and the student need to provide more input
    
    Respond in JSON with 'action_to_take' key containing 'finish' or 'continue'    
    in case no goal is defined use output 'finish'
    Field 2: 'missing' : A string
        - In case action_to_take is 'continue', list here what is currently missing in the conversation to achieve the goal?
        - In case action_to_take is 'finish', return an empty string

    GOAL DEFINITION:
    {goal}
    
    CONVERSATION:
    {conversation}

    """
    # the system_prompt need to be added to the messages. This can not be done by updating the
    # state within the node as updating a state within a node is not allowed. Therefor
    # the following lines extract the required information from the state and places it in
    # messages
    system_message = [SystemMessage(content=prompt, type="system")]

    human_messages = [msg for msg in state["messages"] if isinstance ( msg, HumanMessage)]
    ai_messages = [msg for msg in state["messages"] if isinstance ( msg, AIMessage)]
    messages = system_message + human_messages + ai_messages

    classifier_llm = llm.with_structured_output(MessageClassifier, method="json_schema")
    # Here the method 'json_schema' is used which is keeping the output limited to the provided BaseModel
    # There is also the option of 'json_mode' which would only return a json object, but possibly with other
    # keys
    next_step = classifier_llm.invoke(messages)
    print(next_step, type(next_step))

    if next_step.action_to_take == "finish" or cycle_counter > (MAX_CYCLE-1):
        goal_achieved = True
    elif next_step.action_to_take == "continue":
        goal_achieved = False
        print("goal_achieved = False, this is missing: ", next_step.missing)
    else:
        goal_achieved = False
    return { "goal_achieved": goal_achieved }


def session_evaluator(state:State):
    """
    The scene was completed by the student. All relevant information must be extracted from the transcript and stored
    in the session table. Also
    """
    print_state("Session_Evaluator:\n", state)
    if not current_user.is_authenticated:
        return state

    level = state["scene_info"]["level"]
    language = state["scene_info"]["target_language"]
    title = state['scene_info']['title']
    goal = state['scene_info']['goal']
    premise = state['scene_info']['premise']
    goal_achieved = state["goal_achieved"]
    prompt = f"""
    You are a language professor evaluating a role-play conversation between a student (HumanMessage) and a persona (AIMessage).

    The student's current CEFR level for the {language} language is: {level} 
    
    The scene with title : {title} has the following goal:
    {goal}
    
    This is the premise of the scene: {premise} 
    The goal achievement status is:
    {goal_achieved}
    
    Evaluate ONLY the student's messages.
    
    Evaluation guidelines:
    - Describe what the student achieved during the scene.
    - Estimate the CEFR level demonstrated in this conversation.
    - Identify vocabulary that the student used correctly.
    - Identify successful phrases, quoting the student's actual words.
    - Provide specific grammatical tips based on observed mistakes.
    - Do not invent words or phrases the student did not use.
    - Be encouraging, constructive, and concise.
    - If a category has no examples, return an empty list.and you are evaluating a role-play session between a student (HumanMessage) and a 
        persona (AIMessage). 
        The student currently has level {level} and it is your task to evaluate the conversation and 
        use the provided model to answer the following:
    
    The output must be provided in a JSON format.
    """
    system_message = [SystemMessage(content=prompt, type="system")]
    human_messages = [msg for msg in state["messages"] if isinstance ( msg, HumanMessage)]
    ai_messages = [msg for msg in state["messages"] if isinstance ( msg, AIMessage)]
    evaluations = system_message + human_messages + ai_messages

    evaluator_llm = llm.with_structured_output(SessionEvaluationScheme, method="json_schema")
    evaluation = evaluator_llm.invoke(evaluations)
    evaluation_dict = evaluation.model_dump()

    # Prepare the state for storage. State is only updated on return. We'd like to
    # store the updated state in the DB, including the evaluation_dict
    # 1. Prepare state updates
    updates = {
        "session_evaluation": evaluation_dict
    }

    # 3. Create an updated copy of the state
    updated_state = {**state, **updates}
    dm.store_session_data(state["adventure_id"], state["scene_id"], state["student_id"], updated_state)
    return {"session_evaluation": evaluation_dict}


def print_state(opening_text:str, state:State):
    print("Printing the state" + opening_text + "\n")
    for keys in state.keys():
        print(f"{keys}: {state[keys]}")

def routing_check(state:State)->bool:
    print("ROUTING_CHECK", state.get("goal_achieved", False))
    return state.get("goal_achieved", False)

graph_builder.add_node("persona_actor", persona_actor)
graph_builder.add_node("message_corrector", message_corrector)
graph_builder.add_node("router", router)
graph_builder.add_node("session_evaluator", session_evaluator)

graph_builder.add_edge(START, "persona_actor")
graph_builder.add_edge("persona_actor", "message_corrector")
graph_builder.add_edge("message_corrector", "router")
graph_builder.add_conditional_edges(
    "router",
    routing_check,
    {
        True: "session_evaluator",
        False: END
    }
)
# graph_builder.add_conditional_edges(
#     "routing_check",
#     lambda state: state.get("goal_achieved"),
#     {True: "session_evaluator", False: "END"})
# graph_builder.add_edge("router", "session_evaluator")
graph_builder.add_edge("session_evaluator", END)
checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer)


def get_persona_reply(scene_id:int, adventure_id:int, student_message:str, thread_id) -> tuple:
    student_adventure_status, result = dm.get_full_student_adventure_data(adventure_id, current_user.student_id)
    if "successful" not in result or not student_adventure_status:
        return None, "could not derive the scene"
    scene_info = {}
    scene_info["target_language"] = student_adventure_status["target_language"]
    scene_info["title"] = student_adventure_status["title"]
    scene_info["level"] = student_adventure_status["level"]
    scene_info["premise"] = student_adventure_status["premise"]

    all_adventure_scenes = student_adventure_status["scenes"]
    scene = [scene for scene in all_adventure_scenes if scene.get("scene_id",-1) == scene_id]
    if not isinstance(scene, list) or len(scene) != 1:
        return None, "could not derive the scene"

    scene_info["persona"] = scene[0]["persona"]
    scene_info["situation"] = scene[0]["situation"]
    scene_info["goal"] = scene[0]["goal"]
    scene_info["steps"] = scene[0]["steps"]
    scene_info["exit"] = scene[0]["exit"]
    scene_info["ending"] = scene[0]["ending"]

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    state = graph.get_state(config)
    print("state: ", type(state))
    if state.values:
        print("Existing conversation. Here is state: ", state.values)
        state = {
            "messages" : [
                HumanMessage(content=student_message)
            ],
            "corrections": [
                HumanMessage(content=student_message)
            ],
            "adventure_id": adventure_id,
            "scene_id": scene_id,
            "student_id": current_user.student_id,
        }
        state = graph.invoke(state, config=config)

    else:
        config = {"configurable": {"thread_id": thread_id}}
        state = {
            "messages" : [
                SystemMessage(content=actor_setup(scene_info)),
                # SystemMessage(content="Tell me what you understood of this assignment"),
                HumanMessage(content=student_message)
            ],
            "scene_info": scene_info,
            "corrections": [
                SystemMessage(content=verification_prompt_definition(scene_info)),
                HumanMessage(content=student_message)
            ],
            "goal_achieved": False,
            "adventure_id": adventure_id,
            "scene_id": scene_id,
            "student_id": current_user.student_id,
        }
        print_state("the state is:", state)
        state = graph.invoke(state, config=config)
    return state["messages"][-1].content, state
