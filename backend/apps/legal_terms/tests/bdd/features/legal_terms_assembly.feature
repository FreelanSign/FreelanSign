Feature: Assemblage des termes légaux à partir du template et du profil
  En tant qu'auto-entrepreneur
  Je veux que mes CGV soient construites à partir d'un template légal
  Et de mes préférences de profil
  Afin de garantir que les clauses obligatoires sont toujours présentes
  Et que mes personnalisations sont correctement appliquées.

  Background:
    Étant donné un template légal avec les clauses suivantes
      | identifier      | category   | default_title                   | default_body                                | default_order | default_is_active |
      | payment_terms   | mandatory  | Conditions de paiement          | Le paiement est dû sous 30 jours.           | 1             | true              |
      | warranty        | optional   | Garantie                         | Le prestataire fournit une garantie limitée.| 2             | true              |
      | gdpr            | mandatory  | Données personnelles (RGPD)     | Traitement des données conforme au RGPD.    | 3             | true              |

  Scenario: Assemblage sans overrides - on obtient exactement les clauses du template
    Étant donné un profil légal sans overrides
    Quand j'assemble les termes légaux
    Alors j'obtiens 3 clauses rendues
    Et la clause "payment_terms" est présente et obligatoire
    Et la clause "warranty" est présente et optionnelle
    Et la clause "gdpr" est présente et obligatoire

  Scenario: Désactiver une clause optionnelle - elle disparaît de l'assemblage
    Étant donné un profil légal avec les overrides suivants
      | identifier    | is_active | custom_title | custom_body | custom_order |
      | warranty      | false     |              |             |              |
    Quand j'assemble les termes légaux
    Alors j'obtiens 2 clauses rendues
    Et la clause "payment_terms" est présente et obligatoire
    Et la clause "gdpr" est présente et obligatoire
    Et la clause "warranty" n'est pas présente dans le résultat

  Scenario: Tenter de désactiver une clause obligatoire - erreur métier
    Étant donné un profil légal avec les overrides suivants
      | identifier      | is_active | custom_title | custom_body | custom_order |
      | payment_terms   | false     |              |             |              |
    Quand j'essaie d'assembler les termes légaux
    Alors une erreur de modification de clause obligatoire est levée
