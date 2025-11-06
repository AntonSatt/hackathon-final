# 🔄 Resilient Flow - Temporal Supply Chain Demo

An intelligent shipment tracking system powered by **Temporal workflows** that demonstrates long-running processes, issue detection, and human-in-the-loop decision making.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Temporal CLI installed ([Installation Guide](https://docs.temporal.io/cli#install))

### Running the Application

You need **3 terminal windows** running simultaneously:

#### Terminal 1: Temporal Server
```bash
temporal server start-dev
```
This starts the Temporal development server with the Web UI at `http://localhost:8233`

#### Terminal 2: Temporal Worker
```bash
python run_worker.py
```
This runs the Temporal worker that executes the shipment lifecycle workflows.

#### Terminal 3: FastAPI Backend
```bash
python run_api.py
```
This starts the REST API server at `http://localhost:8000`

#### Terminal 4: Open the Frontend
Simply open `index.html` in your web browser, or use:
```bash
# Using Python's built-in server (optional)
python -m http.server 8080
# Then navigate to http://localhost:8080
```

---

## 🎯 How It Works

### Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Frontend  │ ───> │  FastAPI     │ ───> │    Temporal     │
│  (HTML/JS)  │      │   Backend    │      │     Worker      │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │                        │
                            └────────────────────────┘
                              Temporal Server (Orchestration)
```

### Components

#### 1. **Frontend (index.html)**
- Real-time dashboard that polls every 2 seconds
- Create shipments (random or custom)
- Monitor active shipments with visual timeline
- Resolve issues when they occur
- View completed shipments

#### 2. **FastAPI Backend (run_api.py)**
- REST API endpoints for shipment management
- `/api/shipments` - Get all shipments
- `/api/shipments/create` - Create new shipment (starts Temporal workflow)
- `/api/shipments/{id}/resolve` - Send resolution signal to workflow
- Reads/writes shipment data to `shipments.json`

#### 3. **Temporal Worker (run_worker.py)**
- Defines the `ShipmentLifecycleWorkflow`
- Simulates realistic shipment journey:
  1. **Pending** → In Transit
  2. **In Transit** → At Customs
  3. **At Customs** → Random issue detection (60% chance)
  4. **Issue Detected** → Wait for human resolution signal
  5. **Cleared Customs** → Delivered

#### 4. **Temporal Server**
- Orchestrates all workflows
- Provides durability and fault tolerance
- Web UI at `http://localhost:8233` to inspect workflows

---

## 🎮 Demo Flow

1. **Create a Shipment** - Click "🎲 Quick Random" or "➕ Create Custom" in the navbar
2. **Watch It Progress** - The workflow automatically moves through stages with realistic delays
3. **Handle Issues** - When an issue is detected, choose a resolution strategy:
   - ⚡ **Express** - Fast but expensive (~30s, $3k-$9k)
   - 💼 **Facilitation** - Moderate speed and cost (~40s, $1.5k-$4.5k)
   - 🔄 **Reroute** - Alternative route (~50s, $2k-$6k)
   - ⏳ **Wait** - Slow but free (~60s, $0)
4. **Workflow Resumes** - After resolution, shipment continues to delivery
5. **View in Temporal UI** - See the workflow execution history at `http://localhost:8233`

---

## 🔍 Key Features

### Temporal Workflow Benefits
- **Durable Execution**: Workflows survive crashes and restarts
- **Long-Running Processes**: Handle shipments that take hours/days
- **Human-in-the-Loop**: Pause workflows waiting for user decisions
- **Complete History**: Every state change is recorded and queryable
- **Retry Logic**: Automatic retries on transient failures

### Real-World Simulation
- Funny random shipment names ("Operation Rubber Duck")
- Realistic delays between stages (15-45 seconds)
- Random issue scenarios (customs delays, documentation issues, pirate attacks!)
- Multiple resolution strategies with different costs/timeframes

---

## 📁 File Structure

```
version-2/
├── index.html           # Frontend dashboard
├── run_api.py          # FastAPI backend server
├── run_worker.py       # Temporal worker & workflow definitions
├── shipments.json      # Persistent shipment data storage
├── reset_shipments.sh  # Script to clear all shipments
└── DEMO_SCRIPT.md      # Live demo presentation script
```

---

## 🛠️ Troubleshooting

### Port Already in Use
If you see "Address already in use" errors:
```bash
# Kill process on port 8000 (FastAPI)
lsof -ti:8000 | xargs kill -9

# Kill process on port 7233 (Temporal)
lsof -ti:7233 | xargs kill -9
```

### Reset Everything
```bash
./reset_shipments.sh  # Clears shipments.json
# Then restart all 3 terminals
```

### Workflows Not Starting
1. Make sure Temporal server is running (`temporal server start-dev`)
2. Verify worker is connected (check worker terminal for "Worker started" message)
3. Check FastAPI logs for connection errors

---

## 🎬 Demo Script

For a structured 2-minute demo presentation, see [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

---

## 📚 Learn More

- [Temporal Documentation](https://docs.temporal.io/)
- [Temporal Python SDK](https://docs.temporal.io/dev-guide/python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🎉 Credits

Built for Temporal hackathon to demonstrate the power of durable workflow orchestration in supply chain logistics.

© Team CI/CDamn! Anton Sätterkvist, Alex, Axel, Vincent, Patrik