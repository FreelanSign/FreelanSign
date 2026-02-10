# Architecture FreelanSign

## 1. Context Map (Vue Globale)

Ce diagramme présente les principaux Bounded Contexts de l'application et leurs relations.

```mermaid
graph TD
    User[Auth / Identité]
    Quote[Devis / Facturation]
    Client[Clients / CRM]
    Catalog[Catalogue / Prestations]
    Branding[Branding / Thèmes]
    Email[Email / Notifications]
    Core[Core / Shared Kernel]

    %% Relations
    Quote -->|Dépend de| User
    Quote -->|Dépend de| Client
    Quote -->|Référence| Catalog
    Quote -->|Utilise| Branding

    Catalog -->|Appartient à| User
    Branding -->|Appartient à| User
    Client -->|Appartient à| User

    User -->|Utilise| Email
    Quote -->|Utilise| Email

    User -.->|Hérite de| Core
    Quote -.->|Hérite de| Core
    Catalog -.->|Hérite de| Core
```

## 2. Domain Model (Diagrammes de Classes)

### Auth / Identité / Profil Pro

Gestion des utilisateurs, de leurs profils personnels et de leurs entités professionnelles.

```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String password
    }

    class Profile {
        +String first_name
        +String last_name
        +Role role
    }

    class ProfessionalUser {
        +String name
        +StatusJuridique status_juridique
        +BigInt tjm_cents
        +String number_pro
    }

    class Area {
        +String name
    }

    User "1" -- "1" Profile : has
    User "1" -- "1" ProfessionalUser : has
    ProfessionalUser "*" -- "1" Area : domaine
```

### Devis / Clients / Prestations

Cœur du métier : création de devis pour des clients basés sur des prestations.

```mermaid
classDiagram
    class Quote {
        +UUID id
        +String reference
        +Status status
        +Decimal total
        +Date issue_date
        +Date valid_until
        +recalculate_totals()
    }

    class QuoteLineItem {
        +String description
        +Decimal qty
        +Decimal unit_price
        +Decimal tax_rate
        +Decimal discount
        +Decimal line_total
        +pre_tax_total()
    }

    class Client {
        +String name
        +String email
        +String address
        +String vat_number
    }

    class PaymentTerms {
        +String name
        +Int days
    }

    class Prestation {
        +String name
        +String description
        +Int weight_days
        +BigInt default_rate_cents
        +Status status
    }

    Quote "1" -- "*" QuoteLineItem : contains
    Quote "*" -- "1" Client : billed to
    Quote "*" -- "0..1" PaymentTerms : uses
    QuoteLineItem ..> Prestation : derived from (metadata)
```

### Branding

Personnalisation des documents.

```mermaid
classDiagram
    class BrandTheme {
        +String name
        +Boolean is_active
        +JSON colors
        +JSON typography
        +File logo
    }

    class ProfessionalUser {
    }

    ProfessionalUser "1" -- "*" BrandTheme : owns
```

## 3. State Machines (Lifecycles)

### Quote Lifecycle

Cycle de vie d'un devis.

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> SENT : Envoyer
    DRAFT --> CANCELLED : Annuler
    SENT --> ACCEPTED : Client accepte
    SENT --> REJECTED : Client refuse
    SENT --> EXPIRED : Date validité dépassée
    ACCEPTED --> PAID : Paiement reçu
    ACCEPTED --> CANCELLED : Annuler
    PAID --> [*]
    REJECTED --> [*]
    CANCELLED --> [*]
    EXPIRED --> [*]
```

### Prestation Lifecycle

Cycle de vie d'une prestation catalogue.

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> ACTIVE : Activer
    ACTIVE --> ARCHIVED : Archiver
    ARCHIVED --> ACTIVE : Restaurer
    ARCHIVED --> [*]
```

## 4. Séquences Métier Clés

### Inscription + Démarrage (Simplifié)

```mermaid
sequenceDiagram
    actor Visitor
    participant API as API Gateway
    participant UserDomain as User Domain
    participant DB as Database
    participant Email as Email Service

    Visitor->>API: POST /register (email, password)
    API->>UserDomain: Create User
    UserDomain->>DB: Save User & Profile
    UserDomain->>Email: Send Welcome Email
    Email-->>Visitor: Email received
    UserDomain-->>API: User Created
    API-->>Visitor: 201 Created + Token
```

### Création d'un Devis

```mermaid
sequenceDiagram
    actor Pro as Professional
    participant API
    participant QuoteDomain as Quote Domain
    participant CatalogDomain as Catalog Domain
    participant DB

    Pro->>API: POST /quotes (client_id)
    API->>QuoteDomain: Create Draft Quote
    QuoteDomain->>DB: Save Quote (DRAFT)
    QuoteDomain-->>API: Quote ID

    Pro->>API: POST /quotes/{id}/items (prestation_id, qty)
    API->>CatalogDomain: Get Prestation Details
    CatalogDomain-->>API: Prestation Data (Price, Desc)
    API->>QuoteDomain: Add Line Item
    QuoteDomain->>QuoteDomain: Recalculate Totals
    QuoteDomain->>DB: Save Line Item & Update Quote
    QuoteDomain-->>API: Updated Quote
```

## 5. Éléments Non Résolus / Manquants

Les éléments suivants ont été demandés mais n'ont pas été trouvés dans la base de code actuelle :

- **Billing / Subscription Domain** :
    - Pas de modèles `Plan`, `Subscription`, `Invoice` (pour la facturation de l'abonnement SaaS lui-même) trouvés dans `backend/apps`.
    - Il semble que la gestion des abonnements SaaS (FreelanSign facturant le Freelance) ne soit pas encore implémentée ou se trouve dans un dépôt séparé/module non scanné.
- **CRM Avancé** :
    - Le module `Client` est très simple (Nom, Email, Adresse). Pas de gestion complexe de contacts multiples ou d'historique d'interactions au-delà des devis.
