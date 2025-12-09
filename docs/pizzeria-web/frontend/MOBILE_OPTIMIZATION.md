# Mobiele Optimalisatie - Alle Toestellen

Deze website is geoptimaliseerd voor alle mobiele toestellen, inclusief:
- ✅ Android telefoons (alle versies)
- ✅ iOS (iPhone en iPad)
- ✅ Chinese telefoons (Huawei, Xiaomi, Oppo, Vivo, etc.)
- ✅ Chinese browsers (WeChat, QQ Browser, UC Browser, Baidu Browser)
- ✅ Andere mobiele browsers wereldwijd

## Geïmplementeerde Optimalisaties

### 1. Viewport Meta Tags
- **Basis viewport**: `width=device-width, initial-scale=1.0`
- **Maximum zoom**: `maximum-scale=5.0` (gebruikers kunnen inzoomen)
- **Minimum zoom**: `minimum-scale=1.0`
- **User scalable**: `user-scalable=yes` (gebruikers kunnen zoomen)
- **Viewport fit**: `viewport-fit=cover` (voor notched devices)

### 2. iOS Specifieke Tags
- `apple-mobile-web-app-capable`: App-achtige ervaring op iOS
- `apple-mobile-web-app-status-bar-style`: Status bar styling
- `apple-mobile-web-app-title`: App naam
- `format-detection`: Automatische telefoonnummer detectie
- `apple-touch-fullscreen`: Volledig scherm modus

### 3. Android/Chrome Tags
- `mobile-web-app-capable`: Web app ondersteuning
- `theme-color`: Browser thema kleur (#ad2929)
- `msapplication-TileColor`: Windows tile kleur

### 4. Chinese Browser Tags
- `x5-orientation`: Portrait modus voor Tencent browsers
- `x5-fullscreen`: Volledig scherm voor Tencent browsers
- `x5-page-mode`: App modus voor Tencent browsers
- `360-fullscreen`: 360 Browser ondersteuning
- `browsermode`: Application modus

### 5. Responsive CSS
- **Breakpoints**:
  - Desktop: > 1200px
  - Tablet: 768px - 1200px
  - Mobile: 320px - 768px
  - Small mobile: < 480px
  - Very small: < 360px

- **Touch-friendly**:
  - Minimum button size: 44x44px
  - Minimum input height: 44px
  - Font size: 16px voor inputs (voorkomt zoom op iOS)

- **Text size adjustment**:
  - `-webkit-text-size-adjust: 100%`
  - `-ms-text-size-adjust: 100%`
  - Voorkomt automatische tekst vergroting

### 6. PWA Manifest
- App naam: "Pita Pizza Napoli"
- Theme color: #ad2929
- Display mode: standalone
- Orientation: portrait
- Icons: 192x192 en 512x512

## Testen op Verschillende Toestellen

### Test Checklist:
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] WeChat browser (Chinese telefoons)
- [ ] QQ Browser
- [ ] UC Browser
- [ ] Baidu Browser
- [ ] Samsung Internet
- [ ] Firefox Mobile
- [ ] Opera Mobile

### Test Punten:
1. **Layout**: Ziet alles er goed uit op kleine schermen?
2. **Touch targets**: Zijn knoppen groot genoeg om aan te raken?
3. **Text**: Is tekst leesbaar zonder te zoomen?
4. **Forms**: Werken formuliervelden goed?
5. **Navigation**: Is navigatie gebruiksvriendelijk?
6. **Images**: Laden afbeeldingen correct?
7. **Performance**: Laadt de site snel genoeg?

## Bekende Issues en Oplossingen

### iOS Safari Zoom op Input Focus
**Probleem**: iOS zoomt automatisch in bij input focus als font-size < 16px
**Oplossing**: Alle inputs hebben `font-size: 16px !important`

### Chinese Browsers WeChat/QQ
**Probleem**: Sommige browsers hebben eigen viewport gedrag
**Oplossing**: Specifieke meta tags toegevoegd voor Tencent browsers

### Kleine Schermen (< 360px)
**Probleem**: Sommige Chinese telefoons hebben zeer kleine schermen
**Oplossing**: Extra CSS breakpoint voor < 360px met kleinere fonts

### Landscape Mode
**Probleem**: Layout kan breken in landscape
**Oplossing**: Specifieke CSS voor landscape orientation

## Performance Tips

1. **Images**: Gebruik WebP format waar mogelijk
2. **Lazy Loading**: Images laden alleen wanneer nodig
3. **Minification**: CSS en JS minificeren voor productie
4. **Caching**: Browser caching inschakelen
5. **CDN**: Overweeg CDN voor statische assets

## Browser Support

- ✅ Chrome/Edge (Android & Desktop)
- ✅ Safari (iOS & macOS)
- ✅ Firefox (Mobile & Desktop)
- ✅ Samsung Internet
- ✅ WeChat Browser
- ✅ QQ Browser
- ✅ UC Browser
- ✅ Baidu Browser
- ✅ Opera Mobile

## Toekomstige Verbeteringen

- [ ] Service Worker voor offline ondersteuning
- [ ] Push notifications
- [ ] App installatie prompts
- [ ] Splash screens voor PWA
- [ ] Custom icons voor verschillende devices



