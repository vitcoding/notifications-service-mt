#!/usr/bin/env bash

POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="secret"
POSTGRES_DB="notifications_db"
TABLE="public.notifications"

DATA="\
('00000000-0000-0000-0000-000000000001', 'dcd11e56-75c6-4208-aa6e-bb73caea51dc', \
'noname', 'no1', '3fa85f64-5717-4562-b3fc-2c963f66afa6', 'string', 'string', 'email@email', \
null, '2025-02-15 11:39:57.731067', '2025-02-15 11:40:00.424674'), \
('00000000-0000-0000-0000-000000000002', 'dcd11e56-75c6-4208-aa6e-bb73caea51dc', \
'noname', 'no1', '3fa85f64-5717-4562-b3fc-2c963f66afa6', 'string', 'string', 'email@email', \
null, '2025-02-15 11:39:57.731067', '2025-02-15 11:40:00.424674')\
"

INSERT_QUERY="INSERT INTO ${TABLE} \
(id, user_id, user_name, user_email, template_id, subject, message, \
notification_type, last_sent_at, created_at, updated_at) VALUES ${DATA};"

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "Connecting to PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "${INSERT_QUERY}"

if [ $? -eq 0 ]; then
  echo "Data inserted successfully!"
else
  echo "Failed to insert data."
fi

