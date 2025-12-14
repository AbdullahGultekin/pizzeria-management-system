"""Detailed check of release assets"""
import requests

print("Checking release v1.1.1 assets...")
r = requests.get('https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases/tags/v1.1.1')
release = r.json()

print(f"\nRelease: {release.get('name', 'N/A')}")
print(f"Tag: {release.get('tag_name', 'N/A')}")
print(f"Published: {release.get('published_at', 'N/A')}")

assets = release.get('assets', [])
print(f"\nAssets count: {len(assets)}")

if assets:
    print("\nAssets found:")
    for i, a in enumerate(assets, 1):
        print(f"\n{i}. {a.get('name')}")
        print(f"   Size: {a.get('size', 0) / (1024*1024):.2f} MB")
        print(f"   Content Type: {a.get('content_type', 'N/A')}")
        print(f"   Download URL: {a.get('browser_download_url', 'N/A')}")
        print(f"   State: {a.get('state', 'N/A')}")
else:
    print("\nNo assets found via API")
    print("This might mean:")
    print("  - Assets are still uploading")
    print("  - API cache needs to refresh")
    print("  - Check the GitHub page directly")
