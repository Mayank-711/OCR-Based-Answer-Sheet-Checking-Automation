"""Excel file generation for all rounds."""

import io
import pandas as pd


def generate_omr_excel(results: list) -> bytes:
    """
    Generate Excel for OMR results.
    results = [{'name': ..., 'score': ...}, ...]
    """
    df = pd.DataFrame(results)
    df.columns = ['Name', 'Score']
    return _df_to_bytes(df)


def generate_debug_excel(results: list) -> bytes:
    """
    Generate Excel for Debug results.
    results = [{'name': ..., 'score': ...}, ...]
    """
    df = pd.DataFrame(results)
    df.columns = ['Name', 'Debug Score']
    return _df_to_bytes(df)


def generate_dsa_excel(results: list) -> bytes:
    """
    Generate Excel for DSA results.
    results = [{'name': ..., 'q1': ..., 'q2': ..., 'q3': ..., 'total': ...}, ...]
    """
    df = pd.DataFrame(results)
    df.columns = ['Name', 'Q1', 'Q2', 'Q3', 'Total']
    return _df_to_bytes(df)


def generate_final_excel(results: list) -> bytes:
    """
    Generate final leaderboard Excel.
    results = [{'name': ..., 'omr': ..., 'debug': ..., 'dsa': ...,
                'puzzle': ..., 'total': ..., 'rank': ...}, ...]
    """
    df = pd.DataFrame(results)
    df = df[['rank', 'name', 'omr', 'debug', 'dsa', 'puzzle', 'total']]
    df.columns = ['Rank', 'Name', 'OMR', 'Debug', 'DSA', 'Puzzle', 'Total']
    return _df_to_bytes(df)


def _df_to_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to Excel bytes."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    return buf.getvalue()
