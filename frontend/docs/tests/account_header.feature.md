# Account Header – BDD

## Règle métier

Toutes les requêtes HTTP vers l'API doivent embarquer le header
`X-Account-Id` quand un compte actif est sélectionné côté frontend.

## Scénarios

### Scénario 1 – Account sélectionné

Étant donné qu'un `activeAccountId` est stocké côté frontend
Quand le frontend appelle n'importe quelle route de l'API
Alors la requête contient le header `X-Account-Id` égal à cet id.

### Scénario 2 – Aucun account sélectionné

Étant donné qu'aucun `activeAccountId` n'est stocké
Quand le frontend appelle une route de l'API
Alors la requête ne contient pas de header `X-Account-Id`.

### Scénario 3 – Header déjà fourni

Étant donné qu'un `activeAccountId` est stocké
Et qu'un composant fournit déjà un header `X-Account-Id` dans sa requête
Quand la requête part
Alors le header `X-Account-Id` n’est pas écrasé par l’interceptor.
