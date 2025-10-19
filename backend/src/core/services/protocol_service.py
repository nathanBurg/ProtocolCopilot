from src.dal.integrations.gemini_client import GeminiClientSingleton
from src.core.entities.protocol_entities import Protocol, CreateProtocolPreviewRequest, ProtocolDocument, IngestionStatus, ProtocolStep, ProtocolPreviewResponse
from src.dal.databases.protocol_dal import ProtocolDAL
from src.dal.databases.bucket_client import BucketClient
import uuid
from datetime import datetime
from typing import List
import json

class ProtocolService:
    def __init__(self):
        self.gemini_client = GeminiClientSingleton().client
        self.protocol_dal = ProtocolDAL()
        self.bucket_client = BucketClient()

    def create_protocol_preview(self, request: CreateProtocolPreviewRequest) -> ProtocolPreviewResponse:
        """Create a protocol preview from uploaded file"""
        try:
            # Determine content type based on file extension
            content_type = "application/pdf" if request.file_extension == "pdf" else f"image/{request.file_extension}"
            
            # Upload file to object storage
            object_url = self.bucket_client.upload_file(
                file_content=request.file_content,
                filename=request.filename,
                content_type=content_type
            )
            
            # Create protocol document
            document_id = uuid.uuid4()
            protocol_id = uuid.uuid4()

            # Extract text from file using Gemini AI
            extracted_text = self._get_text_from_file(request.file_content, request.file_extension)
            
            # Create ProtocolDocument with extracted text in description
            protocol_document = ProtocolDocument(
                document_id=document_id,
                document_name=request.filename,
                description=extracted_text,  # Store extracted text from AI
                object_url=object_url,
                mime_type=content_type,
                ingestion_status=IngestionStatus.INGESTED,  # Mark as ingested since we extracted text
                ingested_at=datetime.now(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save protocol document to database
            saved_document = self.protocol_dal.create_protocol_document(protocol_document)
            
            # Parse protocol using AI to extract structured information
            protocol = self._parse_protocol(extracted_text, saved_document.document_id, protocol_id)
            
            # Parse protocol steps using AI
            protocol_steps = self._parse_protocol_steps(extracted_text, protocol_id)
            
            # Save protocol to database
            saved_protocol = self.protocol_dal.create_protocol(protocol)
            
            # Save protocol steps to database
            for step in protocol_steps:
                self.protocol_dal.create_protocol_step(step)
            
            # Return both protocol and steps with object URL
            return ProtocolPreviewResponse(
                protocol=saved_protocol,
                protocol_steps=protocol_steps,
                object_url=object_url
            )
            
        except Exception as e:
            raise Exception(f"Failed to create protocol preview: {str(e)}")


    def _get_text_from_file(self, file_content: bytes, file_extension: str) -> str:
        """
        Extract text from PDF or image using Gemini AI
        
        Args:
            file_content: Raw file content as bytes
            file_extension: File extension (pdf, jpg, png, etc.)
            
        Returns:
            str: Extracted text from the file
        """
        try:
            import base64
            
            # file_content is already bytes, so we can encode it directly
            encoded_file = base64.b64encode(file_content).decode("utf-8")
            
            # Determine MIME type based on file extension
            if file_extension.lower() == 'pdf':
                mime_type = "application/pdf"
            elif file_extension.lower() in ['jpg', 'jpeg']:
                mime_type = "image/jpeg"
            elif file_extension.lower() == 'png':
                mime_type = "image/png"
            elif file_extension.lower() == 'gif':
                mime_type = "image/gif"
            elif file_extension.lower() == 'bmp':
                mime_type = "image/bmp"
            elif file_extension.lower() == 'tiff':
                mime_type = "image/tiff"
            elif file_extension.lower() == 'webp':
                mime_type = "image/webp"
            else:
                mime_type = f"image/{file_extension}"
            
            # Choose model (Gemini 2.5 Pro supports both PDF and image input)
            model_name = "gemini-2.5-pro"
            
            # Send request to extract text from file
            response = self.gemini_client.models.generate_content(
                model=model_name,
                contents=[
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": encoded_file
                                }
                            },
                            {
                                "text": "Extract all text from this document. Preserve line breaks, formatting, and structure if possible. If this is a scientific protocol, focus on extracting the step-by-step instructions, materials, and procedures."
                            }
                        ]
                    }
                ]
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Failed to extract text from file: {str(e)}")

    def _parse_protocol_steps(self, text: str, protocol_id: uuid.UUID) -> List[ProtocolStep]:
        """
        Parse protocol text and extract structured protocol steps using Gemini AI
        
        Args:
            text: Extracted text from the protocol document
            protocol_id: UUID of the protocol these steps belong to
            
        Returns:
            List[ProtocolStep]: List of structured protocol steps
        """
        try:
            now = datetime.now()
            
            # Create a simplified schema that doesn't include UUID fields
            step_schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step_number": {"type": "integer"},
                        "step_name": {"type": "string"},
                        "instruction": {"type": "string"},
                        "expected_duration_minutes": {"type": "integer"}
                    },
                    "required": ["step_number", "step_name", "instruction"]
                }
            }
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": (
                                    f"Given the following protocol text, produce JSON matching the schema for each step of the protocol.\n"
                                    f"There will often be a step with sub steps; in that case treat every step as its own step number.\n"
                                    f"If there is a time range given vs an exact time, select the upper bound of the time range.\n"
                                    f"Text:\n{text}"
                                )
                            }
                        ],
                    }
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": step_schema,
                },
            )
            
            # Parse the JSON response and create ProtocolStep objects with proper UUIDs
            steps_data = json.loads(response.text)
            protocol_steps = []
            
            for step_data in steps_data:
                protocol_step = ProtocolStep(
                    protocol_step_id=uuid.uuid4(),  # Generate proper UUID
                    protocol_id=protocol_id,
                    step_number=step_data["step_number"],
                    step_name=step_data["step_name"],
                    instruction=step_data["instruction"],
                    expected_duration_minutes=step_data.get("expected_duration_minutes"),
                    created_at=now,
                    updated_at=now
                )
                protocol_steps.append(protocol_step)
            
            return protocol_steps
            
        except Exception as e:
            raise Exception(f"Failed to parse protocol steps: {str(e)}")

    def _parse_protocol(self, text: str, document_id: uuid.UUID, protocol_id: uuid.UUID) -> Protocol:
        """
        Parse protocol text and extract structured protocol information using Gemini AI
        
        Args:
            text: Extracted text from the protocol document
            document_id: UUID of the document
            protocol_id: UUID of the protocol
            
        Returns:
            Protocol: Structured protocol object
        """
        try:
            now = datetime.now()
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": (
                                    f"Given the following protocol text, produce JSON matching the schema for the protocol.\n"
                                    f"The description should be a concise summary of what is accomplished in the experiment.\n"
                                    f"Use the following pre-assigned IDs:\n"
                                    f"document_id: {document_id}\n"
                                    f"protocol_id: {protocol_id}\n"
                                    f"Use current timestamp {now} for all created_at and updated_at fields.\n"
                                    f"Text:\n{text}"
                                )
                            }
                        ],
                    }
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Protocol,
                },
            )
            
            protocol_data = json.loads(response.text)
            protocol = Protocol(**protocol_data)
            
            return protocol
            
        except Exception as e:
            raise Exception(f"Failed to parse protocol: {str(e)}")

