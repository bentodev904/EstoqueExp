#!/bin/bash
# ══════════════════════════════════════════════
# deploy.sh — Instala o backend na VM ARM Oracle
# Rode como: bash deploy.sh
# ══════════════════════════════════════════════
set -e

echo "🧩 Instalando Estoque Clínica..."

# ── 1. Dependências ──
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv git

# ── 2. Cria diretório
sudo mkdir -p /opt/clinica
sudo chown $USER:$USER /opt/clinica
cp main.py requirements.txt /opt/clinica/
cd /opt/clinica

# ── 3. Virtualenv + pacotes ──
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# ── 4. Cria serviço systemd ──
sudo tee /etc/systemd/system/clinica.service > /dev/null <<EOF
[Unit]
Description=Clinica Estoque API
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/clinica
ExecStart=/opt/clinica/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ── 5. Habilita e sobe ──
sudo systemctl daemon-reload
sudo systemctl enable clinica
sudo systemctl start clinica

# ── 6. Libera porta no firewall da VM ──
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
# salva regra (Ubuntu)
sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null 2>&1 || true

echo ""
echo "✅ Backend rodando em http://0.0.0.0:8000"
echo "   Verifique: sudo systemctl status clinica"
echo "   Logs:      sudo journalctl -u clinica -f"
