import argparse
import asyncio
import sys
import logging
import uvicorn
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.events import GoToEvent, PageEvent, BackEvent
from noetic_engine.runtime import NoeticEngine
from noetic_engine.loader import NoeticLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start engine in the background when FastAPI starts
    codex_path = app.state.codex_path
    engine = app.state.engine
    
    loader = NoeticLoader()
    loader.load(engine, codex_path)
    
    # Run engine start in a task so it doesn't block lifespan
    task = asyncio.create_task(engine.start())
    logger.info(f"Noetic Engine background task started with codex: {codex_path}")
    
    yield
    
    # Shutdown
    await engine.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

def create_app(engine: NoeticEngine, codex_path: str):
    app = FastAPI(lifespan=lifespan)
    app.state.engine = engine
    app.state.codex_path = codex_path

    @app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
    def api_index(event: Optional[str] = None) -> list[AnyComponent]:
        """
        Returns the latest UI tree rendered by the Reflex loop.
        Processes an optional 'event' trigger.
        """
        if event:
            logger.info(f"Processing Event: {event}")
            if event.startswith("project."):
                # Resolve title from world state
                ws = engine.knowledge.get_world_state()
                title = "Unknown Project"
                # Check for project by ID string or name alias
                for eid, entity in ws.entities.items():
                    if str(eid) == event or entity.attributes.get("name") == event:
                        title = entity.attributes.get("title", "Unnamed")
                        break
                
                summary = f"Viewing details for: {title}. Status is active."
                logger.info(f"Updating local state: selected_project_summary = {summary}")
                engine.reflex.manager.update("selected_project_summary", summary)
            else:
                engine.push_event(event, {})
            
            # Small delay to ensure any background DB writes are finalized 
            import time
            time.sleep(0.1)
            
            # Force refresh so latest_ui is updated before we return it
            engine.refresh_ui()
            logger.info(f"UI Refreshed. Summary in local_state: {engine.reflex.manager.local_state.get('selected_project_summary')}")

        if engine.latest_ui is not None:
            ui = engine.latest_ui
            components = ui if isinstance(ui, list) else [ui]
            logger.info(f"Rendering UI with {len(components)} components. Event param: {event}")
            # logger.debug(f"UI Tree: {components}")
            return components
        
        return [c.Page(components=[c.Text(text="Engine starting... please refresh in a moment.")])]

    @app.get("/{path:path}")
    async def html_landing() -> HTMLResponse:
        """
        Serves the prebuilt HTML shell.
        """
        return HTMLResponse(prebuilt_html(title="Noetic Nexus OS"))
    
    return app

def main():
    parser = argparse.ArgumentParser(description="Noetic Engine Reference Implementation")
    parser.add_argument("--codex", type=str, required=True, help="Path to the .noetic Codex file")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve the UI on")
    args = parser.parse_args()

    engine = NoeticEngine()
    app = create_app(engine, args.codex)

    # Start Web Server (lifespan will handle the engine)
    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()