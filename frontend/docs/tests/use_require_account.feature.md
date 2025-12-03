# useRequireAccount – BDD

## Rôle

Empêcher l'accès aux pages dépendantes d'un compte professionnel lorsqu'aucun compte n'est disponible,
en redirigeant automatiquement l'utilisateur vers `/onboarding-account`.
Laisser l'utilisateur sur la page lorsque un compte existe (via liste de comptes ou `activeAccountId`)
ou lorsque la page est encore en cours de chargement.

## Scénarios

### Scénario 1 – Redirection quand aucun compte n'existe

Étant donné qu'aucun compte n'est disponible (`accounts = []`)
Et que `activeAccountId = null`
Et que la page a fini de charger (`loading = false`)
Quand le hook `useRequireAccount` est utilisé sur cette page
Alors l'utilisateur est redirigé vers `/onboarding-account`.

### Scénario 2 – Pas de redirection pendant le chargement

Étant donné qu'aucun compte n'est disponible (`accounts = []`)
Et que `activeAccountId = null`
Et que la page est encore en cours de chargement (`loading = true`)
Quand le hook `useRequireAccount` est utilisé sur cette page
Alors aucune redirection n'est déclenchée.

### Scénario 3 – Pas de redirection lorsqu'un compte existe via la liste

Étant donné que la liste de comptes contient au moins un compte (`accounts = [acc_1, …]`)
Et que la page a fini de charger (`loading = false`)
Quand le hook `useRequireAccount` est utilisé sur cette page
Alors aucune redirection n'est déclenchée
Et l'utilisateur reste sur la page courante.

### Scénario 4 – Pas de redirection lorsqu'un compte actif est connu

Étant donné que `accounts = []` (la liste n'est pas encore hydratée)
Et que `activeAccountId = acc_123` (valeur persistée depuis une session précédente)
Et que la page a fini de charger (`loading = false`)
Quand le hook `useRequireAccount` est utilisé sur cette page
Alors aucune redirection n'est déclenchée
Et l'utilisateur reste sur la page courante.

### Scénario 5 – Hook désactivé

Étant donné qu'aucun compte n'est disponible (`accounts = []`)
Et que `activeAccountId = null`
Et que la page a fini de charger (`loading = false`)
Mais que le hook est utilisé avec l'option `enabled = false`
Quand le hook `useRequireAccount` est utilisé sur cette page
Alors aucune redirection n'est déclenchée.

### Scénario 6 – Redirection personnalisée

Étant donné qu'aucun compte n'est disponible (`accounts = []`)
Et que `activeAccountId = null`
Et que la page a fini de charger (`loading = false`)
Quand le hook `useRequireAccount` est utilisé avec `redirectTo = "/custom-onboarding"`
Alors l'utilisateur est redirigé vers `/custom-onboarding`.
