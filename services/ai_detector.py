from groq import Groq
from flask import current_app
import os
import json

def detect_ai_content(text):
    """
    Detect if content is AI-generated using Groq's API or patterns
    Returns: {
        'is_ai_generated': bool,
        'confidence': float (0-1),
        'analysis': str
    }
    """
    
    if not text or len(text.strip()) < 50:
        return {
            'is_ai_generated': False,
            'confidence': 0.0,
            'analysis': 'Text too short to analyze'
        }
    
    # Check if Groq API key is configured
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your-groq-api-key-here':
        # Fallback to pattern-based detection
        return pattern_based_detection(text)
    
    try:
        # Use Groq to analyze the text (using free llama model)
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Free and fast model
            messages=[
                {
                    "role": "system",
                    "content": """You are an advanced plagiarism and AI content detector for academic integrity. Analyze text for:

1. **AI-Generated Content** (synthetic writing):
   - Generic, templated phrasing with high-level connectors
   - Perfect grammar with no natural errors or hesitations
   - Uniform sentence structure and lengths
   - Overuse of phrases like "furthermore," "moreover," "it's important to note"
   - Lack of personal voice, anecdotes, or first-person perspective
   - Overly formal tone without colloquialisms or contractions

2. **Potential Plagiarism** (copied/paraphrased):
   - Unnaturally sophisticated vocabulary for exam context
   - Sudden style shifts within the text
   - Very formal academic style with advanced terminology
   - Perfectly structured arguments without personal reasoning
   - Lack of exam-appropriate informal elements

3. **Human Original** (authentic student work):
   - Minor grammar variations or typos
   - Personal examples, opinions, or first-person narratives
   - Natural flow with some imperfections
   - Conversational elements, contractions
   - Student-level vocabulary and reasoning

Respond ONLY with valid JSON:
{"is_ai_generated": true/false, "confidence": 0.0-1.0, "reasoning": "brief explanation including specific indicators found", "type": "ai_generated" | "likely_plagiarized" | "human_original"}
                    """
                },
                {
                    "role": "user",
                    "content": f"Analyze this exam answer for AI generation or plagiarism:\n\n{text[:1500]}"
                }
            ],
            temperature=0.2,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON if wrapped in markdown code blocks
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        # Parse the response
        try:
            result = json.loads(result_text)
            return {
                'is_ai_generated': bool(result.get('is_ai_generated', False)),
                'confidence': float(result.get('confidence', 0.5)),
                'analysis': result.get('reasoning', 'AI analysis completed')
            }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}, Response: {result_text}")
            # Try to extract boolean from text response
            result_lower = result_text.lower()
            is_ai = 'true' in result_lower or 'ai-generated' in result_lower or 'ai generated' in result_lower
            return {
                'is_ai_generated': is_ai,
                'confidence': 0.6 if is_ai else 0.4,
                'analysis': result_text[:200] if len(result_text) < 200 else result_text[:197] + '...'
            }
            
    except Exception as e:
        print(f"Error in AI detection: {str(e)}")
        return pattern_based_detection(text)


def pattern_based_detection(text):
    """
    Enhanced pattern-based AI and plagiarism detection as fallback
    """
    ai_indicators = 0
    total_checks = 0
    reasons = []
    
    # Check 1: Sentence length analysis (AI tends toward uniformity)
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    if len(sentences) >= 3:
        total_checks += 1
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        # Calculate variance
        variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        
        # AI text often has low variance (uniform sentences)
        if variance < 15 and avg_length > 15:
            ai_indicators += 1
            reasons.append(f"Uniform sentence length (variance: {variance:.1f})")
    
    # Check 2: Personal markers (first-person, contractions)
    total_checks += 1
    personal_markers = ["i think", "i believe", "in my", "my opinion", "i've", "i have observed", "i noticed"]
    contractions = ["don't", "won't", "can't", "isn't", "aren't", "haven't", "hasn't", "didn't", "i'm", "it's"]
    
    has_personal = any(marker in text.lower() for marker in personal_markers)
    has_contractions = any(contraction in text.lower() for contraction in contractions)
    
    # Lack of personal voice suggests AI/plagiarism
    if not has_personal and not has_contractions and len(text) > 150:
        ai_indicators += 0.8
        reasons.append("No personal voice or contractions")
    elif has_personal:
        ai_indicators -= 0.5  # Human indicator
        reasons.append("Contains personal voice (human-like)")
    
    # Check 3: AI/formal academic phrases
    total_checks += 1
    ai_phrases = [
        "it's important to note", "it is important to note",
        "it's worth noting", "it is worth noting",
        "in conclusion", "to summarize",
        "furthermore", "moreover", "additionally",
        "consequently", "conversely", "concurrently",
        "delve into", "dive into",
        "holistic approach", "multifaceted",
        "paradigm shift", "unprecedented",
        "facilitate", "leverage", "utilize",
        "demonstrates significant", "substantial impact",
        "comprehensive analysis", "careful consideration"
    ]
    phrase_count = sum(1 for phrase in ai_phrases if phrase in text.lower())
    if phrase_count >= 3:
        ai_indicators += 1.2
        reasons.append(f"Contains {phrase_count} formal/AI phrases")
    elif phrase_count >= 2:
        ai_indicators += 0.6
        reasons.append(f"Contains {phrase_count} formal phrases")
    
    # Check 4: Perfect grammar indicators
    total_checks += 1
    # Look for signs of too-perfect writing
    has_typos = any(pattern in text for pattern in ['  ', ' ,', ' .', '..', ',,'])
    has_informal = any(word in text.lower() for word in ['kinda', 'sorta', 'gonna', 'wanna', 'yeah', 'ok', 'okay'])
    
    if not has_typos and not has_informal and len(text) > 200:
        ai_indicators += 0.5
        reasons.append("Perfect grammar, no informal elements")
    
    # Check 5: Passive voice overuse (common in AI/plagiarized text)
    total_checks += 1
    passive_markers = [
        "is performed", "are performed", "was performed", "were performed",
        "is done", "are done", "was done", "were done",
        "is caused", "are caused", "was caused", "were caused",
        "is created", "are created", "was created", "were created",
        "can be seen", "can be observed", "may be noted"
    ]
    passive_count = sum(1 for marker in passive_markers if marker in text.lower())
    if passive_count >= 2:
        ai_indicators += 0.7
        reasons.append(f"Overuse of passive voice ({passive_count} instances)")
    
    # Check 6: Vocabulary sophistication vs typical student writing
    total_checks += 1
    advanced_words = [
        "facilitate", "utilize", "implement", "comprehensive",
        "substantial", "predominant", "concurrent", "subsequent",
        "exemplify", "elucidate", "ameliorate", "proliferate"
    ]
    advanced_count = sum(1 for word in advanced_words if word in text.lower())
    if advanced_count >= 3:
        ai_indicators += 0.8
        reasons.append(f"Unusually sophisticated vocabulary ({advanced_count} advanced terms)")
    
    # Check 7: Transition word density
    total_checks += 1
    transitions = ["however", "therefore", "thus", "hence", "consequently", "moreover", "furthermore", "additionally", "conversely", "nonetheless"]
    transition_count = sum(1 for trans in transitions if trans in text.lower())
    word_count = len(text.split())
    if word_count > 0 and (transition_count / word_count) > 0.03:  # More than 3% transitions
        ai_indicators += 0.6
        reasons.append(f"High transition word density ({transition_count}/{word_count})")
    
    # Calculate confidence
    confidence = min(ai_indicators / total_checks, 1.0) if total_checks > 0 else 0
    is_ai_generated = confidence > 0.5
    
    # Build analysis message
    if is_ai_generated:
        analysis = f"LIKELY AI/PLAGIARISM (Pattern-based): {'; '.join(reasons)}"
    else:
        analysis = f"Appears human-written: {'; '.join(reasons) if reasons else 'Natural writing patterns detected'}"
    
    return {
        'is_ai_generated': is_ai_generated,
        'confidence': round(confidence, 2),
        'analysis': analysis
    }
