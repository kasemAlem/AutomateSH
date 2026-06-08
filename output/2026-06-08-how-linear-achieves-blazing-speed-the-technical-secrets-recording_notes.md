# Recording Notes for: **The Delta Patch That Makes Linear Instant**

## Code to Record
```
import asyncio, json, websockets
# The magic: server precomputes UI state delta, sending only changed node IDs via WebSocket patch
async def linear_delta(ws, path):
    async for msg in ws:
        patch = json.loads(msg)  # Client sends: {"op":"move","issue":"PROJ-420","to":"in_progress"}
        # Server merges optimistic mutation with precomputed aggregate cache (no JOINs)
        delta = {"updated": [patch["issue"]], "aggregates": {"Proj": {"open": 42}}}  # denormalized count
        await ws.send(json.dumps(delta))  # Only re-render these nodes, not the entire 10k-issue tree
asyncio.run(websockets.serve(linear_delta, "localhost", 8765))
```

## Original Script (with visual cues)
Open Linear with 10,000 issues. Now open your current tool. Count the seconds.

That two-second lag per action costs your team 30 minutes of flow state daily—over 100 hours wasted per year.

Linear precomputes UI state on the server using a custom GraphQL resolver layer, merging incremental database updates with client-side optimistic mutations.

Here's the delta patch over WebSockets—only changed nodes re-render, not the entire tree.

Follow for more engineering secrets.
