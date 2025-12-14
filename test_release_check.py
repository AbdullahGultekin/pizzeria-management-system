"""Test script om specifieke release te checken"""
import requests

print("=" * 60)
print("RELEASE CHECK TEST")
print("=" * 60)

# Test repository access
print("\n1. Checking repository access...")
repo_url = "https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system"
try:
    r = requests.get(repo_url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Repository: {data.get('full_name', 'N/A')}")
        print(f"   Private: {data.get('private', 'unknown')}")
        print(f"   Public: {not data.get('private', True)}")
    elif r.status_code == 404:
        print("   ERROR: Repository niet gevonden of privé!")
        print("   Als de repo privé is, werkt de update check niet zonder authenticatie.")
    else:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test specific release
print("\n2. Checking release v1.1.1...")
release_url = "https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases/tags/v1.1.1"
try:
    r = requests.get(release_url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        release = r.json()
        print(f"   OK: Release gevonden!")
        print(f"   Tag: {release.get('tag_name', 'N/A')}")
        print(f"   Name: {release.get('name', 'N/A')}")
        print(f"   Draft: {release.get('draft', False)}")
        print(f"   Prerelease: {release.get('prerelease', False)}")
        print(f"   Published: {release.get('published_at', 'N/A')}")
        assets = release.get('assets', [])
        print(f"   Assets: {len(assets)}")
        for asset in assets:
            print(f"     - {asset.get('name', 'N/A')} ({asset.get('size', 0)} bytes)")
    elif r.status_code == 404:
        print("   ERROR: Release niet gevonden!")
        print("   Mogelijke oorzaken:")
        print("     - Release is een draft")
        print("     - Repository is privé")
        print("     - Tag naam is verkeerd")
    else:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test latest release endpoint
print("\n3. Checking latest release endpoint...")
latest_url = "https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases/latest"
try:
    r = requests.get(latest_url, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        release = r.json()
        print(f"   OK: Latest release gevonden!")
        print(f"   Tag: {release.get('tag_name', 'N/A')}")
        print(f"   Name: {release.get('name', 'N/A')}")
    elif r.status_code == 404:
        print("   WARNING: Geen latest release gevonden")
        print("   Dit kan betekenen:")
        print("     - Alle releases zijn drafts")
        print("     - Repository is privé")
    else:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
