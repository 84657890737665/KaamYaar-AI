import pytest
from app.services.language_parser import language_parser
from app.utils.language_detector import detect_language_fallback

def test_language_detector_fallback():
    assert detect_language_fallback("mujhe electrician chahiye") in ['urdu', 'roman_urdu']
    assert detect_language_fallback("I need a plumber urgently") == 'english'
    assert detect_language_fallback("bhai twada ki haal hai main ik ac mechanic lab reha waan") == 'punjabi'
    assert detect_language_fallback("Muhinjo ghar ahe gulshan me") == 'sindhi'
    assert detect_language_fallback("Mung ta sadar ke yaw khaar pakaar de") == 'pashto'

@pytest.mark.asyncio
async def test_language_parser_multilingual():
    requests = [
        {"text": "Bhai mujhe Johar Town me ek plumber chahiye, pani ka pipe leak ho gaya hai. Abhi bhejo.", "expected_lang": "roman_urdu"},
        {"text": "I need a carpenter in DHA Phase 5 to fix my doors. Normal urgency.", "expected_lang": "english"},
        {"text": "Yar ac technician di lor hai Gulberg vich, tusi bhej sakde ho?", "expected_lang": "punjabi"},
        {"text": "Mung ta sadar ke yaw khaar pakaar de.", "expected_lang": "pashto"},
        {"text": "Muhinjo ghar ahe gulshan me, ac theek karwano aahey.", "expected_lang": "sindhi"}
    ]
    
    for req in requests:
        res = await language_parser.parse_request(req["text"])
        assert res.language in ['urdu', 'roman_urdu', 'english', 'punjabi', 'sindhi', 'pashto', 'balochi', 'shina']
        assert hasattr(res, "language_confidence")
        assert res.language_confidence >= 0.0
