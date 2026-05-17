from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.services.language_parser import language_parser, ParseRequestOutput
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/parse-request",
    tags=["parse-request"],
)

class ParseRequestInput(BaseModel):
    raw_text: str = Field(..., description="The raw input text from the user.")
    language_hint: Optional[str] = Field("auto", description="Language hint, e.g., 'auto', 'en', 'ur', 'roman_ur'.")

@router.post("", response_model=ParseRequestOutput)
async def parse_request(request: ParseRequestInput):
    result = await language_parser.parse_request(request.raw_text)
    return result
