# Nemotron Personas — Carte El Salvador

Carte interactive des 148 000 personas Nemotron, géolocalisées dans les polygones municipaux (geoBoundaries).

## Build

```bash
# Depuis la racine du repo
uv run sv-build-map

cd apps/map
npm install
npm run dev    # dev : tunnel SSH → localhost:5173
npm run build  # dist/ statique (~2,3 Mo data + JS)
```

## Déploiement statique

Le build Vite produit un site 100 % statique dans `dist/` (HTML + JS + `dist/data/*.bin`).

### Preview sur le VPS

```bash
# Depuis la racine
chmod +x scripts/serve_map.sh
./scripts/serve_map.sh          # build + preview sur :4173
# ou
cd apps/map && npm run preview:host
```

Depuis ton Mac (tunnel SSH, sans ouvrir de port public) :

```bash
ssh -L 4173:localhost:4173 guillaume@<vps>
# puis http://localhost:4173/
```

### Nginx (production)

Servir le dossier `apps/map/dist` :

```nginx
server {
    listen 80;
    server_name map.example.com;
    root /home/guillaume/salvador-personas/apps/map/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /data/ {
        add_header Cache-Control "public, max-age=86400";
    }
}
```

Re-build après mise à jour des personas : `uv run sv-build-map && cd apps/map && npm run build`.

## Attribution (CC BY 4.0)

- **Personas** : [NVIDIA / WideLabs — Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador)
- **Frontières administratives** : [geoBoundaries](https://www.geoboundaries.org) (William & Mary)
