#!/bin/sh
uvicorn app.server:app --log-level=info  --host="0.0.0.0"