FROM python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system archeotech \
    && adduser --system --ingroup archeotech --home /app archeotech \
    && mkdir -p /var/lib/aire-archeotech/storage \
    && chown -R archeotech:archeotech /var/lib/aire-archeotech

COPY requirements-build-ci.lock requirements-ci.lock pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir pip==25.0.1 \
    && python -m pip install --no-cache-dir --no-deps -r requirements-build-ci.lock \
    && python -m pip install --no-cache-dir --no-build-isolation --no-deps -r requirements-ci.lock \
    && python -m pip check

USER archeotech

EXPOSE 8088

CMD ["uvicorn", "aire_archeotech.runtime.app:app", "--host", "0.0.0.0", "--port", "8088"]
