#!/usr/bin/env bash
python -m pip install . --no-deps --ignore-installed --no-cache-dir -vvv

# Add an menu entry for CoSApp
mkdir -p "$PREFIX/Menu"
cp "$RECIPE_DIR/cosapp_lab.json" "$PREFIX/Menu"
cp "$RECIPE_DIR/CoSApp_lab.ico" "$PREFIX/Menu"
