#!/usr/bin/env bash
# Smoke test APIYI — diagnostique auth + choix client OpenAI vs Anthropic
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Charge ~/.hermes/.env puis .env local (le local ÉCRASE Hermes)
load_env() {
  local f
  for f in "$HOME/.hermes/.env" "$ROOT/.env"; do
    if [[ -f "$f" ]]; then
      set -a
      # shellcheck disable=SC1090
      source "$f"
      set +a
    fi
  done
}

load_env

KEY="${APIYI_API_KEY:-${OPENAI_API_KEY:-}}"
KEY="$(printf '%s' "$KEY" | tr -d '[:space:]')"

if [[ -z "$KEY" ]]; then
  echo "Définir APIYI_API_KEY dans salvador-personas/.env ou ~/.hermes/.env" >&2
  exit 1
fi

echo "Clé chargée (longueur=${#KEY}, préfixe=${KEY:0:7}…)"

MODEL="${LLM_MODEL:-gpt-4.1-mini}"
URL="https://api.apiyi.com/v1/chat/completions"

echo "Test OpenAI-compat → $URL (model=$MODEL)"

HTTP=$(curl -s -o /tmp/sv_smoke.json -w "%{http_code}" \
  "$URL" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":10}")

MSG=$(python3 -c "import json; d=json.load(open('/tmp/sv_smoke.json')); print(d.get('error',{}).get('message',''))" 2>/dev/null || head -c 200 /tmp/sv_smoke.json)

echo "HTTP $HTTP — $MSG"

if [[ "$HTTP" == "200" ]]; then
  echo "OK — utiliser OpenAICompatClient"
  echo "  OPENAI_API_KEY=<ta clé APIYI>"
  echo "  OPENAI_BASE_URL=https://api.apiyi.com/v1"
  echo "  LLM_MODEL=$MODEL"
  exit 0
fi

# Erreurs auth / quota → pas un problème de format client
if echo "$MSG" | grep -q "额度已用尽"; then
  echo ""
  echo "→ Quota épuisé sur CE token. Recharge le compte APIYI puis :"
  echo "  1. Copie le [Default Token] sur https://api.apiyi.com/token (bouton Copy)"
  echo "  2. Mets-le dans salvador-personas/.env : APIYI_API_KEY=sk-..."
  echo "  3. Relance ce script"
  exit 2
fi

if echo "$MSG" | grep -q "无效的令牌"; then
  echo ""
  echo "→ Token invalide (pas reconnu par APIYI). Vérifie :"
  echo "  • Copie depuis https://api.apiyi.com/token (bouton Copy, pas de retour ligne)"
  echo "  • Pas d'espace / coupure de ligne dans export ou .env"
  echo "  • Token créé sur le même compte que la recharge"
  echo "  • longueur typique ~48–52 caractères (actuelle: ${#KEY})"
  exit 3
fi

# Autres échecs : tenter interprétation Anthropic seulement si erreur ≠ auth
echo ""
echo "OpenAI path échoué pour une autre raison — test Anthropic-compat optionnel…"
HTTP2=$(curl -s -o /tmp/sv_smoke2.json -w "%{http_code}" \
  "https://api.apiyi.com/v1/messages" \
  -H "x-api-key: $KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"max_tokens\":10,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}")

MSG2=$(python3 -c "import json; d=json.load(open('/tmp/sv_smoke2.json')); print(d.get('error',{}).get('message', d.get('message','')))" 2>/dev/null || head -c 200 /tmp/sv_smoke2.json)
echo "Anthropic path → HTTP $HTTP2 — $MSG2"

if [[ "$HTTP2" == "200" ]]; then
  echo "OK — utiliser AnthropicCompatClient"
  echo "  ANTHROPIC_API_KEY=<ta clé APIYI>"
  echo "  ANTHROPIC_BASE_URL=https://api.apiyi.com"
  echo "  LLM_MODEL=$MODEL"
  exit 0
fi

cat /tmp/sv_smoke.json 2>/dev/null || true
exit 1
