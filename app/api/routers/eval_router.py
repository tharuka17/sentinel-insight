import json
import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/report")
async def get_eval_report():
    path = "reports/eval_report.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"message": "No eval report found. Run: python -m app.eval.run_eval"}
