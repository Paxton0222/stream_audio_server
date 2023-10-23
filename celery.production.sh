#!/bin/sh

celery -A app worker --loglevel=INFO --hostname=audio@%h