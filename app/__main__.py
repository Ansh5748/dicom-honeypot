import sys
import os

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        from app.api.main import app
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        from app.core.dicom_server import main
        main()
