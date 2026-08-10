FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system archeotech \
    && adduser --system --ingroup archeotech --home /app archeotech \
    && mkdir -p /var/lib/aire-archeotech/storage \
    && chown -R archeotech:archeotech /var/lib/aire-archeotech

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

USER archeotech

EXPOSE 8088

CMD ["uvicorn", "aire_archeotech.runtime.app:app", "--host", "0.0.0.0", "--port", "8088"]
