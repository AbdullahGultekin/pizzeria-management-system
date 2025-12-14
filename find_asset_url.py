"""Find the exact asset download URL"""
import requests

print("Searching for assets in release v1.1.1...")

# Method 1: Check via releases/latest
print("\n1. Checking /releases/latest endpoint:")
r1 = requests.get('https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases/latest')
if r1.status_code == 200:
    release = r1.json()
    assets = release.get('assets', [])
    print(f"   Assets: {len(assets)}")
    for a in assets:
        print(f"   - {a.get('name')}: {a.get('browser_download_url')}")

# Method 2: Check via releases/tags/v1.1.1
print("\n2. Checking /releases/tags/v1.1.1 endpoint:")
r2 = requests.get('https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases/tags/v1.1.1')
if r2.status_code == 200:
    release = r2.json()
    assets = release.get('assets', [])
    print(f"   Assets: {len(assets)}")
    for a in assets:
        print(f"   - {a.get('name')}: {a.get('browser_download_url')}")

# Method 3: Check all releases
print("\n3. Checking all releases:")
r3 = requests.get('https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases')
if r3.status_code == 200:
    releases = r3.json()
    for release in releases:
        if release.get('tag_name') == 'v1.1.1':
            assets = release.get('assets', [])
            print(f"   Release v1.1.1 assets: {len(assets)}")
            for a in assets:
                print(f"   - {a.get('name')}: {a.get('browser_download_url')}")
            break

print("\n" + "=" * 60)
if assets:
    print("✅ Assets gevonden via API!")
    print(f"   Download URL: {assets[0].get('browser_download_url')}")
else:
    print("❌ Geen assets gevonden via API")
    print("   Dit kan betekenen:")
    print("   - Assets zijn net geüpload (API cache)")
    print("   - Assets zijn niet correct geüpload")
    print("   - Check de GitHub pagina handmatig")
