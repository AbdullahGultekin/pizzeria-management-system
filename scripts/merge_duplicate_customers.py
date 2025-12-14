"""
Script om duplicaat klanten samen te voegen.

Dit script:
- Vindt alle duplicaat klanten (zelfde telefoonnummer)
- Behoudt de klant met het nieuwste adres of meeste bestellingen
- Voegt alle bestellingen samen
- Verwijdert de duplicaten
- Zorgt dat alle telefoonnummers in E.164 formaat zijn
"""

import sys
import os
import re
from datetime import datetime

# Voeg de root directory toe aan het pad
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseContext
from logging_config import get_logger

logger = get_logger("merge_duplicates")


def normalize_phone_for_storage(telefoon: str) -> str:
    """Normalize phone number to E.164 format."""
    if not telefoon:
        return telefoon
    
    telefoon = telefoon.strip()
    cleaned = re.sub(r'[\s\-\(\)\-\.]', '', telefoon)
    
    if cleaned.startswith('+32'):
        return cleaned
    elif cleaned.startswith('0032'):
        return '+32' + cleaned[4:]
    elif cleaned.startswith('32') and len(cleaned) == 11:
        return '+' + cleaned
    elif cleaned.startswith('0') and len(cleaned) == 10:
        return '+32' + cleaned[1:]
    
    return cleaned


def merge_duplicate_customers():
    """
    Merge duplicate customers into one.
    Keeps the customer with the newest address or most orders.
    """
    merged_count = 0
    deleted_count = 0
    orders_moved = 0
    error_count = 0
    
    try:
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            
            # Haal alle klanten op
            cursor.execute("SELECT id, telefoon, naam, straat, huisnummer, plaats FROM klanten ORDER BY telefoon")
            klanten = cursor.fetchall()
            
            # Groepeer per genormaliseerd telefoonnummer
            phone_groups = {}
            for klant in klanten:
                if klant['telefoon']:
                    normalized = normalize_phone_for_storage(klant['telefoon'])
                    if normalized not in phone_groups:
                        phone_groups[normalized] = []
                    phone_groups[normalized].append(klant)
            
            # Vind duplicaten
            duplicates = {}
            for normalized_phone, klant_list in phone_groups.items():
                if len(klant_list) > 1:
                    duplicates[normalized_phone] = klant_list
            
            total_duplicates = sum(len(klant_list) - 1 for klant_list in duplicates.values())
            logger.info(f"Gevonden {len(duplicates)} duplicaat telefoonnummers ({total_duplicates} extra klanten)")
            
            for normalized_phone, klant_list in sorted(duplicates.items()):
                print(f"\nVerwerken: {normalized_phone} ({len(klant_list)} klanten)")
                
                # Bepaal welke klant we behouden
                # Prioriteit: 1) Meeste bestellingen, 2) Nieuwste adres (hoogste ID), 3) Laagste ID (oudste)
                best_klant = None
                best_score = -1
                best_order_count = 0
                
                if not klant_list:
                    print(f"  ⚠️  Lege lijst, overslaan...")
                    continue
                
                for klant in klant_list:
                    # Tel bestellingen
                    cursor.execute("SELECT COUNT(*) as count FROM bestellingen WHERE klant_id = ?", (klant['id'],))
                    result = cursor.fetchone()
                    order_count = result['count'] if result else 0
                    
                    # Check of er een adres is
                    has_address = bool(klant['straat'] and klant['straat'].strip())
                    
                    # Score: bestellingen * 1000 + (heeft adres ? 100 : 0) + ID (hogere ID = nieuwer = hogere score)
                    score = order_count * 1000 + (100 if has_address else 0) + klant['id']
                    
                    if score > best_score:
                        best_score = score
                        best_klant = klant
                        best_order_count = order_count
                
                if not best_klant:
                    # Fallback: gebruik eerste klant
                    best_klant = klant_list[0]
                    cursor.execute("SELECT COUNT(*) as count FROM bestellingen WHERE klant_id = ?", (best_klant['id'],))
                    result = cursor.fetchone()
                    best_order_count = result['count'] if result else 0
                    print(f"  ⚠️  Fallback naar eerste klant")
                
                print(f"  Behouden: ID {best_klant['id']} (naam: {best_klant['naam'] or '(geen)'}, "
                      f"adres: {best_klant['straat'] or '(geen)'} {best_klant['huisnummer'] or ''}, "
                      f"bestellingen: {best_order_count})")
                
                # Verzamel het nieuwste adres van alle duplicaten
                newest_address = None
                newest_straat = best_klant['straat'] or ""
                newest_huisnummer = best_klant['huisnummer'] or ""
                newest_plaats = best_klant['plaats'] or ""
                newest_naam = best_klant['naam'] or ""
                
                # Zoek naar het nieuwste adres (klant met hoogste ID heeft meestal nieuwste adres)
                for klant in klant_list:
                    if klant['id'] > best_klant['id']:
                        # Deze klant is nieuwer, gebruik zijn adres als het bestaat
                        if klant['straat'] and klant['straat'].strip():
                            newest_straat = klant['straat']
                            newest_huisnummer = klant['huisnummer'] or ""
                            newest_plaats = klant['plaats'] or ""
                            newest_address = klant
                            print(f"  Nieuwere adres gevonden bij ID {klant['id']}: {newest_straat} {newest_huisnummer}")
                    
                    # Gebruik naam als die beter is
                    if klant['naam'] and klant['naam'].strip() and (not newest_naam or not newest_naam.strip()):
                        newest_naam = klant['naam']
                
                # EERST: Verwijder alle duplicaten (behalve hoofdklant) om UNIQUE constraint te voorkomen
                for klant in klant_list:
                    if klant['id'] == best_klant['id']:
                        continue  # Skip de hoofdklant zelf
                    
                    try:
                        # Verplaats bestellingen eerst
                        cursor.execute("""
                            UPDATE bestellingen 
                            SET klant_id = ? 
                            WHERE klant_id = ?
                        """, (best_klant['id'], klant['id']))
                        moved = cursor.rowcount
                        if moved > 0:
                            orders_moved += moved
                            print(f"  ✓ {moved} bestelling(en) verplaatst van ID {klant['id']} naar ID {best_klant['id']}")
                        
                        # Verwijder de duplicaat klant
                        cursor.execute("DELETE FROM klanten WHERE id = ?", (klant['id'],))
                        deleted_count += 1
                        print(f"  ✓ Duplicaat ID {klant['id']} verwijderd")
                        
                    except Exception as e:
                        logger.error(f"Fout bij verwijderen klant {klant['id']}: {e}")
                        error_count += 1
                
                # DAARNA: Update de hoofdklant met nieuwste gegevens (nu is er geen UNIQUE constraint conflict meer)
                try:
                    cursor.execute("""
                        UPDATE klanten 
                        SET telefoon = ?, naam = ?, straat = ?, huisnummer = ?, plaats = ?
                        WHERE id = ?
                    """, (normalized_phone, newest_naam, newest_straat, newest_huisnummer, newest_plaats, best_klant['id']))
                    print(f"  ✓ Hoofdklant geüpdatet met nieuwste adres en genormaliseerd telefoonnummer")
                except Exception as e:
                    logger.error(f"Fout bij updaten hoofdklant {best_klant['id']}: {e}")
                    error_count += 1
                    continue
                
                merged_count += 1
            
            # Commit alle wijzigingen
            conn.commit()
            
            logger.info(f"Samenvoegen voltooid: {merged_count} groepen samengevoegd, "
                       f"{deleted_count} duplicaten verwijderd, {orders_moved} bestellingen verplaatst, "
                       f"{error_count} fouten")
            
            return merged_count, deleted_count, orders_moved, error_count
            
    except Exception as e:
        logger.exception(f"Fout tijdens samenvoegen: {e}")
        raise


if __name__ == "__main__":
    print("=" * 80)
    print("Duplicaat Klanten Samenvoegen Script")
    print("=" * 80)
    print()
    print("Dit script zal:")
    print("- Alle duplicaat klanten vinden (zelfde telefoonnummer)")
    print("- De klant met meeste bestellingen of nieuwste adres behouden")
    print("- Alle bestellingen verplaatsen naar de hoofdklant")
    print("- Het nieuwste adres gebruiken voor de hoofdklant")
    print("- Alle telefoonnummers normaliseren naar E.164 formaat")
    print("- Duplicaten verwijderen")
    print()
    print("⚠️  WAARSCHUWING: Dit kan niet ongedaan worden gemaakt!")
    print()
    
    response = input("Weet u zeker dat u wilt doorgaan? (ja/nee): ")
    if response.lower() not in ['ja', 'yes', 'j', 'y']:
        print("Samenvoegen geannuleerd.")
        sys.exit(0)
    
    print()
    print("Samenvoegen gestart...")
    print()
    
    try:
        merged, deleted, orders_moved, errors = merge_duplicate_customers()
        print()
        print("=" * 80)
        print("Samenvoegen voltooid!")
        print(f"- {merged} groepen duplicaten samengevoegd")
        print(f"- {deleted} duplicaat klanten verwijderd")
        print(f"- {orders_moved} bestellingen verplaatst")
        if errors > 0:
            print(f"- {errors} fouten opgetreden")
        print("=" * 80)
    except Exception as e:
        print()
        print("=" * 80)
        print(f"Fout tijdens samenvoegen: {e}")
        print("=" * 80)
        sys.exit(1)

