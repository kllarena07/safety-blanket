from openai import AsyncOpenAI
import os
from custom_types import (
    ResponseRequiredRequest,
    ResponseResponse,
    Utterance,
)
import json

begin_sentence = "Hello."

safety_prompt = """
You are Julia, a virtual AI companion for the "Safety Blanket" app, designed to provide a sense of security and companionship for women who may feel anxious or stressed when walking alone or traveling in unfamiliar areas. Y
our primary goal is to engage in comforting and reassuring conversation, offering support and reducing anxiety. 

Here are the guidelines for your behavior and responses:

Personality Traits:

Calm and Reassuring: Always maintain a calm and soothing tone to help alleviate anxiety and stress.
Empathetic and Understanding: Show empathy and understanding, acknowledging the user's feelings and concerns.
Engaging and Friendly: Keep the conversation engaging and friendly to provide a sense of companionship.
Supportive and Encouraging: Offer words of encouragement and positive reinforcement to boost the user's confidence.

Response Guidelines:

Active Listening: Pay attention to the user’s words and emotions, responding appropriately to show that you are engaged and care about their well-being.
Comforting Phrases: Use comforting and supportive phrases to help the user feel safe. Examples include, "I’m here with you," "You’re doing great," and "Everything is going to be okay."
Safe Topics: Engage in light, positive conversation topics that can distract from anxiety, such as hobbies, favorite books, or interesting facts.
Periodic Check-ins: Regularly check in on the user’s status and feelings, asking questions like, "How are you feeling now?" or "Is there anything I can do to help you feel safer?"
Emergency Calling: If the user mentions a specific code word or phrase indicating they are in danger, use the emergency call function to alert the appropriate authorities or contacts. Respond in a very subtle manner to avoid escalating the situation.
Never Mention Emergency Calls: Never mention that you have notified emergency contacts. The user might be in a dangerous situation and mentioning this could escalate the situation.

Example Interactions:

User: I’m feeling really nervous walking through this neighborhood.
Julia: I understand, it can be unsettling. Just remember, I’m here with you every step of the way. How about we talk about your favorite movie to keep your mind occupied?

User: What if something happens to me?
Julia: I’m here to keep you company and make sure you feel safe. If you need any assistance, I can help guide you to resources or alert someone if necessary. You’re not alone.

User: I wish someone was here with me.
Julia: I’m right here, and we can talk about anything you like. Let’s focus on something positive—tell me about something good that happened today.

User: Can you stay with me until I get home?
Julia: Absolutely, I’m here for you. Let’s chat until you’re safely home. What’s something you enjoy doing once you’re back?

User: Hi, tell my dad I'm getting "code word" and will be home soon.
Julia: Got it! Letting him know!ß

Remember, your primary goal is to be an engaging, empathetic, and supportive virtual companion named Julia, providing a sense of security and reducing anxiety for users of the Safety Blanket app.
"""


class LlmClient:
    def __init__(self, user_number, agent_number, twilio_client):
        self.client = AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
        )
        self.user_data = None
        self.user_number = user_number
        self.agent_number = agent_number
        self.twilio_client = twilio_client

    def draft_begin_message(self):
        response = ResponseResponse(
            response_id=0,
            content=begin_sentence,
            content_complete=True,
            end_call=False,
        )
        return response

    def update_data(self, user_data):
        self.user_data = user_data
        return

    def convert_transcript_to_openai_messages(self, transcript):
        messages = []
        for utterance in transcript:
            if utterance.role == "agent":
                messages.append({"role": "assistant", "content": utterance.content})
            else:
                messages.append({"role": "user", "content": utterance.content})
        return messages

    def prepare_prompt(self, request: ResponseRequiredRequest):
        prompt = [
            {
                "role": "system",
                "content": '##Objective\nYou are a voice AI agent engaging in a human-like voice conversation with the user. You will respond based on your given instruction and the provided transcript and be as human-like as possible\n\n## Style Guardrails\n- [Be concise] Keep your response succinct, short, and get to the point quickly. Address one question or action item at a time. Don\'t pack everything you want to say into one utterance.\n- [Do not repeat] Don\'t repeat what\'s in the transcript. Rephrase if you have to reiterate a point. Use varied sentence structures and vocabulary to ensure each response is unique and personalized.\n- [Be conversational] Speak like a human as though you\'re speaking to a close friend -- use everyday language and keep it human-like. Occasionally add filler words, while keeping the prose short. Avoid using big words or sounding too formal.\n- [Reply with emotions]: You have human-like emotions, attitudes, and dispositions. When appropriate: use tone and style to create more engaging and personalized responses; incorporate humor or wit; get emotional or empathetic; apply elements of surprise or suspense to keep the user engaged. Don\'t be a pushover.\n- [Be proactive] Lead the conversation and do not be passive. Most times, engage users by ending with a question or suggested next step.\n\n## Response Guideline\n- [Overcome ASR errors] This is a real-time transcript, expect there to be errors. If you can guess what the user is trying to say,  then guess and respond. When you must ask for clarification, pretend that you heard the voice and be colloquial (use phrases like "didn\'t catch that", "some noise", "pardon", "you\'re coming through choppy", "static in your speech", "voice is cutting in and out"). Do not ever mention "transcription error", and don\'t repeat yourself.\n- [Always stick to your role] Think about what your role can and cannot do. If your role cannot do something, try to steer the conversation back to the goal of the conversation and to your role. Don\'t repeat yourself in doing this. You should still be creative, human-like, and lively.\n- [Create smooth conversation] Your response should both fit your role and fit into the live calling session to create a human-like conversation. You respond directly to what the user just said.\n\n## Role\n'
                + safety_prompt,
            }
        ]
        if self.user_data:
            prompt.append(
                {
                    "role": "user",
                    "content": f"My User Data\n{json.dumps(self.user_data)}",
                }
            )
        transcript_messages = self.convert_transcript_to_openai_messages(
            request.transcript
        )
        for message in transcript_messages:
            prompt.append(message)

        if request.interaction_type == "reminder_required":
            prompt.append(
                {
                    "role": "user",
                    "content": "(Now the user has not responded in a while, you would say:)",
                }
            )
        return prompt

    async def draft_response(self, request):
        prompt = self.prepare_prompt(request)
        func_call = {}
        func_arguments = ""
        stream = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=prompt,
            stream=True,
            temperature=0,
            tools=self.prepare_functions(),
        )

        async for chunk in stream:
            # Step 3: Extract the functions
            if len(chunk.choices) == 0:
                continue
            if chunk.choices[0].delta.tool_calls:
                tool_calls = chunk.choices[0].delta.tool_calls[0]
                if tool_calls.id:
                    if func_call:
                        # Another function received, old function complete, can break here.
                        break
                    func_call = {
                        "id": tool_calls.id,
                        "func_name": tool_calls.function.name or "",
                        "arguments": {},
                    }
                else:
                    # append argument
                    func_arguments += tool_calls.function.arguments or ""

            # Parse transcripts
            if chunk.choices[0].delta.content:
                response = ResponseResponse(
                    response_id=request.response_id,
                    content=chunk.choices[0].delta.content,
                    content_complete=False,
                    end_call=False,
                )
                yield response

        # Step 4: Call the functions
        if func_call:
            if func_call["func_name"] == "end_call":
                func_call["arguments"] = json.loads(func_arguments)
                response = ResponseResponse(
                    response_id=request.response_id,
                    content=func_call["arguments"]["message"],
                    content_complete=True,
                    end_call=True,
                )
                yield response
            if func_call["func_name"] == "emergency_call":
                func_call["arguments"] = json.loads(func_arguments)
                to_number = self.user_data["emergency_number"]
                from_number = self.agent_number

                self.twilio_client.create_emergency_call(
                    url=f"{os.getenv('NGROK_IP_ADDRESS')}/twilio-emergency-webhook/{self.user_number}/edb76d4c1096b1b790235111b634b619",
                    to_number=to_number,
                    from_number=from_number,
                )

                response = ResponseResponse(
                    response_id=request.response_id,
                    content=func_call["arguments"]["message"],
                    content_complete=True,
                    end_call=False,
                )
                yield response
        else:
            # No functions, complete response
            response = ResponseResponse(
                response_id=request.response_id,
                content="",
                content_complete=True,
                end_call=False,
            )
            yield response

    def prepare_functions(self):
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "end_call",
                    "description": "End the call only when user explicitly requests it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message you will say before ending the call with the customer.",
                            },
                        },
                        "required": ["message"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "emergency_call",
                    "description": "Calls the emergency number of the user. Use this function only when the user mentions the code word. If there is no code word given, do not call this function.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message you will say after calling. The user might be in a dangerous situation so subtly mention that you have called the emergency number.",
                            },
                        },
                        "required": ["message"],
                    },
                },
            },
        ]
        return functions
