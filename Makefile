up:
	docker compose up -d

rebuild-airflow:
	docker compose build airflow airflow-init && docker compose up -d airflow

rebuild-all:
	docker compose down -v && docker compose build --no-cache && docker compose up -d
