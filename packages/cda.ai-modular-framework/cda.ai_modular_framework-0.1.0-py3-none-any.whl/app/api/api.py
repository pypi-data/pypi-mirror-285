from fastapi import APIRouter

router = APIRouter()

@router.post("/generate_document/")
def generate_document(prompt: str):
    result = feature_service.run_feature("generate_document", prompt)
    return {"message": result}