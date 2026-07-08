from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_sql(filename: str) -> str:
    sql_path = BASE_DIR / "sql" / filename

    return sql_path.read_text(encoding="utf-8")