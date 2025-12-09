# SPECIFICATIONS RGPD - FreelanSign

**Document de référence RGPD pour le SaaS FreelanSign**

**Version**: 1.0
**Date**: 2025-12-09
**Contexte**: SaaS de gestion de devis pour freelances (France)
**Stack**: Django + React + PostgreSQL

---

## 1. Cartographie des Données (Data Mapping)

### 1.1 Entité: User (Utilisateur)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans (archivage fiscal) | Exécution du contrat (Art. 6.1.b RGPD) |
| `email` | Actuel | Indispensable | Moyen | Durée de vie du compte + 5 ans | Exécution du contrat + Obligation légale (facturation) |
| `password` (hashé) | Actuel | Indispensable | Élevé | Durée de vie du compte | Exécution du contrat + Sécurité |
| `first_name` | Actuel | Utile | Faible | Durée de vie du compte + 5 ans | Exécution du contrat |
| `last_name` | Actuel | Utile | Faible | Durée de vie du compte + 5 ans | Exécution du contrat |
| `is_staff` | Actuel | Indispensable | Faible | Durée de vie du compte | Gestion interne |
| `is_superuser` | Actuel | Indispensable | Faible | Durée de vie du compte | Gestion interne |
| `is_active` | Actuel | Indispensable | Faible | Durée de vie du compte | Gestion du service |
| `date_joined` | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans | Traçabilité légale |
| `last_login` | Actuel | Utile | Faible | 13 mois (logs CNIL) | Sécurité + Traçabilité |

### 1.2 Entité: Profile (Profil Utilisateur)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `user_id` (FK) | Actuel | Indispensable | Faible | Lié au User | Exécution du contrat |
| `first_name` | Actuel | Utile | Faible | Durée de vie du compte + 5 ans | Exécution du contrat |
| `last_name` | Actuel | Utile | Faible | Durée de vie du compte + 5 ans | Exécution du contrat |
| `phone` | Actuel | Utile | Moyen | Durée de vie du compte + 5 ans | Exécution du contrat (contact professionnel) |
| `avatar_url` | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation (consentement implicite) |
| `role` (freelance/admin) | Actuel | Indispensable | Faible | Durée de vie du compte | Gestion des permissions |
| `created_at` | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans | Traçabilité |
| `updated_at` | Actuel | Indispensable | Faible | Durée de vie du compte | Traçabilité |

### 1.3 Entité: Account (Compte Professionnel)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `user_id` (FK) | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans | Exécution du contrat |
| `display_name` | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans | Obligation légale (facturation) |
| `legal_form` (micro/EIRL/EURL/SASU) | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans | Obligation légale (facturation) |
| `legal_id` (SIRET - 14 chiffres) | Actuel | Indispensable | Moyen | Durée de vie du compte + 10 ans | Obligation légale (facturation + archivage fiscal) |
| `domain` (FK Area) | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation du service |
| `default_rate_cents` (TJM) | Actuel | Utile | Faible | Durée de vie du compte | Facilitation du service |
| `service_types` (M2M Prestation) | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation du service |
| `is_active` | Actuel | Indispensable | Faible | Durée de vie du compte | Gestion du service |
| `created_at` | Actuel | Indispensable | Faible | Durée de vie du compte + 5 ans | Traçabilité |
| `updated_at` | Actuel | Indispensable | Faible | Durée de vie du compte | Traçabilité |

### 1.4 Entité: Client (Clients du Freelance)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Actuel | Indispensable | Faible | 5 ans après dernière transaction | Exécution du contrat |
| `owner_id` (FK User) | Actuel | Indispensable | Faible | 5 ans après dernière transaction | Exécution du contrat |
| `account_id` (FK Account) | Actuel | Indispensable | Faible | 5 ans après dernière transaction | Exécution du contrat |
| `name` | Actuel | Indispensable | Faible | 5 ans après dernière transaction | Obligation légale (facturation) |
| `email` | Actuel | Indispensable | Moyen | 5 ans après dernière transaction | Exécution du contrat + Envoi devis |
| `phone` | Actuel | Utile | Moyen | 5 ans après dernière transaction | Exécution du contrat |
| `address` | Actuel | Utile | Moyen | 5 ans après dernière transaction | Obligation légale (facturation) |
| `vat_number` | Actuel | Utile | Moyen | 10 ans (obligation fiscale) | Obligation légale (TVA intracommunautaire) |
| `metadata` (JSON) | Actuel | Utile | Faible | 5 ans après dernière transaction | Notes professionnelles |
| `created_at` | Actuel | Indispensable | Faible | 5 ans après dernière transaction | Traçabilité |
| `updated_at` | Actuel | Indispensable | Faible | 5 ans après dernière transaction | Traçabilité |

### 1.5 Entité: Quote (Devis)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Actuel | Indispensable | Faible | 10 ans | Obligation légale (archivage comptable) |
| `owner_id` (FK User) | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `client_id` (FK Client) | Actuel | Indispensable | Moyen | 10 ans | Obligation légale |
| `account_id` (FK Account) | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `title` | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `reference` | Actuel | Indispensable | Faible | 10 ans | Obligation légale (numérotation) |
| `currency` | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `language` | Actuel | Utile | Faible | 10 ans | Facilitation du service |
| `status` | Actuel | Indispensable | Faible | 10 ans | Gestion du cycle de vie |
| `issue_date` | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `valid_until` | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `payment_terms` (FK/text) | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `subtotal`, `tax_total`, `discount_total`, `total` | Actuel | Indispensable | Faible | 10 ans | Obligation légale (comptabilité) |
| `note` | Actuel | Utile | Faible | 10 ans | Information commerciale |
| `pdf_file` | Actuel | Indispensable | Moyen | 10 ans | Obligation légale (archivage) |
| `metadata` (JSON) | Actuel | Utile | Faible | 10 ans | Traçabilité technique |
| `created_at`, `updated_at` | Actuel | Indispensable | Faible | 10 ans | Traçabilité légale |
| `sent_at`, `accepted_at` | Actuel | Indispensable | Faible | 10 ans | Traçabilité commerciale |

### 1.6 Entité: QuoteLineItem (Lignes de Devis)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `quote_id` (FK) | Actuel | Indispensable | Faible | 10 ans | Obligation légale |
| `description` | Actuel | Indispensable | Faible | 10 ans | Obligation légale (détail facturation) |
| `qty`, `unit_price`, `tax_rate`, `discount`, `line_total` | Actuel | Indispensable | Faible | 10 ans | Obligation légale (comptabilité) |
| `order` | Actuel | Utile | Faible | 10 ans | Présentation du document |
| `metadata` (JSON - provenance catalog) | Actuel | Utile | Faible | 10 ans | Traçabilité interne |
| `created_at`, `updated_at` | Actuel | Indispensable | Faible | 10 ans | Traçabilité |

### 1.7 Entité: QuoteHistory (Historique/Audit)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Actuel | Indispensable | Faible | 10 ans | Traçabilité légale |
| `quote_id` (FK) | Actuel | Indispensable | Faible | 10 ans | Traçabilité légale |
| `payload_snapshot` (JSON) | Actuel | Indispensable | Moyen | 10 ans | Traçabilité des modifications |
| `action` (created/updated/sent/status_changed) | Actuel | Indispensable | Faible | 10 ans | Audit |
| `actor_id` (FK User - nullable) | Actuel | Indispensable | Moyen | 10 ans | Traçabilité des actions |
| `timestamp` | Actuel | Indispensable | Faible | 10 ans | Audit légal |

### 1.8 Entité: BrandTheme (Personnalisation Marque)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Actuel | Indispensable | Faible | Durée de vie du compte | Exécution du contrat |
| `account_id` (FK) | Actuel | Indispensable | Faible | Durée de vie du compte | Exécution du contrat |
| `name` | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation |
| `is_active` | Actuel | Indispensable | Faible | Durée de vie du compte | Gestion du service |
| `colors`, `typography`, `spacing` (JSON) | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation (consentement implicite) |
| `logo` (FileField) | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation |
| `created_at`, `updated_at` | Actuel | Indispensable | Faible | Durée de vie du compte | Traçabilité |

### 1.9 Entité: LegalTemplate, LegalProfile, AttachedTerms (CGV/CGU)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `jurisdiction`, `version`, `clauses` (JSON) | Actuel | Indispensable | Faible | Permanent (templates globaux) | Obligation légale (transparence contractuelle) |
| `clause_overrides` (JSON) | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation contractuelle |
| `rendered_html`, `rendered_text` | Actuel | Indispensable | Faible | 10 ans (attaché aux devis) | Obligation légale (preuve contractuelle) |
| `snapshot_data` (JSON) | Actuel | Indispensable | Faible | 10 ans | Traçabilité légale (version exacte acceptée) |

### 1.10 Entité: Catalog (Area, Prestation)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `name`, `description` | Actuel | Indispensable | Faible | Permanent (catalogue global) | Fonctionnement du service |
| `weight_days`, `default_rate_cents` | Actuel | Utile | Faible | Permanent (catalogue) | Facilitation du service |
| `custom`, `account_id` (prestations custom) | Actuel | Utile | Faible | Durée de vie du compte | Personnalisation |
| `is_deleted`, `deleted_at` (soft delete) | Actuel | Indispensable | Faible | Permanent (archivage) | Intégrité référentielle |

---

## 1.11 Données Futures: Email Tracking (Envoi de Devis)

### Table: `EmailLog` (À créer)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | 13 mois (recommandation CNIL) | Traçabilité + Preuve d'envoi |
| `quote_id` (FK) | Futur | Indispensable | Moyen | 13 mois | Lien avec devis |
| `recipient_email` | Futur | Indispensable | Moyen | 13 mois | Preuve d'envoi |
| `sender_id` (FK User) | Futur | Indispensable | Faible | 13 mois | Traçabilité |
| `sent_at` | Futur | Indispensable | Faible | 13 mois | Preuve d'envoi |
| `delivery_status` (sent/delivered/bounced/failed) | Futur | Indispensable | Faible | 13 mois | Gestion des erreurs |
| `tracking_token` (UUID pour tracking opens/clicks) | Futur | Utile | Moyen | 13 mois | Suivi commercial (consentement implicite B2B) |
| `opened_at` (timestamp premier open) | Futur | Utile | Moyen | 13 mois | Suivi commercial |
| `clicked_at` (timestamp premier click) | Futur | Utile | Moyen | 13 mois | Suivi commercial |
| `ip_address_open` | Futur | **⚠️ À ÉVITER** | **Élevé** | **NE PAS STOCKER** | Risque RGPD élevé (donnée personnelle sensible sans justification légale forte) |
| `user_agent_open` | Futur | **⚠️ À ÉVITER** | **Élevé** | **NE PAS STOCKER** | Risque RGPD élevé |
| `webhook_payload` (JSON - provider webhook) | Futur | Utile | Moyen | 13 mois | Débogage technique |
| `provider` (SendGrid/Mailgun/etc.) | Futur | Indispensable | Faible | 13 mois | Traçabilité technique |
| `external_message_id` | Futur | Indispensable | Faible | 13 mois | Référence externe |

**⚠️ RECOMMANDATION CRITIQUE:**
- **NE PAS stocker les IP/user-agent** des destinataires lors de l'ouverture d'emails (risque RGPD élevé sans consentement explicite)
- Se limiter aux **horodatages d'ouverture/clic** (binaire: ouvert oui/non + timestamp)
- Utiliser un service de tracking avec **anonymisation automatique** (ex: Mailgun avec IP masquée)
- Purge automatique après **13 mois** (recommandation CNIL pour logs)

---

## 1.12 Données Futures: Signature Électronique (eIDAS via DocuSign)

### Table: `SignatureRequest` (À créer)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | 10 ans (valeur probatoire) | Obligation légale (preuve contractuelle) |
| `quote_id` (FK) | Futur | Indispensable | Moyen | 10 ans | Lien avec devis |
| `requester_id` (FK User - freelance) | Futur | Indispensable | Faible | 10 ans | Traçabilité |
| `docusign_envelope_id` | Futur | Indispensable | Faible | 10 ans | Référence externe |
| `status` (sent/signed/declined/voided) | Futur | Indispensable | Faible | 10 ans | Gestion du cycle de vie |
| `sent_at`, `signed_at`, `declined_at` | Futur | Indispensable | Faible | 10 ans | Traçabilité légale |
| `certificate_pdf` (FileField - certificat de signature) | Futur | Indispensable | Élevé | 10 ans | Obligation légale (valeur probatoire eIDAS) |
| `document_hash_at_signing` (SHA-256) | Futur | Indispensable | Faible | 10 ans | Intégrité du document |
| `created_at`, `updated_at` | Futur | Indispensable | Faible | 10 ans | Traçabilité |

### Table: `Signer` (Signataires - À créer)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | 10 ans | Traçabilité |
| `signature_request_id` (FK) | Futur | Indispensable | Faible | 10 ans | Lien avec demande |
| `client_id` (FK Client - nullable si external) | Futur | Utile | Moyen | 10 ans | Lien avec client |
| `name` | Futur | Indispensable | Moyen | 10 ans | Obligation légale (identification signataire) |
| `email` | Futur | Indispensable | Moyen | 10 ans | Obligation légale (envoi certificat) |
| `role` (signer/cc/approver) | Futur | Indispensable | Faible | 10 ans | Gestion du workflow |
| `signing_order` | Futur | Utile | Faible | 10 ans | Workflow de signature |
| `signed_at` | Futur | Indispensable | Faible | 10 ans | Preuve légale |
| `ip_address_at_signing` | Futur | **Indispensable** | **Élevé** | **10 ans** | **Obligation légale eIDAS** (Art. 25 eIDAS - preuves de signature qualifiée) |
| `geolocation_at_signing` (optionnel) | Futur | **À ÉVITER** | **Sensible** | **NE PAS STOCKER** | Non nécessaire pour eIDAS (risque excessif) |
| `device_info` (optionnel: user-agent) | Futur | Utile | Moyen | 10 ans | Traçabilité technique (eIDAS) |
| `docusign_recipient_id` | Futur | Indispensable | Faible | 10 ans | Référence externe |
| `decline_reason` | Futur | Utile | Faible | 10 ans | Traçabilité commerciale |

**⚠️ PARTICULARITÉ eIDAS:**
- **IP address du signataire**: OBLIGATOIRE pour signature électronique qualifiée/avancée (Art. 25 règlement eIDAS)
- Conservation: **10 ans** (valeur probatoire légale)
- Base légale: **Obligation légale** (Art. 6.1.c RGPD + eIDAS)
- **Géolocalisation**: NON nécessaire (risque excessif, éviter)
- **Certificat de signature**: Archivage obligatoire (preuve cryptographique)

---

## 1.13 Données Futures: Paiement Stripe (Abonnement SaaS)

### Table: `StripeCustomer` (À créer - sync avec Stripe)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | Durée abonnement + 10 ans (comptabilité) | Exécution du contrat |
| `account_id` (FK Account) | Futur | Indispensable | Faible | Durée abonnement + 10 ans | Exécution du contrat |
| `stripe_customer_id` (ex: cus_XXX) | Futur | Indispensable | Moyen | Durée abonnement + 10 ans | Exécution du contrat (Stripe) |
| `stripe_email` | Futur | Indispensable | Moyen | Durée abonnement + 10 ans | Synchronisation Stripe |
| `currency` (ex: EUR) | Futur | Indispensable | Faible | Durée abonnement + 10 ans | Facturation |
| `metadata` (JSON - sync Stripe) | Futur | Utile | Faible | Durée abonnement + 10 ans | Traçabilité |
| `created_at`, `updated_at` | Futur | Indispensable | Faible | Durée abonnement + 10 ans | Traçabilité |

### Table: `StripeSubscription` (À créer)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | 10 ans | Obligation légale (comptabilité) |
| `stripe_customer_id` (FK) | Futur | Indispensable | Faible | 10 ans | Exécution du contrat |
| `stripe_subscription_id` (ex: sub_XXX) | Futur | Indispensable | Moyen | 10 ans | Référence Stripe |
| `status` (active/past_due/canceled/unpaid) | Futur | Indispensable | Faible | 10 ans | Gestion du service |
| `plan_name` (ex: Starter/Pro/Enterprise) | Futur | Indispensable | Faible | 10 ans | Traçabilité commerciale |
| `current_period_start`, `current_period_end` | Futur | Indispensable | Faible | 10 ans | Gestion de facturation |
| `cancel_at`, `canceled_at` | Futur | Utile | Faible | 10 ans | Traçabilité |
| `cancellation_reason` | Futur | Utile | Faible | 10 ans | Analyse commerciale (consentement implicite) |
| `trial_end` | Futur | Utile | Faible | 10 ans | Gestion du service |
| `created_at`, `updated_at` | Futur | Indispensable | Faible | 10 ans | Traçabilité |

### Table: `StripePaymentMethod` (À créer - tokenisé)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | Durée abonnement actif | Exécution du contrat |
| `stripe_customer_id` (FK) | Futur | Indispensable | Faible | Durée abonnement actif | Exécution du contrat |
| `stripe_payment_method_id` (ex: pm_XXX - TOKEN) | Futur | Indispensable | **Élevé** | Durée abonnement actif | Exécution du contrat (tokenisé par Stripe) |
| `type` (card/sepa_debit/etc.) | Futur | Indispensable | Faible | Durée abonnement actif | Gestion du paiement |
| `card_brand` (visa/mastercard/etc.) | Futur | Utile | Faible | Durée abonnement actif | Affichage UI |
| `card_last4` (ex: 4242) | Futur | Utile | Moyen | Durée abonnement actif | Affichage UI (reconnaissance) |
| `card_exp_month`, `card_exp_year` | Futur | Utile | Moyen | Durée abonnement actif | Gestion expiration |
| `is_default` | Futur | Indispensable | Faible | Durée abonnement actif | Gestion du paiement |
| `created_at`, `updated_at` | Futur | Indispensable | Faible | Durée abonnement actif | Traçabilité |

**⚠️ SÉCURITÉ CRITIQUE:**
- **JAMAIS stocker**: Numéro de carte complet, CVV, code PIN, données bancaires brutes
- **Toujours utiliser**: Tokens Stripe (`pm_XXX`, `card_XXX`)
- **PCI-DSS**: FreelanSign n'est PAS soumis à PCI-DSS car aucune donnée bancaire n'est collectée directement (délégation totale à Stripe)
- **Card brand + last4**: Acceptable pour UI (Art. 6.1.b RGPD - exécution du contrat)

### Table: `StripeInvoice` (À créer - synchronisation Stripe)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | 10 ans | Obligation légale (archivage comptable) |
| `stripe_invoice_id` (ex: in_XXX) | Futur | Indispensable | Faible | 10 ans | Référence Stripe |
| `stripe_subscription_id` (FK) | Futur | Indispensable | Faible | 10 ans | Lien avec abonnement |
| `status` (draft/open/paid/void/uncollectible) | Futur | Indispensable | Faible | 10 ans | Gestion comptable |
| `amount_due`, `amount_paid`, `currency` | Futur | Indispensable | Faible | 10 ans | Obligation légale (comptabilité) |
| `invoice_pdf_url` | Futur | Indispensable | Faible | 10 ans | Obligation légale (archivage) |
| `invoice_number` | Futur | Indispensable | Faible | 10 ans | Obligation légale (numérotation) |
| `period_start`, `period_end` | Futur | Indispensable | Faible | 10 ans | Facturation |
| `paid_at` | Futur | Indispensable | Faible | 10 ans | Traçabilité comptable |
| `webhook_received_at` | Futur | Utile | Faible | 13 mois | Débogage technique |
| `created_at`, `updated_at` | Futur | Indispensable | Faible | 10 ans | Traçabilité |

### Table: `StripeWebhookEvent` (À créer - logs webhooks)

| Champ/Donnée | Statut | Nécessité | Risque RGPD | Conservation | Justification/Base Légale |
|--------------|--------|-----------|-------------|--------------|---------------------------|
| `id` (UUID) | Futur | Indispensable | Faible | 13 mois | Débogage technique |
| `stripe_event_id` (ex: evt_XXX) | Futur | Indispensable | Faible | 13 mois | Idempotence |
| `event_type` (ex: invoice.paid, customer.subscription.updated) | Futur | Indispensable | Faible | 13 mois | Traçabilité |
| `payload` (JSON - full webhook body) | Futur | Utile | Moyen | 13 mois | Débogage (contient données client) |
| `processed` (boolean) | Futur | Indispensable | Faible | 13 mois | Gestion de la queue |
| `processed_at` | Futur | Utile | Faible | 13 mois | Traçabilité |
| `error_message` | Futur | Utile | Faible | 13 mois | Débogage |
| `created_at` | Futur | Indispensable | Faible | 13 mois | Traçabilité |

**⚠️ PURGE AUTOMATIQUE:**
- Logs webhooks: **13 mois** (recommandation CNIL)
- Mise en place d'une **tâche CRON** pour purge automatique

---

## 2. Analyse des Risques et Minimisation

### 2.1 Champs Actuels Potentiellement Excessifs

#### ⚠️ `Profile.avatar_url`
- **Risque**: Donnée personnelle non essentielle (photos = biométrie potentielle)
- **Recommandation**: Acceptable en contexte B2B professionnel, mais implémenter:
  - Option "Supprimer l'avatar" dans l'interface
  - Suppression automatique lors de la clôture du compte
  - Hébergement sécurisé (CDN avec contrôle d'accès)

#### ⚠️ `Client.metadata` (JSON libre)
- **Risque**: Champ JSON libre peut contenir des données sensibles non contrôlées
- **Recommandation**:
  - Documenter clairement les champs autorisés
  - Ajouter une validation côté backend (whitelist de clés autorisées)
  - Ne JAMAIS stocker: données de santé, opinions politiques, données bancaires
  - Afficher un disclaimer dans l'UI: "Ne stockez pas de données sensibles ici"

#### ⚠️ `QuoteHistory.payload_snapshot` (JSON)
- **Risque**: Peut contenir des données client/freelance en clair
- **Recommandation**:
  - Limiter le snapshot aux champs essentiels (montants, statut, référence)
  - Exclure les champs sensibles (email client, téléphone) du snapshot
  - Anonymiser après 10 ans (remplacer noms/emails par des hashes)

### 2.2 Données à NE JAMAIS Stocker

#### 🚫 Pour le Paiement (Stripe)
- **Numéro de carte bancaire complet** (PAN)
- **CVV/CVC** (code de sécurité)
- **Code PIN**
- **Coordonnées bancaires IBAN/BIC** (sauf si SEPA tokenisé par Stripe)
- **Date de naissance complète** (jours/mois suffisent pour âge si nécessaire)
- **Adresse IP de paiement** (Stripe gère la fraude)

#### 🚫 Pour la Signature Électronique
- **Géolocalisation GPS précise** du signataire (risque excessif, non requis eIDAS)
- **Données biométriques** (empreintes digitales, reconnaissance faciale) sauf si signature biométrique qualifiée
- **Historique de navigation** avant/après signature

#### 🚫 Pour l'Email Tracking
- **Adresse IP complète** des destinataires (ouverture/clic email)
- **User-agent détaillé** (fingerprinting)
- **Historique de navigation** post-clic
- **Données de géolocalisation** IP-based

#### 🚫 Données Sensibles (Art. 9 RGPD - Interdiction stricte)
- Origine raciale/ethnique
- Opinions politiques
- Convictions religieuses/philosophiques
- Appartenance syndicale
- Données de santé
- Vie sexuelle/orientation sexuelle
- Données génétiques/biométriques (sauf signature qualifiée encadrée)

### 2.3 Soft Delete: Gestion du "Droit à l'Oubli"

#### Implémentation Actuelle (Catalogue uniquement)
- `Prestation`: Utilise `SoftDeleteModel` (is_deleted, deleted_at)
- Permet de masquer des prestations sans casser les références dans les devis existants

#### Problème: Manque de Soft Delete sur les Entités Critiques
- **`Client`**: Hard delete actuel → RISQUE si client référencé dans des devis
- **`Account`**: Hard delete actuel → RISQUE si compte a des devis/factures archivées

#### Recommandation: Étendre Soft Delete

**Ajouter `SoftDeleteModel` à:**
1. **`Client`** (apps/client/models.py)
   - Évite la suppression des références dans les devis existants
   - Permet d'anonymiser les données après demande RGPD (voir section 3.4)

2. **`Account`** (apps/user/models/account.py)
   - Idem, préserve l'intégrité référentielle
   - Permet un "départ" en douceur avec archivage des documents légaux

**Pseudonymisation après Soft Delete:**
- Remplacer `Client.name` → "Client supprimé [UUID]"
- Remplacer `Client.email` → "deleted_[UUID]@anonymized.local"
- Conserver les montants et références de devis (obligation légale 10 ans)

---

## 3. Recommandations Techniques "Privacy by Design"

### 3.1 Chiffrement et Sécurité

#### 3.1.1 Chiffrement au Repos (Database)
**Données à chiffrer (chiffrement au niveau colonne - Django Cryptography):**
- `Client.email`
- `Client.phone`
- `Client.vat_number`
- `Account.legal_id` (SIRET)
- `Signer.ip_address_at_signing` (quand implémenté)
- `StripeCustomer.stripe_customer_id` (token sensible)
- `StripePaymentMethod.stripe_payment_method_id` (token carte)

**Implémentation:**
```python
# Example avec django-fernet-encrypted-fields
from fernet_fields import EncryptedCharField, EncryptedEmailField

class Client(models.Model):
    email = EncryptedEmailField(max_length=255, blank=True)
    phone = EncryptedCharField(max_length=64, blank=True)
    vat_number = EncryptedCharField(max_length=64, blank=True)
```

**Gestion des clés:**
- Clé de chiffrement: Variable d'environnement `FIELD_ENCRYPTION_KEY`
- Rotation annuelle recommandée (nécessite re-chiffrement)
- Stockage sécurisé: AWS Secrets Manager / Vault / Doppler

#### 3.1.2 Chiffrement en Transit
- **HTTPS obligatoire** (TLS 1.3) pour toute l'application
- **Webhooks Stripe**: HTTPS + signature validation (clé webhook secret)
- **API DocuSign**: HTTPS + OAuth2 avec refresh tokens

#### 3.1.3 Sécurité des Fichiers (PDFs)
- **Quote PDFs**: Stockage sécurisé (S3 privé avec signed URLs temporaires)
- **Certificats de signature**: Chiffrement au repos (S3 SSE-KMS)
- **Accès**: Authentification obligatoire + vérification ownership
- **Durée de vie des signed URLs**: 15 minutes max

### 3.2 Gestion des Webhooks et Logs

#### 3.2.1 Webhooks Stripe
**Table `StripeWebhookEvent` (logs):**
- Conservation: **13 mois** (recommandation CNIL)
- Purge automatique via tâche CRON quotidienne:
  ```python
  # apps/payment/tasks.py
  def purge_old_webhook_events():
      cutoff_date = timezone.now() - timedelta(days=395)  # 13 mois
      StripeWebhookEvent.objects.filter(created_at__lt=cutoff_date).delete()
  ```

**Validation des webhooks:**
- Vérification de signature Stripe (`stripe.Webhook.construct_event()`)
- Idempotence: Vérifier `stripe_event_id` avant traitement
- Logging minimal (event_type + status, pas de payload complet en logs applicatifs)

#### 3.2.2 Email Tracking Logs
**Table `EmailLog`:**
- Conservation: **13 mois**
- Purge automatique:
  ```python
  def purge_old_email_logs():
      cutoff_date = timezone.now() - timedelta(days=395)
      EmailLog.objects.filter(sent_at__lt=cutoff_date).delete()
  ```

**Tracking Opens/Clicks:**
- Utiliser un pixel transparent 1x1 avec token unique
- NE PAS logger l'IP/user-agent du destinataire
- Stocker uniquement: `opened_at` (timestamp), `clicked_at` (timestamp)
- Provider recommandé: **Mailgun** avec option "anonymize IPs"

### 3.3 Architecture "Droit à l'Oubli" (Art. 17 RGPD)

#### Scénario 1: Suppression d'un Freelance (Account)

**Problème:**
- Freelance veut supprimer son compte
- Mais a des devis/factures avec obligation légale d'archivage 10 ans

**Solution: Anonymisation Progressive**

1. **Phase 1: Soft Delete + Désactivation** (Immédiat)
   ```python
   def anonymize_account_for_deletion(account_id):
       account = Account.objects.get(id=account_id)
       user = account.user

       # Soft delete account
       account.is_active = False
       account.display_name = f"Compte supprimé [{account.id}]"
       account.legal_id = None  # SIRET anonymisé
       account.save()

       # Anonymiser user
       user.email = f"deleted_{user.id}@anonymized.local"
       user.first_name = "Utilisateur"
       user.last_name = "Supprimé"
       user.is_active = False
       user.save()

       # Anonymiser profile
       profile = user.profile
       profile.phone = None
       profile.avatar_url = None
       profile.save()
   ```

2. **Phase 2: Conservation des Devis pour Comptabilité** (10 ans)
   - Les devis restent avec référence anonymisée
   - Les montants sont conservés (obligation légale)
   - Les documents PDFs sont conservés (archivage obligatoire)

3. **Phase 3: Hard Delete après 10 ans** (Automatique)
   ```python
   def purge_expired_accounts():
       cutoff_date = timezone.now() - timedelta(days=3650)  # 10 ans

       # Trouver les comptes soft-deleted depuis >10 ans
       accounts = Account.objects.filter(
           is_active=False,
           updated_at__lt=cutoff_date
       )

       for account in accounts:
           # Vérifier que tous les devis sont >10 ans
           if not account.quotes.filter(created_at__gte=cutoff_date).exists():
               # Hard delete (CASCADE sur User, Profile, Quotes, etc.)
               account.user.delete()  # Cascade vers Account, Profile
   ```

#### Scénario 2: Suppression d'un Client

**Problème:**
- Client demande suppression (RGPD)
- Mais est référencé dans des devis du freelance (obligation légale 10 ans)

**Solution: Soft Delete + Anonymisation**

1. **Implémentation:**
   ```python
   def anonymize_client_for_deletion(client_id):
       client = Client.objects.get(id=client_id)

       # Soft delete
       client.is_deleted = True
       client.deleted_at = timezone.now()

       # Anonymisation
       client.name = f"Client supprimé [{client.id}]"
       client.email = f"deleted_{client.id}@anonymized.local"
       client.phone = ""
       client.address = ""
       client.vat_number = ""
       client.metadata = {}

       client.save()
   ```

2. **Conservation:**
   - Les devis conservent la référence anonymisée
   - Les montants et dates sont préservés (comptabilité)

3. **Hard Delete après 10 ans:**
   - Automatique via CRON (même logique que Account)

#### Scénario 3: Suppression des Données Stripe

**Problème:**
- Utilisateur résilie son abonnement
- Stripe conserve ses données de paiement

**Solution:**
1. **Lors de la résiliation:**
   ```python
   def delete_stripe_customer_data(account_id):
       stripe_customer = StripeCustomer.objects.get(account_id=account_id)

       # Supprimer les payment methods chez Stripe
       stripe.PaymentMethod.detach(stripe_customer.stripe_payment_method_id)

       # Anonymiser les données locales (conserver logs comptables)
       StripeCustomer.objects.filter(account_id=account_id).update(
           stripe_email=f"deleted_{account_id}@anonymized.local"
       )

       # Conserver les invoices (obligation légale 10 ans)
       # Mais supprimer les références aux cartes
       StripePaymentMethod.objects.filter(
           stripe_customer_id=stripe_customer.id
       ).delete()
   ```

2. **Hard Delete après 10 ans:**
   - Purge automatique des invoices et customer records

### 3.4 Gestion des Durées de Conservation

**Implémentation d'une Politique de Rétention:**

```python
# apps/core/management/commands/apply_retention_policy.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Applique la politique de rétention RGPD"

    def handle(self, *args, **options):
        now = timezone.now()

        # 1. Purger logs webhooks Stripe (13 mois)
        cutoff_13m = now - timedelta(days=395)
        deleted_webhooks = StripeWebhookEvent.objects.filter(
            created_at__lt=cutoff_13m
        ).delete()
        self.stdout.write(f"✓ {deleted_webhooks[0]} webhook events supprimés")

        # 2. Purger logs email (13 mois)
        deleted_emails = EmailLog.objects.filter(
            sent_at__lt=cutoff_13m
        ).delete()
        self.stdout.write(f"✓ {deleted_emails[0]} email logs supprimés")

        # 3. Hard delete accounts anonymisés (10 ans)
        cutoff_10y = now - timedelta(days=3650)
        accounts = Account.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_10y
        )
        for account in accounts:
            # Vérifier que tous les devis sont >10 ans
            if not account.quotes.filter(created_at__gte=cutoff_10y).exists():
                account.user.delete()  # Cascade
                self.stdout.write(f"✓ Account {account.id} supprimé (>10 ans)")

        # 4. Hard delete clients anonymisés (10 ans après dernière transaction)
        clients = Client.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_10y
        )
        for client in clients:
            if not client.quotes.filter(created_at__gte=cutoff_10y).exists():
                client.hard_delete()  # Contourner soft delete
                self.stdout.write(f"✓ Client {client.id} supprimé (>10 ans)")

        self.stdout.write(self.style.SUCCESS("✓ Politique de rétention appliquée"))
```

**Configuration CRON:**
```bash
# Lancer tous les dimanches à 3h du matin
0 3 * * 0 cd /app && python manage.py apply_retention_policy
```

### 3.5 Minimisation de l'Email Tracking

**Recommandations:**

1. **Ne PAS utiliser de tracking pixels pour les emails professionnels B2B sensibles**
   - Alternative: Demander confirmation de réception explicite

2. **Si tracking nécessaire (commercial):**
   - Utiliser un service avec anonymisation IP (Mailgun, SendGrid avec IP masquée)
   - Stocker uniquement: `opened` (boolean), `opened_at` (timestamp)
   - Ne JAMAIS stocker: IP, user-agent, localisation

3. **Implementation Example (Mailgun):**
   ```python
   # apps/email/services/mailgun_service.py

   def send_quote_email(quote, recipient_email):
       tracking_token = uuid.uuid4()

       # Email avec tracking limité
       mailgun.messages.create(
           from_=settings.MAILGUN_FROM,
           to=recipient_email,
           subject=f"Devis {quote.reference}",
           html=render_email_template(quote, tracking_token),
           o_tracking=True,  # Open tracking
           o_tracking_clicks=False,  # PAS de click tracking (éviter risque RGPD)
           o_tracking_opens=True,  # Open tracking uniquement
       )

       # Logs minimalistes
       EmailLog.objects.create(
           quote=quote,
           recipient_email=recipient_email,
           tracking_token=tracking_token,
           sent_at=timezone.now(),
           delivery_status='sent',
           provider='mailgun',
       )
   ```

4. **Webhooks Mailgun (events):**
   ```python
   @require_POST
   def mailgun_webhook(request):
       # Valider signature Mailgun
       if not verify_mailgun_signature(request):
           return HttpResponseForbidden()

       event_type = request.POST.get('event')
       tracking_token = request.POST.get('user-variables[tracking_token]')

       if event_type == 'opened':
           EmailLog.objects.filter(tracking_token=tracking_token).update(
               opened_at=timezone.now()
           )
           # NE PAS stocker l'IP/user-agent du webhook

       return HttpResponse('OK')
   ```

### 3.6 Sécurité de la Signature Électronique

**Recommandations DocuSign:**

1. **Configuration du compte DocuSign:**
   - Activer le niveau de signature **"Advanced (eIDAS qualified)"** pour conformité européenne
   - Activer l'audit trail complet (obligatoire)
   - Conserver les certificats de signature

2. **Données à collecter (minimum eIDAS):**
   - ✅ Nom/prénom signataire
   - ✅ Email signataire
   - ✅ Timestamp signature (UTC)
   - ✅ IP address signataire (OBLIGATOIRE eIDAS Art. 25)
   - ✅ Certificat de signature (PDF)
   - ✅ Hash du document (SHA-256)
   - ❌ Géolocalisation GPS (ÉVITER - non nécessaire)

3. **Workflow de signature:**
   ```python
   def create_signature_request(quote, client_email):
       # Générer le PDF du devis
       pdf_file = generate_quote_pdf(quote)
       pdf_hash = hashlib.sha256(pdf_file.read()).hexdigest()

       # Créer l'envelope DocuSign
       envelope = docusign_client.envelopes.create(
           account_id=settings.DOCUSIGN_ACCOUNT_ID,
           envelope_definition={
               'emailSubject': f'Signature du devis {quote.reference}',
               'documents': [{
                   'documentBase64': base64.b64encode(pdf_file.read()),
                   'name': f'Devis_{quote.reference}.pdf',
                   'fileExtension': 'pdf',
                   'documentId': '1',
               }],
               'recipients': {
                   'signers': [{
                       'email': client_email,
                       'name': quote.client.name,
                       'recipientId': '1',
                       'routingOrder': '1',
                   }],
               },
               'status': 'sent',
           }
       )

       # Enregistrer la demande de signature
       SignatureRequest.objects.create(
           quote=quote,
           requester=quote.owner,
           docusign_envelope_id=envelope.envelope_id,
           document_hash_at_signing=pdf_hash,
           status='sent',
           sent_at=timezone.now(),
       )
   ```

4. **Webhook DocuSign (signature completée):**
   ```python
   @require_POST
   def docusign_webhook(request):
       # Valider la signature HMAC
       if not verify_docusign_signature(request):
           return HttpResponseForbidden()

       event_data = json.loads(request.body)
       envelope_id = event_data['data']['envelopeId']
       event_type = event_data['event']

       if event_type == 'envelope-completed':
           # Récupérer le certificat de signature
           certificate_pdf = docusign_client.envelopes.get_certificate(
               account_id=settings.DOCUSIGN_ACCOUNT_ID,
               envelope_id=envelope_id,
           )

           # Sauvegarder le certificat
           signature_request = SignatureRequest.objects.get(
               docusign_envelope_id=envelope_id
           )
           signature_request.certificate_pdf.save(
               f'certificate_{envelope_id}.pdf',
               ContentFile(certificate_pdf),
           )
           signature_request.status = 'signed'
           signature_request.signed_at = timezone.now()
           signature_request.save()

           # Mettre à jour le devis
           quote = signature_request.quote
           quote.status = Quote.Status.ACCEPTED
           quote.accepted_at = timezone.now()
           quote.save()

       return HttpResponse('OK')
   ```

### 3.7 Audit et Logging (Traçabilité RGPD)

**Implémentation d'un système d'audit pour les actions sensibles:**

```python
# apps/core/models/audit.py

class AuditLog(models.Model):
    """Log des actions sensibles pour conformité RGPD"""

    class Action(models.TextChoices):
        ACCOUNT_CREATED = 'account_created', 'Compte créé'
        ACCOUNT_DELETED = 'account_deleted', 'Compte supprimé'
        ACCOUNT_ANONYMIZED = 'account_anonymized', 'Compte anonymisé'
        CLIENT_CREATED = 'client_created', 'Client créé'
        CLIENT_DELETED = 'client_deleted', 'Client supprimé'
        CLIENT_ANONYMIZED = 'client_anonymized', 'Client anonymisé'
        QUOTE_SENT = 'quote_sent', 'Devis envoyé'
        QUOTE_SIGNED = 'quote_signed', 'Devis signé'
        PAYMENT_RECEIVED = 'payment_received', 'Paiement reçu'
        DATA_EXPORT_REQUESTED = 'data_export_requested', 'Export données demandé'
        DATA_DELETION_REQUESTED = 'data_deletion_requested', 'Suppression données demandée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    action = models.CharField(max_length=50, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
    )
    target_model = models.CharField(max_length=50)  # ex: 'Account', 'Client'
    target_id = models.UUIDField()
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_audit_log'
        indexes = [
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['target_model', 'target_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"
```

**Conservation des audit logs:**
- **10 ans** (traçabilité légale)
- Ne PAS anonymiser (nécessaire pour preuves en cas de litige RGPD)

### 3.8 Export des Données (Art. 20 RGPD - Portabilité)

**Implémentation d'un endpoint d'export RGPD:**

```python
# apps/user/views/gdpr_views.py

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    """Export complet des données de l'utilisateur (RGPD Art. 20)"""
    user = request.user

    # Collecter toutes les données
    data = {
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'profile': {
            'phone': user.profile.phone,
            'role': user.profile.role,
            'created_at': user.profile.created_at.isoformat(),
        },
        'accounts': [
            {
                'display_name': acc.display_name,
                'legal_form': acc.legal_form,
                'legal_id': acc.legal_id,
                'created_at': acc.created_at.isoformat(),
            }
            for acc in user.accounts.all()
        ],
        'clients': [
            {
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
                'created_at': client.created_at.isoformat(),
            }
            for account in user.accounts.all()
            for client in account.clients.all()
        ],
        'quotes': [
            {
                'reference': quote.reference,
                'title': quote.title,
                'total': str(quote.total),
                'currency': quote.currency,
                'status': quote.status,
                'issue_date': quote.issue_date.isoformat(),
                'created_at': quote.created_at.isoformat(),
            }
            for account in user.accounts.all()
            for quote in account.quotes.all()
        ],
    }

    # Log de l'export
    AuditLog.objects.create(
        action=AuditLog.Action.DATA_EXPORT_REQUESTED,
        actor=user,
        target_model='User',
        target_id=user.id,
        ip_address=get_client_ip(request),
    )

    return JsonResponse(data, json_dumps_params={'indent': 2})
```

---

## 4. Documentation et Conformité

### 4.1 Mentions Légales et Politique de Confidentialité

**À créer/mettre à jour:**

1. **Politique de Confidentialité** (`/legal/privacy`)
   - Données collectées (cf. cartographie ci-dessus)
   - Finalités de traitement
   - Bases légales (RGPD Art. 6)
   - Durées de conservation
   - Droits des utilisateurs (accès, rectification, suppression, portabilité)
   - Coordonnées du DPO (si >250 employés OU traitement sensible)

2. **Conditions Générales d'Utilisation** (`/legal/terms`)
   - Responsabilités de l'utilisateur
   - Propriété intellectuelle
   - Limitation de responsabilité

3. **Cookie Policy** (`/legal/cookies`)
   - Cookies strictement nécessaires (authentification, CSRF)
   - Cookies analytics (Google Analytics avec anonymisation IP)
   - Bannière de consentement (conforme ePrivacy)

### 4.2 Registre des Traitements (Art. 30 RGPD)

**Obligatoire si >250 employés OU traitement sensible.**

**Format recommandé (Excel/PDF):**

| Finalité | Base Légale | Catégories de Données | Durée de Conservation | Destinataires | Transferts Hors UE |
|----------|-------------|----------------------|----------------------|---------------|-------------------|
| Gestion des comptes utilisateurs | Exécution du contrat (Art. 6.1.b) | Email, nom, prénom, téléphone | Durée du compte + 5 ans | Aucun | Non |
| Facturation et comptabilité | Obligation légale (Art. 6.1.c) | SIRET, devis, montants | 10 ans | Aucun | Non |
| Paiement par carte bancaire | Exécution du contrat (Art. 6.1.b) | Tokens Stripe (card_XXX) | Durée abonnement + 10 ans | Stripe (USA - Privacy Shield invalidé, utiliser SCCs) | Oui (Stripe - USA) |
| Signature électronique | Obligation légale eIDAS (Art. 6.1.c) | Nom, email, IP, certificat | 10 ans | DocuSign (USA) | Oui (DocuSign - USA) |
| Envoi d'emails transactionnels | Exécution du contrat (Art. 6.1.b) | Email, logs d'envoi | 13 mois | Mailgun (USA) | Oui (Mailgun - USA) |

### 4.3 Transferts Hors UE (Art. 44-50 RGPD)

**Services tiers avec transferts hors UE:**

1. **Stripe (USA)**
   - Mécanisme: **Standard Contractual Clauses (SCCs)** + Stripe DPA
   - Documentation: https://stripe.com/legal/dpa
   - Impact Privacy Shield invalide (Schrems II): SCCs suffisent

2. **DocuSign (USA)**
   - Mécanisme: **SCCs** + DocuSign DPA
   - Documentation: https://www.docusign.com/company/trust/dpa

3. **Mailgun (USA) / SendGrid (USA)**
   - Mécanisme: **SCCs** + DPA fournisseur
   - Alternative EU: **Brevo (France)**, **Postmark (EU datacenters)**

**Recommandation:** Privilégier des fournisseurs EU si possible (Brevo pour email, Stripe EU datacenters pour paiement).

### 4.4 Analyse d'Impact (AIPD/DPIA)

**Obligatoire si traitement "à haut risque" (Art. 35 RGPD):**
- Signature électronique qualifiée (données sensibles: IP, certificats)
- Paiements récurrents (profiling, suivi comportemental)

**Éléments d'une AIPD:**
1. Description du traitement (signature électronique)
2. Nécessité et proportionnalité (justification légale)
3. Risques pour les droits des personnes (usurpation, fuite de données)
4. Mesures de sécurité (chiffrement, accès restreints, audits)
5. Validation par le DPO (si applicable)

---

## 5. Checklist de Mise en Conformité

### 5.1 Backend (Priorité 1 - Critique)

- [ ] **Étendre Soft Delete**
  - [ ] Ajouter `SoftDeleteModel` à `Client` (apps/client/models.py)
  - [ ] Ajouter `SoftDeleteModel` à `Account` (apps/user/models/account.py)
  - [ ] Créer migration Django

- [ ] **Chiffrement des Données Sensibles**
  - [ ] Installer `django-fernet-fields` ou `django-cryptography`
  - [ ] Chiffrer `Client.email`, `Client.phone`, `Client.vat_number`
  - [ ] Chiffrer `Account.legal_id` (SIRET)
  - [ ] Configurer `FIELD_ENCRYPTION_KEY` (secrets manager)

- [ ] **Système d'Audit**
  - [ ] Créer modèle `AuditLog` (apps/core/models/audit.py)
  - [ ] Logger les actions sensibles (création/suppression compte, client)
  - [ ] Ajouter endpoint admin pour consulter les logs

- [ ] **Politique de Rétention**
  - [ ] Créer command `apply_retention_policy` (management command)
  - [ ] Implémenter purge automatique (13 mois logs, 10 ans comptabilité)
  - [ ] Configurer CRON hebdomadaire

- [ ] **Export RGPD**
  - [ ] Créer endpoint `/api/user/export-data/` (JSON export)
  - [ ] Tester avec utilisateur réel
  - [ ] Ajouter bouton "Télécharger mes données" dans l'UI

- [ ] **Anonymisation "Droit à l'Oubli"**
  - [ ] Créer fonction `anonymize_account_for_deletion()`
  - [ ] Créer fonction `anonymize_client_for_deletion()`
  - [ ] Tester sur données de dev

### 5.2 Backend (Priorité 2 - Fonctionnalités Futures)

- [ ] **Email Tracking**
  - [ ] Créer modèle `EmailLog` avec champs minimaux (pas d'IP)
  - [ ] Intégrer Mailgun/SendGrid avec webhooks
  - [ ] Implémenter purge 13 mois

- [ ] **Signature Électronique**
  - [ ] Créer modèles `SignatureRequest`, `Signer`
  - [ ] Intégrer DocuSign API (OAuth2)
  - [ ] Stocker certificats de signature (S3 chiffré)
  - [ ] Logger IP signataire (obligatoire eIDAS)

- [ ] **Paiement Stripe**
  - [ ] Créer modèles `StripeCustomer`, `StripeSubscription`, `StripePaymentMethod`, `StripeInvoice`, `StripeWebhookEvent`
  - [ ] Intégrer webhooks Stripe (signature validation)
  - [ ] Implémenter purge webhooks (13 mois)
  - [ ] Ne JAMAIS stocker numéros de carte (tokens uniquement)

### 5.3 Frontend (Priorité 1)

- [ ] **Bannière de Consentement Cookies**
  - [ ] Implémenter avec `react-cookie-consent`
  - [ ] Cookies strictement nécessaires uniquement (pas d'analytics sans consentement)

- [ ] **Interface "Mon Compte"**
  - [ ] Ajouter bouton "Télécharger mes données" (export RGPD)
  - [ ] Ajouter bouton "Supprimer mon compte" (avec confirmation)
  - [ ] Afficher la date de dernière connexion

- [ ] **Warning sur Métadonnées Client**
  - [ ] Ajouter disclaimer dans formulaire Client: "Ne stockez pas de données sensibles"

### 5.4 Légal et Documentation

- [ ] **Politique de Confidentialité**
  - [ ] Rédiger page `/legal/privacy` (utiliser cartographie ci-dessus)
  - [ ] Mentionner tous les sous-traitants (Stripe, DocuSign, Mailgun)
  - [ ] Expliquer les transferts hors UE (SCCs)

- [ ] **CGU**
  - [ ] Rédiger page `/legal/terms`

- [ ] **Cookie Policy**
  - [ ] Rédiger page `/legal/cookies`

- [ ] **Registre des Traitements** (si >250 employés)
  - [ ] Créer fichier Excel/PDF avec tous les traitements
  - [ ] Mettre à jour annuellement

- [ ] **DPA avec Sous-traitants**
  - [ ] Signer DPA avec Stripe
  - [ ] Signer DPA avec DocuSign
  - [ ] Signer DPA avec Mailgun/SendGrid (ou alternative EU)

- [ ] **AIPD** (si signature qualifiée)
  - [ ] Rédiger AIPD pour signature électronique
  - [ ] Validation par DPO (si applicable)

### 5.5 Sécurité et Infrastructure

- [ ] **HTTPS Obligatoire**
  - [ ] Forcer HTTPS (redirect HTTP → HTTPS)
  - [ ] Configurer HSTS (Strict-Transport-Security)

- [ ] **Chiffrement Fichiers**
  - [ ] Activer S3 SSE-KMS pour PDFs et certificats
  - [ ] Signed URLs temporaires (15 min) pour téléchargements

- [ ] **Secrets Management**
  - [ ] Migrer secrets vers AWS Secrets Manager / Vault
  - [ ] Rotation annuelle de `FIELD_ENCRYPTION_KEY`

- [ ] **Monitoring et Alertes**
  - [ ] Configurer alertes Sentry pour erreurs RGPD (ex: échec chiffrement)
  - [ ] Monitoring des accès aux données sensibles

---

## 6. Questions Non Résolues

1. **DPO (Data Protection Officer):**
   - FreelanSign a-t-il >250 employés OU traite des données sensibles à grande échelle ?
   - Si oui: Nomination d'un DPO obligatoire (Art. 37 RGPD)
   - Si non: Recommandé de désigner un responsable RGPD interne

2. **Choix du Provider Email:**
   - **Mailgun/SendGrid (USA)**: Nécessite SCCs, tracking IP possible
   - **Brevo (France)**: Alternative EU, pas de transfert hors UE, tracking limité
   - **Recommandation**: Privilégier **Brevo** pour éviter transferts hors UE

3. **Signature Électronique - Niveau eIDAS:**
   - **Simple**: Pas d'exigences légales (mais faible valeur probatoire)
   - **Avancée** (AdES): Certificat qualifié + IP obligatoire
   - **Qualifiée** (QES): Équivalent signature manuscrite (exigences strictes)
   - **Recommandation**: **Avancée (AdES)** via DocuSign suffisant pour devis B2B

4. **Géolocalisation des Signatures:**
   - Certains fournisseurs proposent géolocalisation GPS en plus de l'IP
   - **Recommandation**: **NE PAS activer** (risque RGPD excessif, non requis eIDAS)

5. **Analytics et Tracking Utilisateurs:**
   - Google Analytics avec anonymisation IP ?
   - Alternative: Plausible Analytics (EU, privacy-first, pas de cookies)
   - **Recommandation**: **Plausible** ou **Matomo** (hébergé en EU)

6. **Backup et Restauration:**
   - Les backups contiennent des données chiffrées → clés de chiffrement doivent être backupées séparément
   - Politique de rétention des backups: 30 jours (puis suppression automatique)

---

## 7. Résumé Exécutif

### 7.1 Données Actuelles: Conformité Globale ✅

**Points forts:**
- Architecture propre avec séparation User/Account/Client
- Timestamps de traçabilité présents partout
- Soft delete déjà implémenté sur Catalog (Prestation)
- Pas de données sensibles (Art. 9 RGPD) collectées

**Points à améliorer (critiques):**
- ⚠️ Manque de soft delete sur `Client` et `Account`
- ⚠️ Pas de chiffrement des données sensibles (SIRET, emails, téléphones)
- ⚠️ Pas de système d'audit pour traçabilité RGPD
- ⚠️ Pas de politique de rétention automatisée

### 7.2 Fonctionnalités Futures: Risques Identifiés ⚠️

**Email Tracking:**
- ✅ Acceptable si pas de stockage IP/user-agent destinataire
- ⚠️ Nécessite purge automatique (13 mois)

**Signature Électronique (eIDAS):**
- ⚠️ IP address du signataire: **OBLIGATOIRE** (Art. 25 eIDAS)
- ✅ Conservation 10 ans justifiée (valeur probatoire)
- 🚫 Géolocalisation GPS: **À ÉVITER** (risque excessif)

**Paiement Stripe:**
- ✅ Tokens uniquement (pas de numéros de carte)
- ⚠️ Transfert hors UE (USA) → SCCs obligatoires
- 🚫 Ne JAMAIS stocker: CVV, PAN complet, coordonnées bancaires

### 7.3 Priorités d'Implémentation

**Phase 1 (Avant Lancement Production):**
1. Soft delete sur Client + Account
2. Chiffrement des données sensibles (SIRET, emails, téléphones)
3. Politique de confidentialité + CGU
4. Bannière cookies frontend

**Phase 2 (Avant Email Tracking):**
1. Modèle `EmailLog` avec purge 13 mois
2. Intégration Brevo (EU) ou Mailgun (avec anonymisation)
3. Système d'audit (AuditLog)

**Phase 3 (Avant Signature Électronique):**
1. Modèles `SignatureRequest` + `Signer`
2. Intégration DocuSign (SCCs + DPA)
3. Stockage certificats de signature (S3 chiffré)
4. AIPD (Analyse d'Impact)

**Phase 4 (Avant Paiement Stripe):**
1. Modèles `StripeCustomer`, `StripeSubscription`, etc.
2. Webhooks Stripe avec purge 13 mois
3. DPA Stripe + SCCs
4. Export RGPD complet (inclure données Stripe)

### 7.4 Ressources et Outils

**Bibliothèques Python:**
- `django-fernet-fields` ou `django-cryptography`: Chiffrement colonne
- `stripe-python`: SDK Stripe officiel
- `docusign-python-client`: SDK DocuSign officiel

**Services Recommandés:**
- Email: **Brevo** (France, RGPD-friendly)
- Signature: **DocuSign** (leader, SCCs disponibles)
- Paiement: **Stripe** (leader, DPA solide)
- Analytics: **Plausible** (EU, sans cookies)

**Documentation:**
- CNIL: https://www.cnil.fr/fr/reglement-europeen-protection-donnees
- eIDAS: https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A32014R0910
- Stripe DPA: https://stripe.com/legal/dpa
- DocuSign DPA: https://www.docusign.com/company/trust/dpa

---

**Fin du document SPECIFICATIONS_RGPD.md**

---

**Prochaines Étapes:**
1. Valider ce document avec un DPO ou avocat spécialisé RGPD
2. Prioriser les tâches selon le roadmap
3. Implémenter Phase 1 avant mise en production
4. Mettre à jour ce document à chaque nouvelle fonctionnalité impactant les données personnelles

**Auteur**: Claude AI (DPO virtuel)
**Validé par**: [À compléter par un DPO humain]
**Dernière mise à jour**: 2025-12-09
