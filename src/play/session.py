import datetime
import src.play.openai_gpt_4o_mini as current_model
import src.play.openai_gpt_4o_mini as current_model
import openai
from openai import OpenAI, APIConnectionError
from flask_login import current_user
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from src.data_manager import DataManager as dm

api_key = os.environ.get("OPENAI_API_KEY")


llm=init_chat_model(model="gpt-4.1-mini", temperature=0.4)

class Transcript():
    def __init__(self, adventure_id:int, scene_id:int, persona_id):
        start_time = datetime.datetime.now(datetime.UTC)
        end_time = datetime.datetime.now(datetime.UTC)
        # transcript = client.transcribe_audio()
        self.transcript = {}
        self.transcript["start_time"] = start_time
        self.transcript["end_time"] = end_time
        self.transcript["adventure_id"] = adventure_id
        self.transcript["scene_id"] = scene_id
        self.transcript["student_id"] = current_user.student_id
        self.transcript["persona"] = persona_id
        self.scene_transcript = [{}]

    def add_conversation_part(self, individual:str, conversation_part:str):
        conversation_part = {"speaker": individual,
                             "conversation": conversation_part.strip()
                             }
        self.scene_transcript.append(conversation_part)

    def get_start_time(self):
        return self.transcript["start_time"]

    def set_end_time(self, new_end_time):
        self.transcript["end_time"] = new_end_time

    def summarize_transcript(self):
        pass

    def __str__(self):
        transcription =  f"{self.transcript['start_time']} - {self.transcript['end_time']}\n"
        transcription += f"Adventure_id: {self.transcript['adventure_id']}\n"
        transcription += f"Scene_id: {self.transcript['scene_id']}\n"
        transcription += f"Student_id: {self.transcript['student_id']}\n"
        transcription += f"Persona: {self.transcript['persona']}\n"
        for conversation in self.scene_transcript:
            if len(conversation) != 0:
                transcription += f"Conversation: {conversation.get("speaker","")}: {conversation.get("conversation", "")}\n"

        return transcription

    def __repr__(self):
        transcription =  f"{self.transcript['start_time']}"

        return transcription

class State(TypedDict):
    messages: Annotated[list, add_messages] # Annotated[type, information that tells Langgraph what function to execute ádd_messages]
    corrected_text: Annotated[list, add_messages]
    scene_info: dict
    goal_achieved: bool


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

def verification_prompt_definition(state: State) -> str:
    language = state["scene_info"].get("target_language", "Portuguese")

    system_prompt = f"""
    You are a language use corrector for the target language {language}. Your task is to correct the language of the phrase provided by the student. It is important to realize
    that the language is spoken, not written. Please take this in consideration when correcting.
    Example for portugues language:
    Student: 'Eu viu uma gato'
    You: 'Eu vi um gato'
    """
    return system_prompt


def persona_actor(state:State):
    # prompt = "Please check the current state of the conversation and provide a next message which is aligned with the steps. "
    try:
        print("Used prompt:")
        for message in state["messages"]:
            print("Prompt part: ", message)
        response = llm.invoke(state["messages"])

        # added_message = {"messages" : [response.content]}

        state = {
            "messages" : [
                AIMessage(content=response.content)
            ]
        }
        print("content of added message")
        print(state)
        return state
    except (APIConnectionError, openai.BadRequestError) as e:
        return f"Agent not available: {e}"

def message_evaluator(state:State):
    print(f"message_evaluator received state: \n{state}")
    system_prompt=verification_prompt_definition(state)
    return {"messages" : []}

#     try:
#         prompt = ("Evaluate the following message on used vocabulary, grammar and fluency. "
#               "Take a note that the person spoke this message which should change the evaluation from a written interaction"
#               "Provide the evaluation constructively, start with a positive remark, followed by a constructive remark"
#               "followed again with a positive remark what would occur if the person improved a next time"
#               f" message:\n{state['messages'][-2]}"
#               "Example: Well done, you were almost perfect, but you used the word 'house' in stead of 'casa'"
#               "if you improve this a next time, it will be even better")
#
#         evaluations = {"evaluations" : [llm.invoke(state["messages"][-1].content)]}
#         print("content of evaluations within state:")
#         for message in state["messages"]:
#             print(message)
#         return evaluations
#     except (APIConnectionError, openai.BadRequestError) as e:
#         return f"Agent not available: {e}"


def router(state:State):
    return state


def session_evaluator(state:State):
    return state


graph_builder.add_node("persona_actor", persona_actor)
graph_builder.add_node("message_evaluator", message_evaluator)
graph_builder.add_node("router", router)
graph_builder.add_node("session_evaluator", session_evaluator)

graph_builder.add_edge(START, "persona_actor")
graph_builder.add_edge("persona_actor", "message_evaluator")
graph_builder.add_edge("message_evaluator", "router")
graph_builder.add_edge("router", "session_evaluator")
graph_builder.add_edge("session_evaluator", END)
checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer)


def prompt_generator(role:str, prompt:str, transcript:Transcript):
    pass

def get_persona_reply(scene_id:int, adventure_id:int, student_message:str, thread_id) -> tuple:
    ts = Transcript(adventure_id, scene_id, 0)
    student_adventure_status, result = dm.get_full_student_adventure_data(adventure_id, current_user.student_id)
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

    if state.values:
        print("Existing conversation. Here is state: ", state.values)
        state = {
            "messages" : [
                HumanMessage(content=student_message)
            ]
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
            "corrected_text": [],
            "goal_achieved": False
        }
        print("the state is:", state)
        state = graph.invoke(state, config=config)
    return state["messages"][-1].content, state

