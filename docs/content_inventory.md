# Inventaire du contenu historique

Audit réalisé le 17 septembre 2026 depuis le site public <https://strasbulles.com/>. Les textes courts récupérables ont été reformulés avec correction des problèmes évidents d’espacement. Aucune image n’est copiée ni liée à distance : les droits et fichiers originaux doivent être confirmés.

| Titre existant | URL existante | Nouveau type | Nouvelle URL | État | Médias à confirmer | Redirection |
|---|---|---|---|---|---|---|
| Accueil Strasbulles | `/` | HomePage | `/` | Introduction association et titres des trois chroniques importés | campagne, logo, photos | non |
| Le festival | navigation uniquement | FestivalPage | `/strasbulles/` | structure créée, informations actuelles manquantes | affiche, programme | non applicable |
| Auteurs et autrices | `/auteurs-et-autrices/` | AuthorIndexPage / AuthorPage | identique | index vide sur la source ; trois noms cités dans les Classes créés comme fiches à vérifier | portraits, biographies | non |
| Archives | `/archives/` | FestivalArchiveIndexPage / FestivalEditionPage | identique | années 2008–2021 créées | toutes les affiches et documents | non |
| L’association | `/lassociation/` | StandardPage | `/association/` | texte principal importé | cinq photos de classes | oui, 301 |
| Classes de Bande Dessinée | section de `/lassociation/` | StandardPage | `/association/classes-de-bande-dessinee/` | résumé fiable importé | photos et autorisations de mineurs | nouvelle URL |
| Partenariats solidaires | section de `/lassociation/` | StandardPage | `/association/partenariats-solidaires/` | résumé importé, organismes non repris sans confirmation | logos et conventions | nouvelle URL |
| Adhérer / Soutenir | `/adherer-soutenir/` | StandardPage | `/association/adherer-soutenir/` | page source sans contenu exploitable | modalités, tarif, bulletin | oui, 301 |
| Événements à venir | `/evenements-a-venir/` | EventIndexPage / EventPage | `/evenements/` | Strasbulles d’Automne archivé ; année et lieu restent à confirmer | visuel et programme | oui, 301 |
| Les rencontres | `/annonces/` | StandardPage | `/rencontres/` | texte synthétisé et corrigé | galerie de onze images | oui, 301 |
| Chroniques | `/chroniques/` | BlogIndexPage / BlogPage | identique | trois entrées publiques initialisées ; texte intégral non copié sans validation éditoriale | couvertures, crédits, textes complets | non |
| Contact | lien historique incohérent vers `/archives/` | ContactPage | `/contact/` | formulaire neuf, coordonnées à renseigner | aucun | à contrôler dans Search Console |
| Mentions légales | `/mentions-legles/` | StandardPage | `/mentions-legales/` | structure créée ; données légales incomplètes non inventées | adresse, RNA/SIRET, direction | oui, 301 |
| Politique de confidentialité | `/politique-de-confidentialites/` | StandardPage | `/politique-de-confidentialite/` | politique minimale du formulaire ; validation juridique requise | aucun | oui, 301 |

## Éléments vérifiés

- Alsace Bande Dessinée indique une création en 2007.
- Strasbulles est présenté comme le festival européen de la bande dessinée de Strasbourg.
- Le site source affiche des archives d’affiches de 2008 à 2021.
- Les trois chroniques les plus récentes visibles au moment de l’audit sont *Moi, ce que j’aime, c’est les monstres*, *Joe Shuster* et *Baker Street — All you need is Holmes*, datées du 10 août 2026.

## Avant mise en ligne

Obtenir les fichiers originaux et autorisations pour chaque affiche, photo, couverture et logo ; confirmer les dates, horaires, lieux et tarifs ; relire les biographies ; compléter les coordonnées et mentions légales ; décider quelles chroniques peuvent être reprises intégralement. La commande `seed_content` marque explicitement ces valeurs provisoires et ne télécharge aucun média.

