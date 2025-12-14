"""
Script om alle klantgegevens in de database te normaliseren.

Dit script:
- Normaliseert alle namen (eerste letter hoofdletter, rest kleine letters)
- Normaliseert alle telefoonnummers naar E.164 formaat (+32123456789)
- Normaliseert alle adressen (straat, plaats) (eerste letter hoofdletter, rest kleine letters)
"""

import sys
import os
import re

# Voeg de root directory toe aan het pad
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseContext
from logging_config import get_logger

logger = get_logger("normalize_klanten")


def normalize_customer_name(naam: str) -> str:
    """
    Normalize customer name: first letter uppercase, rest lowercase.
    
    Args:
        naam: Customer name to normalize
        
    Returns:
        Normalized name with first letter uppercase
    """
    if not naam or not naam.strip():
        return naam
    
    naam = naam.strip()
    # Capitalize first letter, lowercase the rest
    return naam[0].upper() + naam[1:].lower() if len(naam) > 1 else naam.upper()


def normalize_address(address: str) -> str:
    """
    Normalize address: first letter uppercase, rest lowercase.
    Handles special cases like "van", "de", "der", etc.
    
    Args:
        address: Address to normalize
        
    Returns:
        Normalized address
    """
    if not address or not address.strip():
        return address
    
    address = address.strip()
    
    # Split on spaces and capitalize each word
    words = address.split()
    normalized_words = []
    
    # Words that should remain lowercase (unless first word)
    lowercase_words = {'van', 'de', 'der', 'den', 'het', 'te', 'ter', 'ten', 'op', 'aan', 'in', 'en', 'of'}
    
    for i, word in enumerate(words):
        if i == 0:
            # First word always capitalized
            normalized_words.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
        elif word.lower() in lowercase_words:
            # Keep lowercase words lowercase
            normalized_words.append(word.lower())
        else:
            # Capitalize other words
            normalized_words.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
    
    return ' '.join(normalized_words)


def normalize_phone_for_storage(telefoon: str) -> str:
    """
    Normalize phone number to E.164 format for consistent storage.
    Handles different formats: +32123456789, 0123456789, 0032123456789
    Also handles Dutch numbers: +31123456789, 0031123456789
    
    Args:
        telefoon: Phone number to normalize
        
    Returns:
        Normalized phone number (E.164 format: +32123456789 or +31123456789)
    """
    if not telefoon:
        return telefoon
    
    telefoon = telefoon.strip()
    
    # Remove all spaces, dashes, parentheses, dots
    cleaned = re.sub(r'[\s\-\(\)\-\.]', '', telefoon)
    
    # Belgian numbers (+32)
    if cleaned.startswith('+32'):
        return cleaned
    elif cleaned.startswith('0032'):
        return '+32' + cleaned[4:]
    elif cleaned.startswith('32') and len(cleaned) == 11:
        return '+' + cleaned
    elif cleaned.startswith('0') and len(cleaned) == 10 and cleaned[1] in '1-9':
        # Belgian local format (0X...)
        return '+32' + cleaned[1:]
    
    # Dutch numbers (+31)
    if cleaned.startswith('+31'):
        return cleaned
    elif cleaned.startswith('0031'):
        return '+31' + cleaned[4:]
    elif cleaned.startswith('31') and len(cleaned) >= 11:
        return '+' + cleaned
    elif cleaned.startswith('0') and len(cleaned) == 10 and cleaned[1] in '1-9':
        # Could be Dutch, but we can't be sure without country code
        # Try to detect: Dutch numbers often start with 06 (mobile) or 0X where X is 1-9
        # For now, assume Belgian if starts with 0
        return '+32' + cleaned[1:]
    
    # Return as-is if already in E.164 or unknown format
    return cleaned


def normalize_all_customers():
    """
    Normalize all customer data in the database.
    """
    updated_count = 0
    error_count = 0
    duplicate_phones = {}
    
    try:
        with DatabaseContext() as conn:
            cursor = conn.cursor()
            
            # Eerst: detecteer duplicaten (verschillende formaten van hetzelfde nummer)
            cursor.execute("SELECT id, telefoon FROM klanten")
            all_phones = cursor.fetchall()
            
            # Groepeer klanten per genormaliseerd telefoonnummer
            phone_groups = {}
            for klant in all_phones:
                if klant['telefoon']:
                    normalized = normalize_phone_for_storage(klant['telefoon'])
                    if normalized not in phone_groups:
                        phone_groups[normalized] = []
                    phone_groups[normalized].append(klant['id'])
            
            # Vind duplicaten
            for normalized_phone, klant_ids in phone_groups.items():
                if len(klant_ids) > 1:
                    duplicate_phones[normalized_phone] = klant_ids
                    logger.warning(f"Duplicaat telefoonnummer gevonden: {normalized_phone} (klant IDs: {klant_ids})")
            
            # Haal alle klanten op
            cursor.execute("SELECT id, telefoon, naam, straat, huisnummer, plaats FROM klanten")
            klanten = cursor.fetchall()
            
            total_klanten = len(klanten)
            logger.info(f"Gevonden {total_klanten} klanten om te normaliseren")
            if duplicate_phones:
                logger.warning(f"Waarschuwing: {len(duplicate_phones)} duplicaat telefoonnummers gevonden")
            
            for klant in klanten:
                klant_id = klant['id']
                oude_telefoon = klant['telefoon'] or ""
                oude_naam = klant['naam'] or ""
                oude_straat = klant['straat'] or ""
                oude_huisnummer = klant['huisnummer'] or ""
                oude_plaats = klant['plaats'] or ""
                
                # Normaliseer alle velden
                nieuwe_telefoon = normalize_phone_for_storage(oude_telefoon)
                nieuwe_naam = normalize_customer_name(oude_naam)
                nieuwe_straat = normalize_address(oude_straat)
                nieuwe_huisnummer = oude_huisnummer.strip()  # Huisnummer blijft zoals het is (kan letters bevatten)
                nieuwe_plaats = normalize_address(oude_plaats)
                
                # Check of er iets is veranderd
                if (nieuwe_telefoon != oude_telefoon or 
                    nieuwe_naam != oude_naam or 
                    nieuwe_straat != oude_straat or 
                    nieuwe_plaats != oude_plaats):
                    
                    try:
                        # Check of het nieuwe telefoonnummer al bestaat (behalve voor deze klant)
                        if nieuwe_telefoon:
                            cursor.execute("SELECT id FROM klanten WHERE telefoon = ? AND id != ?", 
                                         (nieuwe_telefoon, klant_id))
                            existing = cursor.fetchone()
                            if existing:
                                logger.warning(f"Klant {klant_id}: telefoonnummer {nieuwe_telefoon} bestaat al bij klant {existing['id']}. Overslaan...")
                                error_count += 1
                                continue
                        
                        # Update de klant
                        cursor.execute("""
                            UPDATE klanten 
                            SET telefoon = ?, naam = ?, straat = ?, huisnummer = ?, plaats = ?
                            WHERE id = ?
                        """, (nieuwe_telefoon, nieuwe_naam, nieuwe_straat, nieuwe_huisnummer, nieuwe_plaats, klant_id))
                        
                        updated_count += 1
                        if updated_count % 100 == 0:
                            print(f"  {updated_count} klanten verwerkt...")
                        logger.debug(f"Klant {klant_id} geüpdatet: "
                                   f"telefoon '{oude_telefoon}' -> '{nieuwe_telefoon}', "
                                   f"naam '{oude_naam}' -> '{nieuwe_naam}', "
                                   f"straat '{oude_straat}' -> '{nieuwe_straat}', "
                                   f"plaats '{oude_plaats}' -> '{nieuwe_plaats}'")
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Fout bij updaten klant {klant_id}: {e}")
            
            # Commit alle wijzigingen
            conn.commit()
            
            logger.info(f"Normalisatie voltooid: {updated_count} klanten geüpdatet, {error_count} fouten")
            return updated_count, error_count
            
    except Exception as e:
        logger.exception(f"Fout tijdens normalisatie: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Klantendatabase Normalisatie Script")
    print("=" * 60)
    print()
    print("Dit script zal:")
    print("- Alle namen normaliseren (eerste letter hoofdletter, rest kleine letters)")
    print("- Alle telefoonnummers normaliseren naar E.164 formaat (+32123456789)")
    print("- Alle adressen normaliseren (straat, plaats)")
    print()
    
    response = input("Weet u zeker dat u wilt doorgaan? (ja/nee): ")
    if response.lower() not in ['ja', 'yes', 'j', 'y']:
        print("Normalisatie geannuleerd.")
        sys.exit(0)
    
    print()
    print("Normalisatie gestart...")
    print()
    
    try:
        updated, errors = normalize_all_customers()
        print()
        print("=" * 60)
        print(f"Normalisatie voltooid!")
        print(f"- {updated} klanten geüpdatet")
        if errors > 0:
            print(f"- {errors} fouten opgetreden")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"Fout tijdens normalisatie: {e}")
        print("=" * 60)
        sys.exit(1)

