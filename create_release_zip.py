"""
Script om PizzeriaBestelformulier.exe in een ZIP te verpakken voor GitHub upload.
"""
import zipfile
from pathlib import Path
import shutil

EXE_PATH = Path("dist/PizzeriaBestelformulier.exe")
ZIP_PATH = Path("dist/PizzeriaBestelformulier.zip")

def create_zip():
    """Create ZIP file with EXE."""
    if not EXE_PATH.exists():
        print(f"ERROR: {EXE_PATH} niet gevonden!")
        print("Bouw eerst de EXE met: pyinstaller pizzeria.spec --clean --noconfirm")
        return False
    
    print(f"ZIP maken: {ZIP_PATH}")
    print(f"Van: {EXE_PATH}")
    
    try:
        # Remove existing ZIP if it exists
        if ZIP_PATH.exists():
            ZIP_PATH.unlink()
            print("Bestaande ZIP verwijderd.")
        
        # Create ZIP file
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(EXE_PATH, EXE_PATH.name)
        
        # Get file sizes
        exe_size = EXE_PATH.stat().st_size / (1024 * 1024)
        zip_size = ZIP_PATH.stat().st_size / (1024 * 1024)
        
        print(f"\nOK: ZIP gemaakt!")
        print(f"   EXE grootte: {exe_size:.2f} MB")
        print(f"   ZIP grootte: {zip_size:.2f} MB")
        print(f"   Compressie: {(1 - zip_size/exe_size)*100:.1f}%")
        print(f"\nLocatie: {ZIP_PATH.absolute()}")
        print("\nJe kunt nu dit ZIP bestand uploaden naar GitHub!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EXE naar ZIP Converter")
    print("=" * 60)
    print()
    
    if create_zip():
        print("\n" + "=" * 60)
        print("KLAAR!")
        print("=" * 60)
        print("\nUpload instructies:")
        print("1. Ga naar: https://github.com/AbdullahGultekin/pizzeria-management-system/releases/edit/v1.1.1")
        print("2. Sleep het ZIP bestand naar 'Attach binaries'")
        print("3. Klik 'Update release'")
        print("\nOF gebruik het upload script:")
        print("  python upload_exe_to_release.py")
    else:
        print("\nERROR: ZIP maken gefaald!")
