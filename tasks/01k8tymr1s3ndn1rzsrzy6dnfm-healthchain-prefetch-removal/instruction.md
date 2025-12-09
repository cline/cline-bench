I'm implementing MIMIC and Synthea loaders for the sandbox. The Prefetch model is getting in the way - it's causing a lot of unnecessary conversions between pydantic models and dictionaries. I don't think the validation adds much value, especially since MIMIC needs specific FHIR versions. I want to clean this up so loaders can work directly with CdsRequest(**data).

<environment_details>
# Cursor Visible Files
healthchain/sandbox/loaders/mimic.py

# Cursor Open Tabs
docs/cookbook/discharge_summarizer.md
docs/reference/utilities/sandbox.md
healthchain/sandbox/loaders/mimic.py
tests/sandbox/test_mimic_loader.py
docs/api/sandbox.md
healthchain/sandbox/sandboxclient.py
docs/reference/pipeline/adapters/cdaadapter.md
docs/reference/pipeline/adapters/cdsfhiradapter.md
</environment_details>
