from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

static_dir = Path(__file__).parent.parent.parent / "static"

@router.get("/")
async def get_index():
    """Serve the index.html file."""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index page not found")
    return FileResponse(index_path)

@router.get("/{filename}")
async def get_static_file(filename: str):
    """Serve a static file."""
    file_path = static_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    return FileResponse(file_path)
