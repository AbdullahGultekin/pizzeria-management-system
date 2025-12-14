"""
Script om PizzeriaBestelformulier.exe automatisch te uploaden naar GitHub release.

Gebruik:
1. Maak een GitHub Personal Access Token:
   - Ga naar: https://github.com/settings/tokens
   - Klik "Generate new token (classic)"
   - Geef "repo" scope
   - Kopieer de token

2. Run dit script:
   python upload_exe_to_release.py
   
   OF set environment variable:
   $env:GITHUB_TOKEN="your_token_here"
   python upload_exe_to_release.py
"""
import os
import sys
import requests
from pathlib import Path

# Configuration
REPO_OWNER = "AbdullahGultekin"
REPO_NAME = "pizzeria-management-system"
RELEASE_TAG = "v1.1.1"
EXE_PATH = Path("dist/PizzeriaBestelformulier.exe")
ZIP_PATH = Path("dist/PizzeriaBestelformulier.zip")

def get_github_token():
    """Get GitHub token from environment or user input."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        print("✅ GitHub token gevonden in environment variable.")
        return token
    
    print("GitHub Personal Access Token nodig om bestand te uploaden.")
    print("Maak een token op: https://github.com/settings/tokens")
    print("Geef 'repo' scope.")
    print()
    print("OF set environment variable:")
    print("  PowerShell: $env:GITHUB_TOKEN='jouw_token'")
    print("  CMD: set GITHUB_TOKEN=jouw_token")
    print()
    
    try:
        token = input("Voer je GitHub token in (of druk Enter om te annuleren): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGeannuleerd. Gebruik environment variable GITHUB_TOKEN.")
        sys.exit(0)
    
    if not token:
        print("Geannuleerd. Gebruik environment variable GITHUB_TOKEN.")
        sys.exit(0)
    
    return token

def get_release_id(token, tag):
    """Get release ID for given tag."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{tag}"
    headers = {"Authorization": f"token {token}"}
    
    print(f"Ophalen release info voor {tag}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 404:
        print(f"ERROR: Release {tag} niet gevonden!")
        return None
    elif response.status_code != 200:
        print(f"ERROR: Kon release niet ophalen: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return None
    
    release = response.json()
    release_id = release.get("id")
    release_name = release.get("name", tag)
    
    print(f"Release gevonden: {release_name} (ID: {release_id})")
    return release_id

def upload_asset(token, release_id, file_path):
    """Upload file to GitHub release."""
    if not file_path.exists():
        print(f"ERROR: Bestand niet gevonden: {file_path}")
        return False
    
    file_size = file_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\nUploaden: {file_path.name}")
    print(f"Grootte: {file_size_mb:.2f} MB")
    
    # GitHub API endpoint for uploading release assets
    upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/octet-stream"
    }
    
    params = {
        "name": file_path.name
    }
    
    print("Uploaden naar GitHub...")
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                upload_url,
                headers=headers,
                params=params,
                data=f,
                timeout=300  # 5 minuten timeout voor grote bestanden
            )
        
        if response.status_code == 201:
            asset = response.json()
            print(f"\n✅ SUCCESS! Bestand geüpload.")
            print(f"   Naam: {asset.get('name')}")
            print(f"   Grootte: {asset.get('size', 0) / (1024*1024):.2f} MB")
            print(f"   Download URL: {asset.get('browser_download_url')}")
            return True
        else:
            print(f"\n❌ ERROR: Upload gefaald!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Upload timeout (bestand te groot of trage verbinding)")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("GitHub Release Asset Uploader")
    print("=" * 60)
    print()
    
    # Check if EXE exists
    if not EXE_PATH.exists():
        print(f"ERROR: {EXE_PATH} niet gevonden!")
        print("Bouw eerst de EXE met: pyinstaller pizzeria.spec --clean --noconfirm")
        sys.exit(1)
    
    # Get token
    token = get_github_token()
    if not token:
        sys.exit(1)
    
    # Get release ID
    release_id = get_release_id(token, RELEASE_TAG)
    if not release_id:
        sys.exit(1)
    
    # Check if asset already exists
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        release = response.json()
        assets = release.get("assets", [])
        existing = [a for a in assets if a.get("name") == EXE_PATH.name]
        if existing:
            print(f"\n⚠️  WAARSCHUWING: {EXE_PATH.name} bestaat al in deze release!")
            overwrite = input("Overschrijven? (j/n): ").strip().lower()
            if overwrite != 'j':
                print("Geannuleerd.")
                sys.exit(0)
            # Delete existing asset
            asset_id = existing[0].get("id")
            delete_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{asset_id}"
            del_response = requests.delete(delete_url, headers=headers)
            if del_response.status_code == 204:
                print("Bestaande asset verwijderd.")
            else:
                print(f"Kon bestaande asset niet verwijderen: {del_response.status_code}")
    
    # Upload
    success = upload_asset(token, release_id, EXE_PATH)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Upload voltooid!")
        print("=" * 60)
        print(f"\nJe kunt de release nu bekijken op:")
        print(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{RELEASE_TAG}")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Upload gefaald!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
