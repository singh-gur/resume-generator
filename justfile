
push commit_message:
    @git add .
    @git commit -m "{{commit_message}}"
    @git push

fmt:
    @ruff format
    @ruff check --fix