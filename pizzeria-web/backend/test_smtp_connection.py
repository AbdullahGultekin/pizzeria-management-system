"""
Test SMTP verbinding voor one.com met verschillende instellingen.
"""
import smtplib
import ssl
import socket

def test_smtp_connection(host, port, use_ssl=False):
    """Test SMTP verbinding."""
    print(f"\n{'='*60}")
    print(f"Testing: {host}:{port} (SSL: {use_ssl})")
    print(f"{'='*60}")
    
    try:
        # Test DNS resolution first
        print(f"1. DNS resolution test...")
        ip = socket.gethostbyname(host)
        print(f"   ✅ {host} resolves to {ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False
    
    try:
        # Test port connectivity
        print(f"2. Port connectivity test...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port {port} is open")
        else:
            print(f"   ❌ Port {port} is closed or filtered")
            return False
    except Exception as e:
        print(f"   ❌ Port test failed: {e}")
        return False
    
    try:
        # Test SMTP connection
        print(f"3. SMTP connection test...")
        if use_ssl or port == 465:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(host, port, timeout=30, context=context)
            print(f"   ✅ Connected via SMTP_SSL")
        else:
            server = smtplib.SMTP(host, port, timeout=30)
            print(f"   ✅ Connected via SMTP")
            if port == 587:
                try:
                    server.starttls()
                    print(f"   ✅ STARTTLS successful")
                except Exception as e:
                    print(f"   ⚠️  STARTTLS failed: {e}")
        
        server.quit()
        print(f"   ✅ SMTP connection successful!")
        return True
        
    except smtplib.SMTPException as e:
        print(f"   ❌ SMTP error: {e}")
        return False
    except socket.timeout:
        print(f"   ❌ Connection timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("One.com SMTP Connection Test")
    print("="*60)
    
    # Test different configurations
    configs = [
        ("mail.one.com", 587, False),  # TLS
        ("mail.one.com", 465, True),   # SSL
        ("mail.one.com", 25, False),   # Plain (usually blocked)
        ("smtp.one.com", 587, False),  # Alternative hostname
    ]
    
    working_configs = []
    
    for host, port, use_ssl in configs:
        if test_smtp_connection(host, port, use_ssl):
            working_configs.append((host, port, use_ssl))
            print(f"\n✅ WORKING CONFIGURATION FOUND!")
            print(f"   Use in .env:")
            print(f"   SMTP_HOST={host}")
            print(f"   SMTP_PORT={port}")
            if port == 465:
                print(f"   SMTP_USE_TLS=false  # Port 465 uses SSL, not TLS")
            else:
                print(f"   SMTP_USE_TLS=true")
    
    if not working_configs:
        print(f"\n❌ No working SMTP configuration found.")
        print(f"\nTroubleshooting:")
        print(f"1. Check if port 587 or 465 is blocked by firewall")
        print(f"2. Check one.com documentation for correct SMTP settings")
        print(f"3. Try connecting from a different network")
        print(f"4. Contact one.com support for SMTP settings")
    else:
        print(f"\n✅ Found {len(working_configs)} working configuration(s)")

