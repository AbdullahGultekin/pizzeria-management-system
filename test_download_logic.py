"""Test de verbeterde download logica"""
import urllib.request
from utils.updater import UpdateChecker

print("=" * 60)
print("TEST DOWNLOAD LOGICA")
print("=" * 60)

checker = UpdateChecker("1.1.0")
checker.check_for_updates()
update_info = checker.get_update_info()

download_url = update_info.get("download_url")
release_url = update_info.get("release_url")
latest_version = update_info.get("latest_version", "unknown")

print(f"\nUpdate info:")
print(f"  Latest version: {latest_version}")
print(f"  Download URL (from API): {download_url}")
print(f"  Release URL: {release_url}")

# Simuleer de verbeterde logica
if not download_url and release_url:
    print("\n" + "=" * 60)
    print("TESTING DIRECT URL CONSTRUCTION")
    print("=" * 60)
    
    tag_name = latest_version
    if not tag_name.startswith("v"):
        tag_name = f"v{tag_name}"
    
    # Extract repo info
    parts = release_url.replace("https://github.com/", "").split("/releases/tag/")
    if len(parts) == 2:
        repo_path = parts[0]
        print(f"  Repo path: {repo_path}")
        print(f"  Tag: {tag_name}")
        
        # Try common asset names
        possible_assets = [
            f"https://github.com/{repo_path}/releases/download/{tag_name}/PizzeriaBestelformulier.exe",
            f"https://github.com/{repo_path}/releases/download/{tag_name}/PizzeriaBestelformulier.zip",
        ]
        
        print(f"\n  Testing URLs:")
        working_url = None
        for test_url in possible_assets:
            print(f"    Testing: {test_url.split('/')[-1]}")
            try:
                test_req = urllib.request.Request(test_url, method='HEAD')
                with urllib.request.urlopen(test_req, timeout=3) as response:
                    if response.status == 200:
                        working_url = test_url
                        print(f"      ✅ FOUND! Status: {response.status}")
                        break
                    else:
                        print(f"      ❌ Status: {response.status}")
            except urllib.error.HTTPError as e:
                print(f"      ❌ HTTP {e.code}: {e.reason}")
            except Exception as e:
                print(f"      ❌ Error: {type(e).__name__}")
        
        if working_url:
            print(f"\n✅ WORKING URL GEVONDEN!")
            print(f"   {working_url}")
            print(f"\n   De download functie zou nu automatisch moeten downloaden!")
        else:
            print(f"\n❌ Geen werkende URL gevonden")
            print(f"   Dit betekent:")
            print(f"   - Assets zijn nog niet beschikbaar via directe URLs")
            print(f"   - Of de bestandsnaam is anders dan verwacht")
            print(f"   - Wacht 2-5 minuten en probeer opnieuw")

print("\n" + "=" * 60)
