from pathlib import Path

from app.celery_app import celery_app
from app.parsers.pdf import parse_pdf
from app.parsers.excel import parse_tabular


@celery_app.task(name="files.parse_pdf_task")
def parse_pdf_task(file_path: str, char_limit: int = 2000) -> str:
    """
    Celery task that parses a PDF on disk and returns a text preview.

    :param file_path: Absolute or project-relative path to the PDF file.
    :param char_limit: Maximum characters to return from the parsed text.
    """
    path = Path(file_path)
    return parse_pdf(path, char_limit=char_limit)


@celery_app.task(name="files.parse_excel_task")
def parse_excel_task(file_path: str, char_limit: int = 2000) -> str:
    """
    Celery task that parses a CSV/Excel file and returns a text preview.

    :param file_path: Absolute or project-relative path to the file.
    :param char_limit: Maximum characters to return from the parsed text.
    """
    path = Path(file_path)
    return parse_tabular(path, char_limit=char_limit)

