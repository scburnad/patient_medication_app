# patient_medication_app

FastAPI app for creating patient medication requests

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/) (for local development)

## Running the App

1. **Install dependencies** (using Poetry):
    **Note:**  
    This should be run in the root directory where pyproject.toml is located
    
    ```sh
    poetry install
    ```

2. **Set up environment variables**  
   Make sure your `.env` file is present in `src/` with the correct `DATABASE_URL`.

**Note:**  
All commands below should be run from the `src` directory unless otherwise specified.

3. **Apply database migrations**:

    ```sh
    poetry run alembic upgrade head
    ```

4. **Start the app**:

    ```sh
    poetry run uvicorn patient_medication_app.app:app --reload
    ```

5. **Access the API docs**:  
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

**Run tests:**

```sh
poetry run pytest
```