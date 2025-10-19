from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
from datetime import datetime
from src.core.entities.protocol_entities import Protocol, ProtocolStep, ProtocolDocument, IngestionStatus, CreateProtocolPreviewRequest
from src.core.services.protocol_service import ProtocolService

router = APIRouter()

# Create fake data at module level so it stays consistent across requests
_fake_documents = [
    ProtocolDocument(
        document_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
        document_name="Western Blot Protocol.pdf",
        description="Standard Western Blot procedure for protein analysis",
        object_url="https://example.com/documents/western_blot.pdf",
        mime_type="application/pdf",
        ingestion_status=IngestionStatus.INGESTED,
        ingested_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    ProtocolDocument(
        document_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),
        document_name="PCR Amplification Guide.pdf",
        description="Polymerase Chain Reaction protocol for DNA amplification",
        object_url="https://example.com/documents/pcr_guide.pdf",
        mime_type="application/pdf",
        ingestion_status=IngestionStatus.INGESTED,
        ingested_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    ProtocolDocument(
        document_id=uuid.UUID("550e8400-e29b-41d4-a716-446655440003"),
        document_name="Cell Culture Maintenance.pdf",
        description="Routine cell culture maintenance and passaging procedures",
        object_url="https://example.com/documents/cell_culture.pdf",
        mime_type="application/pdf",
        ingestion_status=IngestionStatus.PENDING,
        ingested_at=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

_fake_protocols = [
    Protocol(
        protocol_id=uuid.UUID("650e8400-e29b-41d4-a716-446655440001"),
        document_id=_fake_documents[0].document_id,
        protocol_name="Western Blot Analysis",
        description="Complete Western Blot protocol for protein detection and quantification",
        created_by_user_id=uuid.UUID("750e8400-e29b-41d4-a716-446655440001"),
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    Protocol(
        protocol_id=uuid.UUID("650e8400-e29b-41d4-a716-446655440002"),
        document_id=_fake_documents[1].document_id,
        protocol_name="PCR DNA Amplification",
        description="Standard PCR protocol for amplifying specific DNA sequences",
        created_by_user_id=uuid.UUID("750e8400-e29b-41d4-a716-446655440002"),
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    Protocol(
        protocol_id=uuid.UUID("650e8400-e29b-41d4-a716-446655440003"),
        document_id=_fake_documents[2].document_id,
        protocol_name="Mammalian Cell Culture",
        description="Protocol for maintaining and passaging mammalian cell lines",
        created_by_user_id=uuid.UUID("750e8400-e29b-41d4-a716-446655440003"),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

@router.get("/protocols", tags=["protocols"], response_model=List[Protocol])
async def get_protocols():
    """Get all protocols with fake data for testing"""
    return _fake_protocols

@router.get("/protocols/{protocol_id}", tags=["protocols"], response_model=Protocol)
async def get_protocol_by_id(protocol_id: str):
    """Get a specific protocol by ID"""
    try:
        protocol_uuid = uuid.UUID(protocol_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid protocol ID format")
    
    for protocol in _fake_protocols:
        if protocol.protocol_id == protocol_uuid:
            return protocol
    
    raise HTTPException(status_code=404, detail="Protocol not found")

@router.post("/protocols/upload", tags=["protocols"], response_model=Protocol)
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
