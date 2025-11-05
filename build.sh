#!/usr/bin/env bash
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright Chromium..."
playwright install --with-deps chromium

# Manage Playwright cache with build cache
if [[ ! -d $PLAYWRIGHT_BROWSERS_PATH ]]; then
  echo "...Copying Playwright from cache"
  mkdir -p $PLAYWRIGHT_BROWSERS_PATH
  if [[ -d $XDG_CACHE_HOME/playwright/ ]]; then
    cp -R $XDG_CACHE_HOME/playwright/* $PLAYWRIGHT_BROWSERS_PATH/
  fi
else
  echo "...Saving Playwright to build cache"
  mkdir -p $XDG_CACHE_HOME
  cp -R $PLAYWRIGHT_BROWSERS_PATH $XDG_CACHE_HOME/
fi

echo "Build complete!"
