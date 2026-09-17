# Déploiement sur un VPS IONOS

Ce guide vise un VPS Ubuntu avec accès SSH ; un hébergement mutualisé classique ne convient pas à cette pile Docker.

## 1. Préparer le VPS et le DNS

Choisissez au minimum 2 vCPU, 2 Go de RAM et un volume sauvegardé. Dans la zone DNS du domaine, créez un enregistrement A vers l’IPv4 du VPS et, si disponible, un AAAA vers son IPv6. Attendez la propagation avant de demander le certificat.

Créez un utilisateur d’administration non-root avec clé SSH, désactivez l’authentification SSH par mot de passe après validation de la clé, mettez Ubuntu à jour et activez le pare-feu pour SSH, HTTP 80 et HTTPS 443 seulement. Adaptez le port SSH avant toute règle restrictive pour éviter de perdre l’accès.

Installez Docker Engine et le plugin Docker Compose en suivant exclusivement la documentation officielle Docker pour Ubuntu. Vérifiez :

```bash
docker --version
docker compose version
```

## 2. Installer l’application

```bash
git clone URL_DU_DEPOT strasbulles
cd strasbulles
cp .env.example .env
chmod 600 .env
```

Dans `.env`, créez des secrets aléatoires et renseignez le domaine sans protocole, PostgreSQL, SMTP, l’expéditeur et le destinataire du formulaire. Mettez `DEBUG=0`, `EMAIL_USE_TLS=1` et laissez d’abord `SECURE_HSTS_SECONDS=0`.

```bash
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py seed_content
docker compose -f docker-compose.prod.yml exec web python manage.py setup_staff_groups
docker compose -f docker-compose.prod.yml exec web python manage.py create_initial_admin
```

Les deux premières commandes Django sont aussi exécutées automatiquement au démarrage ; les relancer est sans danger.

## 3. Vérifier

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=200 web caddy
curl -I https://votre-domaine.example/health/
docker compose -f docker-compose.prod.yml exec web python manage.py check --deploy --settings=config.settings.production
```

Vérifiez le cadenas HTTPS, la redirection HTTP, le site, `/cms/`, une image, le sitemap et l’envoi du formulaire. Une fois HTTPS durablement validé et tous les sous-domaines audités, fixez `SECURE_HSTS_SECONDS=31536000`. N’activez `SECURE_HSTS_PRELOAD=1` qu’après avoir accepté les conséquences durables de la liste de préchargement des navigateurs, puis redémarrez `web`.

## 4. Mise à jour sûre

Créez d’abord une sauvegarde. Puis :

```bash
git fetch --all --prune
git checkout main
git pull --ff-only
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=100 web
```

Compose remplace le conteneur applicatif sans supprimer les volumes. Les migrations doivent être rétrocompatibles lorsqu’un déploiement sans interruption stricte est requis.

## 5. Retour arrière

Repérez le commit stable, sauvegardez l’état courant, puis replacez le dépôt sur ce tag ou commit avec `git checkout <tag-stable>` et reconstruisez. Ne rétrogradez jamais une migration destructive sans procédure écrite ; restaurez plutôt la sauvegarde PostgreSQL correspondante. Voir [backup-restore.md](backup-restore.md).
