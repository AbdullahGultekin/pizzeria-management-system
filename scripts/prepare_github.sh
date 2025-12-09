#!/bin/bash
# Script om repository voorbereiden voor GitHub met nieuwe naam

NEW_REPO_NAME="pizzeria-management-system"
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null | grep -oP 'github\.com/[^/]+/\K[^/]+(?=\.git)')

echo "=========================================="
echo "GitHub Repository Voorbereiding"
echo "=========================================="
echo ""
echo "Huidige repository naam: $CURRENT_REMOTE"
echo "Nieuwe repository naam: $NEW_REPO_NAME"
echo ""

# Vraag bevestiging
read -p "Wil je doorgaan met deze naam? (j/n): " confirm
if [ "$confirm" != "j" ] && [ "$confirm" != "J" ]; then
    echo "Geannuleerd."
    exit 1
fi

echo ""
echo "Stappen om de repository op GitHub te hernoemen:"
echo "1. Ga naar: https://github.com/AbdullahGultekin/$CURRENT_REMOTE/settings"
echo "2. Scroll naar 'Repository name'"
echo "3. Wijzig de naam naar: $NEW_REPO_NAME"
echo "4. Klik op 'Rename'"
echo ""
read -p "Druk op Enter wanneer je de repository op GitHub hebt hernoemd..."

# Update remote URL
NEW_REMOTE_URL="https://github.com/AbdullahGultekin/$NEW_REPO_NAME.git"
echo ""
echo "Remote URL updaten naar: $NEW_REMOTE_URL"
git remote set-url origin "$NEW_REMOTE_URL"

# Verifieer
echo ""
echo "Nieuwe remote URL:"
git remote -v

echo ""
echo "✅ Klaar! Je kunt nu committen en pushen met:"
echo "   git add ."
echo "   git commit -m 'Update: Webex integratie en verbeteringen'"
echo "   git push origin main"



