#!/bin/sh
# Gera um certificado autoassinado para HTTPS em desenvolvimento local.
# Em produção, troca por um certificado real (ex.: Let's Encrypt via certbot)
# apontado em nginx/nginx.conf.
#
# Uso: sh scripts/generate-dev-cert.sh

set -e
DIR="$(dirname "$0")/../nginx/certs"
mkdir -p "$DIR"

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$DIR/privkey.pem" \
  -out "$DIR/fullchain.pem" \
  -subj "/CN=localhost"

echo "Certificado de desenvolvimento gerado em $DIR"
echo "Nunca envies estes ficheiros para o git (já estão no .gitignore)."
