# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.5.0](https://github.com/FreelanSign/FreelanSign/compare/v0.4.0...v0.5.0) (2026-02-16)


### Features

* **railway:** add railway configuration for production deployment ([74831cb](https://github.com/FreelanSign/FreelanSign/commit/74831cb))


### Bug Fixes

* **quote:** Dependency issue for preview quote ([c49c3bd](https://github.com/FreelanSign/FreelanSign/commit/c49c3bd))

## [0.4.0](https://github.com/FreelanSign/FreelanSign/compare/v0.2.1...v0.4.0) (2026-02-10)


### Features

* **account:** Add address fields for professional structure ([#106](https://github.com/FreelanSign/FreelanSign/issues/106)) ([2cc22cc](https://github.com/FreelanSign/FreelanSign/commit/2cc22cc))
* **account:** Add professional_headline field for quotes ([#101](https://github.com/FreelanSign/FreelanSign/issues/101)) ([81cb152](https://github.com/FreelanSign/FreelanSign/commit/81cb152))
* **account:** implement account logo upload and management functionality ([#102](https://github.com/FreelanSign/FreelanSign/issues/102)) ([d0a3a73](https://github.com/FreelanSign/FreelanSign/commit/d0a3a73))
* **account:** Account requirement enforcement and onboarding UX ([#61](https://github.com/FreelanSign/FreelanSign/issues/61)) ([aec70bf](https://github.com/FreelanSign/FreelanSign/commit/aec70bf))
* **account:** Complete Account domain implementation (Phases 1-7) ([#55](https://github.com/FreelanSign/FreelanSign/issues/55)-[#60](https://github.com/FreelanSign/FreelanSign/issues/60)) ([0aad4e8](https://github.com/FreelanSign/FreelanSign/commit/0aad4e8))
* **audit:** implement audit logging for sensitive actions in Client and Account models ([#71](https://github.com/FreelanSign/FreelanSign/issues/71)) ([f7e4171](https://github.com/FreelanSign/FreelanSign/commit/f7e4171))
* **client:** add delete button with soft delete protection and modern UI ([#84](https://github.com/FreelanSign/FreelanSign/issues/84)) ([201941e](https://github.com/FreelanSign/FreelanSign/commit/201941e))
* **client:** enhance client management with CRUD operations and pagination ([#78](https://github.com/FreelanSign/FreelanSign/issues/78)) ([d32a35c](https://github.com/FreelanSign/FreelanSign/commit/d32a35c))
* **client:** Structured client address management ([#90](https://github.com/FreelanSign/FreelanSign/issues/90)) ([ff6fc7c](https://github.com/FreelanSign/FreelanSign/commit/ff6fc7c))
* **dashboard:** add dashboard metrics with revenue and quote analytics ([#81](https://github.com/FreelanSign/FreelanSign/issues/81)) ([7600a30](https://github.com/FreelanSign/FreelanSign/commit/7600a30))
* **legal_terms:** Add LegalTerms page and integrate into sidebar and quote details ([#66](https://github.com/FreelanSign/FreelanSign/issues/66)) ([aed966d](https://github.com/FreelanSign/FreelanSign/commit/aed966d))
* **legal_terms:** Implement LegalTerms bounded context for CGV/CGU management ([#65](https://github.com/FreelanSign/FreelanSign/issues/65)) ([2c0d3ec](https://github.com/FreelanSign/FreelanSign/commit/2c0d3ec))
* **pdf:** replace Playwright with WeasyPrint for PDF generation ([#113](https://github.com/FreelanSign/FreelanSign/issues/113)) ([c3d3228](https://github.com/FreelanSign/FreelanSign/commit/c3d3228))
* **quote:** Allow editable description per quote line item ([#103](https://github.com/FreelanSign/FreelanSign/issues/103)) ([3d3c6b0](https://github.com/FreelanSign/FreelanSign/commit/3d3c6b0))
* **quote:** improve PDF layout and auto-hide redundant TVA column ([#108](https://github.com/FreelanSign/FreelanSign/issues/108)) ([5b6deea](https://github.com/FreelanSign/FreelanSign/commit/5b6deea))
* **quote:** Implement robust quote status management with restricted editing for non-draft quotes ([#111](https://github.com/FreelanSign/FreelanSign/issues/111)) ([d589fa2](https://github.com/FreelanSign/FreelanSign/commit/d589fa2))
* **quote:** implement soft delete for quotes with RGPD compliance ([#83](https://github.com/FreelanSign/FreelanSign/issues/83)) ([9a12d30](https://github.com/FreelanSign/FreelanSign/commit/9a12d30))
* **quote:** Legal compliance for quote templates ([#105](https://github.com/FreelanSign/FreelanSign/issues/105)) ([ae26e37](https://github.com/FreelanSign/FreelanSign/commit/ae26e37))
* **rgpd:** add SoftDeleteModel to Client and Account with cascade logic ([#68](https://github.com/FreelanSign/FreelanSign/issues/68)) ([7efb03c](https://github.com/FreelanSign/FreelanSign/commit/7efb03c))
* **rgpd:** implement Article 17 anonymization for accounts and clients ([#77](https://github.com/FreelanSign/FreelanSign/issues/77)) ([ef415fd](https://github.com/FreelanSign/FreelanSign/commit/ef415fd))
* **rgpd:** implement automated retention policy for GDPR compliance ([#73](https://github.com/FreelanSign/FreelanSign/issues/73)) ([70ca31e](https://github.com/FreelanSign/FreelanSign/commit/70ca31e))
* **rgpd:** implement data export endpoint (Article 20) ([#76](https://github.com/FreelanSign/FreelanSign/issues/76)) ([08d098e](https://github.com/FreelanSign/FreelanSign/commit/08d098e))
* **rgpd:** implement field-level encryption for sensitive personal data ([#70](https://github.com/FreelanSign/FreelanSign/issues/70)) ([7efb03c](https://github.com/FreelanSign/FreelanSign/commit/7efb03c))
* **subscription:** add subscription plan quota system with beta warning ([#109](https://github.com/FreelanSign/FreelanSign/issues/109)) ([b2562dc](https://github.com/FreelanSign/FreelanSign/commit/b2562dc))
* **ui:** migrate QuoteDetailPage and LegalTermsPage to shadcn/ui ([#86](https://github.com/FreelanSign/FreelanSign/issues/86)) ([29d430c](https://github.com/FreelanSign/FreelanSign/commit/29d430c))
* **user:** Avatar upload with Supabase Storage ([#100](https://github.com/FreelanSign/FreelanSign/issues/100)) ([e550bf5](https://github.com/FreelanSign/FreelanSign/commit/e550bf5))


### Bug Fixes

* **account:** Enhance account management and validation ([#64](https://github.com/FreelanSign/FreelanSign/issues/64)) ([601c2d5](https://github.com/FreelanSign/FreelanSign/commit/601c2d5))
* **deployment:** Fix technical errors and deployment readiness ([#92](https://github.com/FreelanSign/FreelanSign/issues/92), [#94](https://github.com/FreelanSign/FreelanSign/issues/94)) ([8b4e86d](https://github.com/FreelanSign/FreelanSign/commit/8b4e86d))
* **quote:** Implement percentage-based discounts for quote lines ([#110](https://github.com/FreelanSign/FreelanSign/issues/110)) ([f72d297](https://github.com/FreelanSign/FreelanSign/commit/f72d297))
* **quote:** Discount field not taken into account in calculations and display ([#107](https://github.com/FreelanSign/FreelanSign/issues/107)) ([7066b6d](https://github.com/FreelanSign/FreelanSign/commit/7066b6d))
* **quote:** Legal terms (CGV) not generated in quote PDFs + branding migration ([#88](https://github.com/FreelanSign/FreelanSign/issues/88)) ([c9e7540](https://github.com/FreelanSign/FreelanSign/commit/c9e7540))
* **quote:** Fix update quote issue ([#79](https://github.com/FreelanSign/FreelanSign/issues/79)) ([caaa040](https://github.com/FreelanSign/FreelanSign/commit/caaa040))
* **ui:** improve auth pages UX and visual consistency ([#97](https://github.com/FreelanSign/FreelanSign/issues/97)) ([190aba3](https://github.com/FreelanSign/FreelanSign/commit/190aba3))
* **user:** remove dead field birthday in user form (register and edit) ([#99](https://github.com/FreelanSign/FreelanSign/issues/99)) ([1e9b725](https://github.com/FreelanSign/FreelanSign/commit/1e9b725))
* **user:** profile updates not reflected in API response ([#95](https://github.com/FreelanSign/FreelanSign/issues/95)) ([f6ad2eb](https://github.com/FreelanSign/FreelanSign/commit/f6ad2eb))


### [0.2.1](https://github.com/FreelanSign/FreelanSign/compare/v0.2.0...v0.2.1) (2025-11-23)


### Features

* Implement comprehensive production deployment setup ([#51](https://github.com/FreelanSign/FreelanSign/issues/51)) ([ee29f8d](https://github.com/FreelanSign/FreelanSign/commit/ee29f8d9e9989cab82189e243b6a03a9e0a5b00f))
* **infra:** implement production-ready Docker environment ([#50](https://github.com/FreelanSign/FreelanSign/issues/50)) ([74cf6b9](https://github.com/FreelanSign/FreelanSign/commit/74cf6b903bf728ed6d3300b024fbb42c5e13ce54))
* **quote:** add PDF preview functionality for quotes ([#34](https://github.com/FreelanSign/FreelanSign/issues/34)) ([802990a](https://github.com/FreelanSign/FreelanSign/commit/802990a51bf69ba618f7e4f23fe710707333bfe3))
* **quote:** implement PDF download functionality for quotes ([#35](https://github.com/FreelanSign/FreelanSign/issues/35)) ([b325f46](https://github.com/FreelanSign/FreelanSign/commit/b325f46d051a5fe605813373197d3f0b6fdb1287))
* **ui:** add a basic footer with essential informations ([#52](https://github.com/FreelanSign/FreelanSign/issues/52)) ([1578c81](https://github.com/FreelanSign/FreelanSign/commit/1578c81c3cd1d14c5972bccde778a2d51cce77f1))


### Bug Fixes

* **auth:** allow staff to edit role and block admin self-signup ([#33](https://github.com/FreelanSign/FreelanSign/issues/33)) ([51ad782](https://github.com/FreelanSign/FreelanSign/commit/51ad7823d6aa90aa145743f7884798239538942d))

## [0.2.0](https://github.com/FreelanSign/FreelanSign/compare/v0.1.0...v0.2.0) (2025-11-19)


### Features

* **quote:** add PDF preview functionality for quotes ([#34](https://github.com/FreelanSign/FreelanSign/issues/34)) ([802990a](https://github.com/FreelanSign/FreelanSign/commit/802990a51bf69ba618f7e4f23fe710707333bfe3))
* **quote:** implement PDF download functionality for quotes ([#35](https://github.com/FreelanSign/FreelanSign/issues/35)) ([b325f46](https://github.com/FreelanSign/FreelanSign/commit/b325f46d051a5fe605813373197d3f0b6fdb1287))


### Bug Fixes

* **auth:** allow staff to edit role and block admin self-signup ([#33](https://github.com/FreelanSign/FreelanSign/issues/33)) ([51ad782](https://github.com/FreelanSign/FreelanSign/commit/51ad7823d6aa90aa145743f7884798239538942d))

### [0.1.1](https://github.com/FreelanSign/FreelanSign/compare/v0.1.0...v0.1.1) (2025-11-08)


### Features

* **quote:** add PDF preview functionality for quotes ([#34](https://github.com/FreelanSign/FreelanSign/issues/34)) ([802990a](https://github.com/FreelanSign/FreelanSign/commit/802990a51bf69ba618f7e4f23fe710707333bfe3))
* **quote:** generate unique monthly reference on quote creation ([c50a3d5](https://github.com/FreelanSign/FreelanSign/commit/c50a3d5e01cb30e2b24a96b5187d7cc76d748b73))
* **quote:** implement PDF download functionality for quotes ([#35](https://github.com/FreelanSign/FreelanSign/issues/35)) ([b325f46](https://github.com/FreelanSign/FreelanSign/commit/b325f46d051a5fe605813373197d3f0b6fdb1287))


### Bug Fixes

* **auth:** allow staff to edit role and block admin self-signup ([#33](https://github.com/FreelanSign/FreelanSign/issues/33)) ([51ad782](https://github.com/FreelanSign/FreelanSign/commit/51ad7823d6aa90aa145743f7884798239538942d))

## v0.1.0 (2025-10-12)

### ✨ Features
- devis: dropdown pour choisir une prestation lors de l’édition/création (#FS-xxx)

### 🎨 UI/UX
- devis: améliorer le style de la page de création (espacement, lisibilité)
- devis: padding sous le bouton “ajouter une ligne” + rendu plus propre

### 🧹 Chore
- config: ajouter site config
- maintenance: nettoyer les fichiers database (traces locales)
- env: nettoyer les fichiers d’environnement (exclusions .gitignore, sécurité)

### 🔧 Notes techniques
- Mettre à jour les .env d’exemple si nécessaire
- Vérifier que les fichiers DB/ENV sensibles ne sont pas versionnés (voir .gitignore)

### 👨‍💻 Authors
- [@Bertrand2808](https://github.com/Bertrand2808)
