import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app.app import app, create_pipeline
import src.app.app as app_module

# Initialize pipeline eagerly at startup so it survives worker restarts.
# Skip in CI mode (no API key available).
if os.getenv("CI") != "true":
    try:
        app_module._pipeline = create_pipeline()
    except Exception as exc:
        app_module._pipeline_error = str(exc)

if __name__ == "__main__":
    app.run()
