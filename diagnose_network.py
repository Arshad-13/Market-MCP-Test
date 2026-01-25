"""
Network Diagnostics Script for Exchange API Issues

Run this to diagnose why exchange APIs are failing in Claude Desktop.
"""

import sys
import socket
import ssl
import subprocess

def test_dns_resolution():
    """Test if DNS resolution works"""
    print("="*60)
    print("TEST 1: DNS Resolution")
    print("="*60)
    
    hosts = [
        "api.binance.com",
        "api.kraken.com",
        "api.coinbase.com",
        "www.okx.com"
    ]
    
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            print(f"✅ {host} → {ip}")
        except Exception as e:
            print(f"❌ {host} → FAILED: {e}")
    print()


def test_tcp_connection():
    """Test if TCP connections work"""
    print("="*60)
    print("TEST 2: TCP Connection (Port 443 - HTTPS)")
    print("="*60)
    
    hosts = [
        ("api.binance.com", 443),
        ("api.kraken.com", 443),
        ("api.coinbase.com", 443),
    ]
    
    for host, port in hosts:
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            print(f"✅ {host}:{port} → Connected")
        except Exception as e:
            print(f"❌ {host}:{port} → FAILED: {e}")
    print()


def test_ssl_handshake():
    """Test if SSL/TLS handshake works"""
    print("="*60)
    print("TEST 3: SSL/TLS Handshake")
    print("="*60)
    
    hosts = [
        "api.binance.com",
        "api.kraken.com",
    ]
    
    for host in hosts:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    print(f"✅ {host} → SSL OK (Protocol: {ssock.version()})")
        except Exception as e:
            print(f"❌ {host} → SSL FAILED: {e}")
    print()


def test_http_request():
    """Test if HTTP requests work"""
    print("="*60)
    print("TEST 4: HTTP Request (using urllib)")
    print("="*60)
    
    import urllib.request
    
    urls = [
        "https://api.binance.com/api/v3/time",
        "https://api.kraken.com/0/public/Time",
    ]
    
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read()
                print(f"✅ {url} → {response.status} ({len(data)} bytes)")
        except Exception as e:
            print(f"❌ {url} → FAILED: {e}")
    print()


def check_environment():
    """Check environment variables that might affect network"""
    print("="*60)
    print("TEST 5: Environment Variables")
    print("="*60)
    
    import os
    
    env_vars = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "REQUESTS_CA_BUNDLE",
    ]
    
    found_any = False
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"⚠️  {var} = {value}")
            found_any = True
    
    if not found_any:
        print("✅ No proxy/SSL environment variables set")
    print()


def check_python_version():
    """Check Python version and location"""
    print("="*60)
    print("PYTHON INFO")
    print("="*60)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXCHANGE API NETWORK DIAGNOSTICS")
    print("="*60 + "\n")
    
    check_python_version()
    check_environment()
    test_dns_resolution()
    test_tcp_connection()
    test_ssl_handshake()
    test_http_request()
    
    print("="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)
    print("\nNext Steps:")
    print("1. If DNS fails → Check internet connection/DNS settings")
    print("2. If TCP fails → Check firewall/antivirus")
    print("3. If SSL fails → Check SSL certificates/antivirus SSL inspection")
    print("4. If HTTP fails with proxy vars → Disable proxy")
    print("5. If everything passes → Issue is in Claude Desktop subprocess")
