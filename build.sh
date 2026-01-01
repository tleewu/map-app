#!/bin/bash
# Build script for deployment platforms
pip install -r requirements.txt
playwright install chromium
playwright install-deps

