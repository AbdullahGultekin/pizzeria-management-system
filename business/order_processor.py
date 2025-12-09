"""Order processing business logic."""

from typing import Dict, List, Any, Optional, Tuple
from tkinter import messagebox
from services.order_service import OrderService
from services.customer_service import CustomerService
from exceptions import ValidationError, DatabaseError
from logging_config import get_logger

logger = get_logger("pizzeria.business.order")


class OrderProcessor:
    """Processor for order-related business operations."""
    
    def __init__(
        self,
        order_service: Optional[OrderService] = None,
        customer_service: Optional[CustomerService] = None
    ):
        """
        Initialize order processor.
        
        Args:
            order_service: Optional order service (defaults to new instance)
            customer_service: Optional customer service (defaults to new instance)
        """
        self.order_service = order_service or OrderService()
        self.customer_service = customer_service or CustomerService()
    
    def get_current_order_data(
        self,
        telefoon_entry,
        naam_entry,
        adres_entry,
        nr_entry,
        postcode_var,
        opmerkingen_entry,
        bestelregels: List[Dict[str, Any]],
        postcodes: Dict[str, str],
        is_afhaal: bool = False
    ) -> Tuple[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Collect current order data with validation.
        
        Args:
            telefoon_entry: Phone entry widget
            naam_entry: Name entry widget
            adres_entry: Address entry widget
            nr_entry: House number entry widget
            postcode_var: Postcode StringVar
            opmerkingen_entry: Notes entry widget
            bestelregels: List of order items
            postcodes: Dictionary of postcodes
            is_afhaal: Whether this is a pickup order (address not required)
            
        Returns:
            Tuple of (klant_data, order_items, temp_bonnummer) or (None, None, None) if invalid
        """
        from validation import (
            validate_phone, validate_name, validate_address,
            validate_house_number, validate_postcode, sanitize_string
        )
        import database
        
        if not bestelregels:
            messagebox.showerror("Fout", "Er zijn geen producten toegevoegd aan de bestelling!")
            return None, None, None
        
        try:
            telefoon = telefoon_entry.get().strip()
            telefoon = validate_phone(telefoon)
        except ValidationError as e:
            messagebox.showerror("Validatiefout", str(e))
            return None, None, None
        
        try:
            naam = validate_name(naam_entry.get().strip(), required=False)
            # Address fields are optional for pickup orders
            if is_afhaal:
                adres = ""  # Not required for pickup
                nr = ""  # Not required for pickup
                postcode = ""  # Not required for pickup
            else:
                adres = validate_address(adres_entry.get().strip())
                nr = validate_house_number(nr_entry.get().strip(), required=False)  # Optional for addresses like harbor numbers
                postcode = validate_postcode(postcode_var.get(), postcodes)
            opmerking = sanitize_string(opmerkingen_entry.get().strip(), max_length=500)
        except ValidationError as e:
            messagebox.showerror("Validatiefout", str(e))
            return None, None, None
        
        klant_data = {
            "naam": naam or "",
            "telefoon": telefoon,
            "adres": adres,
            "nr": nr,
            "postcode_gemeente": postcode,
            "opmerking": opmerking
        }
        
        # Bonnummer wordt pas bij opslaan definitief, maar we hebben een tijdelijke nodig voor preview
        temp_bonnummer = database.get_next_bonnummer(peek_only=True)
        
        return klant_data, list(bestelregels), temp_bonnummer
    
    def save_order(
        self,
        klant_data: Dict[str, Any],
        order_items: List[Dict[str, Any]],
        show_confirmation: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Save order to database.
        
        Args:
            klant_data: Customer data dictionary
            order_items: List of order items
            show_confirmation: Whether to show confirmation message
            
        Returns:
            Tuple of (success, bonnummer)
        """
        try:
            # Get afhaal status
            is_afhaal = klant_data.get('afhaal', False)
            
            # Add new street name to straatnamen.json if it doesn't exist
            # Only for delivery orders, not pickup orders
            if not is_afhaal:
                adres = klant_data.get("adres", "").strip()
                if adres:
                    from utils.address_utils import update_straatnamen_json
                    try:
                        update_straatnamen_json(adres)
                        logger.debug(f"Straatnaam '{adres}' toegevoegd aan straatnamen.json (indien nieuw)")
                    except Exception as e:
                        logger.warning(f"Kon straatnaam niet toevoegen aan JSON: {e}")
            
            # Ensure customer exists
            # Voor bezorging: altijd laatste ingevulde adres opslaan
            # Voor afhaal: bestaand adres NIET leegmaken (adres van klant blijft bewaard)
            straat: str
            huisnummer: str
            plaats: str

            if is_afhaal:
                # Pickup: probeer bestaande klant op te halen zodat we het adres behouden
                existing_customer = self.customer_service.find_customer(klant_data["telefoon"])
                if existing_customer:
                    straat = existing_customer.get("straat", "") or ""
                    huisnummer = existing_customer.get("huisnummer", "") or ""
                    plaats = existing_customer.get("plaats", "") or ""
                else:
                    # Nieuwe klant zonder adres (mag bij afhaal)
                    straat = ""
                    huisnummer = ""
                    plaats = ""
            else:
                # Bezorging: gebruik het adres uit het formulier (laatste adres wint altijd)
                straat = klant_data.get("adres", "") or ""
                huisnummer = klant_data.get("nr", "") or ""
                plaats = klant_data.get("postcode_gemeente", "") or ""

            self.customer_service.create_or_update_customer(
                telefoon=klant_data["telefoon"],
                straat=straat,
                huisnummer=huisnummer,
                plaats=plaats,
                naam=klant_data.get("naam", "")
            )
            
            # Create order
            korting_percentage = klant_data.get('korting_percentage', 0.0)
            is_afhaal = klant_data.get('afhaal', False)
            success, bonnummer = self.order_service.create_order(
                klant_telefoon=klant_data["telefoon"],
                order_items=order_items,
                opmerking=klant_data.get("opmerking"),
                levertijd=klant_data.get("levertijd"),
                korting_percentage=korting_percentage,
                afhaal=is_afhaal
            )
            
            if success and show_confirmation:
                messagebox.showinfo("Succes", f"Bestelling opgeslagen! Bonnummer: {bonnummer}")
            
            return success, bonnummer
            
        except ValidationError as e:
            logger.warning(f"Validatiefout bij opslaan: {e}")
            messagebox.showerror("Validatiefout", f"Validatiefout: {str(e)}")
            return False, None
        except DatabaseError as e:
            logger.error(f"Databasefout bij opslaan: {e}")
            messagebox.showerror("Databasefout", f"Databasefout: {str(e)}")
            return False, None
        except Exception as e:
            logger.exception("Fout bij opslaan van bestelling")
            messagebox.showerror("Fout bij opslaan", f"Er is een onverwachte fout opgetreden: {str(e)}")
            return False, None
    
    def load_order_for_editing(
        self,
        klant_data: Dict[str, Any],
        bestelregels_data: List[Dict[str, Any]],
        oude_bestelling_id: int,
        telefoon_entry,
        naam_entry,
        adres_entry,
        nr_entry,
        opmerkingen_entry,
        bestelregels: List[Dict[str, Any]],
        postcodes: List[str],
        postcode_var,
        levertijd_entry=None
    ) -> None:
        """
        Load an existing order into the UI for editing.
        
        Args:
            klant_data: Customer data
            bestelregels_data: Order items data
            oude_bestelling_id: Order ID to delete
            telefoon_entry: Phone entry widget
            naam_entry: Name entry widget
            adres_entry: Address entry widget
            nr_entry: House number entry widget
            opmerkingen_entry: Notes entry widget
            bestelregels: Global order items list to update
            postcodes: List of postcodes
            postcode_var: Postcode StringVar
        """
        import database
        
        if bestelregels and not messagebox.askyesno(
            "Bevestigen",
            "De huidige (onopgeslagen) bestelling wordt gewist om de oude te laden. Weet u zeker dat u wilt doorgaan?"
        ):
            return
        
        # Delete old order
        try:
            self.order_service.delete_order(oude_bestelling_id)
        except Exception as e:
            logger.exception(f"Fout bij verwijderen bestelling: {e}")
            messagebox.showerror("Fout", f"Kon de originele bestelling niet verwijderen: {e}")
            return
        
        # Clear UI
        telefoon_entry.delete(0, 'end')
        naam_entry.delete(0, 'end')
        adres_entry.delete(0, 'end')
        nr_entry.delete(0, 'end')
        opmerkingen_entry.delete(0, 'end')
        bestelregels.clear()
        
        # Load new data
        telefoon_entry.insert(0, klant_data.get('telefoon', ''))
        naam_entry.insert(0, klant_data.get('naam', ''))
        adres_entry.insert(0, klant_data.get('adres', ''))
        nr_entry.insert(0, klant_data.get('nr', ''))
        opmerkingen_entry.insert(0, klant_data.get('opmerking', ''))
        
        # Load levertijd if available
        if levertijd_entry and klant_data.get('levertijd'):
            levertijd_entry.delete(0, 'end')
            levertijd_entry.insert(0, klant_data.get('levertijd', ''))
            try:
                levertijd_entry.config(fg="black")
            except:
                pass
        
        gevonden_postcode = ""
        for p in postcodes:
            if klant_data.get('postcode_gemeente', '') in p:
                gevonden_postcode = p
                break
        postcode_var.set(gevonden_postcode if gevonden_postcode else postcodes[0])
        
        # Load order items
        bestelregels.extend(bestelregels_data)

