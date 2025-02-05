FROM python:3.13.1

WORKDIR /app

COPY . .

RUN pip install poetry

RUN poetry install --no-root

EXPOSE 8000

CMD ["python", "gemini_api.py"]
