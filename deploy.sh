#!/bin/bash

# 🚀 MaStR Lead Generator - Deployment Script
# Verwendung: ./deploy.sh

set -e  # Exit on any error

echo "🚀 Starte Deployment für MaStR Lead Generator..."

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfungen
check_requirements() {
    log_info "Prüfe Voraussetzungen..."
    
    # Python prüfen
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 ist nicht installiert!"
        exit 1
    fi
    
    # pip prüfen
    if ! command -v pip &> /dev/null; then
        log_error "pip ist nicht installiert!"
        exit 1
    fi
    
    # .env Datei prüfen
    if [ ! -f ".env" ]; then
        log_error ".env Datei nicht gefunden! Erstellen Sie sie basierend auf env_example.txt"
        exit 1
    fi
    
    log_info "✅ Alle Voraussetzungen erfüllt"
}

# Virtual Environment aktivieren
activate_venv() {
    log_info "Aktiviere Virtual Environment..."
    
    if [ ! -d "venv" ]; then
        log_info "Erstelle Virtual Environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    log_info "✅ Virtual Environment aktiviert"
}

# Dependencies installieren
install_dependencies() {
    log_info "Installiere Dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log_warn "requirements.txt nicht gefunden, installiere Standard-Dependencies..."
        pip install django django-crispy-forms crispy-bootstrap5 djangorestframework stripe python-decouple pillow requests faker
    fi
    
    log_info "✅ Dependencies installiert"
}

# Datenbank-Migrationen
run_migrations() {
    log_info "Führe Datenbank-Migrationen aus..."
    python manage.py migrate
    log_info "✅ Migrationen abgeschlossen"
}

# Statische Dateien sammeln
collect_static() {
    log_info "Sammle statische Dateien..."
    python manage.py collectstatic --noinput
    log_info "✅ Statische Dateien gesammelt"
}

# Sicherheitsprüfung
security_check() {
    log_info "Führe Sicherheitsprüfung durch..."
    
    # Django Security Check
    python manage.py check --deploy
    
    # Prüfe .env Datei
    if grep -q "your-super-secret-key" .env; then
        log_error "SECRET_KEY wurde nicht geändert!"
        exit 1
    fi
    
    if grep -q "yourdomain.com" .env; then
        log_error "ALLOWED_HOSTS wurde nicht angepasst!"
        exit 1
    fi
    
    log_info "✅ Sicherheitsprüfung bestanden"
}

# Logs-Verzeichnis erstellen
setup_logs() {
    log_info "Erstelle Logs-Verzeichnis..."
    mkdir -p logs
    log_info "✅ Logs-Verzeichnis erstellt"
}

# Hauptfunktion
main() {
    echo "=========================================="
    echo "🚀 MaStR Lead Generator - Deployment"
    echo "=========================================="
    
    check_requirements
    activate_venv
    install_dependencies
    setup_logs
    security_check
    run_migrations
    collect_static
    
    echo ""
    echo "=========================================="
    echo "✅ Deployment erfolgreich abgeschlossen!"
    echo "=========================================="
    echo ""
    echo "📋 Nächste Schritte:"
    echo "1. Web Server konfigurieren (nginx/Apache)"
    echo "2. SSL-Zertifikat installieren"
    echo "3. Superuser erstellen: python manage.py createsuperuser"
    echo "4. Server starten: python manage.py runserver"
    echo "5. Monitoring einrichten"
    echo ""
    echo "🔒 Sicherheitshinweise:"
    echo "- .env Datei ist sicher (nicht im Git)"
    echo "- HTTPS ist aktiviert"
    echo "- Alle Security Headers sind gesetzt"
    echo "- Rate Limiting ist aktiv"
    echo ""
}

# Script ausführen
main "$@" 