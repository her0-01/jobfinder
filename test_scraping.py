import sys
sys.path.append('job_scraper')

from scrapers.adaptive_scraper import AdaptiveScraper

# Test scraping avec "Data Engineer Alternance France"
scraper = AdaptiveScraper(headless=True)

keywords = "Data Engineer Alternance"
location = "France"
contract_type = "Alternance"

print(f"🔍 Test scraping: {keywords} - {location} - {contract_type}\n")

# Tester TotalEnergies
print("=" * 50)
print("TEST: TotalEnergies")
print("=" * 50)

jobs = scraper.scrape_totalenergies(keywords, location, contract_type)

print(f"\n✅ {len(jobs)} offres trouvées:\n")

for i, job in enumerate(jobs[:10], 1):  # Afficher les 10 premières
    print(f"{i}. {job['title']}")
    print(f"   Entreprise: {job['company']}")
    print(f"   Localisation: {job['location']}")
    print(f"   Lien: {job['link'][:80]}...")
    print()

scraper.close()

print("\n" + "=" * 50)
print("ANALYSE:")
print("=" * 50)
print(f"Recherche: '{keywords}'")
print(f"Offres retournées: {len(jobs)}")
print("\nProblème identifié:")
print("- Les sites carrières retournent TOUTES les alternances")
print("- Pas de filtrage par mots-clés 'Data Engineer'")
print("- Le scraper récupère tout sans filtrer")
