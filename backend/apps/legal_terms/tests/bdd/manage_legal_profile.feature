# language: fr
Fonctionnalité: Gestion du profil légal
  En tant qu'utilisateur
  Je veux gérer mes conditions légales
  Afin de personnaliser mes CGV pour mes devis

  Contexte:
    Étant donné un template légal actif "CGV Auto-Entrepreneur FR" avec les clauses:
      | identifiant      | catégorie    | titre                   | contenu                      | ordre | actif |
      | payment_terms    | mandatory    | Conditions de paiement  | Paiement sous 30 jours       | 1     | true  |
      | warranty         | optional     | Garantie                | Garantie de 6 mois           | 2     | false |
      | liability        | optional     | Responsabilité          | Limitation de responsabilité | 3     | true  |

  Scénario: L'utilisateur active une clause optionnelle et la voit dans l'aperçu
    Étant donné un compte avec les données légales requises
    Et je suis connecté
    Quand j'active la clause "warranty"
    Et je consulte l'aperçu des conditions légales
    Alors l'aperçu contient la clause "warranty"
    Et la clause "warranty" est marquée comme personnalisée

  Scénario: L'utilisateur personnalise le texte d'une clause et le voit dans l'aperçu
    Étant donné un compte avec les données légales requises
    Et je suis connecté
    Quand je modifie le titre de la clause "liability" en "Responsabilité limitée"
    Et je modifie le contenu de la clause "liability" en "Notre responsabilité est limitée au montant du devis"
    Et je consulte l'aperçu des conditions légales
    Alors l'aperçu contient le titre "Responsabilité limitée"
    Et l'aperçu contient le texte "Notre responsabilité est limitée au montant du devis"
    Et la clause "liability" est marquée comme personnalisée

  Scénario: L'utilisateur ne peut pas désactiver une clause obligatoire
    Étant donné un compte avec les données légales requises
    Et je suis connecté
    Quand j'essaie de désactiver la clause "payment_terms"
    Alors je reçois une erreur indiquant que les clauses obligatoires ne peuvent pas être désactivées

  Scénario: L'utilisateur désactive une clause optionnelle
    Étant donné un compte avec les données légales requises
    Et je suis connecté
    Quand je désactive la clause "liability"
    Et je consulte l'aperçu des conditions légales
    Alors l'aperçu ne contient pas la clause "liability"

  Scénario: Les variables sont substituées dans l'aperçu
    Étant donné un compte avec les données légales:
      | champ          | valeur              |
      | SIRET          | 12345678901234      |
      | nom            | ACME Corp           |
      | email          | contact@acme.fr     |
      | téléphone      | +33 1 23 45 67 89   |
    Et je suis connecté
    Et le template contient une clause avec "SIRET: {{SIRET}}, Contact: {{BUSINESS_NAME}}"
    Quand je consulte l'aperçu des conditions légales
    Alors l'aperçu contient "SIRET: 12345678901234"
    Et l'aperçu contient "Contact: ACME Corp"
    Et l'aperçu ne contient pas "{{"
