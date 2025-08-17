
push commit_message:
    @git add .
    @git commit -m "{{commit_message}}"
    @git push

fmt:
    @echo "Formatting code..."
    @ruff format .
    @echo "Linting and fixing issues..."
    @ruff check --fix .
    @echo "Done!"

lint:
    @echo "Checking for linting issues..."
    @ruff check .

fix:
    @echo "Fixing linting issues..."
    @ruff check --fix .

format-check:
    @echo "Checking code formatting..."
    @ruff format --check .