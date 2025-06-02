generate a virtual py env ---- python -m venv venv_name ---- for both aer_service and ver_service.

activate venv ---- .\venv\Scripts\activate

install requirments files seperately in venvs ---- pip install -r ver_requirements.txt

run services seperately using following commands in local env
aer_service.py ----  uvicorn aer_service:app --host 0.0.0.0 --port 8000 --reload
ver_service.py ---- uvicorn ver_service:app --host 0.0.0.0 --port 8001 --reload

now the services are running