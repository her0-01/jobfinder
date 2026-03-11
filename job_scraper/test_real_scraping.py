"""Test scraping reel avec Playwright"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("TEST SCRAPING REEL PLAYWRIGHT")
print("="*60)

# Test Indeed
print("\n[1/3] Test Indeed Playwright...")
try:
    from scrapers.playwright_scrapers.indeed import scrape_indeed_async
    
    print("  Scraping Indeed (10-15s)...")
    jobs = asyncio.run(scrape_indeed_async("python", "Paris"))
    
    if len(jobs) > 0:
        print(f"  OK - {len(jobs)} offres trouvees")
        print(f"  Exemple: {jobs[0]['title'][:60]}")
    else:
        print("  ATTENTION - 0 offres (Cloudflare?)")
except Exception as e:
    print(f"  ERREUR: {e}")

# Test LinkedIn
print("\n[2/3] Test LinkedIn Playwright...")
try:
    from scrapers.playwright_scrapers.linkedin import scrape_linkedin_async
    
    print("  Scraping LinkedIn (10-15s)...")
    jobs = asyncio.run(scrape_linkedin_async("python", "Paris"))
    
    if len(jobs) > 0:
        print(f"  OK - {len(jobs)} offres trouvees")
        print(f"  Exemple: {jobs[0]['title'][:60]}")
    else:
        print("  ATTENTION - 0 offres")
except Exception as e:
    print(f"  ERREUR: {e}")

# Test Orchestrateur complet
print("\n[3/3] Test Orchestrateur Auto-Apprenant...")
try:
    from orchestrator.auto_learning import AutoLearningOrchestrator
    
    print("  Scraping 23 sites en parallele (20-30s)...")
    orchestrator = AutoLearningOrchestrator()
    jobs = orchestrator.sync_search("python", "Paris")
    
    if len(jobs) > 0:
        print(f"  OK - {len(jobs)} offres trouvees")
        
        # Compter par source
        sources = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("\n  Top 5 sources:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {source}: {count} offres")
    else:
        print("  ATTENTION - 0 offres")
except Exception as e:
    print(f"  ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST TERMINE")
print("="*60)
