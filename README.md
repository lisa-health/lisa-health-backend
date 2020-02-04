# lisa-health-backend

The backend of lisa-health

## Configuration Steps
1. Build frontend.
2. Copy built assets to one folder.
3. Change the folder name in `medicine/settings.py`, `STATIC_ROOT` variable.

## Install Steps
1. Ensure Python3 is installed.
2. Install dependencies in `requirements.txt` via `pip install -r requirements.txt`. Virtual environments are recommended.
3. Ensure `MongoDB` is installed and running.
4. If default address or port is changed, please change settings in `DiseasePedia/MongoDBSaver.py`.
5. Run `initialize_db.py` to initialize database. This action only needs to be done once.
6. Run `run.py` to start server.
