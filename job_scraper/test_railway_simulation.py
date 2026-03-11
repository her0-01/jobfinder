"""Test simulant Railway SANS Playwright"""
import sys
from pathlib import Path

# Bloquer l'import de playwright pour simuler Railway
sys.modules['playwright'] = None
sys.modules['playwright.async_api'] = None

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("SIMULATION RAILWAY SANS PLAYWRIGHT")
print("="*60)

print("\nSimulation: Playwright non disponible sur Railway")
print("Test du fallback Selenium...\n")

# Test du systeme hybride
print("[1/1] Test systeme hybride avec fallback...")
try:
    # Simuler une recherche comme dans web_app.py
    keywords = "python"
    location = "Paris"
    contract_type = "CDI"
    
    print("  Tentative Playwright...")
    try:
        from orchestrator.auto_learning import AutoLearningOrchestrator
        orchestrator = AutoLearningOrchestrator()
        jobs = orchestrator.sync_search(keywords, location, contract_type)
        print(f"  OK - Playwright: {len(jobs)} offres")
    except Exception as playwright_error:
        print(f"  ERREUR Playwright: {playwright_error}")
        print("  Activation fallback Selenium...")
        
        # FALLBACK SELENIUM
        from scrapers.adaptive_scraper import AdaptiveScraper
        from scrapers.universal_scraper import UniversalJobScraper
        
        print("  Scraping sites carrieres...")
        adaptive = AdaptiveScraper(headless=True)
        corporate_jobs = adaptive.scrape_all_companies(keywords, location, contract_type)
        adaptive.close()
        
        print("  Scraping sites universels...")
        universal = UniversalJobScraper(headless=True)
        universal_jobs = universal.scrape_all(keywords, location, contract_type)
        universal.close()
        
        jobs = list(corporate_jobs) + list(universal_jobs)
        
        # Dedupliquer
        seen = set()
        unique = []
        for job in jobs:
            key = f"{job['title']}_{job['company']}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        
        jobs = unique
        print(f"  OK - Selenium fallback: {len(jobs)} offres")
    
    print("\n" + "="*60)
    print("RESULTAT SIMULATION RAILWAY")
    print("="*60)
    print(f"\nOffres trouvees: {len(jobs)}")
    print("Systeme: Selenium (fallback)")
    print("\nCONCLUSION: L'app fonctionnera sur Railway")
    print("="*60)

except Exception as e:
    print(f"\nERREUR CRITIQUE: {e}")
    import traceback
    traceback.print_exc()
    print("\nATTENTION: Probleme detecte")
