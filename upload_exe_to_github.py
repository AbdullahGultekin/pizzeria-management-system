"""
Upload EXE/ZIP naar GitHub Release via API (geen 25 MB limiet).
"""
import requests
import os
from pathlib import Path
import sys

# Configuratie
REPO_OWNER = "AbdullahGultekin"
REPO_NAME = "pizzeria-management-system"
RELEASE_TAG = "v1.1.1"
FILE_PATH = Path("dist/PizzeriaBestelformulier.zip")

def upload_asset_to_release():
    """Upload asset naar GitHub release via API."""
    
    # Check if file exists
    if not FILE_PATH.exists():
        print(f"ERROR: {FILE_PATH} niet gevonden!")
        print("Bouw eerst de EXE en maak een ZIP met: python create_release_zip.py")
        return False
    
    file_size = FILE_PATH.stat().st_size / (1024 * 1024)
    print(f"Bestand: {FILE_PATH.name}")
    print(f"Grootte: {file_size:.2f} MB")
    
    # Get GitHub token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("\nERROR: GITHUB_TOKEN environment variable niet gevonden!")
        print("\nHoe te krijgen:")
        print("1. Ga naar: https://github.com/settings/tokens")
        print("2. Klik 'Generate new token (classic)'")
        print("3. Geef naam: 'Upload Release Assets'")
        print("4. Selecteer scope: 'repo' (volledige controle)")
        print("5. Klik 'Generate token'")
        print("6. Kopieer de token")
        print("\nDan in PowerShell:")
        print(f'  $env:GITHUB_TOKEN="jouw_token_hier"')
        print(f'  python upload_exe_to_github.py')
        print("\nOF permanent:")
        print(f'  [System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "jouw_token", "User")')
        return False
    
    # Get release info
    print(f"\nOphalen release info voor {RELEASE_TAG}...")
    release_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{RELEASE_TAG}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(release_url, headers=headers)
    if response.status_code != 200:
        print(f"ERROR: Kon release niet vinden (status {response.status_code})")
        print(f"Response: {response.text}")
        return False
    
    release = response.json()
    release_id = release["id"]
    print(f"Release gevonden: {release.get('name', RELEASE_TAG)}")
    
    # Check if asset already exists and delete it automatically
    existing_assets = release.get("assets", [])
    for asset in existing_assets:
        if asset["name"] == FILE_PATH.name:
            print(f"\nBestaande asset gevonden: {FILE_PATH.name}")
            print("Verwijderen oude asset...")
            asset_id = asset["id"]
            delete_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{asset_id}"
            del_response = requests.delete(delete_url, headers=headers)
            if del_response.status_code == 204:
                print("Oude asset verwijderd.")
            else:
                print(f"Waarschuwing: Kon oude asset niet verwijderen (status {del_response.status_code})")
                print("Proberen door te gaan...")
    
    # Upload asset using chunked upload for large files
    print(f"\nUploaden {FILE_PATH.name}...")
    print("Dit kan enkele minuten duren voor grote bestanden (102 MB)...")
    upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"
    
    upload_headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/zip",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Read file in chunks and upload
    chunk_size = 10 * 1024 * 1024  # 10 MB chunks
    file_size = FILE_PATH.stat().st_size
    
    # Create a session for better connection handling
    session = requests.Session()
    session.headers.update(upload_headers)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Upload poging {attempt + 1}/{max_retries}...")
            
            # Read entire file into memory (for large files, this is necessary)
            # GitHub API requires the full file in one request
            with open(FILE_PATH, 'rb') as f:
                file_data = f.read()
            
            params = {"name": FILE_PATH.name}
            
            # Upload with very long timeout for large files
            upload_response = session.post(
                upload_url,
                params=params,
                data=file_data,
                timeout=(60, 1200),  # 60s connect, 20min read timeout for 100MB+
                stream=False
            )
            
            if upload_response.status_code == 201:
                break  # Success, exit retry loop
            elif upload_response.status_code == 422:
                error_msg = upload_response.text
                if "already exists" in error_msg.lower():
                    print("Asset bestaat al! Verwijderen en opnieuw proberen...")
                    # Find and delete existing asset
                    for asset in existing_assets:
                        if asset["name"] == FILE_PATH.name:
                            asset_id = asset["id"]
                            delete_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{asset_id}"
                            del_response = requests.delete(delete_url, headers=upload_headers)
                            if del_response.status_code == 204:
                                print("Oude asset verwijderd, opnieuw proberen...")
                                continue
                raise Exception(f"Upload gefaald: {error_msg}")
            else:
                raise Exception(f"Status {upload_response.status_code}: {upload_response.text}")
                
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"Network error (poging {attempt + 1}/{max_retries}), wacht {wait_time}s en probeer opnieuw...")
                import time
                time.sleep(wait_time)
                continue
            else:
                print(f"\nERROR na {max_retries} pogingen: {e}")
                print("\nMogelijke oplossingen:")
                print("1. Check je internet verbinding")
                print("2. Probeer later opnieuw (GitHub kan tijdelijk overbelast zijn)")
                print("3. Gebruik GitHub CLI: gh release upload v1.1.1 dist\\PizzeriaBestelformulier.zip")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error (poging {attempt + 1}/{max_retries}): {e}")
                import time
                time.sleep(5)
                continue
            else:
                raise
    
    if upload_response.status_code == 201:
        asset_info = upload_response.json()
        print(f"\nOK: Upload succesvol!")
        print(f"   Bestand: {asset_info['name']}")
        print(f"   Grootte: {asset_info['size'] / (1024*1024):.2f} MB")
        print(f"   Download URL: {asset_info['browser_download_url']}")
        print(f"\nRelease URL: {release['html_url']}")
        return True
    else:
        print(f"\nERROR: Upload gefaald (status {upload_response.status_code})")
        print(f"Response: {upload_response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub Release Asset Uploader")
    print("=" * 60)
    print()
    
    if upload_asset_to_release():
        print("\n" + "=" * 60)
        print("KLAAR!")
        print("=" * 60)
        print("\nDe asset is geüpload naar GitHub!")
        print("Wacht 2-5 minuten voordat de API cache bijwerkt.")
    else:
        print("\n" + "=" * 60)
        print("GEFAALD!")
        print("=" * 60)
