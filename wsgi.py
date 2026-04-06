import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app.app import app, create_pipeline
import src.app.app as app_module

# With gunicorn --preload, this runs in the master process BEFORE workers fork.
# Workers inherit _pipeline via copy-on-write, so:
# - No re-loading on worker restart (master still holds loaded pipeline)
# - No blocking health checks (workers are only spawned after this completes)
# - Memory is shared between master and workers (not duplicated until written)
if os.getenv("CI") != "true":
    try:
        print("Loading pipeline in master process...", flush=True)
        app_module._pipeline = create_pipeline()
        print("Pipeline ready.", flush=True)
    except Exception as exc:
        app_module._pipeline_error = str(exc)
        print(f"Pipeline load failed: {exc}", flush=True)

if __name__ == "__main__":
    app.run()
