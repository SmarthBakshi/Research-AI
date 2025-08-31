#!/bin/bash

DAG_ID="process_pdfs"

echo "🔻 Stopping all services..."
docker compose down

echo "🔄 Launching temporary Airflow CLI container..."
docker compose run --rm airflow bash -c "
  echo '🧼 Clearing all task instances for $DAG_ID...'
  airflow tasks clear $DAG_ID --start-date 2000-01-01 --end-date 2100-01-01 --yes

  echo '🗑 Deleting all DAG runs...'
  airflow dags delete $DAG_ID --yes

  echo '🧽 Clearing DAG serialization cache...'
  airflow db shell <<EOF
DELETE FROM serialized_dag WHERE dag_id = '$DAG_ID';
.exit
EOF
"

echo "🚀 Restarting Airflow services..."
docker compose up -d

sleep 5

echo "🏁 All done! You now have a clean slate, restart the scheduler and trigger the DAG. Happy DAGging!"
