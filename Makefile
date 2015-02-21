
nuke-db:
	rm "test.db" && python -c "import app.models; app.models.init_db()"

serve:
	python serve.py
