#!/usr/bin/env python3
"""
Script om GitHub Release aan te maken voor v1.1.1
"""
import os
import sys
import json
import requests
from pathlib import Path

REPO = "AbdullahGultekin/pizzeria-management-system"
VERSION = "1.1.1"
TAG = f"v{VERSION}"
TITLE = f"Release {TAG} - Koeriers en Klantendatabase Verbeteringen"

def get_release_notes():
    """Lees release notes uit bestand."""
    notes_file = Path(__file__).parent / "RELEASE_NOTES_v1.1.1.md"
    if notes_file.exists():
        return notes_file.read_text(encoding='utf-8')
    return f"Release {TAG} - Zie commit history voor details."

def create_release():
    """Maak GitHub Release aan."""
    # Check voor GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠️  GITHUB_TOKEN niet gevonden!")
        print()
        print("Om een release te maken, heb je een GitHub Personal Access Token nodig.")
        print()
        print("Stappen:")
        print("1. Ga naar: https://github.com/settings/tokens")
        print("2. Klik op 'Generate new token (classic)'")
        print("3. Geef het token de naam: 'Release Creator'")
        print("4. Selecteer scope: 'repo' (volledige controle)")
        print("5. Klik op 'Generate token'")
        print("6. Kopieer het token")
        print()
        print("Dan run:")
        print(f"  export GITHUB_TOKEN=your_token_here")
        print(f"  python3 {sys.argv[0]}")
        print()
        print("Of maak de release handmatig via:")
        print(f"  https://github.com/{REPO}/releases/new")
        print()
        print(f"Tag: {TAG}")
        print(f"Title: {TITLE}")
        print(f"Description: (zie RELEASE_NOTES_v1.1.1.md)")
        return False
    
    # Lees release notes
    release_notes = get_release_notes()
    
    # Maak release via GitHub API
    url = f"https://api.github.com/repos/{REPO}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "tag_name": TAG,
        "name": TITLE,
        "body": release_notes,
        "draft": False,
        "prerelease": False
    }
    
    print(f"📦 Creating GitHub Release...")
    print(f"   Repository: {REPO}")
    print(f"   Tag: {TAG}")
    print(f"   Title: {TITLE}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        release_url = result.get("html_url", f"https://github.com/{REPO}/releases/tag/{TAG}")
        
        print(f"✅ Release succesvol aangemaakt!")
        print(f"   URL: {release_url}")
        print()
        print("🎉 Exe gebruikers kunnen nu de nieuwe versie downloaden!")
        return True
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print("⚠️  Release bestaat mogelijk al!")
            print(f"   Check: https://github.com/{REPO}/releases")
            print()
            print("Als de release al bestaat, kun je deze bewerken via GitHub web interface.")
        else:
            print(f"❌ Fout bij aanmaken release: {e}")
            if e.response.text:
                try:
                    error_data = e.response.json()
                    print(f"   Details: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Response: {e.response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

if __name__ == "__main__":
    success = create_release()
    sys.exit(0 if success else 1)

