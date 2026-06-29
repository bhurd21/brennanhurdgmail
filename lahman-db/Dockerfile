FROM lahman-db
# Add the lookup views init script. Runs after 01_schema.sql and 02_load.sql
# on first boot of an empty data directory.
COPY init/03_views.sql /docker-entrypoint-initdb.d/03_views.sql
