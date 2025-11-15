Feature: Préparation d'un email pour un devis

    Scenario: L'utilisateur récupère l'email préparé pour son devis
        Given un utilisateur connecté "alice"
        And un devis "Q-123" appartenant à "alice"
        When elle appelle GET /api/quote/Q-123/prepared-email
        Then la réponse est 200
        And le JSON contient "to", "subject", "body", "template_version"

    Scenario: L'utilisateur n'est pas connecté
        Given un devis "Q-123" appartenant à "alice"
        When elle appelle GET /api/quote/Q-123/prepared-email sans être connectée
        Then la réponse est 401


    Scenario: L'utilisateur n'est pas propriétaire du devis
        Given un utilisateur connecté "bob"
        And un devis "Q-123" appartenant à "alice"
        When il appelle GET /api/quote/Q-123/prepared-email
        Then la réponse est 403

    Scenario: Le devis n'existe pas
        Given un utilisateur connecté "alice"
        When elle appelle GET /api/quote/INVALID_ID/prepared-email
        Then la réponse est 404
