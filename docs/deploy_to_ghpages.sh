#!/usr/bin/env bash
# Deploy Bororo UD pre-release site to GitHub Pages
# Usage:
#   ./deploy_to_ghpages.sh <github-username> <repo-name> [branch] [cname]
#
# Example:
#   ./deploy_to_ghpages.sh fabriciofg bororo-ud gh-pages bororo.ud.example.org
#
# Requirements:
# - git installed
# - GITHUB_TOKEN in env (with repo permissions) OR SSH configured for GitHub
# - This script should be executed in the folder containing the site files:
#     index.html, README.md, citation.bib, bororo_corpus_pre-release_v5.zip, etc.

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <github-username> <repo-name> [branch] [cname]"
  exit 1
fi

USER="$1"
REPO="$2"
BRANCH="${3:-gh-pages}"
CNAME_DOMAIN="${4:-}"

WORKDIR="$(pwd)"
BUILD_DIR="$WORKDIR"
TMP_DIR="$(mktemp -d)"
CLONE_DIR="$TMP_DIR/repo"

# Detect auth method
USE_SSH=false
if git config --get user.name >/dev/null 2>&1; then
  : # ok
fi

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  REPO_URL="https://${GITHUB_TOKEN}@github.com/${USER}/${REPO}.git"
else
  # Fallback to SSH (requires ssh key configured for GitHub)
  REPO_URL="git@github.com:${USER}/${REPO}.git"
  USE_SSH=true
fi

echo ">> Cloning ${REPO_URL} (branch: ${BRANCH}) into ${CLONE_DIR}"
git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${CLONE_DIR}" 2>/dev/null || {
  echo ">> Branch '${BRANCH}' not found, creating orphan branch."
  git clone --depth 1 "${REPO_URL}" "${CLONE_DIR}"
  cd "${CLONE_DIR}"
  git checkout --orphan "${BRANCH}"
  rm -rf ./*
  git commit --allow-empty -m "chore: initialize ${BRANCH} branch"
  git push origin "${BRANCH}"
  cd "${WORKDIR}"
}

cd "${CLONE_DIR}"

echo ">> Cleaning old files"
find . -mindepth 1 -maxdepth 1 ! -name ".git" -exec rm -rf {} +

echo ">> Copying site files from ${BUILD_DIR}"
# Include the main site artifacts
cp -v "${BUILD_DIR}/index.html" . || true
cp -v "${BUILD_DIR}/README.md" . || true
cp -v "${BUILD_DIR}/citation.bib" . || true
cp -v "${BUILD_DIR}/LICENSE.txt" . || true
cp -v "${BUILD_DIR}/bororo_corpus_pre-release_v5.zip" . || true

# Optionally include other public assets (edit as needed)
# cp -v "${BUILD_DIR}/Bororo_UD_enriched_v5.conllu" . || true

# Create CNAME if domain provided
if [[ -n "${CNAME_DOMAIN}" ]]; then
  echo ">> Writing CNAME (${CNAME_DOMAIN})"
  echo "${CNAME_DOMAIN}" > CNAME
fi

echo ">> Committing and pushing"
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "deploy: Bororo UD pre-release v5 site"
  git push origin "${BRANCH}"
fi

echo ">> Done!"
echo "GitHub Pages URL:"
if [[ -n "${CNAME_DOMAIN}" ]]; then
  echo "  https://${CNAME_DOMAIN}"
else
  if [[ "${BRANCH}" == "gh-pages" ]]; then
    echo "  https://${USER}.github.io/${REPO}/"
  else
    echo "  https://${USER}.github.io/${REPO}/${BRANCH}/"
  fi
fi
