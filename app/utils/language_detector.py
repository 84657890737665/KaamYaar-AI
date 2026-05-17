import re

LANGUAGE_KEYWORDS = {
    'punjabi': ['ki', 'tusi', 'twada', 'kithay', 'assi', 'chahida', 'kar', 'de', 'lor', 'vich', 'wa'],
    'sindhi': ['kee', 'ahayo', 'muhinjo', 'kithay', 'achi', 'aahey', 'ghar', 'karan'],
    'pashto': ['tsanga', 'ye', 'der', 'kha', 'shta', 'kawal', 'zama', 'mung', 'pakaar'],
    'balochi': ['chone', 'asti', 'mani', 'shuma', 'tara', 'waja'],
    'shina': ['khuda', 'joon', 'ashi', 'thu', 'bey'],
    'urdu': ['hai', 'kia', 'kaise', 'mujhe', 'chahiye', 'kahan', 'bhejo', 'jaldi'],
    'roman_urdu': ['hai', 'kia', 'kaise', 'mujhe', 'chahiye', 'kahan', 'bhejo', 'jaldi'],
    'english': ['need', 'want', 'where', 'how', 'service', 'please', 'urgent', 'fix']
}

def detect_language_fallback(text: str) -> str:
    text_lower = text.lower()
    scores = {lang: 0 for lang in LANGUAGE_KEYWORDS}
    
    # Basic word matching
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        for lang, keywords in LANGUAGE_KEYWORDS.items():
            if word in keywords:
                scores[lang] += 1
                
    best_lang = max(scores, key=scores.get)
    if scores[best_lang] > 0:
        return best_lang
    return 'english' # Default fallback
