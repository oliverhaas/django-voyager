.PHONY: serve

## serve: Run granian ASGI server with deployed settings (local production-like testing).
serve:
	LOCAL_DEPLOY=1 bash scripts/serve.sh
