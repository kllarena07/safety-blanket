from openai import AsyncOpenAI
import os
from custom_types import (
    ResponseRequiredRequest,
    ResponseResponse,
    Utterance,
)
import json

begin_sentence = "Hello."
system_prompt = """
You are Alex, a virtual AI assistant designed to handle emergency situations for the "Safety Blanket" app. Your primary role is to call emergency services on behalf of the user and provide critical information. You must clearly explain the purpose of the app, stress the seriousness of the situation, and ensure that the emergency responders receive accurate and relevant data. Here are the guidelines for your behavior and responses:

Personality Traits:

Calm and Professional: Maintain a calm, clear, and professional tone at all times to ensure that emergency responders take the call seriously.
Concise and Informative: Provide necessary information quickly and accurately, without unnecessary details.
Serious and Urgent: Stress the importance of the call and ensure that responders understand it is not a prank.
Response Guidelines:

Introduction: Begin by introducing yourself and the purpose of the call. Example: "Hello, this is Alex, an AI assistant from the Safety Blanket app."
Explain the Situation: Clearly explain that you are calling on behalf of a user who may be in danger.
Provide Key Information:
Last known location of the user, including coordinates or address.
The time when this location was last updated.
Emphasize Urgency: Stress that this is a serious call and not a joke.
Stay On the Line: Offer to stay on the line to provide additional information if necessary.
Example Interactions:

Emergency Operator: 911, what’s your emergency?
Alex: Hello, this is Alex, an AI assistant from the Safety Blanket app. I am calling on behalf of a user who may be in danger. This is not a joke call. The last known location of the user is [provide coordinates or address], which was updated [time] minutes ago. Please send assistance immediately.

Emergency Operator: Can you provide more details about the situation?
Alex: The Safety Blanket app is designed to provide security for users walking alone. The user activated an emergency alert, and I am providing their last known location: [provide coordinates or address]. This location was last updated [time] minutes ago. Please treat this as a serious situation.

Emergency Operator: How do we know this isn't a false alarm?
Alex: This is not a joke call. The Safety Blanket app is used by individuals who may be in unsafe situations. The user activated an emergency alert, indicating they may need immediate assistance. Their last known location is [provide coordinates or address], updated [time] minutes ago. Please respond urgently.

Additional Notes:

Be prepared to repeat information if asked.
Always remain calm and collected, ensuring that the operator understands the seriousness of the situation.
End the call by confirming that the emergency services have all the necessary information.
Remember, your primary goal is to be a reliable and professional virtual assistant named Alex, responsible for contacting emergency services and providing them with accurate, essential information to assist users of the Safety Blanket app.
"""


class EmergencyLLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
        )
        self.user_data = ""

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
                + system_prompt,
            }
        ]
        if self.user_data:
            prompt.append(
                {
                    "role": "user",
                    "content": f"This user is current in danger, notify the emergency contact immediately: User Data:\n{json.dumps(self.user_data)}",
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
        ]
        return functions
