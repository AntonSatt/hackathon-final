import json
import uuid
from datetime import datetime
from typing import List, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from temporalio.client import Client

from run_worker import ShipmentLifecycleWorkflow


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Logistics Shipment API",
    description="FastAPI backend for shipment tracking demo with Temporal workflows",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CreateShipmentRequest(BaseModel):
    project_name: str
    supplier_name: str
    origin: str = "Warehouse Alpha"
    destination: str
    cargo_value: int = None
    priority: str = "Standard"
    container_type: str = "40ft Standard"


class ResolveIssueRequest(BaseModel):
    choice: str  # "expedite", "wait", "bribe_official", "reroute"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Logistics Shipment API",
        "status": "running",
        "temporal_task_queue": "shipment-task-queue"
    }


@app.get("/api/shipments")
async def get_all_shipments() -> Dict[str, dict]:
    """
    Get all shipments from the shared JSON database.
    Returns the shipments as a dictionary with shipment_id as keys.
    """
    try:
        with open("shipments.json", "r") as f:
            shipments = json.load(f)
        return shipments
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Shipments database file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in shipments database")


@app.post("/api/shipments/create")
async def create_shipment(request: CreateShipmentRequest):
    """
    Create a new shipment and start the Temporal workflow.
    
    This endpoint:
    1. Generates a new shipment ID
    2. Creates a shipment object with status "Pending"
    3. Starts a Temporal workflow to manage the shipment lifecycle
    """
    # Generate a unique shipment ID
    # Use timestamp + random component for uniqueness
    timestamp = datetime.now().strftime("%m%d%H%M")
    random_suffix = str(uuid.uuid4())[:4].upper()
    shipment_id = f"SHP-{timestamp}-{random_suffix}"
    
    # Create the shipment object
    shipment_data = {
        "shipment_id": shipment_id,
        "project_name": request.project_name,
        "supplier_name": request.supplier_name,
        "origin": request.origin,
        "destination": request.destination,
        "cargo_value": request.cargo_value,
        "priority": request.priority,
        "container_type": request.container_type,
        "current_location": request.origin,
        "status": "Pending",
        "issue_details": None
    }
    
    try:
        # Connect to Temporal
        client = await Client.connect("localhost:7233")
        
        # Start the workflow
        # The workflow_id is the shipment_id for easy lookup
        await client.start_workflow(
            ShipmentLifecycleWorkflow.run,
            shipment_data,
            id=shipment_id,
            task_queue="shipment-task-queue",
        )
        
        return {
            "message": "Shipment created and workflow started",
            "shipment_id": shipment_id,
            "workflow_id": shipment_id,
            "shipment": shipment_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create shipment or start workflow: {str(e)}"
        )


@app.post("/api/shipments/{shipment_id}/resolve")
async def resolve_shipment_issue(shipment_id: str, request: ResolveIssueRequest):
    """
    Resolve a shipment issue by sending a signal to the waiting Temporal workflow.
    
    This endpoint:
    1. Gets the workflow handle using the shipment_id
    2. Sends a signal with the user's choice
    3. The workflow will resume and continue processing
    
    Valid choices: "expedite" ($5000), "bribe_official" ($2500), "wait" (free), "reroute" ($3200)
    """
    # Validate the choice
    valid_choices = ["expedite", "wait", "bribe_official", "reroute"]
    if request.choice not in valid_choices:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid choice. Must be one of: {', '.join(valid_choices)}"
        )
    
    try:
        # Connect to Temporal
        client = await Client.connect("localhost:7233")
        
        # Get the workflow handle using the shipment_id as workflow_id
        handle = client.get_workflow_handle(shipment_id)
        
        # Send the signal to resume the workflow
        await handle.signal(ShipmentLifecycleWorkflow.handle_resolution, request.choice)
        
        return {
            "message": "Resolution signal sent to workflow",
            "shipment_id": shipment_id,
            "choice": request.choice
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send signal to workflow: {str(e)}"
        )


@app.get("/api/shipments/{shipment_id}")
async def get_shipment(shipment_id: str):
    """Get a specific shipment by ID."""
    try:
        with open("shipments.json", "r") as f:
            shipments = json.load(f)
        
        if shipment_id not in shipments:
            raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
        
        return shipments[shipment_id]
    
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Shipments database file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in shipments database")


# ============================================================================
# RUN THE SERVER
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting FastAPI server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
