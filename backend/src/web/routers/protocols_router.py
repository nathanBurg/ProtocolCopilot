from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
from datetime import datetime
from src.core.entities.protocol_entities import Protocol, ProtocolStep, ProtocolDocument, IngestionStatus, CreateProtocolPreviewRequest, ProtocolPreviewResponse
from src.dal.databases.protocol_dal import ProtocolDAL
from src.core.services.protocol_service import ProtocolService

router = APIRouter()

# Fake data removed - now using real database endpoints

@router.get("/protocols", tags=["protocols"], response_model=List[Protocol])
async def get_protocols():
    """Get all protocols from database"""
    try:
        protocol_dal = ProtocolDAL()
        protocols = protocol_dal.get_all_protocols()
        return protocols
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching protocols: {str(e)}")

@router.get("/protocols/{protocol_id}", tags=["protocols"], response_model=Protocol)
async def get_protocol_by_id(protocol_id: str):
    """Get a specific protocol by ID"""
    try:
        protocol_uuid = uuid.UUID(protocol_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid protocol ID format")
    
    try:
        protocol_dal = ProtocolDAL()
        protocol = protocol_dal.get_protocol(str(protocol_uuid))
        
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        return protocol
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching protocol: {str(e)}")

@router.post("/protocols/upload", tags=["protocols"], response_model=ProtocolPreviewResponse)
async def upload_protocol(file: UploadFile = File(...)):
    """Upload a protocol document and validate file type"""
    
    # Check if file is provided
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Get file extension
    file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    
    # Validate file type
    allowed_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    allowed_pdf_extensions = ['pdf']
    
    is_image = file_extension in allowed_image_extensions
    is_pdf = file_extension in allowed_pdf_extensions
    
    if not (is_image or is_pdf):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Only images ({', '.join(allowed_image_extensions)}) and PDFs are allowed."
        )
    
    # Determine file type
    file_type = "image" if is_image else "pdf"
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Create request object
        request = CreateProtocolPreviewRequest(
            filename=file.filename,
            file_type=file_type,
            file_extension=file_extension,
            file_content=file_content,
            file_size=len(file_content),
            description=None,  # Can be added later if needed
            created_by_user_id=None  # Can be added later if needed
        )
        
        # Call protocol service
        protocol_service = ProtocolService()
        protocol = protocol_service.create_protocol_preview(request)
        
        return protocol
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/protocols/create", tags=["protocols"], response_model=ProtocolPreviewResponse)
async def create_protocol(protocol: Protocol, protocol_steps: List[ProtocolStep]):
    """Create a new protocol with its steps"""
    
    try:
        # TODO: should be service method 
        protocol_dal = ProtocolDAL()
        saved_protocol = protocol_dal.create_protocol(protocol)
        for step in protocol_steps:
            protocol_dal.create_protocol_step(step)
        
        return ProtocolPreviewResponse(protocol=saved_protocol, protocol_steps=protocol_steps, object_url="")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating protocol: {str(e)}")

@router.get("/protocol_steps/{protocol_id}", tags=["protocols"], response_model=List[ProtocolStep])
async def get_protocol_steps(protocol_id: str):
    """Get all steps for a specific protocol"""
    try:
        protocol_uuid = uuid.UUID(protocol_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid protocol ID format")
    
    try:
        protocol_dal = ProtocolDAL()
        steps = protocol_dal.get_protocol_steps_by_protocol_id(str(protocol_uuid))
        return steps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching protocol steps: {str(e)}")
