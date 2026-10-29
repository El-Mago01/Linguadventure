from src.adventures.scene import Scene
from src.adventures.adventure import Adventure
import src.play.openai_gpt_4o_mini as current_model
from src.play.session import Transcript


class Character():


    def __init__(self, personality:str, role:str, adventure:Adventure, scene:Scene, goal_achieved_when:str):
        self.personality = personality
        self.role = role
        self.scene = scene
        self.adventure = adventure
        self.goal_achieved_when = goal_achieved_when

    def talk_to_student(self, conversation_history:Transcript):
        """
        Here 1 utterance (or turn) of the conversation-part of the bot is provided based upon the
        conversation history and the profile of the agent that was set during the conversation.
        :param conversation_history:
        :param prompt:
        :return:
        """
        pass

    def make_transcript_item(self, prompt):
        pass

    def adjust_personality(self, personality):