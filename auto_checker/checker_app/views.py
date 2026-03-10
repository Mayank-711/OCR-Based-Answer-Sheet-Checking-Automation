import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages

from .utils.gemma_client import GemmaClient
from .utils.ocr_utils import extract_text_from_image, extract_text_from_pdf, parse_answer_key
from .utils.scoring import score_omr, score_debug, score_dsa
from .utils.excel_generator import (
    generate_omr_excel,
    generate_debug_excel,
    generate_dsa_excel,
    generate_final_excel,
)


def _save_upload(uploaded_file):
    """Save an uploaded file to a temp path and return the path."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    return path


# ─── PAGE 1: OMR CHECKING ────────────────────────────────────────────

def omr_view(request):
    if request.method == 'POST':
        answer_key_file = request.FILES.get('answer_key')
        sheet_files = request.FILES.getlist('sheets')

        if not answer_key_file or not sheet_files:
            messages.error(request, 'Please upload both the answer key and at least one OMR sheet.')
            return render(request, 'omr.html')

        # Parse answer key
        key_text = answer_key_file.read().decode('utf-8', errors='ignore')
        answer_key = parse_answer_key(key_text)

        client = GemmaClient()
        results = []

        for sheet in sheet_files:
            tmp_path = _save_upload(sheet)
            try:
                ext = os.path.splitext(sheet.name)[1].lower()
                if ext in ('.pdf',):
                    extracted = extract_text_from_pdf(tmp_path, client)
                else:
                    extracted = extract_text_from_image(tmp_path, client)

                # Ask Gemma to parse OMR data
                prompt = (
                    "You are an OMR sheet reader. From the following extracted text of an OMR answer sheet, "
                    "extract the student's name and their marked answers.\n"
                    "Return ONLY in this exact format (no extra text):\n"
                    "NAME: <student name>\n"
                    "1:A\n2:B\n3:C\n...\n\n"
                    f"Extracted text:\n{extracted}"
                )
                parsed = client.generate(prompt)
                name, student_answers = _parse_omr_response(parsed)
                score = score_omr(student_answers, answer_key)
                results.append({'name': name, 'score': score})
            finally:
                os.unlink(tmp_path)

        # Generate Excel
        excel_bytes = generate_omr_excel(results)
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="omr_results.xlsx"'
        return response

    return render(request, 'omr.html')


def _parse_omr_response(text):
    """Parse Gemma's OMR response into (name, {q_num: answer})."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    name = "Unknown"
    answers = {}
    for line in lines:
        if line.upper().startswith('NAME:'):
            name = line.split(':', 1)[1].strip()
        elif ':' in line:
            parts = line.split(':', 1)
            try:
                q_num = int(parts[0].strip())
                ans = parts[1].strip().upper()
                if ans in ('A', 'B', 'C', 'D'):
                    answers[q_num] = ans
            except ValueError:
                continue
    return name, answers


# ─── PAGE 2: DEBUG SHEET CHECKING ────────────────────────────────────

def debug_view(request):
    if request.method == 'POST':
        answer_key_file = request.FILES.get('answer_key')
        sheet_files = request.FILES.getlist('sheets')

        if not answer_key_file or not sheet_files:
            messages.error(request, 'Please upload both the answer key and at least one answer sheet.')
            return render(request, 'debug.html')

        key_text = answer_key_file.read().decode('utf-8', errors='ignore')
        answer_key = _parse_debug_answer_key(key_text)

        client = GemmaClient()
        results = []

        for sheet in sheet_files:
            tmp_path = _save_upload(sheet)
            try:
                extracted = extract_text_from_pdf(tmp_path, client)

                prompt = (
                    "You are checking a debug competition answer sheet. "
                    "The sheet has questions where students identify errors in buggy pseudocode "
                    "and provide the correct output.\n"
                    "Extract the student name (found on the first page) and for each question extract:\n"
                    "- The error identified by the student\n"
                    "- The correct output written by the student\n\n"
                    "Return ONLY in this exact format:\n"
                    "NAME: <student name>\n"
                    "Q1_ERROR: <identified error>\n"
                    "Q1_OUTPUT: <correct output>\n"
                    "Q2_ERROR: <identified error>\n"
                    "Q2_OUTPUT: <correct output>\n"
                    "...\n\n"
                    f"Extracted text:\n{extracted}"
                )
                parsed = client.generate(prompt)
                name, student_answers = _parse_debug_response(parsed)
                score = score_debug(student_answers, answer_key)
                results.append({'name': name, 'score': score})
            finally:
                os.unlink(tmp_path)

        excel_bytes = generate_debug_excel(results)
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="debug_results.xlsx"'
        return response

    return render(request, 'debug.html')


def _parse_debug_answer_key(text):
    """
    Parse debug answer key. Expected format:
    Q1_ERROR: description of error
    Q1_OUTPUT: expected output
    Q2_ERROR: ...
    Q2_OUTPUT: ...
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    key = {}
    for line in lines:
        if ':' not in line:
            continue
        label, value = line.split(':', 1)
        label = label.strip().upper()
        value = value.strip()
        key[label] = value
    return key


def _parse_debug_response(text):
    """Parse Gemma's debug response."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    name = "Unknown"
    answers = {}
    for line in lines:
        if line.upper().startswith('NAME:'):
            name = line.split(':', 1)[1].strip()
        elif ':' in line:
            label, value = line.split(':', 1)
            label = label.strip().upper()
            value = value.strip()
            answers[label] = value
    return name, answers


# ─── PAGE 3: DSA ROUND CHECKING ──────────────────────────────────────

def dsa_view(request):
    if request.method == 'POST':
        sheet_files = request.FILES.getlist('sheets')

        if not sheet_files:
            messages.error(request, 'Please upload at least one answer sheet.')
            return render(request, 'dsa.html')

        client = GemmaClient()
        results = []

        for sheet in sheet_files:
            tmp_path = _save_upload(sheet)
            try:
                extracted = extract_text_from_pdf(tmp_path, client)

                prompt = (
                    "You are evaluating a DSA coding competition answer sheet. "
                    "The student solved 3 coding questions in Python, Java, C++, or Pseudocode.\n\n"
                    "For EACH question (Q1, Q2, Q3), analyze the code and determine:\n"
                    "1. Are variables/data structures properly declared? (yes/no)\n"
                    "2. Is proper looping/iteration logic present? (yes/no)\n"
                    "3. Is the overall algorithm correct and complete? (yes/no)\n\n"
                    "Also extract the student's name from the sheet.\n\n"
                    "Return ONLY in this exact format:\n"
                    "NAME: <student name>\n"
                    "Q1_DECLARATION: yes/no\n"
                    "Q1_LOOP: yes/no\n"
                    "Q1_ALGORITHM: yes/no\n"
                    "Q2_DECLARATION: yes/no\n"
                    "Q2_LOOP: yes/no\n"
                    "Q2_ALGORITHM: yes/no\n"
                    "Q3_DECLARATION: yes/no\n"
                    "Q3_LOOP: yes/no\n"
                    "Q3_ALGORITHM: yes/no\n\n"
                    f"Extracted text:\n{extracted}"
                )
                parsed = client.generate(prompt)
                name, evaluations = _parse_dsa_response(parsed)
                scores = score_dsa(evaluations)
                results.append({
                    'name': name,
                    'q1': scores['q1'],
                    'q2': scores['q2'],
                    'q3': scores['q3'],
                    'total': scores['total'],
                })
            finally:
                os.unlink(tmp_path)

        excel_bytes = generate_dsa_excel(results)
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="dsa_results.xlsx"'
        return response

    return render(request, 'dsa.html')


def _parse_dsa_response(text):
    """Parse Gemma's DSA evaluation response."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    name = "Unknown"
    evaluations = {}
    for line in lines:
        if line.upper().startswith('NAME:'):
            name = line.split(':', 1)[1].strip()
        elif ':' in line:
            label, value = line.split(':', 1)
            label = label.strip().upper()
            value = value.strip().lower()
            evaluations[label] = value in ('yes', 'true', '1')
    return name, evaluations


# ─── PAGE 4: FINAL SCORE MERGER ──────────────────────────────────────

def merger_view(request):
    if request.method == 'POST':
        omr_file = request.FILES.get('omr_file')
        debug_file = request.FILES.get('debug_file')
        dsa_file = request.FILES.get('dsa_file')
        puzzle_file = request.FILES.get('puzzle_file')
        puzzle_manual = request.POST.get('puzzle_manual', '').strip()

        import pandas as pd

        scores = {}  # name -> {omr, debug, dsa, puzzle}

        def _add_scores(df, round_name, score_col):
            for _, row in df.iterrows():
                n = str(row.get('Name', row.iloc[0])).strip()
                s = float(row.get(score_col, row.iloc[1]) if score_col in df.columns else row.iloc[1])
                if n not in scores:
                    scores[n] = {'omr': 0, 'debug': 0, 'dsa': 0, 'puzzle': 0}
                scores[n][round_name] = s

        if omr_file:
            tmp = _save_upload(omr_file)
            try:
                df = pd.read_excel(tmp)
                _add_scores(df, 'omr', 'Score')
            finally:
                os.unlink(tmp)

        if debug_file:
            tmp = _save_upload(debug_file)
            try:
                df = pd.read_excel(tmp)
                _add_scores(df, 'debug', 'Debug Score')
            finally:
                os.unlink(tmp)

        if dsa_file:
            tmp = _save_upload(dsa_file)
            try:
                df = pd.read_excel(tmp)
                _add_scores(df, 'dsa', 'Total')
            finally:
                os.unlink(tmp)

        if puzzle_file:
            tmp = _save_upload(puzzle_file)
            try:
                df = pd.read_excel(tmp)
                _add_scores(df, 'puzzle', 'Puzzle Score')
            finally:
                os.unlink(tmp)

        # Parse manual puzzle scores: "Name1:10, Name2:15"
        if puzzle_manual:
            for entry in puzzle_manual.split(','):
                entry = entry.strip()
                if ':' in entry:
                    n, s = entry.rsplit(':', 1)
                    n = n.strip()
                    try:
                        s = float(s.strip())
                    except ValueError:
                        continue
                    if n not in scores:
                        scores[n] = {'omr': 0, 'debug': 0, 'dsa': 0, 'puzzle': 0}
                    scores[n]['puzzle'] = s

        if not scores:
            messages.error(request, 'No data found. Please upload at least one result file.')
            return render(request, 'merger.html')

        # Build final results
        final = []
        for name, s in scores.items():
            total = s['omr'] + s['debug'] + s['dsa'] + s['puzzle']
            final.append({
                'name': name,
                'omr': s['omr'],
                'debug': s['debug'],
                'dsa': s['dsa'],
                'puzzle': s['puzzle'],
                'total': total,
            })

        # Sort by total descending and assign ranks
        final.sort(key=lambda x: x['total'], reverse=True)
        for i, entry in enumerate(final, 1):
            entry['rank'] = i

        excel_bytes = generate_final_excel(final)
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="final_leaderboard.xlsx"'
        return response

    return render(request, 'merger.html')


# ─── PAGE 5: SPIN THE WHEEL ──────────────────────────────────────────

def wheel_view(request):
    return render(request, 'wheel.html')
