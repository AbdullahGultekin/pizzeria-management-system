"""Verwijder oude asset en upload nieuwe"""
import requests
import os
from pathlib import Path

REPO_OWNER = "AbdullahGultekin"
REPO_NAME = "pizzeria-management-system"
RELEASE_TAG = "v1.1.1"
FILE_PATH = Path("dist/PizzeriaBestelformulier.zip")

# Get token from environment variable
import os
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable niet gevonden!")
    print("Stel de token in met: $env:GITHUB_TOKEN='jouw_token'")
    exit(1)

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

print("Ophalen release info...")
release_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{RELEASE_TAG}"
response = requests.get(release_url, headers=headers)
release = response.json()
release_id = release["id"]
print(f"Release ID: {release_id}")

# Verwijder alle bestaande assets
assets = release.get("assets", [])
print(f"\nGevonden assets: {len(assets)}")
for asset in assets:
    print(f"  Verwijderen: {asset['name']} (ID: {asset['id']})")
    delete_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{asset['id']}"
    del_response = requests.delete(delete_url, headers=headers)
    if del_response.status_code == 204:
        print(f"    OK: Verwijderd")
    else:
        print(f"    ERROR: Status {del_response.status_code}")

print("\nWacht 2 seconden...")
import time
time.sleep(2)

# Upload nieuwe asset
print(f"\nUploaden {FILE_PATH.name}...")
upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"

upload_headers = {
    "Authorization": f"token {TOKEN}",
    "Content-Type": "application/zip",
    "Accept": "application/vnd.github.v3+json"
}

with open(FILE_PATH, 'rb') as f:
    file_data = f.read()

params = {"name": FILE_PATH.name}
upload_response = requests.post(
    upload_url,
    headers=upload_headers,
    params=params,
    data=file_data,
    timeout=(60, 1200)
)

if upload_response.status_code == 201:
    asset_info = upload_response.json()
    print(f"\nOK: Upload succesvol!")
    print(f"   Bestand: {asset_info['name']}")
    print(f"   Grootte: {asset_info['size'] / (1024*1024):.2f} MB")
    print(f"   Download URL: {asset_info['browser_download_url']}")
else:
    print(f"\nERROR: Status {upload_response.status_code}")
    print(f"Response: {upload_response.text}")
