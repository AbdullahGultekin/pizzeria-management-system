"""Test script voor update checker"""
import requests
from utils.updater import UpdateChecker, get_releases_url

print("=" * 60)
print("UPDATE CHECK TEST")
print("=" * 60)

# Test 1: Check GitHub releases
print("\n1. Checking GitHub releases...")
try:
    repo_url = "https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases"
    response = requests.get(repo_url, timeout=5)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        releases = response.json()
        print(f"   Aantal releases gevonden: {len(releases)}")
        if releases:
            print("\n   Releases:")
            for r in releases[:5]:
                tag = r.get("tag_name", "N/A")
                name = r.get("name", "N/A")
                published = r.get("published_at", "N/A")
                print(f"     - {tag} ({name}) - Published: {published}")
        else:
            print("   WARNING: GEEN RELEASES GEVONDEN!")
            print("   Maak een release op GitHub om updates te kunnen checken.")
    else:
        print(f"   ERROR: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Check latest release endpoint
print("\n2. Checking latest release endpoint...")
print(f"   URL: {get_releases_url()}")
try:
    response = requests.get(get_releases_url(), timeout=5)
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        release = response.json()
        tag = release.get("tag_name", "N/A")
        print(f"   OK: Latest release gevonden: {tag}")
    elif response.status_code == 404:
        print("   WARNING: 404 - Geen releases gevonden")
        print("   Dit betekent dat er nog geen releases zijn gepubliceerd.")
    else:
        print(f"   ERROR: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Test UpdateChecker
print("\n3. Testing UpdateChecker...")
try:
    checker = UpdateChecker("1.1.0")
    has_update = checker.check_for_updates()
    print(f"   Current version: {checker.current_version}")
    print(f"   Latest version: {checker.latest_version}")
    print(f"   Update available: {has_update}")
    print(f"   Download URL: {checker.download_url}")
    
    if has_update:
        print("   OK: Update beschikbaar!")
    else:
        if checker.latest_version:
            print("   INFO: Geen update nodig (al op nieuwste versie)")
        else:
            print("   WARNING: Geen releases gevonden op GitHub")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST VOLTOOID")
print("=" * 60)
