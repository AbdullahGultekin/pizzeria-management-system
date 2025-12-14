# Update Check voor Privé Repository

## Probleem
Je repository is **privé**, waardoor de GitHub API geen toegang heeft zonder authenticatie. De update checker werkt standaard alleen met **publieke repositories**.

## Oplossingen

### Optie 1: Repository Publiek Maken (Aanbevolen)
1. Ga naar je GitHub repository settings
2. Scroll naar beneden naar "Danger Zone"
3. Klik "Change visibility" → "Make public"
4. **Voordeel**: Update checker werkt direct zonder extra code
5. **Nadeel**: Code is publiek zichtbaar

### Optie 2: Authenticatie Toevoegen (Geavanceerd)
Als je de repository privé wilt houden, moet je een GitHub Personal Access Token gebruiken.

**Stappen:**
1. Maak een GitHub Personal Access Token:
   - Ga naar: https://github.com/settings/tokens
   - Klik "Generate new token (classic)"
   - Geef alleen `public_repo` scope (of `repo` voor privé repos)
   - Kopieer de token

2. Voeg token toe aan code (niet aanbevolen voor EXE):
   - Token zou in code moeten, wat een security risico is
   - Beter: gebruik environment variable of config file

3. Update `utils/updater.py` om token te gebruiken:
   ```python
   headers = {}
   token = os.getenv('GITHUB_TOKEN') or settings.get('github_token')
   if token:
       headers['Authorization'] = f'token {token}'
   response = requests.get(releases_url, headers=headers, timeout=timeout)
   ```

**Nadeel**: Token moet in EXE of config, wat security risico is.

### Optie 3: Gebruik Publieke Mirror (Alternatief)
- Houd main repo privé
- Maak een publieke mirror repo alleen voor releases
- Update checker wijst naar publieke mirror

## Aanbeveling
**Optie 1 (Publiek maken)** is het eenvoudigst en veiligst voor update checks. Als je gevoelige code hebt, overweeg dan:
- Alleen de release branch publiek maken
- Of gebruik een aparte publieke repository alleen voor releases

## Test na Fix
Na het publiek maken van de repository, test opnieuw:
```bash
python test_release_check.py
```

De status zou nu 200 moeten zijn in plaats van 404.
