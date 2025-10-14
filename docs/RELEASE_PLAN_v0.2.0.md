# FreelanSign — Release v0.2.0 (prévue : 2025-10-28)

## Objectifs

1- Finaliser le flux utilisateur complet jusqu’à l’envoi du devis par mail.

2- Introduire une première base de personnalisation du devis (template statique + preview).

3- Améliorer la fiabilité (PDF, envoi, auth) et la cohérence visuelle du parcours.

## Périmètre (tickets)
- features: mettre en place la réinitialisation du mot de passe
- feature: pouvoir créer un client à la volée
- feat: Endpoint “prestations liées à l’utilisateur”
- feat: Générer une référence automatiquement
- features: Générer PDF
- features: envoi par mail
- Template statique modifiable
- Preview PDF
- bug: revoir les prix des prestations
- Pouvoir déposer une photo pour avatar
- Bloquer la création d’un compte admin
- Revoir le style de la page login
- Automatiser les étapes d’installation (front & back)
- Ajouter pre-commit

## Hors-scope (glissera en v0.3.0 si non prêt)
- Personnalisation avancée du template (système de “tiles”)
- Paramétrage couleurs / logo / typographie du devis
- Refonte responsive complète (pass 2)

## Critères Go Release

- Tous les tickets ci-dessus mergés dans dev
- Génération et envoi de devis testés de bout en bout
- Authentification + réinitialisation fonctionnelles
- Preview PDF opérationnelle dans le form
- CI verte (lint + build + tests clés)
- Aucun bug bloquant ou anomalie ouverte sur le parcours devis

## Planning
- Code freeze : sam. 25 oct. → créer release/v0.2.0 depuis dev
- Stabilisation : sam. soir → lun. 27 oct. (tests, fix, doc, changelog only)
- Release : mar. 28 oct. → merge vers main, tag freelansign/v0.2.0, création GitHub Release + déploiement
- Back-merge : main → dev

## Auteurs

- [@Bertrand2808](https://github.com/Bertrand2808)
