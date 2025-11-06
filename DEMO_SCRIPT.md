# 🎬 2-Minute Live Demo Script: Temporal-Powered Shipment Tracking

---

## **[0:00 - 0:15] THE SETUP**
**[SHOW: Frontend Dashboard]**

"Welcome! Today I'm showing you how we've built an intelligent shipment tracking system that handles real-world logistics challenges. This is our dashboard—clean, simple, real-time updates every 2 seconds. But the *real* magic is happening behind the scenes with Temporal workflows."

---

## **[0:15 - 0:25] THE CREATION**
**[SHOW: Frontend Dashboard - Form]**

"Let's create a new shipment. I'll enter a supplier—let's say 'TechParts Global'—and a destination: 'London, UK'. I'll click 'Create Shipment & Start Workflow'... and done! Look—our new shipment appears in the table with status 'Pending'."

---

## **[0:25 - 0:35] THE PROOF**
**[SHOW: Temporal Web UI - Workflows List]**

"Now here's where it gets interesting. *This* is the Temporal Web UI. See this workflow? It just started—same shipment ID we just created. Temporal is *actually* orchestrating this entire process. Every status change, every decision point, all managed by a durable, fault-tolerant workflow."

---

## **[0:35 - 0:55] THE JOURNEY**
**[SHOW: Frontend Dashboard]**

"Back to our dashboard. Watch what happens—no button clicks, no manual updates. The shipment status is changing automatically: 'In Transit'... now 'At Customs'. The workflow is simulating the real journey of this package, with realistic delays between each step. This is a long-running process that spans minutes, hours, or even days in production."

---

## **[0:55 - 1:05] THE PROBLEM**
**[SHOW: Frontend Dashboard]**

"Uh oh—'Issue Detected'. Documentation discrepancy found. In traditional systems, this is where things fall apart. But watch this..."

---

## **[1:05 - 1:15] THE "SHOW, DON'T TELL"**
**[SHOW: Temporal Web UI - Specific Workflow Details/History]**

"Switch to Temporal. See the workflow status? It's in a 'Pending' state—literally *waiting* for a signal. The workflow hasn't crashed, hasn't timed out, it's just... waiting. This is the power of durable execution. This workflow can wait for *hours* while maintaining its complete state."

---

## **[1:15 - 1:25] THE HUMAN-IN-THE-LOOP**
**[SHOW: Frontend Dashboard]**

"Back to the dashboard. Now we have action buttons: 'Expedite' or 'Wait'. This is our human-in-the-loop moment. A customs officer reviews the issue and decides to expedite. I'll click 'Expedite'..."

---

## **[1:25 - 1:35] THE RESOLUTION**
**[SHOW: Temporal Web UI - Workflow History]**

"Instantly—look at Temporal—the workflow received the signal! It's running again. You can see the signal event right here in the history. The workflow woke up, received our choice, and continued exactly where it left off. No state lost, no manual intervention."

---

## **[1:35 - 1:50] THE FINISH**
**[SHOW: Frontend Dashboard]**

"Back to the dashboard for the finale. The status updates: 'Cleared Customs'—expedited processing because of our choice. And... 'Delivered'! The complete journey, fully orchestrated, fully auditable, with a human decision seamlessly integrated into an automated process."

---

## **[1:50 - 2:00] THE VALUE**
**[SHOW: Either view, or split screen if possible]**

"This is the power of Temporal: stateful workflows that survive failures, can wait for human input for any duration, and resume exactly where they left off. Perfect for logistics, order processing, loan approvals—any complex process that spans time and requires reliability. That's our demo. Questions?"

---

## 🎯 **Demo Tips:**
- **Practice the timing** - Know exactly when to switch screens
- **Have both windows ready** - Frontend in one tab, Temporal UI in another
- **Test the flow beforehand** - Run through it 2-3 times to ensure smooth transitions
- **Emphasize the "waiting" state** - This is the most impressive part for technical audiences
- **Keep energy high** - Use phrases like "watch this", "see that?", "instantly"

## 🔧 **Technical Setup Before Demo:**
1. Start Temporal server: `temporal server start-dev`
2. Start Worker: `python run_worker.py`
3. Start API: `python run_api.py`
4. Open Temporal UI: `http://localhost:8233`
5. Open Frontend: `index.html` in browser
6. Clear old workflows in Temporal UI for clean slate

**Break a leg! 🚀**
