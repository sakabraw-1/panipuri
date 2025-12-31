.PHONY: up down setup test

up:
	docker-compose up -d

down:
	docker-compose down

setup:
	pip install -r requirements.txt
	# julia --project=. -e 'using Pkg; Pkg.instantiate()'

test:
	# pytest tests/
	# julia --project=. -e 'using Pkg; Pkg.test()'
