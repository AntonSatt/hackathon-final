import asyncio
import json
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


# ============================================================================
# ACTIVITIES - These interact with the shared shipments.json file
# ============================================================================

@activity.defn
async def update_shipment_status(shipment_id: str, status: str, current_location: str = None, issue_details: str = None):
    """Update the shipment status in the shared JSON database."""
    activity.logger.info(f"Updating shipment {shipment_id} to status: {status}")
    
    # Read the current state
    with open("shipments.json", "r") as f:
        shipments = json.load(f)
    
    # Update the shipment
    if shipment_id in shipments:
        shipments[shipment_id]["status"] = status
        if current_location:
            shipments[shipment_id]["current_location"] = current_location
        if issue_details is not None:
            shipments[shipment_id]["issue_details"] = issue_details
    
    # Write back to file
    with open("shipments.json", "w") as f:
        json.dump(shipments, f, indent=2)
    
    return {"shipment_id": shipment_id, "status": status}


@activity.defn
async def create_shipment_record(shipment_data: dict):
    """Create a new shipment record in the JSON database."""
    activity.logger.info(f"Creating shipment record: {shipment_data['shipment_id']}")
    
    # Read the current state
    with open("shipments.json", "r") as f:
        shipments = json.load(f)
    
    # Add the new shipment
    shipments[shipment_data["shipment_id"]] = shipment_data
    
    # Write back to file
    with open("shipments.json", "w") as f:
        json.dump(shipments, f, indent=2)
    
    return shipment_data


# ============================================================================
# WORKFLOW - The main shipment lifecycle orchestration
# ============================================================================

@workflow.defn
class ShipmentLifecycleWorkflow:
    def __init__(self):
        self.resolution_choice = None
    
    @workflow.run
    async def run(self, shipment_data: dict) -> dict:
        """
        Main workflow that orchestrates the shipment lifecycle.
        Flow: Pending -> In Transit -> At Customs -> Issue Detected -> (wait for signal) -> Cleared Customs -> Delivered
        """
        shipment_id = shipment_data["shipment_id"]
        workflow.logger.info(f"Starting shipment lifecycle for {shipment_id}")
        
        # Step 1: Create the shipment record
        await workflow.execute_activity(
            create_shipment_record,
            shipment_data,
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # Step 2: Simulate travel time - move to "In Transit"
        workflow.logger.info(f"{shipment_id}: Simulating travel time...")
        await asyncio.sleep(3)
        
        await workflow.execute_activity(
            update_shipment_status,
            args=[shipment_id, "In Transit", f"En route to {shipment_data['destination']}"],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # Step 3: More travel time - arrive at customs
        workflow.logger.info(f"{shipment_id}: Continuing journey...")
        await asyncio.sleep(3)
        
        await workflow.execute_activity(
            update_shipment_status,
            args=[shipment_id, "At Customs", f"Customs checkpoint - {shipment_data['destination']}"],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # Step 4: Issue detected! Set status and PAUSE
        workflow.logger.info(f"{shipment_id}: Issue detected at customs!")
        await asyncio.sleep(2)
        
        await workflow.execute_activity(
            update_shipment_status,
            args=[
                shipment_id,
                "Issue Detected",
                f"Customs checkpoint - {shipment_data['destination']}",
                "Documentation discrepancy found - requires manual review"
            ],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # PAUSE: Wait for signal with resolution choice
        workflow.logger.info(f"{shipment_id}: Waiting for resolution signal...")
        await workflow.wait_condition(lambda: self.resolution_choice is not None)
        
        # Step 5: Process the resolution based on user choice
        workflow.logger.info(f"{shipment_id}: Received resolution choice: {self.resolution_choice}")
        
        if self.resolution_choice == "expedite":
            # Express Clearance - $5000 - Fastest option
            workflow.logger.info(f"{shipment_id}: Processing express clearance (+$5000)...")
            await asyncio.sleep(2)  # Very fast processing
            await workflow.execute_activity(
                update_shipment_status,
                args=[
                    shipment_id,
                    "Cleared Customs",
                    f"Customs cleared (Express Service) - {shipment_data['destination']}",
                    None
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )
        elif self.resolution_choice == "bribe_official":
            # Facilitation Fee - $2500 - Fast but not instant
            workflow.logger.info(f"{shipment_id}: Processing facilitation payment (+$2500)...")
            await asyncio.sleep(3)  # Moderate speed
            await workflow.execute_activity(
                update_shipment_status,
                args=[
                    shipment_id,
                    "Cleared Customs",
                    f"Customs cleared (Expedited Processing) - {shipment_data['destination']}",
                    None
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )
        elif self.resolution_choice == "reroute":
            # Reroute - $3200 - Takes time to reroute but avoids delays
            workflow.logger.info(f"{shipment_id}: Rerouting shipment through alternative port (+$3200)...")
            await asyncio.sleep(4)  # Takes longer to reroute
            await workflow.execute_activity(
                update_shipment_status,
                args=[
                    shipment_id,
                    "Cleared Customs",
                    f"Rerouted and cleared (Alternative Port) - {shipment_data['destination']}",
                    None
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )
        elif self.resolution_choice == "wait":
            # Standard Wait - Free - Slowest option
            workflow.logger.info(f"{shipment_id}: Waiting for standard processing (no additional cost)...")
            await asyncio.sleep(6)  # Slowest processing
            await workflow.execute_activity(
                update_shipment_status,
                args=[
                    shipment_id,
                    "Cleared Customs",
                    f"Customs cleared (Standard Processing) - {shipment_data['destination']}",
                    None
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )
        else:
            workflow.logger.warning(f"{shipment_id}: Unknown choice, defaulting to standard processing")
            await asyncio.sleep(6)
            await workflow.execute_activity(
                update_shipment_status,
                args=[
                    shipment_id,
                    "Cleared Customs",
                    f"Customs cleared - {shipment_data['destination']}",
                    None
                ],
                start_to_close_timeout=timedelta(seconds=10),
            )
        
        # Step 6: Final delivery
        workflow.logger.info(f"{shipment_id}: Out for delivery...")
        await asyncio.sleep(3)
        
        await workflow.execute_activity(
            update_shipment_status,
            args=[
                shipment_id,
                "Delivered",
                f"Delivered to {shipment_data['destination']}"
            ],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info(f"{shipment_id}: Shipment lifecycle complete!")
        return {"shipment_id": shipment_id, "status": "Delivered", "resolution": self.resolution_choice}
    
    @workflow.signal
    async def handle_resolution(self, choice: str):
        """Signal handler that receives the user's resolution choice."""
        workflow.logger.info(f"Received resolution signal with choice: {choice}")
        self.resolution_choice = choice


# ============================================================================
# WORKER MAIN - Connect to Temporal and run the worker
# ============================================================================

async def main():
    """Connect to Temporal server and start the worker."""
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create and run the worker
    worker = Worker(
        client,
        task_queue="shipment-task-queue",
        workflows=[ShipmentLifecycleWorkflow],
        activities=[create_shipment_record, update_shipment_status],
    )
    
    print("🚀 Temporal Worker started on task queue: shipment-task-queue")
    print("📦 Listening for shipment workflows...")
    
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
