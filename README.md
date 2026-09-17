# Strasbulles — Alsace Bande Dessinée

Refonte Django/Wagtail du site de l’association Alsace Bande Dessinée. Le site présente le festival Strasbulles, les événements, artistes, chroniques et archives. Toute l’interface publique et le CMS sont configurés en français.

## Architecture

- Python 3.12, Django 5.2 LTS et Wagtail 7.4 LTS ;
- rendu serveur avec templates Django, Tailwind CSS 4 et un JavaScript minimal pour le menu mobile ;
- PostgreSQL 17 en développement et production ;
- Gunicorn derrière Caddy en production ;
- Mailpit en développement ;
- pytest-django et Ruff pour la qualité.

Les versions sont épinglées dans `requirements.txt`, `requirements-dev.txt`, `package.json` et les fichiers Compose. Django 5.2 LTS a été préféré à une version fonctionnelle plus récente pour sa maintenance de sécurité jusqu’en 2028 ; Wagtail 7.4 LTS la prend officiellement en charge.

## Démarrage local

Prérequis : Docker récent avec le plugin Compose, Git et environ 2 Go d’espace libre.

```bash
cp .env.example .env
docker compose up --build
```

Dans un autre terminal :

```bash
docker compose exec web python manage.py seed_content
docker compose exec web python manage.py setup_staff_groups
docker compose exec web python manage.py create_initial_admin
```

Renseignez auparavant les trois variables `DJANGO_SUPERUSER_*` dans `.env`. Le chargement initial est idempotent : il peut être relancé sans créer de doublons.

Services locaux :

- site : <http://localhost:8000/> ;
- CMS Wagtail : <http://localhost:8000/cms/> ;
- Mailpit : <http://localhost:8025/> ;
- contrôle de santé : <http://localhost:8000/health/>.

L’entrée du conteneur applique les migrations et collecte les fichiers statiques. Pour les lancer manuellement :

```bash
make migrate
make collectstatic
```

## Commandes courantes

```bash
make up             # construire et démarrer
make down           # arrêter
make logs           # suivre les journaux web
make seed           # charger le contenu initial
make groups         # créer les groupes du CMS
make superuser      # créer le premier administrateur depuis .env
make test           # lancer les tests
make lint           # Ruff (lint et format)
make check          # contrôles Django
make backup         # sauvegarder base et médias dans backups/
make restore        # restaurer ces deux archives
```

Après une modification des classes de modèle :

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Après une modification de `static_src/site.css`, reconstruisez Tailwind :

```bash
make css
```

Le service `assets` surveille aussi Tailwind pendant `docker compose up`. Aucun Node local n’est nécessaire.

## Variables d’environnement

`.env.example` documente toutes les clés. En production, les plus importantes sont `DJANGO_SECRET_KEY`, `DOMAIN`, `POSTGRES_*`, `CONTACT_RECIPIENT` et les variables SMTP. Ne commitez jamais `.env`.

`SECURE_HSTS_SECONDS` reste à `0` lors de la première mise en ligne. Après validation complète de HTTPS, passez progressivement à `31536000`. Le destinataire du formulaire n’apparaît jamais dans les templates.

## Gestion éditoriale

Les événements et chroniques possèdent brouillons, prévisualisations, révisions et publication planifiée grâce à Wagtail. Les événements passés basculent automatiquement dans les archives. Les images acceptent un point focal et chaque champ principal rappelle le besoin d’un texte alternatif.

Les groupes créés sont :

- **Administrateurs** : tous les réglages et contenus du CMS ;
- **Rédacteurs** : ajout/modification/lecture sans publication ;
- **Éditeurs** : révision et publication, sans suppression globale.

Après création des groupes, un administrateur doit définir dans Wagtail les périmètres de pages de chaque équipe si certaines rubriques doivent être isolées. Voir [Gestion des contenus](docs/content-management.md).

## Statique et médias

Tailwind génère `static/css/site.css`. WhiteNoise sert les fichiers statiques versionnés ; Caddy sert directement `/static/` et `/media/` en production. Les médias et la base résident dans des volumes nommés, hors du dépôt Git.

Les documents sont limités aux formats PDF et bureautiques usuels. La taille maximale d’une requête est de 20 Mio par défaut et Caddy refuse les corps supérieurs à 25 Mo.

## Tests et intégration continue

```bash
make test
make lint
make check
```

GitHub Actions reproduit le lint, les contrôles, les tests et construit la cible Docker de production pour chaque push et pull request. Il ne déploie rien.

## Déploiement et sauvegardes

Consultez [Déploiement sur IONOS](docs/deployment-ionos.md) et [Sauvegarde/restauration](docs/backup-restore.md). Résumé : créer un VPS Ubuntu, pointer le DNS, cloner le dépôt, remplir `.env`, puis lancer `docker compose -f docker-compose.prod.yml up -d --build`.

## Dépannage

- **PostgreSQL pas prêt** : `docker compose logs db`, puis attendez l’état `healthy`.
- **Erreur CSRF** : vérifiez `DOMAIN` et `CSRF_TRUSTED_ORIGINS` avec le schéma `https://`.
- **CSS absent** : reconstruisez l’image ou exécutez `npm run css:build` sur l’hôte.
- **Courriel absent** : en local, ouvrez Mailpit ; en production, vérifiez les variables SMTP et les journaux.
- **Médias non affichés** : vérifiez les volumes et les droits du processus non-root.

L’inventaire de migration se trouve dans [docs/content_inventory.md](docs/content_inventory.md). Les coordonnées, dates, tarifs, biographies, affiches, partenaires et autorisations d’images marqués « à confirmer » doivent être validés avant le lancement.
