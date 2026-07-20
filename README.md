# Gestion de Vente

Boutique en ligne Django avec deux espaces :

- `client` : accueil, catalogue par categories, detail produit, panier dynamique, commande et page a propos.
- `admin` : connexion Django Admin, gestion des produits, categories, configuration du site et suivi des commandes.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_store
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8010
```

## Administration

- URL admin : `http://127.0.0.1:8010/admin/`
- Gestion de la vitrine : `Configuration du site`
- Gestion du catalogue : `Categories` et `Produits`
- Gestion des ventes : `Commandes`
