"""Test du systeme hybride"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("TEST SYSTEME HYBRIDE")
print("="*60)

# Test 1: Playwright disponible ?
print("\n[1/2] Test Playwright...")
try:
    import playwright
    print("  OK - Playwright installe")
    PLAYWRIGHT_OK = True
except:
    print("  INFO - Playwright non installe (fallback Selenium actif)")
    PLAYWRIGHT_OK = False

# Test 2: Selenium disponible ?
print("\n[2/2] Test Selenium...")
try:
    import selenium
    print("  OK - Selenium installe")
    SELENIUM_OK = True
except:
    print("  ERREUR - Selenium non installe")
    SELENIUM_OK = False

# Resultat
print("\n" + "="*60)
print("RESULTAT")
print("="*60)

if PLAYWRIGHT_OK:
    print("\nSysteme ULTRA-RAPIDE actif (Playwright)")
    print("Temps de scraping: 15-20 secondes")
elif SELENIUM_OK:
    print("\nSysteme STANDARD actif (Selenium)")
    print("Temps de scraping: 1-2 minutes")
else:
    print("\nERREUR: Aucun systeme disponible")

print("\nL'application s'adaptera automatiquement.")
print("="*60)
