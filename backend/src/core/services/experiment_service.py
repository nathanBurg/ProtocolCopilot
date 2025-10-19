from src.dal.databases.experiment_dal import ExperimentDAL
from src.dal.integrations.gemini_client import GeminiClientSingleton
from fastapi import UploadFile
import base64

class ExperimentService:
    def __init__(self):
        self.experiment_dal = ExperimentDAL()
        self.gemini_client = GeminiClientSingleton()

    async def voice_turn(self, file: UploadFile) -> dict:
        """Process voice input and return transcript and AI reply"""
        
        # Check if file is provided
        if not file.filename:
            raise ValueError("No audio file provided")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise ValueError("Invalid file type. Only audio files are allowed.")
        
        try:
            # Read audio bytes
            audio_bytes = await file.read()
            print(f"Received audio file: {file.filename}, content_type: {file.content_type}, size: {len(audio_bytes)} bytes")
            
            if len(audio_bytes) == 0:
                raise ValueError("Empty audio file")

            # 1️⃣ Transcribe the audio
            try:
                # Encode audio as base64
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Use correct content structure for Gemini API
                response = self.gemini_client.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {
                            "parts": [
                                {"text": "Transcribe the following audio:"},
                                {
                                    "inline_data": {
                                        "mime_type": file.content_type,
                                        "data": audio_base64
                                    }
                                }
                            ]
                        }
                    ]
                )
                transcript = response.text.strip()
                print(f"Transcribed: {transcript}")
            except Exception as e:
                print(f"Error in transcription: {e}")
                transcript = "I couldn't understand what you said."
                print(f"Using fallback transcript: {transcript}")

            # 2️⃣ Get Gemini reply
            try:
                prompt = f"""You are an experiment assistant guiding a scientist step-by-step through a protocol.

The user said: "{transcript}"

Please provide a helpful response to guide them with their experiment. Keep it conversational and brief."""
                
                response = self.gemini_client.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {
                            "parts": [{"text": prompt}]
                        }
                    ]
                )
                reply = response.text.strip()
            except Exception as e:
                print(f"Error in conversation: {e}")
                reply = f"I heard you say: '{transcript}'. How can I help you with your experiment?"
            
            print(f"Reply: {reply}")
            return {"transcript": transcript, "reply": reply}
            
        except Exception as e:
            print(f"Error in voice_turn: {e}")
            # Return a proper JSON response even on error
            return {"transcript": "Error occurred", "reply": "I'm sorry, I encountered an error. Please try again."}