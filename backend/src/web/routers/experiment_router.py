from fastapi import APIRouter, HTTPException, UploadFile, File
from src.dal.databases.experiment_dal import ExperimentDAL
from src.core.entities.experiment_entities import (
    Experiment, 
    StartExperimentRequest, 
    StartExperimentResponse,
    StopExperimentRequest,
    StopExperimentResponse
)
from src.core.services.experiment_service import ExperimentService
from datetime import datetime
import uuid

router = APIRouter(prefix="/experiments")

# Initialize experiment DAL
experiment_dal = ExperimentDAL()

# Initialize experiment service
experiment_service = ExperimentService()

# Global conversation state - in production this should be session-based
conversation = [
    {"role": "system", "content": "You are an experiment assistant guiding a scientist step-by-step through a protocol."}
]

@router.post("/start", response_model=StartExperimentResponse)
async def start_experiment(request: StartExperimentRequest):
    """Start a new experiment for a protocol"""
    try:
        # Generate new experiment ID
        experiment_id = uuid.uuid4()
        now = datetime.now()
        
        # Create experiment entity
        experiment = Experiment(
            experiment_id=experiment_id,
            protocol_id=uuid.UUID(request.protocol_id),
            user_id=uuid.UUID(request.user_id) if request.user_id else None,
            start_time=now,
            end_time=None,
            status="in_progress",
            created_at=now,
            updated_at=now
        )
        
        # Save to database
        saved_experiment = experiment_dal.create_experiment(experiment)
        
        return StartExperimentResponse(
            experiment_id=str(saved_experiment.experiment_id),
            status=saved_experiment.status,
            message=f"Experiment started successfully for protocol {request.protocol_id}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting experiment: {str(e)}")

@router.post("/stop", response_model=StopExperimentResponse)
async def stop_experiment(request: StopExperimentRequest):
    """Stop an existing experiment"""
    try:
        # Get the existing experiment
        experiment = experiment_dal.get_experiment(request.experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail=f"Experiment {request.experiment_id} not found")
        
        # Update experiment with end time
        end_time = request.end_time if request.end_time else datetime.now()
        experiment.end_time = end_time
        experiment.status = "completed"
        experiment.updated_at = datetime.now()
        
        # Save updated experiment
        updated_experiment = experiment_dal.update_experiment(experiment)
        
        return StopExperimentResponse(
            experiment_id=str(updated_experiment.experiment_id),
            status=updated_experiment.status,
            message=f"Experiment {request.experiment_id} stopped successfully"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping experiment: {str(e)}")

@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str):
    """Get experiment details by ID"""
    try:
        experiment = experiment_dal.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found")
        
        return {
            "experiment_id": str(experiment.experiment_id),
            "protocol_id": str(experiment.protocol_id),
            "user_id": str(experiment.user_id) if experiment.user_id else None,
            "start_time": experiment.start_time,
            "end_time": experiment.end_time,
            "status": experiment.status,
            "created_at": experiment.created_at,
            "updated_at": experiment.updated_at
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting experiment: {str(e)}")

@router.get("/protocol/{protocol_id}")
async def get_experiments_by_protocol(protocol_id: str):
    """Get all experiments for a specific protocol"""
    try:
        experiments = experiment_dal.get_experiments_by_protocol_id(protocol_id)
        
        return {
            "protocol_id": protocol_id,
            "experiments": [
                {
                    "experiment_id": str(exp.experiment_id),
                    "user_id": str(exp.user_id) if exp.user_id else None,
                    "start_time": exp.start_time,
                    "end_time": exp.end_time,
                    "status": exp.status,
                    "created_at": exp.created_at,
                    "updated_at": exp.updated_at
                }
                for exp in experiments
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting experiments by protocol: {str(e)}")

@router.post("/voice-turn")
async def voice_turn(file: UploadFile = File(...)):
    """Process voice input and return transcript and AI reply"""
    try:
        return await experiment_service.voice_turn(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in voice_turn endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing voice input: {str(e)}")
