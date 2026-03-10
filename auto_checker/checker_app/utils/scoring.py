"""Scoring logic for all competition rounds."""


def score_omr(student_answers: dict, answer_key: dict) -> int:
    """
    Score OMR answers.
    Correct = +1, Wrong = 0.
    """
    score = 0
    for q_num, correct in answer_key.items():
        if student_answers.get(q_num, '').upper() == correct.upper():
            score += 1
    return score


def score_debug(student_answers: dict, answer_key: dict) -> int:
    """
    Score debug sheet.
    Correct error identification = 1 point.
    Correct output = 2 points.
    Total per question = 3 points.
    """
    score = 0
    # Find all question numbers in the answer key
    q_nums = set()
    for label in answer_key:
        if '_ERROR' in label or '_OUTPUT' in label:
            try:
                q = int(label.replace('Q', '').split('_')[0])
                q_nums.add(q)
            except ValueError:
                continue

    for q in sorted(q_nums):
        error_key = f"Q{q}_ERROR"
        output_key = f"Q{q}_OUTPUT"

        # Check error identification (fuzzy match — check if key terms overlap)
        if error_key in answer_key and error_key in student_answers:
            if _fuzzy_match(student_answers[error_key], answer_key[error_key]):
                score += 1

        # Check correct output
        if output_key in answer_key and output_key in student_answers:
            if _fuzzy_match(student_answers[output_key], answer_key[output_key]):
                score += 2

    return score


def _fuzzy_match(student_text: str, key_text: str) -> bool:
    """Simple fuzzy matching — check if key terms from answer key appear in student answer."""
    student_lower = student_text.lower().strip()
    key_lower = key_text.lower().strip()

    # Exact match
    if student_lower == key_lower:
        return True

    # Check if significant words from key appear in student answer
    key_words = {w for w in key_lower.split() if len(w) > 2}
    if not key_words:
        return student_lower == key_lower

    matches = sum(1 for w in key_words if w in student_lower)
    return matches / len(key_words) >= 0.6


def score_dsa(evaluations: dict) -> dict:
    """
    Score DSA round with partial marking.
    Q1 = 10 marks, Q2 = 20 marks, Q3 = 30 marks.

    Partial marking per question:
        Declaration present → 10% of marks
        Looping logic present → 20% of marks
        Correct algorithm → remaining 70% of marks
    """
    max_marks = {'Q1': 10, 'Q2': 20, 'Q3': 30}
    scores = {}

    for q_label, total_marks in max_marks.items():
        q_score = 0.0
        decl_key = f"{q_label}_DECLARATION"
        loop_key = f"{q_label}_LOOP"
        algo_key = f"{q_label}_ALGORITHM"

        if evaluations.get(decl_key, False):
            q_score += total_marks * 0.10  # 10%

        if evaluations.get(loop_key, False):
            q_score += total_marks * 0.20  # 20%

        if evaluations.get(algo_key, False):
            q_score += total_marks * 0.70  # 70%

        scores[q_label.lower()] = round(q_score, 1)

    scores['total'] = round(scores['q1'] + scores['q2'] + scores['q3'], 1)
    return scores
