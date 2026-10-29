import datetime
import src.play.openai_gpt_4o_mini as current_model


class Transcript():
    def __init__(self, student_id:int, adventure_id:int, scene_id:int, persona_id):
        start_time = datetime.datetime.now(datetime.UTC)
        end_time = datetime.datetime.now(datetime.UTC)
        # transcript = client.transcribe_audio()
        self.transcript = {}
        self.transcript["start_time"] = start_time
        self.transcript["end_time"] = end_time
        self.transcript["adventure_id"] = adventure_id
        self.transcript["scene_id"] = scene_id
        self.transcript["student_id"] = student_id
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

def prompt_generator(role:str, prompt:str, transcript:Transcript):
    prompt = prompt.strip()
    prompt += str(transcript)
    return {"role": role, "content": prompt}

def play_scene(student_id:int, scene_id:int, adventure_id:int) -> Transcript:
    ts = Transcript(student_id, adventure_id, scene_id, 0)
    goal_reached = False
    timeout = False
    talk_stick = 0
    persona_talk_prompt = []
    while not goal_reached and not timeout:
        if talk_stick % 2 == 0:
            system_prompt = prompt_generator(role="system", prompt=f"You are a customer "
                   f"and you want something from the store. You talk to the owner of the store. Just say one thing and he'll talk right back to you. "
                   f"Use the prompt to understand what was already said and the last words (if any) of the shop owner"
                   f"grocery store owner if available. You are a kind and warm soul and as long as the shop owner "
                   f"talks to you, you answer kindly. Important: You understand Italian, but only speak in English",transcript=ts)
            persona_talk_prompt.append(system_prompt)
            answer = current_model.talk_to_student(persona_talk_prompt, "Customer")
            ts.add_conversation_part("customer", str(answer))
        else:
            system_prompt = prompt_generator(role="system", prompt=f"You are an Italian owner of a grocery store and"
                   f"you are kind to your customers. Use the prompt to understand the last words of the "
                   f"customer. As you are kind, you don't stop chatting about the weather and the quality of your products as long as the customer "
                   f"is responding you, you continue talking and responding. Important: You only speak Italian but you understand English", transcript=ts)
            persona_talk_prompt.append(system_prompt)
            answer = current_model.talk_to_student(persona_talk_prompt, "Shop owner")
            ts.add_conversation_part("grocery store owner", str(answer))
        current_time = datetime.datetime.now(datetime.UTC)
        time_ongoing = current_time - ts.get_start_time()
        if time_ongoing > datetime.timedelta(minutes=5):
            timeout = True
        talk_stick += 1
    transcript = Transcript(student_id,adventure_id,scene_id,5)
    print(f"Transcript of this scene:\n {ts})")
    return transcript

