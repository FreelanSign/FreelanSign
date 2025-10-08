# FreelanSign — Release v0.1.0 (prévue: 2025-10-12)

## Objectifs
1- Livrer la refonte du front et les améliorations UX sur l’édition de devis.

2- Aligner `main` avec `dev`.


## Périmètre (tickets)
- Revoir le design
- Édition devis : padding + renommer le bouton "ajouter une prestation"
- feat: Devis → dropdown pour choisir une prestation liée
- Améliorer le style de la page de création de devis
- feat: Responsive (pass 1)
- Synchroniser `main` en important ~15 commits “nouveau front” depuis `dev`

## Hors-scope (glissera en v0.1.1 si non prêt)
- Responsive complet si pass 1 insuffisant

## Critères Go Release
- Tous les tickets ci-dessus merge dans `dev`
- CI verte (lint, build, tests clés)
- Aucune anomalie ouverte
- Smoke test UI (création/édition de devis OK)

## Planning
- Code freeze: sam. → créer `release/v0.1.0` depuis `dev`
- Stabilisation: sam. soir → dim. soir (fix/doc/changelog only)
- Release: dim. → merge vers `main`, tag `freelansign/v0.1.0`, GitHub Release, déploiement
- Back-merge: `main` → `dev`

