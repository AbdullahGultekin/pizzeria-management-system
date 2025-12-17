#!/bin/bash
# Script om GitHub Release te maken via GitHub API

REPO="AbdullahGultekin/pizzeria-management-system"
VERSION="1.1.1"
TAG="v${VERSION}"
TITLE="Release v${VERSION} - Koeriers en Klantendatabase Verbeteringen"

# Lees release notes
NOTES=$(cat RELEASE_NOTES_v1.1.1.md)

# Maak release via GitHub API
echo "Creating GitHub Release..."
echo "Repository: $REPO"
echo "Tag: $TAG"
echo ""

# Check of GITHUB_TOKEN is gezet
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN niet gevonden!"
    echo ""
    echo "Om een release te maken, heb je een GitHub Personal Access Token nodig."
    echo ""
    echo "Stappen:"
    echo "1. Ga naar: https://github.com/settings/tokens"
    echo "2. Maak een nieuwe token met 'repo' permissions"
    echo "3. Export de token:"
    echo "   export GITHUB_TOKEN=your_token_here"
    echo "4. Run dit script opnieuw"
    echo ""
    echo "Of maak de release handmatig via:"
    echo "https://github.com/$REPO/releases/new"
    echo ""
    echo "Tag: $TAG"
    echo "Title: $TITLE"
    echo "Description: (zie RELEASE_NOTES_v1.1.1.md)"
    exit 1
fi

# Maak release
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO/releases" \
  -d "{
    \"tag_name\": \"$TAG\",
    \"name\": \"$TITLE\",
    \"body\": $(echo "$NOTES" | jq -Rs .),
    \"draft\": false,
    \"prerelease\": false
  }"

echo ""
echo "✅ Release aangemaakt: https://github.com/$REPO/releases/tag/$TAG"
