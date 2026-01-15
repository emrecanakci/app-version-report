# Version Checker Tool

Kullandığınız araçların (Kubernetes, Zabbix, Graylog vb.) yeni versiyonlarını otomatik olarak kontrol eden araç.

## 🚀 Hızlı Başlangıç

```bash
# Manuel çalıştırma
python3 version_checker.py

# Cron job kurulumu (her gün sabah 08:00)
chmod +x setup_cron.sh
./setup_cron.sh
```

## 📁 Dosya Yapısı

```
versionTool/
├── version_checker.py   # Ana script
├── setup_cron.sh        # Cron job kurulum scripti
├── versions_state.json  # Kaydedilen sürümler (otomatik oluşur)
├── reports/             # Günlük raporlar (otomatik oluşur)
└── logs/                # Cron log dosyaları
```

## ➕ Yeni Araç Ekleme

`version_checker.py` dosyasında `CHECKERS` sözlüğüne yeni bir checker fonksiyonu ekleyin:

```python
def check_myTool() -> dict:
    # GitHub tags sayfasından kontrol
    return check_github_tags("owner", "repo")
    
CHECKERS["MyTool"] = check_myTool
```

## 📧 E-posta Bildirimi (Opsiyonel)

Sistemde `mail` komutu kuruluysa, cron job'a e-posta ekleyebilirsiniz:

```bash
# crontab -e ile düzenleyin:
MAILTO="sizin@email.com"
0 8 * * * /usr/bin/python3 /path/to/version_checker.py
```
# app-version-report
