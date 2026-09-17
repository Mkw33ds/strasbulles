# Gestion des contenus

## Prise en main

Connectez-vous à `/cms/`. Utilisez l’explorateur de pages pour créer un événement sous **Événements**, une chronique sous **Chroniques**, une fiche artiste sous **Auteurs et autrices** ou une édition sous **Archives**. Les boutons **Aperçu**, **Enregistrer comme brouillon**, **Soumettre pour modération** et **Publier** suivent le cycle standard de Wagtail.

Renseignez un titre SEO et une description dans l’onglet **Promotion**. Une image de partage au format horizontal est recommandée. Chaque image informative doit recevoir un texte alternatif décrivant ce qu’elle apporte ; une image purement décorative peut garder un texte vide.

## Événements

La date de fin ne peut pas précéder la date de début. Un événement reste publié après sa tenue et apparaît automatiquement dans la section « Événements passés ». Ne le supprimez pas : il contribue aux archives.

## Chroniques

La date éditoriale détermine l’ordre. Les métadonnées du livre sont facultatives. Catégories et contributeurs sont gérés dans **Extraits**. Une publication future se programme depuis le menu de publication Wagtail.

## Référentiels et réglages

Les lieux, partenaires, catégories, contributeurs, liens sociaux et liens de pied de page sont des extraits réutilisables. Les coordonnées et informations générales du festival se trouvent dans **Réglages**. L’infolettre reste désactivée tant qu’une URL de service validée n’est pas fournie.

## Rôles

Exécutez `python manage.py setup_staff_groups`, puis affectez les comptes aux groupes. Pour un contrôle fin, ouvrez les réglages du groupe dans Wagtail et limitez ses droits à la branche de pages concernée. Les rédacteurs soumettent ; les éditeurs relisent, programment et publient ; les administrateurs gèrent également réglages et utilisateurs.

## Confidentialité

Le formulaire envoie un courriel et ne crée aucune ligne en base. Les coordonnées sont traitées uniquement pour répondre. Le piège invisible et une temporisation par adresse IP limitent le spam. Aucun outil de mesure d’audience ni traceur publicitaire n’est actif.

