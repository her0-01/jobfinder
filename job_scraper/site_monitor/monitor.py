"""Détection des changements HTML et auto-régénération"""
import asyncio
from playwright.async_api import async_playwright
import hashlib
import json
from pathlib import Path

class SiteMonitor:
    def __init__(self):
        self.snapshots_file = Path("site_snapshots.json")
        self.snapshots = self._load_snapshots()
    
    def _load_snapshots(self):
        if self.snapshots_file.exists():
            with open(self.snapshots_file, "r") as f:
                return json.load(f)
        return {}
    
    async def check_changes(self, site_name, site_url):
        """Vérifie si le HTML a changé"""
        current_hash = await self._get_html_hash(site_url)
        previous_hash = self.snapshots.get(site_name)
        
        if previous_hash != current_hash:
            self.snapshots[site_name] = current_hash
            self._save_snapshots()
            return True
        
        return False
    
    async def _get_html_hash(self, url):
        """Récupère le hash du HTML"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=10000)
                await page.wait_for_timeout(2000)
                html = await page.content()
                await browser.close()
                return hashlib.md5(html.encode()).hexdigest()
            except:
                await browser.close()
                return ""
    
    def _save_snapshots(self):
        with open(self.snapshots_file, "w") as f:
            json.dump(self.snapshots, f, indent=2)
    
    async def auto_regenerate(self, site_name, site_url):
        """Régénère automatiquement le scraper si changement détecté"""
        from scraper_generator.generate import ScraperGenerator
        
        if await self.check_changes(site_name, site_url):
            print(f"🔄 Changement détecté sur {site_name}, régénération...")
            generator = ScraperGenerator()
            await generator.generate(site_url, site_name)
            print(f"✅ Scraper {site_name} régénéré")
