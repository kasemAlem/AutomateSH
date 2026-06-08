# 🚀 The Delta Secret Behind Linear's Blazing Speed

**Subject:** How Linear Saves Your Team 100+ Hours/Year

---

This week in automation, we're diving deep into one of the most impressive feats of modern engineering: **how Linear achieves its near-instant UI responsiveness**—even with 10,000+ issues.

Here's the technical breakdown.

---

## 📦 This Week's Spotlight: Linear's Delta Patch Architecture

Linear doesn't just "feel fast"—it's architecturally designed to minimize every millisecond between user action and UI update.

**The core insight:** Most tools re-render entire UI trees on every change. Linear precomputes UI state on the server, then sends only the *difference* (delta) over WebSockets.

The result? Only changed nodes re-render. The entire tree stays untouched.

**The hidden cost of lag:** A 2-second delay per action → 30 minutes of lost flow state daily → **100+ hours wasted per year** per developer.

---

## 🛠️ Actionable Takeaway: Implement Delta Patches Yourself

Here's the pattern you can steal today—simplified, but the architecture is the same:

```python
import asyncio
import json
import websockets

# The magic: server precomputes UI state delta,
# sending only changed node IDs via WebSocket patch

async def handle_client(websocket):
    async for message in websocket:
        # Simulate server-side state computation
        current_state = get_full_state()  # Precomputed on server
        
        # Compute only the delta (changed nodes)
        delta = compute_delta(current_state, previous_state)
        
        # Send minimal payload over WebSocket
        await websocket.send(json.dumps({
            "type": "delta_patch",
            "nodes": delta["changed_node_ids"],
            "data": delta["changed_data"]
        }))

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # run forever
```

**Key insight:** The server holds the canonical state. The client holds optimistic mutations. The delta patch reconciles both—sending *only* what changed.

---

## 🔑 Why This Matters for Your Stack

If you're building anything with real-time collaboration, issue tracking, or dashboards:
- **Stop re-rendering everything.** Start computing diffs server-side.
- **Use WebSocket patches** (not full state syncs).
- **Let the server be the source of truth**—the client just applies patches.

Linear's approach isn't just "fast"—it's architecturally efficient. And that's the difference between a tool you tolerate and one you *love* using.

---

*Try implementing a delta patch in your next real-time feature. Your users' flow state will thank you.*

**Reply to this email** if you want me to dive deeper into GraphQL resolver optimization for delta computation.

— The Automate.sh Team