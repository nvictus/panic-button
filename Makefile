
nuke-db:
	rm "test.db"

create-db:
	python -c "import app.models; app.models.init_db()"

serve:
	python serve.py
