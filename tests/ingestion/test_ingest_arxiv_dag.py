import os
from airflow.models import DagBag

# Optional: point DagBag at your repo's dags folder in CI
# os.environ.setdefault("AIRFLOW__CORE__DAGS_FOLDER", "dags")

DAG_ID = "ingest_arxiv_pdf"  # <- set this to your actual DAG id

def test_ingest_arxiv_dag_loaded():
    dag_bag = DagBag()
    assert DAG_ID in dag_bag.dags, f"{DAG_ID} not found. Check dag_id/dags folder."
    dag = dag_bag.dags[DAG_ID]
    # Keep these aligned with your default_args in the DAG file
    assert dag.default_args.get("retries", None) == 2
    assert len(dag.tasks) > 0

def test_ingest_dag_tasks_present():
    dag_bag = DagBag()
    dag = dag_bag.get_dag(DAG_ID)
    task_ids = {t.task_id for t in dag.tasks}
    # Align with your actual task_ids
    assert "read_metadata" in task_ids
    assert "ingest" in task_ids
