# Tcl/Tk Fix voor PyInstaller EXE

## Probleem
De EXE geeft fout: "Can't find a usable init.tcl"

Dit gebeurt omdat PyInstaller de Tcl/Tk bestanden (vereist voor Tkinter GUI) niet automatisch meeneemt.

## Oplossing
De `pizzeria.spec` file is aangepast om:
1. ✅ Tcl/Tk directories automatisch te vinden
2. ✅ Tcl/Tk data files toe te voegen aan de build
3. ✅ Requests library terug toegevoegd (voor update checker)

## Rebuild de EXE

Na deze fix, rebuild de EXE:

```powershell
pyinstaller pizzeria.spec --clean --noconfirm
```

## Verificatie

Na rebuild, test de EXE:
1. Start `dist\PizzeriaBestelformulier.exe`
2. De applicatie zou nu moeten opstarten zonder Tcl/Tk fout

## Wat is Aangepast

### pizzeria.spec
- ✅ `find_tcl_tk()` functie toegevoegd om Tcl/Tk directories te vinden
- ✅ Tcl/Tk data files worden automatisch toegevoegd aan `datas`
- ✅ Requests en dependencies terug toegevoegd aan `hiddenimports`

### Belangrijk
- De Tcl/Tk directories worden automatisch gevonden tijdens build
- Geen handmatige configuratie nodig
- Werkt op alle Windows systemen met Python 3.12

## Troubleshooting

### Als de fout blijft bestaan:
1. Controleer of Python Tkinter correct geïnstalleerd is:
   ```python
   python -c "import tkinter; tkinter.Tk()"
   ```

2. Rebuild met clean:
   ```powershell
   pyinstaller pizzeria.spec --clean --noconfirm
   ```

3. Test de EXE op een andere PC om te zien of het systeem-specifiek is
