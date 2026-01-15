#!/usr/bin/env python3
"""
Version Checker Tool
Kullandığınız araçların yeni versiyonlarını kontrol eder.
GitHub API rate limit'e takılmamak için alternatif yöntemler kullanır.
"""

import json
import subprocess
import os
import re
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class ToolInfo:
    """Takip edilecek araç bilgileri"""
    name: str
    check_url: str
    version_pattern: str  # Regex pattern for extracting version
    release_url: str  # URL to show in report
    
# Takip etmek istediğiniz araçları buraya ekleyin
TOOLS = [
    ToolInfo(
        name="Kubernetes",
        check_url="https://dl.k8s.io/release/stable.txt",
        version_pattern=r"(v[\d\.]+)",
        release_url="https://github.com/kubernetes/kubernetes/releases"
    ),
    ToolInfo(
        name="Zabbix",
        check_url="https://www.zabbix.com/download",
        version_pattern=r"Zabbix\s+([\d\.]+)",
        release_url="https://www.zabbix.com/download"
    ),
    ToolInfo(
        name="Graylog",
        check_url="https://go2docs.graylog.org/current/downloading_and_installing_graylog/installing_graylog.htm",
        version_pattern=r"graylog-([\d\.]+)",
        release_url="https://github.com/Graylog2/graylog2-server/releases"
    ),
    ToolInfo(
        name="PostgreSQL",
        check_url="https://www.postgresql.org/ftp/source/",
        version_pattern=r'href="v([\d\.]+)/"',
        release_url="https://www.postgresql.org/docs/release/"
    ),
    ToolInfo(
        name="Jenkins",
        check_url="https://www.jenkins.io/changelog-stable/",
        version_pattern=r'Jenkins ([\d\.]+)',
        release_url="https://www.jenkins.io/changelog-stable/"
    ),
    ToolInfo(
        name="Grafana",
        check_url="https://github.com/grafana/grafana/tags",
        version_pattern=r'v([\d\.]+)',
        release_url="https://github.com/grafana/grafana/releases"
    ),
    ToolInfo(
        name="Kafka",
        check_url="https://github.com/apache/kafka/tags",
        version_pattern=r'([\d\.]+)',
        release_url="https://kafka.apache.org/downloads"
    ),
    ToolInfo(
        name="Redis",
        check_url="https://github.com/redis/redis/tags",
        version_pattern=r'([\d\.]+)',
        release_url="https://github.com/redis/redis/releases"
    ),
    ToolInfo(
        name="Vault",
        check_url="https://github.com/hashicorp/vault/tags",
        version_pattern=r'v([\d\.]+)',
        release_url="https://github.com/hashicorp/vault/releases"
    ),
    ToolInfo(
        name="FortiClient",
        check_url="https://docs.fortinet.com/product/forticlient",
        version_pattern=r'([\d\.]+)',
        release_url="https://www.fortinet.com/support/product-downloads"
    ),
    ToolInfo(
        name="Pinpoint",
        check_url="https://github.com/pinpoint-apm/pinpoint/tags",
        version_pattern=r'v([\d\.]+)',
        release_url="https://github.com/pinpoint-apm/pinpoint/releases"
    ),
    ToolInfo(
        name="MongoDB",
        check_url="https://github.com/mongodb/mongo/tags",
        version_pattern=r'r([\d\.]+)',
        release_url="https://www.mongodb.com/try/download/community"
    ),
]

# Mevcut versiyonlarınızı kaydetmek için dosya
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "versions_state.json")
REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

def fetch_url(url: str) -> str:
    """URL'den içerik çeker"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-H", "User-Agent: VersionChecker/1.0", url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"  ⚠️ Hata: {url} - {e}")
    return ""

def check_kubernetes() -> dict:
    """Kubernetes'in son sürümünü kontrol eder"""
    url = "https://dl.k8s.io/release/stable.txt"
    content = fetch_url(url)
    if content:
        version = content.strip()
        return {
            "version": version,
            "url": f"https://github.com/kubernetes/kubernetes/releases/tag/{version}"
        }
    return {}

def check_github_tags(owner: str, repo: str) -> dict:
    """GitHub tags sayfasından son sürümü kontrol eder (API kullanmadan)"""
    url = f"https://github.com/{owner}/{repo}/tags"
    content = fetch_url(url)
    if content:
        # Tags sayfasından versiyon çıkarma
        pattern = rf'/{owner}/{repo}/releases/tag/(v?[\d\.]+)'
        match = re.search(pattern, content)
        if match:
            version = match.group(1)
            return {
                "version": version,
                "url": f"https://github.com/{owner}/{repo}/releases/tag/{version}"
            }
    return {}

def check_zabbix() -> dict:
    """Zabbix'in son sürümünü kontrol eder"""
    url = "https://www.zabbix.com/download"
    content = fetch_url(url)
    if content:
        match = re.search(r'Zabbix\s+([\d\.]+\s*LTS|[\d\.]+)', content, re.IGNORECASE)
        if match:
            version = match.group(1).strip()
            return {
                "version": version,
                "url": "https://www.zabbix.com/download"
            }
        return check_github_tags("zabbix", "zabbix")
    return {}

def check_graylog() -> dict:
    """Graylog'un son sürümünü kontrol eder"""
    return check_github_tags("Graylog2", "graylog2-server")

def check_postgresql() -> dict:
    """PostgreSQL'in son sürümünü kontrol eder"""
    url = "https://www.postgresql.org/ftp/source/"
    content = fetch_url(url)
    if content:
        match = re.search(r'href="v([\d\.]+)/"', content)
        if match:
            version = match.group(1)
            return {
                "version": version,
                "url": f"https://www.postgresql.org/docs/release/{version}/"
            }
    return check_github_tags("postgres", "postgres")

def check_jenkins() -> dict:
    """Jenkins LTS'in son sürümünü kontrol eder"""
    url = "https://www.jenkins.io/changelog-stable/"
    content = fetch_url(url)
    if content:
        match = re.search(r'(\d+\.\d+\.\d+)', content)
        if match:
            version = match.group(1)
            return {
                "version": version,
                "url": "https://www.jenkins.io/changelog-stable/"
            }
    return check_github_tags("jenkinsci", "jenkins")

def check_grafana() -> dict:
    """Grafana'nın son sürümünü kontrol eder"""
    return check_github_tags("grafana", "grafana")

def check_kafka() -> dict:
    """Apache Kafka'nın son sürümünü kontrol eder"""
    return check_github_tags("apache", "kafka")

def check_redis() -> dict:
    """Redis'in son sürümünü kontrol eder"""
    return check_github_tags("redis", "redis")

def check_vault() -> dict:
    """HashiCorp Vault'un son sürümünü kontrol eder"""
    return check_github_tags("hashicorp", "vault")

def check_forticlient() -> dict:
    """FortiClient'ın son sürümünü kontrol eder"""
    url = "https://docs.fortinet.com/product/forticlient"
    content = fetch_url(url)
    if content:
        versions = re.findall(r'forticlient/([\d]+\.[\d]+(?:\.[\d]+)?)', content)
        if versions:
            valid_versions = [v for v in versions if v and all(p.isdigit() for p in v.split('.'))]
            if valid_versions:
                latest = max(valid_versions, key=lambda v: [int(x) for x in v.split('.')])
                return {
                    "version": latest,
                    "url": "https://www.fortinet.com/support/product-downloads"
                }
    return {}

def check_pinpoint() -> dict:
    """Pinpoint APM'in son sürümünü kontrol eder"""
    return check_github_tags("pinpoint-apm", "pinpoint")

def check_mongodb() -> dict:
    """MongoDB'nin son sürümünü kontrol eder"""
    # MongoDB r prefix kullanıyor (r8.0.0 gibi)
    url = "https://github.com/mongodb/mongo/tags"
    content = fetch_url(url)
    if content:
        match = re.search(r'/mongodb/mongo/releases/tag/r([\d\.]+)', content)
        if match:
            version = match.group(1)
            return {
                "version": version,
                "url": "https://www.mongodb.com/try/download/community"
            }
    return {}

# Tool kontrol fonksiyonları
CHECKERS = {
    "Kubernetes": check_kubernetes,
    "Zabbix": check_zabbix,
    "Graylog": check_graylog,
    "PostgreSQL": check_postgresql,
    "Jenkins": check_jenkins,
    "Grafana": check_grafana,
    "Kafka": check_kafka,
    "Redis": check_redis,
    "Vault": check_vault,
    "FortiClient": check_forticlient,
    "Pinpoint": check_pinpoint,
    "MongoDB": check_mongodb,
}

def load_state() -> dict:
    """Kaydedilmiş sürüm durumunu yükler"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state: dict):
    """Sürüm durumunu kaydeder"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_versions():
    """Tüm araçların versiyonlarını kontrol eder"""
    state = load_state()
    results = []
    new_state = {}
    
    print("\n" + "="*60)
    print(f"🔍 Version Checker - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    for name, checker in CHECKERS.items():
        print(f"Kontrol ediliyor: {name}...")
        release = checker()
        
        if release and release.get("version"):
            latest_version = release.get("version")
            previous_version = state.get(name, {}).get("version", None)
            
            is_new = previous_version and previous_version != latest_version
            
            result = {
                "name": name,
                "latest_version": latest_version,
                "previous_version": previous_version,
                "is_new": is_new,
                "url": release.get("url", ""),
            }
            results.append(result)
            
            new_state[name] = {
                "version": latest_version,
                "checked_at": datetime.now().isoformat(),
            }
        else:
            results.append({
                "name": name,
                "error": "Bilgi alınamadı"
            })
    
    # Raporu yazdır
    print("\n" + "-"*60)
    print("📋 RAPOR")
    print("-"*60 + "\n")
    
    new_updates = []
    for r in results:
        if "error" in r:
            print(f"❌ {r['name']}: {r['error']}")
        else:
            status = "🆕 YENİ!" if r["is_new"] else "✅"
            print(f"{status} {r['name']}: {r['latest_version']}")
            print(f"   🔗 {r['url']}")
            if r["previous_version"]:
                print(f"   📌 Önceki: {r['previous_version']}")
            if r["is_new"]:
                new_updates.append(r)
            print()
    
    # Özet
    print("-"*60)
    if new_updates:
        print(f"\n🎉 {len(new_updates)} yeni güncelleme bulundu!")
        for u in new_updates:
            print(f"   • {u['name']}: {u['previous_version']} → {u['latest_version']}")
    else:
        print("\n✨ Tüm araçlar güncel!")
    
    # State'i kaydet
    save_state(new_state)
    
    # Raporu dosyaya kaydet
    save_report(results)
    
    return results

def save_report(results: list):
    """Raporu dosyaya kaydeder"""
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_file = os.path.join(REPORT_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(report_file, "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"\n📁 Rapor kaydedildi: {report_file}")

if __name__ == "__main__":
    check_versions()
