"""Check assets in release"""
import requests

r = requests.get('https://api.github.com/repos/AbdullahGultekin/pizzeria-management-system/releases/tags/v1.1.1')
release = r.json()
assets = release.get('assets', [])
print(f'Assets in v1.1.1: {len(assets)}')
for a in assets:
    print(f'  - {a.get("name")} ({a.get("size", 0) / (1024*1024):.2f} MB)')
    print(f'    URL: {a.get("browser_download_url", "N/A")}')
