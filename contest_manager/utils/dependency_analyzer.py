#!/usr/bin/env python3
"""
Website Dependency Analyzer
Analyzes websites to discover essential external dependencies using Playwright.
"""

import time
import json
import re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup


class DependencyAnalyzer:
    def __init__(self):
        self.blocked_keywords = [
            # AI and Chatbots
            'openai', 'chatgpt', 'anthropic', 'claude', 'gemini', 'bard',
            # Search Engines
            'google', 'bing', 'yahoo', 'duckduckgo', 'yandex', 'baidu',
            # Social Media
            'facebook', 'twitter', 'instagram', 'linkedin', 'reddit', 'discord',
            'telegram', 'whatsapp', 'tiktok', 'youtube', 'snapchat',
            # Development/Coding
            'github', 'gitlab', 'stackoverflow', 'stackexchange', 'medium',
            'dev.to', 'hackernews', 'codepen', 'jsfiddle',
            # Educational/Tutorial
            'wikipedia', 'w3schools', 'tutorialspoint', 'freecodecamp',
            'coursera', 'udemy', 'khan', 'edx',
            # Shopping/Commerce
            'amazon', 'ebay', 'alibaba', 'shopify',
            # Cloud/Storage
            'dropbox', 'onedrive', 'icloud', 'mega',
            # News/Media
            'cnn', 'bbc', 'reuters', 'news', 'techcrunch'
        ]
        self.essential_keywords = [
            # CDNs and Static Content
            'cdn', 'static', 'assets', 'img', 'css', 'js', 'fonts',
            'cloudflare', 'cloudfront', 'fastly', 'jsdelivr', 'unpkg',
            'bootstrapcdn', 'jquery', 'ajax', 'gstatic',
            'cdnjs', 'netdna', 'akamai', 'edgecast', 'stackpath', 'vercel',
            'fbcdn', 'licdn', 'heap-api', 'ctfassets', 'segment', 'us.heap-api',
            # User feedback additions:
            'addtoany', 'd2-apps', 'cloudflareinsights', 'codechef', 'codeforces', 'hsforms',
            'prod.website-files', 'cloudfront', 'ctfassets', 'heap-api', 'segment', 'uni-nav',
            'maxcdn.bootstrapcdn', 'stx1.spoj', 'img.atcoder', 'static.addtoany', 'jsdelivr',
            'bootstrapcdn', 'jquery', 'ajax.googleapis', 'fonts.gstatic', 'cdnjs', 'static.toph',
            'uploads.toph', 'images.ctfassets', 'cdn.us.heap-api', 'cdn.segment', 'cdn.prod.website-files',
            'cdn.codechef', 'cdn.d2-apps', 'cdn.jsdelivr', 'cdn4.buysellads', 'static.hotjar',
            'static.cloudflareinsights', 'static.xx.fbcdn', 'static.criteo', 'static.lightoj',
            'static.toph', 'visitor.omnitagjs', 'video.fdac31', 'scontent', 'api.vector.co',
            'pro.ip-api', 'js.hsforms', 'js.hs-analytics', 'js.hs-banner', 'js.hs-scripts',
            'js.hsadspixel', 'js.hscollectedforms', 'js.hubspot', 'js.usemessages',
            'tracking-api.g2', 'tracking.g2crowd', 'snap.licdn', 'fonts.googleapis',
            # Security and Auth
            'captcha', 'recaptcha', 'hcaptcha', 'auth', 'oauth',
            'ssl', 'tls', 'cert', 'security',
            # Essential APIs
            'api', 'webhook', 'analytics', 'tracking',
            # Math and Rendering
            'mathjax', 'katex', 'mermaid', 'highlight',
            # Fonts and Icons
            'fontawesome', 'typekit', 'googlefonts',
            # Social/Media/Other
            'fbcdn', 'linkedin', 'licdn', 'heap', 'ctfassets', 'segment', 'snap.licdn',
            'heap-api', 'ctfassets.net', 'us.heap-api.com', 'cdn.segment.com', 'cdn.us.heap-api.com',
            'static.cloudflareinsights', 'static.lightoj', 'static.toph', 'visitor.omnitagjs',
            'video.fdac31', 'scontent', 'img.atcoder', 'static.addtoany', 'cdn.d2-apps',
            'cdn.jsdelivr', 'cdn.codechef', 'fonts.gstatic', 'static.xx.fbcdn', 'static.cdn.admatic',
            'static.cdn.adtarget', 'static.criteo', 'static.hotjar', 'static.lightoj', 'static.toph',
            'static.xx.fbcdn', 'video.fdac31', 'visitor.omnitagjs', 'images.ctfassets',
            # CAPTCHA and challenge domains
            'challenges.cloudflare.com',
        ]

    def extract_domain(self, url):
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove port numbers
            if ':' in domain:
                domain = domain.split(':')[0]
            # Remove www prefix for consistency
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain if domain else None
        except:
            return None

    def filter_dependencies(self, dependencies, whitelist_domains=None):
        """Filter dependencies to keep only essential ones, with improved logic and .org/.com variant support for all contest sites."""
        essential_deps = set()
        whitelist_domains = set(whitelist_domains or [])
        # Automatically add .org/.com variants for all whitelisted domains
        extended_whitelist = set(whitelist_domains)
        for domain in whitelist_domains:
            if domain.endswith('.com'):
                extended_whitelist.add(domain[:-4] + '.org')
            elif domain.endswith('.org'):
                extended_whitelist.add(domain[:-4] + '.com')
        for dep in dependencies:
            dep_l = dep.lower()
            # Always allow if dep is a subdomain of any whitelisted domain (including extended)
            is_first_party = any(dep_l == d or dep_l.endswith('.' + d) for d in extended_whitelist)
            if is_first_party:
                print(f"    ✅ First-party: {dep}")
                essential_deps.add(dep)
                continue
            # Always allow CAPTCHAs and challenge domains
            if any(x in dep_l for x in ['captcha', 'recaptcha', 'hcaptcha', 'challenges.cloudflare.com']):
                print(f"    ✅ CAPTCHA/Challenge: {dep}")
                essential_deps.add(dep)
                continue
            # Include if it matches essential keywords (this takes precedence over blocked)
            is_essential = any(keyword in dep_l for keyword in self.essential_keywords)
            if is_essential:
                print(f"    ✅ Essential keyword: {dep}")
                essential_deps.add(dep)
                continue
            # Skip if it matches blocked keywords (only if not essential)
            is_blocked = any(keyword in dep_l for keyword in self.blocked_keywords)
            if is_blocked:
                print(f"    ⛔ Blocked: {dep}")
                continue
            # Also include CDN patterns and common essential services
            is_cdn = any(pattern in dep_l for pattern in [
                'cdn.', 'static.', 'assets.', 'img.', 'css.', 'js.',
                'fonts.', 'api.', 'auth.', 'ssl.'
            ])
            if is_cdn:
                print(f"    ✅ CDN/Static pattern: {dep}")
                essential_deps.add(dep)
                continue
            # Include common TLD patterns for CDNs
            is_common_cdn = dep.endswith(('.net', '.io')) and any(cdn in dep_l for cdn in [
                'cloudflare', 'fastly', 'amazon', 'microsoft', 'akamai'
            ])
            if is_common_cdn:
                print(f"    ✅ Common CDN: {dep}")
                essential_deps.add(dep)
                continue
            print(f"    ❓ Skipped: {dep}")
        return essential_deps

    def discover_paths_static(self, domain, max_links=10):
        """Discover internal paths using requests+BeautifulSoup (static HTML)."""
        url = f"https://{domain}"
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/') and len(href) > 1:
                    links.add(href.split('?')[0].split('#')[0])
                elif href.startswith(f"https://{domain}"):
                    path = href[len(f"https://{domain}") :].split('?')[0].split('#')[0]
                    if path:
                        links.add('/' + path.lstrip('/'))
            # Limit to max_links to avoid crawling too much
            return sorted(list(links))[:max_links]
        except Exception as e:
            print(f"  ❌ Error discovering paths for {domain}: {e}")
            return []

    def get_default_paths(self, domain):
        """Return a set of default important paths for a contest site. Can be extended externally."""
        # Instead of hardcoding, use a generic set and allow for extension via a config or argument in the future.
        # This can be replaced or extended by reading from a config file or user input.
        generic_paths = ['/contests', '/problems', '/login', '/register', '/home', '/challenges', '/problemset', '/submit']
        # Always include root
        return set(['/'] + generic_paths)

    def analyze_domain_multi(self, domain, whitelist_domains=None, max_links=10):
        """Analyze a domain by crawling multiple important and discovered pages."""
        print(f"🔍 [HYBRID] Analyzing {domain} on multiple pages...")
        all_paths = set(self.get_default_paths(domain))
        # Discover additional paths statically
        discovered = self.discover_paths_static(domain, max_links=max_links)
        all_paths.update(discovered)
        dependencies = set()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for path in all_paths:
                url = f"https://{domain}{path}" if not path.startswith('http') else path
                har_path = f"/tmp/{domain.replace('.', '_')}_{path.strip('/').replace('/', '_') or 'root'}.har"
                print(f"  → Crawling: {url}")
                try:
                    context = browser.new_context(record_har_path=har_path)
                    page = context.new_page()
                    page.goto(url, timeout=20000)
                    page.wait_for_timeout(5000)
                    context.close()
                    # Parse HAR file for domains
                    with open(har_path, 'r') as f:
                        har = json.load(f)
                    for entry in har['log']['entries']:
                        req_url = entry['request']['url']
                        dep_domain = self.extract_domain(req_url)
                        if dep_domain and dep_domain != domain:
                            dependencies.add(dep_domain)
                except Exception as e:
                    print(f"    ❌ Error crawling {url}: {e}")
            browser.close()
        filtered_deps = self.filter_dependencies(dependencies, whitelist_domains=whitelist_domains)
        print(f"  ✅ [HYBRID] Found {len(filtered_deps)} essential dependencies across {len(all_paths)} pages")
        return filtered_deps

    def analyze_domain(self, domain, whitelist_domains=None):
        """Analyze a domain and discover its dependencies using Playwright HAR capture."""
        print(f"🔍 Analyzing {domain}...")
        dependencies = set()
        url = f"https://{domain}"
        har_path = f"/tmp/{domain.replace('.', '_')}.har"
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(record_har_path=har_path)
                page = context.new_page()
                page.goto(url)
                page.wait_for_timeout(5000)
                context.close()
                browser.close()
            # Parse HAR file for domains
            with open(har_path, 'r') as f:
                har = json.load(f)
            for entry in har['log']['entries']:
                req_url = entry['request']['url']
                dep_domain = self.extract_domain(req_url)
                if dep_domain and dep_domain != domain:
                    dependencies.add(dep_domain)
        except Exception as e:
            print(f"  ❌ Error analyzing {domain}: {e}")
        # Filter dependencies
        filtered_deps = self.filter_dependencies(dependencies, whitelist_domains=whitelist_domains)
        print(f"  ✅ Found {len(filtered_deps)} essential dependencies")
        return filtered_deps

    def analyze_site(self, site: str):
        """Analyze a site and return essential dependencies (wrapper for restrict.py compatibility)."""
        return self.analyze_domain(site)
    
    def analyze_domains_from_file(self, whitelist_file):
        """Analyze all domains from a whitelist file using the hybrid approach, and extend whitelist with .org/.com variants."""
        dependencies = set()
        try:
            with open(whitelist_file, 'r') as f:
                domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            # Extend whitelist with .org/.com variants
            extended_domains = set(domains)
            for domain in domains:
                if domain.endswith('.com'):
                    extended_domains.add(domain[:-4] + '.org')
                elif domain.endswith('.org'):
                    extended_domains.add(domain[:-4] + '.com')
            print(f"📋 [HYBRID] Analyzing {len(extended_domains)} domains (including .org/.com variants)...")
            for domain in extended_domains:
                domain_clean = domain.replace('http://', '').replace('https://', '').split('/')[0]
                deps = self.analyze_domain_multi(domain_clean, whitelist_domains=extended_domains)
                dependencies.update(deps)
                time.sleep(2)  # Rate limiting
            print(f"🎯 [HYBRID] Total essential dependencies found: {len(dependencies)}")
            return dependencies
        except FileNotFoundError:
            print(f"❌ Whitelist file not found: {whitelist_file}")
            return set()
        except Exception as e:
            print(f"❌ Error reading whitelist file: {e}")
            return set()


def main():
    """Test the dependency analyzer."""
    analyzer = DependencyAnalyzer()
    
    # Test with a single domain
    test_domain = "codeforces.com"
    deps = analyzer.analyze_domain(test_domain)
    
    print(f"\nDependencies for {test_domain}:")
    for dep in sorted(deps):
        print(f"  • {dep}")


if __name__ == "__main__":
    main()
