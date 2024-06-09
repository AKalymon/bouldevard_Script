install:
	pip install -r requirements.txt

start:
	python main.py

dependencies:
	pip freeze > requirements.txt