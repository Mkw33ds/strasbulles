# Sauvegarde et restauration

Les sauvegardes doivent être chiffrées, copiées hors du VPS et testées régulièrement. Elles contiennent potentiellement des données personnelles dans les comptes CMS et les journaux éditoriaux.

## Sauvegarder

Depuis le dépôt sur le serveur :

```bash
mkdir -p backups
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "backups/database-$(date +%F-%H%M).sql.gz"
docker compose -f docker-compose.prod.yml exec -T web tar -czf - /app/media > "backups/media-$(date +%F-%H%M).tar.gz"
sha256sum backups/*
```

Conservez ensemble l’export SQL, les médias, le commit Git et une copie sécurisée des variables d’environnement. Automatisez ensuite cette commande avec un minuteur systemd et une politique de rétention adaptée.

## Restaurer

Arrêtez les écritures, créez une sauvegarde de précaution et vérifiez les sommes de contrôle. Pour une base vide compatible :

```bash
gunzip -c backups/database-AAAA-MM-JJ-HHMM.sql.gz | docker compose -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
docker compose -f docker-compose.prod.yml exec -T web tar -xzf - -C / < backups/media-AAAA-MM-JJ-HHMM.tar.gz
docker compose -f docker-compose.prod.yml restart web caddy
```

Pour remplacer une base existante, créez de préférence une nouvelle base ou supprimez/recréez explicitement l’ancienne après double vérification. Cette opération destructive n’est volontairement pas automatisée dans le Makefile.

Après restauration, lancez `python manage.py check`, ouvrez plusieurs pages et médias, vérifiez le CMS et contrôlez les journaux.

