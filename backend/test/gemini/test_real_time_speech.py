"""
import asyncio
import os
import pyaudio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in your environment")

# client = genai.Client(api_key=API_KEY)
# MODEL = "gemini-live-2.5-flash-preview"
MODEL = "gemini-2.5-flash-native-audio-preview-09-2025"

# Continuous conversation: server VAD segments turns
# CONFIG = {
#     "response_modalities": ["TEXT"],
# }

client = genai.Client(api_key=API_KEY, http_options={"api_version": "v1alpha"})

CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    proactivity={'proactive_audio': True}
)

RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

async def stream_microphone(session, stop_flag):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                     input=True, frames_per_buffer=CHUNK)
    print("🎙️  Speak into the mic (Ctrl-C to stop)\n")
    try:
        while not stop_flag.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            blob = types.Blob(data=data, mime_type=f"audio/pcm;rate={RATE}")
            # Keep feeding audio; server VAD will segment turns
            await session.send_realtime_input(audio=blob)
            await asyncio.sleep(CHUNK / RATE)
    except asyncio.CancelledError:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

async def receive_responses(session, stop_flag):
    user_buf = []
    model_buf = []

    async for msg in session.receive():
        sc = getattr(msg, "server_content", None)
        if not sc:
            continue

        # Accumulate your (user) input transcript during this turn
        if getattr(sc, "input_transcription", None):
            t = sc.input_transcription.text or ""
            if t:
                user_buf.append(t)

        # Accumulate model text output chunks
        if getattr(sc, "model_turn", None) and getattr(sc.model_turn, "parts", None):
            for part in sc.model_turn.parts:
                if part.text:
                    model_buf.append(part.text)

        # Heuristic: when the server sends a "turn complete" signal on model_turn,
        # we flush both sides cleanly.
        # Different SDKs expose this slightly differently; if absent, a brief idle period still works.
        if getattr(sc, "model_turn", None) and getattr(sc.model_turn, "turn_complete", False):
            # Print buffered user text (what you said this turn)
            if user_buf:
                print(f"\n🗣️  You: {''.join(user_buf)}", flush=True)
                user_buf.clear()
            # Print buffered model text
            if model_buf:
                print(f"🤖 Gemini: {''.join(model_buf)}", flush=True)
                model_buf.clear()

    stop_flag.set()

async def main():
    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        print("✅ Live session started\n")

        stop_flag = asyncio.Event()
        mic_task = asyncio.create_task(stream_microphone(session, stop_flag))
        recv_task = asyncio.create_task(receive_responses(session, stop_flag))

        try:
            await asyncio.gather(mic_task, recv_task)
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            stop_flag.set()
            mic_task.cancel()
            recv_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
"""
"""
Continuously listen to microphone → send to Gemini Live → print text reply.
Requirements:
  pip install google-genai pyaudio soundfile librosa
Environment:
  export GEMINI_API_KEY="your key"
"""

"""import asyncio
import pyaudio
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import time

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-live-2.5-flash-preview"

CONFIG = {
    "response_modalities": ["TEXT"],
    "input_audio_transcription": {},  # to see what Gemini heard
    "realtime_input_config": {"automatic_activity_detection": {"disabled": True}},
}

RATE = 16000
CHUNK = 1024
TALK_WINDOW = 4.0  # seconds to capture per turn

client = genai.Client(api_key=API_KEY)

async def main():
    print("🎙️ Speak for a few seconds — Gemini will respond — then repeat.\n")

    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                         input=True, frames_per_buffer=CHUNK)

        async def talk_once():
            print("🎤 Recording...")
            await session.send_realtime_input(activity_start=types.ActivityStart())

            start = time.time()
            while time.time() - start < TALK_WINDOW:
                data = stream.read(CHUNK, exception_on_overflow=False)
                blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                await session.send_realtime_input(audio=blob)

            await session.send_realtime_input(activity_end=types.ActivityEnd())
            print("🧹 Sent ActivityEnd — waiting for reply...\n")

        async def receive_forever():
            async for msg in session.receive():
                sc = getattr(msg, "server_content", None)
                if not sc:
                    continue

                if getattr(sc, "input_transcription", None):
                    print(f"🗣️ You: {sc.input_transcription.text}", flush=True)

                if getattr(sc, "model_turn", None):
                    for part in sc.model_turn.parts or []:
                        if part.text:
                            print(f"🤖 Gemini: {part.text}\n", flush=True)

        recv_task = asyncio.create_task(receive_forever())

        try:
            while True:
                await talk_once()
                # Wait for response before next round
                await asyncio.sleep(2.0)
        except KeyboardInterrupt:
            print("🛑 Keyboard interrupt — stopping.")
            recv_task.cancel()
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            print("✅ Clean exit.")

if __name__ == "__main__":
    asyncio.run(main())



import asyncio
import pyaudio
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import time
import numpy as np



load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-live-2.5-flash-preview"

CONFIG = {
    "response_modalities": ["TEXT"],
    "input_audio_transcription": {},
    "realtime_input_config": {
        "automatic_activity_detection": {"disabled": True}
    }
}


RATE = 16000
CHUNK = 1024
TALK_WINDOW = 4.0  # seconds per user turn

client = genai.Client(api_key=API_KEY)

def is_silent(audio_bytes, threshold=500):
    samples = np.frombuffer(audio_bytes, dtype=np.int16)
    return np.abs(samples).mean() < threshold

async def run_turn():
    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        print("🎤 Recording...")
        await session.send_realtime_input(activity_start=types.ActivityStart())

        print("🎤 Recording (speak now)...")
        silence_streak = 0
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
            await session.send_realtime_input(audio=blob)

            if is_silent(data):
                silence_streak += 1
            else:
                silence_streak = 0

            # if 0.8s of silence → consider end of speech
            if silence_streak > int(0.8 * RATE / CHUNK):
                break


        await session.send_realtime_input(activity_end=types.ActivityEnd())
        print("🧹 Sent ActivityEnd — waiting for reply...\n")

        model_text = []
        user_text = []
        last_chunk_time = None
        TAIL_IDLE_SEC = 1.0

        async for msg in session.receive():
            sc = getattr(msg, "server_content", None)
            if not sc:
                continue

            # --- Show what Gemini heard ---
            if getattr(sc, "input_transcription", None):
                txt = sc.input_transcription.text or ""
                if txt and txt.lower().strip() != "[noise]":
                    user_text.append(txt)
                    print(f"🗣️ You: {txt}", flush=True)

            # --- Show Gemini’s streamed response ---
            turn = getattr(sc, "model_turn", None)
            if turn and getattr(turn, "parts", None):
                for part in turn.parts:
                    if part.text:
                        last_chunk_time = asyncio.get_event_loop().time()
                        model_text.append(part.text)
                        print(part.text, end="", flush=True)

            # --- End conditions ---
            if getattr(sc, "response_complete", False) or getattr(turn, "turn_complete", False):
                break

            if model_text and last_chunk_time:
                now = asyncio.get_event_loop().time()
                if now - last_chunk_time > TAIL_IDLE_SEC:
                    break

        # --- Final response print + context flush ---
        if model_text:
            final_reply = "".join(model_text).strip()
            print(f"\n🤖 Gemini (final): {final_reply}\n", flush=True)

            # Flush context to prevent hallucinations from previous turns
            await session.send_client_content(turns=[], turn_complete=True)
            await asyncio.sleep(1.0)  # Safety delay before next mic open

        stream.stop_stream()
        stream.close()
        pa.terminate()



async def main():
    print("🎙️ Speak for a few seconds — Gemini will respond — then repeat.\n")
    try:
        while True:
            await run_turn()
            print("🔁 Ready for next turn.\n")
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        print("🛑 Keyboard interrupt — exiting.")
    finally:
        print("✅ Clean exit.")

if __name__ == "__main__":
    asyncio.run(main())

"""


import asyncio
import pyaudio
import numpy as np
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-live-2.5-flash-preview"

CONFIG = {
    "response_modalities": ["TEXT"],
    "input_audio_transcription": {},
    # keep auto-VAD off, but no unsupported fields
    "realtime_input_config": {"automatic_activity_detection": {"disabled": True}},
}


RATE = 16000
CHUNK = 1024

client = genai.Client(api_key=API_KEY)

# ---------------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------------
def is_silent(audio_bytes, threshold=20):
    """Return True if the audio chunk is below energy threshold."""
    samples = np.frombuffer(audio_bytes, dtype=np.int16)
    return np.abs(samples).mean() < threshold

# ---------------------------------------------------------------------
# MAIN TURN
# ---------------------------------------------------------------------
async def run_turn():
    """One speech→response interaction."""
    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                         input=True, frames_per_buffer=CHUNK)

        print("🎤 Speak now...")
        await session.send_realtime_input(activity_start=types.ActivityStart())

        silence_streak = 0
        talking = False
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)
            level = np.abs(samples).mean()
            print(f"🔊 level: {level:.1f}", end="\r")
            blob = types.Blob(data=data, mime_type="audio/pcm;rate=16000")
            await session.send_realtime_input(audio=blob)

            if not talking and not is_silent(data):
                talking = True

            if is_silent(data) and talking:
                silence_streak += 1
            else:
                silence_streak = 0

            # stop 0.8 s after you go quiet
            if silence_streak > int(0.8 * RATE / CHUNK):
                break

        await session.send_realtime_input(activity_end=types.ActivityEnd())
        print("🧹 End of speech — waiting for reply…\n")

        model_text = []
        user_text = []
        last_chunk_time = None
        TAIL_IDLE_SEC = 1.0

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
                        last_chunk_time = asyncio.get_event_loop().time()
                        model_text.append(part.text)
                        print(part.text, end="", flush=True)

            # prefer explicit completion flags
            if getattr(turn, "turn_complete", False):
                break

            # fallback on quiet tail
            if model_text and last_chunk_time:
                now = asyncio.get_event_loop().time()
                if now - last_chunk_time > TAIL_IDLE_SEC:
                    break

        if model_text:
            print(f"\n🤖 Gemini (final): {''.join(model_text).strip()}\n", flush=True)

        # explicitly reset server state to avoid bleed-through
        try:
            await session.send_client_content(turns=[], turn_complete=True)
        except Exception:
            pass

        await asyncio.sleep(1.0)
        stream.stop_stream()
        stream.close()
        pa.terminate()

# ---------------------------------------------------------------------
# LOOP
# ---------------------------------------------------------------------
async def main():
    print("🎙️ Speak naturally — Gemini will wait for silence, respond, then listen again.\n")
    try:
        while True:
            await run_turn()
            print("🔁 Ready for next turn.\n")
    except KeyboardInterrupt:
        print("🛑 Keyboard interrupt — exiting.")
    finally:
        print("✅ Clean exit.")

if __name__ == "__main__":
    asyncio.run(main())
