# Account Store – BDD

## Rôle

Centraliser l'état lié aux comptes (Account) côté frontend :

- liste des comptes de l'utilisateur
- compte actif
- persistance du compte actif entre les sessions

## Scénarios

### Scénario 1 – Persistance du compte actif

Étant donné qu'un utilisateur a sélectionné un compte `acc_123`
Quand il recharge l'application
Alors le store initialise `activeAccountId` avec `acc_123`.

### Scénario 2 – Sélection manuelle du compte

Étant donné qu'aucun compte n'est encore sélectionné
Quand l'utilisateur choisit un compte `acc_456` dans l'UI
Alors le store met à jour `activeAccountId` à `acc_456`
Et cette valeur est persistée dans le stockage local.

### Scénario 3 – Auto-sélection du premier compte

Étant donné qu'aucun `activeAccountId` n'est défini
Et que le backend renvoie la liste de comptes `[acc_1, acc_2, …]`
Quand on met à jour la liste des comptes dans le store
Et qu'on appelle `selectFirstAccountIfNeeded()`
Alors le store définit `activeAccountId` à `acc_1`.
