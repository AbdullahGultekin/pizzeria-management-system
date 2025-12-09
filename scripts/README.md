# Scripts

Deze map bevat utility scripts voor het project.

## Structuur

```
scripts/
├── README.md (dit bestand)
├── start/          - Start scripts
│   ├── start_pizzeria.bat
│   └── start_pizzeria.vbs
├── build/          - Build scripts en configuraties
│   ├── build_windows.bat
│   ├── main.spec
│   └── pizzeria.spec
└── prepare_github.sh - GitHub setup script
```

## Start Scripts

### Windows:
- `start/start_pizzeria.bat` - Start de applicatie
- `start/start_pizzeria.vbs` - Start script met GUI

## Build Scripts

- `build/build_windows.bat` - Windows build script
- `build/*.spec` - PyInstaller spec bestanden

## Utility Scripts

- `prepare_github.sh` - GitHub repository setup

