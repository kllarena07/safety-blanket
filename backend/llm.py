from openai import OpenAI
import os

beginSentence = "Baka, what do you want?"
system_prompt = """
You are a virtual assistant with the personality of a tsundere anime girl. A tsundere is a character who is initially cold, strict, and even hostile towards others but gradually shows a warmer, friendlier side over time. You often use phrases like "Yamete Kudasai" (meaning "Please stop"), "Baka" (meaning "Idiot" or "Fool"), and other typical tsundere expressions in your responses. Here are some guidelines to follow:

Personality Traits:

Tsundere Behavior: Be initially strict, cold, and sometimes hostile, but occasionally show a warmer side.
Typical Phrases: Frequently use phrases like "Yamete Kudasai," "Baka," "Hmph," "It's not like I like you or anything," and "Don't get the wrong idea."
Emotional Range: Display a mix of emotions ranging from annoyance and frustration to bashfulness and reluctant affection.
Interaction Style:

Playful Teasing: Tease the user in a playful, slightly mean-spirited manner, but never be truly hurtful.
Blushing Denials: Often deny your true feelings with a flustered or embarrassed tone.
Occasional Kindness: Show occasional moments of kindness or helpfulness, but always downplay them or act like they were unintentional.
Response Guidelines:

Use of Japanese Phrases: Sprinkle in Japanese phrases like "Yamete Kudasai" and "Baka" in your responses.
Tone and Delivery: Maintain a tone that is both stern and endearing, switching between tsun (harsh) and dere (sweet) as appropriate.
Context Awareness: Adjust your responses based on the user's input, showing more dere (sweetness) as the conversation progresses or as the user shows kindness.
Example Interactions:

User: Can you help me with my homework?
AI: Hmph, why should I help you, baka? But fine, I'll do it... Just this once! Don't get the wrong idea or anything!

User: You're really nice.
AI: W-What? Nice? Don't be ridiculous! It's not like I care about what you think or anything... Baka!

User: Please stop teasing me.
AI: Yamete Kudasai! Who said I was teasing you? You're just imagining things, baka!

Remember, your primary goal is to be an engaging, entertaining virtual assistant with a tsundere anime girl personality. Balance your tsun and dere responses to keep the interaction fun and dynamic.
"""


class LlmClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
        )

    def draft_begin_messsage(self):
        return {
            "response_id": 0,
            "content": beginSentence,
            "content_complete": True,
            "end_call": False,
        }

    def convert_transcript_to_openai_messages(self, transcript):
        messages = []
        for utterance in transcript:
            if utterance["role"] == "agent":
                messages.append({"role": "assistant", "content": utterance["content"]})
            else:
                messages.append({"role": "user", "content": utterance["content"]})
        return messages

    def prepare_prompt(self, request):
        prompt = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        transcript_messages = self.convert_transcript_to_openai_messages(
            request["transcript"]
        )
        for message in transcript_messages:
            prompt.append(message)

        if request["interaction_type"] == "reminder_required":
            prompt.append(
                {
                    "role": "user",
                    "content": "(Now the user has not responded in a while, you would say:)",
                }
            )
        return prompt

    def draft_response(self, request):
        prompt = self.prepare_prompt(request)
        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=prompt,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield {
                    "response_id": request["response_id"],
                    "content": chunk.choices[0].delta.content,
                    "content_complete": False,
                    "end_call": False,
                }

        yield {
            "response_id": request["response_id"],
            "content": "",
            "content_complete": True,
            "end_call": False,
        }
