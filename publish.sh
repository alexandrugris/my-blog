#!/bin/bash
set -e

# Path to the cloned alexandrugris.github.io repo.
# Clone it once with: git clone git@github.com:alexandrugris/alexandrugris.github.io.git $PAGES_DIR
PAGES_DIR="${PAGES_DIR:-$(dirname "$0")/../alexandrugris.github.io}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building site..."
python3 build.py

echo "Copying to $PAGES_DIR ..."
rsync -a --delete html/ "$PAGES_DIR/"

cd "$PAGES_DIR"

git add -A

DATE=$(date)
echo "Publishing: $DATE"
git commit -m "Published $DATE" || { echo "Nothing to commit."; exit 0; }

git pull --rebase
git push origin
