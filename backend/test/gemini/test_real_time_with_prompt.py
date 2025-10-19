import asyncio
import pyaudio
import numpy as np
import time
import uuid
from datetime import datetime, UTC
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


# ---------------------------------------------------------------------
# FAKE MODELS
# ---------------------------------------------------------------------
class Protocol:
    def __init__(self, name: str, description: str, steps: list):
        self.protocol_id = uuid.uuid4()
        self.document_id = uuid.uuid4()
        self.protocol_name = name
        self.description = description
        self.created_by_user_id = uuid.uuid4()
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.steps = steps


class ProtocolStep:
    def __init__(
        self, number: int, name: str, instruction: str, duration: int | None = None
    ):
        self.protocol_step_id = uuid.uuid4()
        self.protocol_id = uuid.uuid4()
        self.step_number = number
        self.step_name = name
        self.instruction = instruction
        self.expected_duration_minutes = duration
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-live-2.5-flash-preview"
# CONFIG = {
#     "response_modalities": ["TEXT"],
#     "input_audio_transcription": {},
#     "realtime_input_config": {
#         "automatic_activity_detection": {
#             "disabled": True
#         }
#     }
# }
CONFIG = {
    "response_modalities": ["TEXT"],
    "input_audio_transcription": {},
    "realtime_input_config": {
        "automatic_activity_detection": {  # <-- dict, NOT bool
            "disabled": True
        }
    }
}




RATE = 16000
CHUNK = 1024
client = genai.Client(api_key=API_KEY)

# ---------------------------------------------------------------------
# GLOBAL EXPERIMENT STATE
# ---------------------------------------------------------------------
experiment_state = {
    "started": False,
    "current_step": 0,
    "awaiting_confirmation": False,
    "awaiting_completion": False,
}

# sample protocol
protocol = Protocol(
    name="Micropipette Calibration",
    description="A test protocol to calibrate micropipettes using water drops.",
    steps=[
        ProtocolStep(1, "Prepare workspace", "Clean the bench and place materials."),
        ProtocolStep(2, "Weigh container", "Record the weight of the empty container."),
        ProtocolStep(
            3,
            "Dispense water",
            "Use pipette to dispense 1 mL of water and record new weight.",
        ),
        ProtocolStep(
            4, "Calculate difference", "Subtract initial weight and log mass of water."
        ),
    ],
)


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def is_silent(audio_bytes, threshold=20):
    samples = np.frombuffer(audio_bytes, dtype=np.int16)
    return np.abs(samples).mean() < threshold


def build_prompt():
    """Return a pure string system prompt describing experiment state."""
    step_idx = experiment_state["current_step"]
    current_step = protocol.steps[step_idx] if step_idx < len(protocol.steps) else None

    if not experiment_state["started"]:
        return (
            "You are the experiment assistant. The user will say 'start experiment' "
            "when ready. Ask them if they’re ready for the first step."
        )

    if experiment_state["awaiting_completion"] and current_step:
        return (
            f"You are guiding a live experiment. You are currently on step {current_step.step_number}: "
            f"'{current_step.step_name}' — {current_step.instruction}. "
            "Wait for the user to confirm the step is complete. "
            "Only when they say the step is done, mark it complete and move to the next step."
        )

    if experiment_state["awaiting_confirmation"] and current_step:
        return (
            f"The experiment is about to begin step {current_step.step_number}: "
            f"'{current_step.step_name}'. "
            "Confirm readiness with the user before proceeding."
        )

    return "The experiment is complete. Congratulate the user and end the run."


# ---------------------------------------------------------------------
# MAIN INTERACTION LOOP
# ---------------------------------------------------------------------
"""async def run_turn():
    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        prompt_text = build_prompt()
        print(f"🧠 Sending system prompt:\n{prompt_text}\n")
        await session.send_client_content(
            turns=[{"role": "user", "parts": [{"text": build_prompt()}]}],
            turn_complete=True,
        )

        print("🎤 Speak now...")
        await session.send_realtime_input(activity_start=types.ActivityStart())

        silence_streak = 0
        talking = False
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
            await session.send_realtime_input(audio=blob)
            if not talking and not is_silent(data):
                talking = True
            if is_silent(data) and talking:
                silence_streak += 1
            else:
                silence_streak = 0
            if silence_streak > int(0.8 * RATE / CHUNK):
                break

        await session.send_realtime_input(activity_end=types.ActivityEnd())
        print("🧹 End of speech — waiting for reply…\n")

        user_text, model_text = [], []
        async for msg in session.receive():
            sc = getattr(msg, "server_content", None)
            if not sc:
                continue
            if getattr(sc, "input_transcription", None):
                txt = sc.input_transcription.text or ""
                if txt and txt.lower().strip() != "[noise]":
                    user_text.append(txt)
                    print(f"🗣️ You: {txt}", flush=True)
            turn = getattr(sc, "model_turn", None)
            if turn and getattr(turn, "parts", None):
                for part in turn.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                        model_text.append(part.text)
            if getattr(turn, "turn_complete", False):
                break

        final_reply = "".join(model_text).strip()
        print(f"\n🤖 Gemini: {final_reply}\n")

        # --- minimal intent logic for next-state transitions ---
        user_input = " ".join(user_text).lower()
        if "start experiment" in user_input and not experiment_state["started"]:
            experiment_state["started"] = True
            experiment_state["awaiting_confirmation"] = True
            experiment_state["current_step"] = 0
        elif experiment_state["awaiting_confirmation"] and any(
            w in user_input for w in ["ready", "yes", "begin"]
        ):
            experiment_state["awaiting_confirmation"] = False
            experiment_state["awaiting_completion"] = True
        elif experiment_state["awaiting_completion"] and any(
            w in user_input for w in ["done", "complete", "finished"]
        ):
            print("🧠 Saving step data...")
            experiment_state["current_step"] += 1
            if experiment_state["current_step"] < len(protocol.steps):
                experiment_state["awaiting_confirmation"] = True
                experiment_state["awaiting_completion"] = False
            else:
                experiment_state["awaiting_completion"] = False
                experiment_state["started"] = False

        stream.stop_stream()
        stream.close()
        pa.terminate()

"""
"""async def run_turn(session):
    print("🎤 Speak now...")
    await session.send_realtime_input(activity_start=types.ActivityStart())

    silence_streak = 0
    talking = False
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                     input=True, frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
        await session.send_realtime_input(audio=blob)

        if not talking and not is_silent(data):
            talking = True
        if is_silent(data) and talking:
            silence_streak += 1
        else:
            silence_streak = 0

        if silence_streak > int(0.8 * RATE / CHUNK):
            break

    await session.send_realtime_input(activity_end=types.ActivityEnd())
    print("🧹 End of speech — waiting for reply…\n")

    model_text = []
    async for msg in session.receive():
        sc = getattr(msg, "server_content", None)
        if not sc:
            continue
        if getattr(sc, "input_transcription", None):
            txt = sc.input_transcription.text or ""
            if txt and txt.lower().strip() != "[noise]":
                print(f"🗣️ You: {txt}", flush=True)
        turn = getattr(sc, "model_turn", None)
        if turn and getattr(turn, "parts", None):
            for part in turn.parts:
                if part.text:
                    print(f"🤖 Gemini: {part.text}\n", flush=True)
                    model_text.append(part.text)
        if getattr(turn, "turn_complete", False):
            break

    stream.stop_stream()
    stream.close()
    pa.terminate()
    return "".join(model_text).strip()"""\

"""async def run_turn(session):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                     input=True, frames_per_buffer=CHUNK)

    print("🎤 Speak now...")
    await session.send_realtime_input(activity_start=types.ActivityStart())

    silence_streak = 0
    talking = False
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
        await session.send_realtime_input(audio=blob)

        if not talking and not is_silent(data):
            talking = True
        if is_silent(data) and talking:
            silence_streak += 1
        else:
            silence_streak = 0

        if silence_streak > int(0.8 * RATE / CHUNK):
            break

    await session.send_realtime_input(activity_end=types.ActivityEnd())
    print("🧹 End of speech — waiting for reply…\n")

    # --- Receive until model finishes ---
    model_text, user_text = [], []
    turn_complete = False

    async for msg in session.receive():
        sc = getattr(msg, "server_content", None)
        if not sc:
            continue

        # Live transcription
        if getattr(sc, "input_transcription", None):
            txt = sc.input_transcription.text or ""
            if txt and txt.lower().strip() != "[noise]":
                print(f"🗣️ You: {txt}", flush=True)
                user_text.append(txt)

        # Model partial responses
        turn = getattr(sc, "model_turn", None)
        if turn and getattr(turn, "parts", None):
            for part in turn.parts:
                if part.text:
                    print(f"🤖 Gemini: {part.text}", flush=True)
                    model_text.append(part.text)

        if getattr(turn, "turn_complete", False):
            turn_complete = True
            break

    # wait an extra 200ms to ensure socket drain
    await asyncio.sleep(0.2)

    stream.stop_stream()
    stream.close()
    pa.terminate()

    return " ".join(user_text).strip(), " ".join(model_text).strip()


# ---------------------------------------------------------------------
# LOOP
# ---------------------------------------------------------------------

async def main():
    print("🎙️ Starting experiment assistant — speak naturally.\n")

    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        # Send context once
        prompt_text = build_prompt()
        print(f"🧠 Sending system prompt:\n{prompt_text}\n")
        await session.send_client_content(
            turns=[{"role": "user", "parts": [{"text": prompt_text}]}],
            turn_complete=True,
        )

        try:
            while True:
                user_text, reply = await run_turn(session)
                print(f"🔁 Turn complete.\n🗣️ You said: {user_text}\n🤖 Gemini replied: {reply}\n")
        except KeyboardInterrupt:
            print("✅ Clean exit.")"""
async def run_turn(session):
    """Record, send, and receive one conversational turn."""
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                     input=True, frames_per_buffer=CHUNK)

    # Send context for this specific turn, but don't close the turn yet
    prompt_text = build_prompt()
    print(f"🧠 Updating prompt context:\n{prompt_text}\n")
    await session.send_client_content(
        turns=[{"role": "user", "parts": [{"text": prompt_text}]}]
    )

    print("🎤 Speak now...")
    await session.send_realtime_input(activity_start=types.ActivityStart())

    silence_streak = 0
    talking = False
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
        await session.send_realtime_input(audio=blob)

        if not talking and not is_silent(data):
            talking = True
        if is_silent(data) and talking:
            silence_streak += 1
        else:
            silence_streak = 0

        if silence_streak > int(0.8 * RATE / CHUNK):
            break

    await session.send_realtime_input(activity_end=types.ActivityEnd())
    print("🧹 End of speech — waiting for reply…\n")

    user_text, model_text = [], []
    async for msg in session.receive():
        sc = getattr(msg, "server_content", None)
        if not sc:
            continue
        if getattr(sc, "input_transcription", None):
            txt = sc.input_transcription.text or ""
            if txt and txt.lower().strip() != "[noise]":
                print(f"🗣️ You: {txt}", flush=True)
                user_text.append(txt)
        turn = getattr(sc, "model_turn", None)
        if turn and getattr(turn, "parts", None):
            for part in turn.parts:
                if part.text:
                    print(f"🤖 Gemini: {part.text}", flush=True)
                    model_text.append(part.text)
        if getattr(turn, "turn_complete", False):
            break

    await asyncio.sleep(0.2)  # drain buffer

    stream.stop_stream()
    stream.close()
    pa.terminate()

    return " ".join(user_text).strip(), " ".join(model_text).strip()


async def main():
    print("🎙️ Starting experiment assistant — speak naturally.\n")
    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        # Send base system prompt once at startup
        system_prompt = "You are an experiment assistant. Respond conversationally and follow instructions."
        await session.send_client_content(
            turns=[{"role": "system", "parts": [{"text": system_prompt}]}]
        )

        try:
            while True:
                user_text, reply = await run_turn(session)
                print(f"🔁 Turn complete.\n🗣️ You said: {user_text}\n🤖 Gemini replied: {reply}\n")
        except KeyboardInterrupt:
            print("✅ Clean exit.")


if __name__ == "__main__":
    asyncio.run(main())