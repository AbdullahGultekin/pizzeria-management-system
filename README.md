# Pizzeria Management System

A comprehensive desktop application for managing pizzeria operations including orders, customers, inventory, and reporting.

## Features

- **Order Management**: Create and manage customer orders with customizable menu items
- **Customer Management**: Track customer information, order history, and preferences
- **Menu Management**: Configure menu items, categories, and pricing
- **Inventory Management**: Track ingredients and stock levels
- **Reporting**: Generate sales reports and analytics
- **Receipt Printing**: Print receipts to thermal printers (Windows)
- **Delivery Management**: Assign orders to delivery drivers
- **Backup & Restore**: Backup and restore database

## Requirements

- Python 3.8 or higher
- Tkinter (usually included with Python)
- See `requirements.txt` for additional dependencies

## Project Structuur

```
├── app.py                 # Hoofd applicatie
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── README.md            # Dit bestand
├── docs/                # Documentatie
├── tests/               # Test code
│   └── scripts/         # Test scripts en rapporten
├── scripts/             # Utility scripts
│   ├── start/           # Start scripts
│   └── build/           # Build scripts
├── logs/                # Log bestanden
└── data/                # Data bestanden
    └── backup/          # Backup bestanden
```

## Installation

### Quick Start (Windows - Exe)

1. Download de nieuwste release van [GitHub Releases](https://github.com/AbdullahGultekin/pizzeria-management-system/releases)
2. Pak het zip bestand uit
3. Dubbelklik op `main.exe` - **Klaar!** 🎉

**Geen Python installatie nodig!**

### Van Broncode

1. Clone or download this repository

2. **Windows:** Run setup script:
```bash
scripts\setup_windows.bat
```

**Of handmatig:**
```bash
pip install -r requirements.txt
pip install pywin32  # Voor Windows printer support
```

3. Start de applicatie:
```bash
python main.py
```

📖 **Zie [PC Installatie Gids](docs/PC_INSTALLATIE_GUIDE.md) voor volledige instructies**

## Configuration

The application uses `settings.json` for configuration. On first run, a default configuration file will be created.

### Settings

- `thermal_printer_name`: Name of the thermal printer (Windows only)
- `category_order`: Custom order for menu categories

## Usage

Run the application:
```bash
python main.py
```

### Keyboard Shortcuts

- `Ctrl+P` / `Cmd+P`: Print preview

## Project Structure

```
.
├── main.py                 # Main application entry point
├── database.py             # Database operations
├── config.py               # Configuration management
├── app_state.py            # Application state management
├── logging_config.py       # Logging configuration
├── exceptions.py           # Custom exceptions
├── bon_generator.py        # Receipt generation
├── menu.json               # Menu configuration
├── extras.json             # Product extras configuration
├── settings.json           # Application settings
├── modules/                # Feature modules
│   ├── klanten.py          # Customer management
│   ├── koeriers.py         # Delivery driver management
│   ├── geschiedenis.py     # Order history
│   ├── menu_management.py  # Menu configuration
│   ├── extras_management.py # Extras configuration
│   ├── rapportage.py       # Reporting
│   ├── backup.py           # Backup/restore
│   ├── voorraad.py         # Inventory management
│   └── bon_viewer.py       # Receipt preview
├── printers/               # Printer abstraction layer
│   ├── base.py             # Base printer interface
│   └── windows_printer.py  # Windows printer implementation
└── requirements.txt        # Python dependencies
```

## Database

The application uses SQLite database (`pizzeria.db`). The database is automatically initialized on first run.

### Database Schema

- `klanten`: Customer information
- `bestellingen`: Orders
- `bestelregels`: Order line items
- `koeriers`: Delivery drivers
- `ingredienten`: Ingredients for inventory
- `recepturen`: Recipes linking products to ingredients
- `voorraad_mutaties`: Inventory transactions

## Logging

The application logs to:
- `app.log`: General application log
- `app_errors.log`: Error log only

Logs are automatically rotated when they reach 10MB, keeping 5 backup files.

## Building Executable

To build a standalone executable using PyInstaller:

```bash
pyinstaller main.spec
```

## Development

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to all functions and classes

### Error Handling

- Use custom exceptions from `exceptions.py`
- Log errors using the logging framework
- Provide user-friendly error messages

## Troubleshooting

### Database Locked Error

If you encounter "database is locked" errors:
- Ensure no other instance of the application is running
- Check that database connections are properly closed
- The application uses WAL mode for better concurrency

### Printer Not Working

- On Windows: Ensure `pywin32` is installed
- Check that the printer name in settings matches the Windows printer name
- Verify printer is connected and powered on

## License

[Add your license here]

## Support

For issues and questions, please [add contact information or issue tracker link].



