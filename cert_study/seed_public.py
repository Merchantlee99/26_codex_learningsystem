from __future__ import annotations

import sqlite3

from .seed_adsp import seed as seed_adsp
from .seed_info_processing import seed as seed_info_processing
from .seed_sqld import seed as seed_sqld


def seed_public_banks(conn: sqlite3.Connection) -> None:
    """Seed public-safe synthetic banks that can live in the portfolio repo."""
    seed_sqld(conn)
    seed_adsp(conn)
    seed_info_processing(conn)

