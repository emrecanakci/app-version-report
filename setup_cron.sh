#!/bin/bash
# Cron Job Setup Script
# Bu script version_checker.py'yi her gün sabah 08:00'de çalıştırmak için cron job ekler

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/version_checker.py"
LOG_FILE="$SCRIPT_DIR/logs/cron.log"

# Log dizinini oluştur
mkdir -p "$SCRIPT_DIR/logs"

# Mevcut crontab'ı al
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

# Version checker için satır
CRON_LINE="0 8 * * * /usr/bin/python3 $PYTHON_SCRIPT >> $LOG_FILE 2>&1"

# Eğer zaten ekliyse ekleme
if echo "$CURRENT_CRON" | grep -q "version_checker.py"; then
    echo "⚠️  Cron job zaten mevcut!"
    echo "Mevcut cron jobs:"
    crontab -l | grep "version_checker"
else
    # Yeni cron job ekle
    (echo "$CURRENT_CRON"; echo "$CRON_LINE") | crontab -
    echo "✅ Cron job başarıyla eklendi!"
    echo "📅 Her gün sabah 08:00'de çalışacak"
    echo "📁 Log dosyası: $LOG_FILE"
fi

echo ""
echo "Cron job'ı kaldırmak için:"
echo "  crontab -e  # ve ilgili satırı silin"
echo ""
echo "Manuel test için:"
echo "  python3 $PYTHON_SCRIPT"
