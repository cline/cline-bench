My web app should regularly be syncing all police neighbourhoods, but is always crashing at one and then stops.  The error message is below.  Please help me diagnose and fix it, then test it locally to ensure everything works?

HTTP Request: GET https://data.police.uk/api/greater-manchester/MC28/boundary "HTTP/1.1 200 OK"
Fatal Python error: Segmentation fault
Thread 0x00007fcbf1d7f6c0 (most recent call first):
  File "/root/.nix-profile/lib/python3.11/concurrent/futures/thread.py", line 81 in _worker
  File "/root/.nix-profile/lib/python3.11/threading.py", line 982 in run
  File "/root/.nix-profile/lib/python3.11/threading.py", line 1045 in _bootstrap_inner
  File "/root/.nix-profile/lib/python3.11/threading.py", line 1002 in _bootstrap

<environment_details>
# Visual Studio Code Visible Files
main.py

# Visual Studio Code Open Tabs
services/calendar.py
services/location.py
tests/__init__.py
tests/test_calendar_service.py
pytest.ini
railway.json
middleware/__init__.py
middleware/rate_limit.py
middleware/monitoring.py
utils/__init__.py
utils/error_messages.py
.env
pyproject.toml
tests/conftest.py
tests/test_location_service.py
api/ordnance_survey.py
tests/test_duckdb_client.py
api/police_uk.py
database/sync_state.py
tests/test_sync_state.py
tests/test_status_endpoint.py
static/index.html
database/duckdb_client.py
README.md
database/sync.py
database/sync_strategy.py
tests/test_smart_sync.py
main.py
railway.toml
.gitignore
api/__init__.py
database/__init__.py
services/__init__.py
</environment_details>
