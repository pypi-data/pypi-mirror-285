tourist-build:
	python3 -m build

tourist-server:
	docker compose down
	docker compose up --build tourist

sam-interactive:
	docker compose down
	docker compose up --build -d sam-deploy
	docker exec -it sam-deploy bash
	docker compose down
