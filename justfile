list:
    just --list

run arg1="":
    uv run src/ai_api/main.py {{arg1}}

test arg1="":
    uv run -m pytest {{arg1}}
