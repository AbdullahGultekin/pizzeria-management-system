"""
Script om duplicaat klanten te analyseren en te bepalen of het echte duplicaten zijn
of verschillende adressen (thuis vs afhaal).
"""

import sys
import os
import re

# Voeg de root directory toe aan het pad
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseContext
from logging_config import get_logger

logger = get_logger("check_duplicates")


def normalize_phone_for_search(telefoon: str) -> str:
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


def check_duplicates():
    """Analyseer duplicaat klanten."""
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
                    normalized = normalize_phone_for_search(klant['telefoon'])
                    if normalized not in phone_groups:
                        phone_groups[normalized] = []
                    phone_groups[normalized].append(klant)
            
            # Vind duplicaten
            duplicates = {}
            for normalized_phone, klant_list in phone_groups.items():
                if len(klant_list) > 1:
                    duplicates[normalized_phone] = klant_list
            
            print("=" * 80)
            print(f"Gevonden {len(duplicates)} duplicaat telefoonnummers")
            print("=" * 80)
            print()
            
            for normalized_phone, klant_list in sorted(duplicates.items()):
                print(f"Telefoonnummer: {normalized_phone}")
                print(f"Aantal klanten: {len(klant_list)}")
                print("-" * 80)
                
                for klant in klant_list:
                    adres = f"{klant['straat'] or ''} {klant['huisnummer'] or ''}".strip()
                    plaats = klant['plaats'] or ''
                    volledig_adres = f"{adres}, {plaats}".strip(', ')
                    
                    print(f"  ID: {klant['id']}")
                    print(f"  Naam: {klant['naam'] or '(geen naam)'}")
                    print(f"  Adres: {volledig_adres or '(geen adres)'}")
                    print(f"  Origineel telefoon: {klant['telefoon']}")
                    
                    # Check aantal bestellingen
                    cursor.execute("SELECT COUNT(*) as count FROM bestellingen WHERE klant_id = ?", (klant['id'],))
                    order_count = cursor.fetchone()['count']
                    print(f"  Aantal bestellingen: {order_count}")
                    print()
                
                # Analyseer of het verschillende adressen zijn
                adressen = []
                for klant in klant_list:
                    adres = f"{klant['straat'] or ''} {klant['huisnummer'] or ''}".strip()
                    plaats = klant['plaats'] or ''
                    volledig = f"{adres}, {plaats}".strip(', ')
                    if volledig:
                        adressen.append(volledig)
                    else:
                        adressen.append("(geen adres)")
                
                unieke_adressen = set(adressen)
                if len(unieke_adressen) > 1:
                    print(f"  ⚠️  VERSCHILLENDE ADRESSEN: {len(unieke_adressen)} verschillende adressen gevonden")
                    print(f"     Dit kan betekenen: thuis adres vs afhaal, of meerdere bezorgadressen")
                elif len(unieke_adressen) == 1 and "(geen adres)" not in unieke_adressen:
                    print(f"  ⚠️  ZELFDE ADRES: Alle klanten hebben hetzelfde adres - waarschijnlijk echte duplicaat")
                else:
                    print(f"  ℹ️  Geen adres informatie beschikbaar")
                
                print("=" * 80)
                print()
            
            return duplicates
            
    except Exception as e:
        logger.exception(f"Fout tijdens analyse: {e}")
        raise


if __name__ == "__main__":
    print("Duplicaat Klanten Analyse")
    print()
    
    try:
        duplicates = check_duplicates()
        print()
        print(f"Totaal: {len(duplicates)} duplicaat telefoonnummers gevonden")
    except Exception as e:
        print(f"Fout: {e}")
        sys.exit(1)

