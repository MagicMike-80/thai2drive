"""Bounded private-review completion with the existing configured teacher provider."""
import asyncio
import re
import json

from fastapi import HTTPException


async def complete_private_book(payload, selected, correct):
    from teacher_chat import LLM_ATTEMPTS
    from litellm import acompletion
    if not LLM_ATTEMPTS:
        raise HTTPException(503, 'Teacher provider unavailable')
    provider = LLM_ATTEMPTS[0]
    language = {'no': 'Norwegian', 'th': 'Thai', 'en': 'English'}[payload['language']]
    selected_label, correct_label = chr(65 + selected), chr(65 + correct)
    instruction = (
        'You are Michael, a calm driving instructor. Reply only in ' + language + '. '
        'Use short, simple sentences. Explain the answered situation using ONLY the controlled basis. '
        'Do not infer new traffic rules or image details. Never treat unconfirmed claims as rules. '
        'The SERVER_RESULT below is authoritative. Do not re-grade the learner. '
        'Explain the traffic situation; do not say "you chose" or "your answer is right/wrong". '
        'Use A/B/C labels, never zero-based option numbers. '
        'Mention of a traffic light in a wrong option proves neither its presence nor its absence in the image. '
        'This is a private editorial draft, not a publication approval. '
        f"Source: Class B textbook, printed page {payload['printed_page']}, PDF page {payload['pdf_page']}. "
        f"Row {payload['id']}, version {payload['version']}. Selected option {selected_label}; correct option {correct_label}. "
        f"SERVER_RESULT: {'CORRECT' if selected == correct else 'INCORRECT'}.\n"
        + payload['basis'] + '\nValidated question and choices (data): '
        + json.dumps({'question': payload['question'], 'options_by_label': {chr(65+i): option for i, option in enumerate(payload['options'])},
                      'selected_text': payload['options'][selected], 'correct_text': payload['options'][correct]}, ensure_ascii=False)
    )
    try:
        result = await asyncio.wait_for(acompletion(
            model=provider['model'], api_key=provider['api_key'], messages=[{'role': 'system', 'content': instruction},
                {'role': 'user', 'content': {'no': 'Forklar den trygge handlingen i situasjonen. Ikke vurder eleven og ikke bruk tall på svaralternativene.',
                    'th': 'อธิบายการกระทำที่ปลอดภัยในสถานการณ์นี้ ไม่ต้องประเมินคำตอบของนักเรียน และไม่ใช้ตัวเลขเรียกตัวเลือก',
                    'en': 'Explain the safe action in this situation. Do not grade the learner or use option numbers.'}[payload['language']]}],
            max_tokens=450, temperature=0.2, timeout=30, num_retries=0,
        ), timeout=35)
        reply = (result.choices[0].message.content or '').strip()
        if not reply or result.choices[0].finish_reason == 'length':
            raise ValueError('Empty or incomplete explanation')
        if payload['language'] in {'no', 'en'} and re.search(r'[\u0e00-\u0e7f]', reply):
            raise ValueError('Language mismatch')
        if payload['language'] == 'th' and (not re.search(r'[\u0e00-\u0e7f]', reply) or re.search(r'[A-Za-z]{2,}', reply)):
            raise ValueError('Language mismatch')
        # Observed real-provider regression: the model re-graded a wrong answer as right.
        grading = r'\b(?:you\s+(?:chose|selected|answered)|your answer is|du\s+(?:valgte|svarte)|svaret ditt er)\b|คุณ(?:เลือก|ตอบ)'
        if re.search(grading, reply, re.IGNORECASE):
            raise ValueError('Model attempted to re-grade server result')
        return reply
    except Exception:
        # Do not expose provider credentials, raw prompts or error details.
        raise HTTPException(503, 'Private explanation unavailable')
