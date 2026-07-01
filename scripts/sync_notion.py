#!/usr/bin/env python3
"""완료된 세션의 Notion 동기화 계획을 만든다.

이 스크립트는 실제 Notion 쓰기를 하지 않는다. Notion MCP 도구는 로컬 Python
프로세스가 아니라 Codex agent 쪽에서 사용할 수 있기 때문이다.
"""

from __future__ import annotations

import argparse

from cert_study.db import connect
from cert_study.notion_sync import prepare_notion_sync_plan, render_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("session_id")
    args = parser.parse_args()
    with connect() as conn:
        plan = prepare_notion_sync_plan(conn, args.session_id)
    print(render_plan(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
