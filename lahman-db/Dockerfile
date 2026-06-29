FROM postgres:17

ENV POSTGRES_DB=lahman

COPY lahman_1871-2025_csv/ /csv/
COPY init/ /docker-entrypoint-initdb.d/
