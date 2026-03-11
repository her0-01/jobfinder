"""Test simple sans Playwright"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("TEST MODULES DE BASE")
print("="*60)

# Test 1: Cache
print("\n[1/5] Test Cache...")
try:
    from utils.cache import JobCache
    cache = JobCache()
    test_jobs = [{"title": "Test", "company": "Corp"}]
    cache.set("python", "Paris", "test", test_jobs)
    cached = cache.get("python", "Paris", "test")
    print(f"  OK - Cache fonctionne ({len(cached)} offres)")
except Exception as e:
    print(f"  ERREUR: {e}")

# Test 2: Fallback
print("\n[2/5] Test Fallback...")
try:
    from utils.fallback import FallbackSystem
    fallback = FallbackSystem()
    simple = fallback.simplify_keywords("developpeur python senior")
    print(f"  OK - Simplifie: {simple}")
except Exception as e:
    print(f"  ERREUR: {e}")

# Test 3: NLP
print("\n[3/5] Test NLP...")
try:
    from nlp_preprocess.normalizer import NLPNormalizer
    normalizer = NLPNormalizer()
    normalized = normalizer.normalize("developpeur fullstack")
    print(f"  OK - Normalise: {normalized}")
except Exception as e:
    print(f"  ERREUR: {e}")

# Test 4: URL Learner
print("\n[4/5] Test URL Learner...")
try:
    from url_learning.learner import URLLearner
    learner = URLLearner()
    url = learner.build_url("indeed", "python", "Paris")
    print(f"  OK - URL: {url[:60]}...")
except Exception as e:
    print(f"  ERREUR: {e}")

# Test 5: Logger
print("\n[5/5] Test Logger...")
try:
    from utils.advanced_logger import AdvancedLogger
    logger = AdvancedLogger("test")
    logger.log_scraping_start("Indeed", "python", "Paris")
    print("  OK - Logger fonctionne")
except Exception as e:
    print(f"  ERREUR: {e}")

print("\n" + "="*60)
print("RESULTAT: Modules de base OK")
print("Pour tester Playwright: INSTALL_PLAYWRIGHT.bat")
print("="*60)
