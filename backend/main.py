from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware

from socket_manager import ConnectionManager
from typing import Optional
from llm import LlmClient
from emergency_llm import EmergencyLLMClient
from openai import AsyncOpenAI

from starlette.responses import JSONResponse

import json
import os
import asyncio
from fastapi.responses import JSONResponse, PlainTextResponse
from concurrent.futures import TimeoutError as ConnectionTimeoutError
from twilio.twiml.voice_response import VoiceResponse
from retell import Retell
from twilio_client import TwilioClient
from retell.resources.call import RegisterCallResponse
from custom_types import (
    ConfigResponse,
    ResponseRequiredRequest,
)

import firebase_admin
from firebase import save_user_data, read_user_data
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

cred = credentials.Certificate("firebase.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

origins = ["*"]

manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retell = Retell(api_key=os.environ["RETELL_API_KEY"])
twilio_client = TwilioClient()
twilio_client.register_inbound_agent("+12254173514", "0814f86883b0337bb040580219120f66")


# Handle webhook from Retell server. This is used to receive events from Retell server.
# Including call_started, call_ended, call_analyzed
@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        post_data = await request.json()
        valid_signature = retell.verify(
            json.dumps(post_data, separators=(",", ":")),
            api_key=str(os.environ["RETELL_API_KEY"]),
            signature=str(request.headers.get("X-Retell-Signature")),
        )
        if not valid_signature:
            print(
                "Received Unauthorized",
                post_data["event"],
                post_data["data"]["call_id"],
            )
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})
        if post_data["event"] == "call_started":
            print("Call started event", post_data["data"]["call_id"])
        elif post_data["event"] == "call_ended":
            print("Call ended event", post_data["data"]["call_id"])
        elif post_data["event"] == "call_analyzed":
            print("Call analyzed event", post_data["data"]["call_id"])
        else:
            print("Unknown event", post_data["event"])
        return JSONResponse(status_code=200, content={"received": True})
    except Exception as err:
        print(f"Error in webhook: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


@app.post("/register-call-on-your-server")
async def handle_register_call(request: Request):
    try:
        post_data = await request.json()
        call_response = retell.call.register(
            agent_id=post_data["agent_id"],
            audio_websocket_protocol="web",
            audio_encoding="s16le",
            sample_rate=post_data[
                "sample_rate"
            ],  # Sample rate has to be 8000 for Twilio
        )
        print(f"Call response: {call_response}")
    except Exception as err:
        print(f"Error in register call: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


# Register call with Retell at this stage and pass in returned call_id to Retell.
@app.post("/twilio-voice-webhook/{agent_id_path}")
async def handle_twilio_voice_webhook(request: Request, agent_id_path: str):
    try:
        # Check if it is machine
        post_data = await request.form()
        if "AnsweredBy" in post_data and post_data["AnsweredBy"] == "machine_start":
            twilio_client.end_call(post_data["CallSid"])
            return PlainTextResponse("")
        elif "AnsweredBy" in post_data:
            return PlainTextResponse("")

        call_response: RegisterCallResponse = retell.call.register(
            agent_id=agent_id_path,
            audio_websocket_protocol="twilio",
            audio_encoding="mulaw",
            sample_rate=8000,  # Sample rate has to be 8000 for Twilio
            from_number=post_data["From"],
            to_number=post_data["To"],
            metadata={"twilio_call_sid": post_data["CallSid"]},
        )
        print(f"Call response: {call_response}")

        response = VoiceResponse()
        start = response.connect()
        start.stream(
            url=f"wss://api.retellai.com/audio-websocket/{call_response.call_id}"
        )
        return PlainTextResponse(str(response), media_type="text/xml")
    except Exception as err:
        print(f"Error in twilio voice webhook: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


# Register call with Retell at this stage and pass in returned call_id to Retell.
@app.post("/twilio-emergency-webhook/{phone_number}/{agent_id_path}")
async def handle_twilio_voice_webhook(
    request: Request, phone_number: str, agent_id_path: str
):
    try:
        # Check if it is machine
        post_data = await request.form()
        if "AnsweredBy" in post_data and post_data["AnsweredBy"] == "machine_start":
            twilio_client.end_call(post_data["CallSid"])
            return PlainTextResponse("")
        elif "AnsweredBy" in post_data:
            return PlainTextResponse("")

        call_response: RegisterCallResponse = retell.call.register(
            agent_id=agent_id_path,
            audio_websocket_protocol="twilio",
            audio_encoding="mulaw",
            sample_rate=8000,  # Sample rate has to be 8000 for Twilio
            from_number=post_data["From"],
            to_number=post_data["To"],
            metadata={
                "twilio_call_sid": post_data["CallSid"],
                "emergency": True,
                "user_id": phone_number,
            },
        )
        print(f"Call response: {call_response}")

        response = VoiceResponse()
        start = response.connect()
        start.stream(
            url=f"wss://api.retellai.com/audio-websocket/{call_response.call_id}"
        )
        return PlainTextResponse(str(response), media_type="text/xml")
    except Exception as err:
        print(f"Error in twilio voice webhook: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    try:
        await websocket.accept()
        # A unique call id is the identifier of each call
        print(f"Handle llm ws for: {call_id}")
        llm_client = None

        config = ConfigResponse(
            response_type="config",
            config={
                "auto_reconnect": True,
                "call_details": True,
            },
            response_id=1,
        )
        await websocket.send_json(config.__dict__)

        response_id = 0
        llm_client = LlmClient(
            user_number="", agent_number="+12254173514", twilio_client=twilio_client
        )
        first_event = llm_client.draft_begin_message()
        await websocket.send_json(first_event.__dict__)

        async def handle_message(request_json):
            nonlocal response_id
            nonlocal llm_client

            # There are 5 types of interaction_type: call_details, pingpong, update_only, response_required, and reminder_required.
            # Not all of them need to be handled, only response_required and reminder_required.
            if request_json["interaction_type"] == "call_details":
                print(json.dumps(request_json, indent=2))
                if "emergency" in request_json["call"]["metadata"]:
                    llm_client = EmergencyLLMClient()
                    user_data = read_user_data(
                        db, request_json["call"]["metadata"]["user_id"]
                    )
                    llm_client.update_data(user_data=user_data)
                else:

                    other_number = ""
                    if request_json["call"]["from_number"] == "+12254173514":
                        other_number = request_json["call"]["to_number"]
                    elif request_json["call"]["to_number"] == "+12254173514":
                        other_number = request_json["call"]["from_number"]
                    llm_client = LlmClient(
                        user_number=other_number,
                        agent_number="+12254173514",
                        twilio_client=twilio_client,
                    )
                    user_data = read_user_data(db, other_number)

                    if "last_location" not in user_data:
                        user_data["last_location"] = ""
                        user_data["last_updated"] = ""
                    else:

                        # Get current utc time in utc format
                        current_time = datetime.now(timezone.utc)

                        prev_time_str = user_data["last_updated"]
                        prev_time = datetime.strptime(
                            prev_time_str, "%Y-%m-%dT%H:%M:%SZ"
                        ).replace(tzinfo=timezone.utc)
                        time_difference = current_time - prev_time

                        # Convert the time difference to minutes
                        difference_in_minutes = time_difference.total_seconds() / 60

                        if difference_in_minutes > 60:
                            user_data["last_location"] = ""
                            user_data["last_updated"] = ""
                        else:
                            user_data["last_updated"] = (
                                str(difference_in_minutes) + " minutes ago"
                            )

                    llm_client.update_data(user_data=user_data)
                return
            if request_json["interaction_type"] == "ping_pong":
                await websocket.send_json(
                    {
                        "response_type": "ping_pong",
                        "timestamp": request_json["timestamp"],
                    }
                )
                return
            if request_json["interaction_type"] == "update_only":
                return
            if (
                request_json["interaction_type"] == "response_required"
                or request_json["interaction_type"] == "reminder_required"
            ):
                response_id = request_json["response_id"]
                request = ResponseRequiredRequest(
                    interaction_type=request_json["interaction_type"],
                    response_id=response_id,
                    transcript=request_json["transcript"],
                )
                print(
                    f"""Received interaction_type={request_json['interaction_type']}, response_id={response_id}, last_transcript={request_json['transcript'][-1]['content']}"""
                )

                async for event in llm_client.draft_response(request):
                    await websocket.send_json(event.__dict__)
                    if request.response_id < response_id:
                        break  # new response needed, abandon this one

        async for data in websocket.iter_json():
            asyncio.create_task(handle_message(data))

    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_id}")
    except Exception as e:
        print(f"LLM WebSocket error for {call_id}: {e}")
        await websocket.close(1011, "Server error")
    finally:
        print(f"LLM WebSocket connection closed for {call_id}")


@app.get("/user/{phone_number}")
def get_user(phone_number: str):
    user_data = read_user_data(db, phone_number)
    return user_data


@app.post("/user/{phone_number}")
def save_user(phone_number: str, user_data: dict):
    try:
        save_user_data(db, phone_number, user_data)
        return JSONResponse(status_code=200, content={"message": "User data saved"})
    except Exception as err:
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


@app.get("/phone/{phone_number}")
def call_phone(phone_number: str):
    twilio_client.create_phone_call(
        from_number="+12254173514",
        to_number=phone_number,
        agent_id="0814f86883b0337bb040580219120f66",
    )
    return JSONResponse(status_code=200, content={"message": "Call initiated"})


@app.websocket("/timed-ws")
async def timed_websocket_endpoint(
    websocket: WebSocket, client_id: Optional[str] = None
):
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return
    # save this client into server memory
    await manager.connect(websocket, client_id)

    await websocket.send_text(
            json.dumps({"owner": "agent", "content": "Are you okay? Answer yes or no"})
            )

    countdown = 5
    potential_emergency = False
    emergency_countdown = 10

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=1)

                event = data["event"]
                if event == "conversation_message":
                    if data["content"].lower() == "yes" or data["content"].lower == "y":    
                        print("Okay.")
                        await websocket.send_text(
                            json.dumps(
                                {"owner": "agent", "content": "Queueing another message."}
                            )
                        )
                        countdown = 5
                        emergency_countdown = 10
                    elif data["content"].lower() == "no" or data["content"].lower == "n":
                        user_id = client_id
                        user_id = "+" + user_id[1:]
                        url = (
                            f"{os.getenv('NGROK_IP_ADDRESS')}/twilio-emergency-webhook/{user_id}/edb76d4c1096b1b790235111b634b619",
                        )
                        from_number = os.getenv("AGENT_NUMBER")
                        user_data = read_user_data(db, user_id)
                        to_number = user_data["emergency_number"]
                        twilio_client.create_emergency_call(
                            from_number=from_number, to_number=to_number, url=url
                        )
            except asyncio.TimeoutError:
                if countdown > 0:
                    countdown -= 1
                elif potential_emergency is False:
                    await websocket.send_text(
                        json.dumps({"owner": "agent", "content": "Are you okay? Answer yes or no"})
                    )
                    potential_emergency = True
                elif emergency_countdown > 0:
                    print(emergency_countdown)
                    emergency_countdown -= 1
                else:
                    user_id = client_id
                    user_id = "+" + user_id[1:]
                    url = (
                        f"{os.getenv('NGROK_IP_ADDRESS')}/twilio-emergency-webhook/{user_id}/edb76d4c1096b1b790235111b634b619",
                    )
                    from_number = os.getenv("AGENT_NUMBER")
                    user_data = read_user_data(db, user_id)
                    to_number = user_data["emergency_number"]
                    twilio_client.create_emergency_call(
                        from_number=from_number, to_number=to_number, url=url
                    )
                    await websocket.send_text(
                        json.dumps({"owner": "agent", "content": "No messages were sent. Calling emergency phone number."})
                    )
                    break

            await websocket.send_text(
                json.dumps({"owner": "system", "content": countdown})
            )

    except WebSocketDisconnect:
        print("Disconnecting...")
        await manager.disconnect(client_id)


@app.get("/emergency/{phone_number}")
def call_emergency(phone_number: str):
    user_data = read_user_data(db, phone_number)
    emergency_number = user_data["emergency_number"]
    url = (
        f"{os.getenv('NGROK_IP_ADDRESS')}/twilio-emergency-webhook/{phone_number}/edb76d4c1096b1b790235111b634b619",
    )

    twilio_client.create_emergency_call(
        from_number="+12254173514", to_number=emergency_number, url=url
    )
    return JSONResponse(
        status_code=200, content={"message": "Emergency call initiated"}
    )


@app.websocket("/message-ws")
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return
    # save this client into server memory
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=1)

            event = data["event"]
            if event == "notify":
                user_id = data["user_id"]

                url = (
                    f"{os.getenv('NGROK_IP_ADDRESS')}/twilio-emergency-webhook/{user_id}/edb76d4c1096b1b790235111b634b619",
                )
                from_number = os.getenv("AGENT_NUMBER")
                user_data = read_user_data(db, user_id)
                to_number = user_data["emergency_number"]
                twilio_client.create_emergency_call(
                    from_number=from_number, to_number=to_number, url=url
                )
            elif event == "user_data":
                user_data = json.loads(data["user_data"])
                save_user_data(db, data["phone_number"], user_data)
            elif event == "get_user_data":
                user_data = read_user_data(db, data["phone_number"])
                await websocket.send_json({"user_data": user_data})
    except WebSocketDisconnect:
        print("Disconnecting...")
        await manager.disconnect(client_id)


@app.get("/end-trip")
def end_trip():
    print("Ending trip.")


@app.get("/end-safety-timer")
def end_safety_timer():
    print("Ending safety timer.")
