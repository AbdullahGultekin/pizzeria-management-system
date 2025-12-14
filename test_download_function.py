"""Test de download functie direct"""
import sys
from pathlib import Path
from utils.updater import UpdateChecker

print("=" * 60)
print("DOWNLOAD FUNCTIE TEST")
print("=" * 60)

# Test update checker
checker = UpdateChecker("1.1.0")
has_update = checker.check_for_updates()
update_info = checker.get_update_info()

print(f"\nUpdate beschikbaar: {has_update}")
print(f"Latest version: {update_info.get('latest_version')}")
print(f"Download URL: {update_info.get('download_url')}")
print(f"Release URL: {update_info.get('release_url')}")

if update_info.get('download_url'):
    print("\n✅ Download URL gevonden!")
    print(f"   URL: {update_info.get('download_url')}")
    print("\n   De download functie zou automatisch moeten downloaden.")
    print("   Als het nog steeds naar GitHub gaat, is er een probleem in de download functie.")
else:
    print("\n❌ Geen download URL gevonden!")
    print("   Dit betekent dat de release geen assets heeft OF de API cache nog niet is bijgewerkt.")
    print("\n   Oplossingen:")
    print("   1. Wacht 2-5 minuten en test opnieuw")
    print("   2. Check of assets echt geüpload zijn op GitHub")
    print("   3. Test de download functie in de EXE (soms werkt die eerder)")

# Simuleer wat de download functie zou doen
print("\n" + "=" * 60)
print("SIMULATIE DOWNLOAD FUNCTIE")
print("=" * 60)

download_url = update_info.get("download_url")
release_url = update_info.get("release_url")

if download_url:
    print(f"\n✅ download_url is gevuld: {download_url}")
    print("   De download functie zou automatisch moeten downloaden")
    print("   (niet naar GitHub gaan)")
elif release_url:
    print(f"\n⚠️  download_url is None, maar release_url is: {release_url}")
    print("   De download functie zou naar GitHub gaan (zoals nu gebeurt)")
    print("\n   Dit betekent:")
    print("   - Release heeft geen assets, OF")
    print("   - Assets zijn nog niet zichtbaar via API")
else:
    print("\n❌ Geen URLs gevonden!")
