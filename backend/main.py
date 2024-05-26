from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware

from socket_manager import ConnectionManager
from typing import Optional
from llm import LlmClient
import json

from starlette.responses import JSONResponse
import os
import asyncio

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

user_settings = {
    "name": "Bill Zhang",
    "emergency_number": "12486353063",
    "keyword": "pineapple",
}

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


@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    try:
        await websocket.accept()
        # A unique call id is the identifier of each call
        print(f"Handle llm ws for: {call_id}")
        llm_client = LlmClient()

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
        first_event = llm_client.draft_begin_message()
        await websocket.send_json(first_event.__dict__)

        async def handle_message(request_json):
            nonlocal response_id

            # There are 5 types of interaction_type: call_details, pingpong, update_only, response_required, and reminder_required.
            # Not all of them need to be handled, only response_required and reminder_required.
            if request_json["interaction_type"] == "call_details":
                print(json.dumps(request_json, indent=2))
                llm_client.update_settings(user_settings)
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
