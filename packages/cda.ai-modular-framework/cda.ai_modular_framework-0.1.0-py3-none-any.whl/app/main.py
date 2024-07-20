# main.py

from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from unified_control_engine.unified_control_engine import UnifiedControlEngine
from feature_service.feature_service import FeatureService
from operational_layer.operational_layer import OperationalLayer
from feature_service.openai_service.openai_service import GPTService
from request_handler.request_handler import RequestHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Initialize components
control_engine = UnifiedControlEngine()
feature_service = FeatureService()
operational_layer = OperationalLayer()
request_handler = RequestHandler()
openai_service = GPTService()

# Example custom function usage
def generate_document_feature(prompt: str) -> str:
    markdown_doc = openai_service.get_completion(prompt, "document_section", "")
    return f"Generated document content: {markdown_doc}"

feature_service.add_feature("generate_document", generate_document_feature)

# Add routes from frontend chatbot interface
app.include_router(control_engine.frontend_chatbot.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)