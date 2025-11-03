# scripts/precommit.sh

#!/bin/bash

# Exécuter black, sort dans le répertoire backend
echo "--------------------------------------------------"
echo "Exécution de black et isort dans le répertoire backend"
echo "--------------------------------------------------"
cd backend && source venv/bin/activate
echo "✅  Venv activée"
echo "Exécution de black..."
black .
echo "Exécution de isort..."
isort .

deactivate

echo "--------------------------------------------------"
echo "✅  Black et isort terminés"
echo "--------------------------------------------------"

# front end
echo "--------------------------------------------------"
echo "Exécution de formatage et linting dans le répertoire frontend"
echo "--------------------------------------------------"
cd ../frontend
echo "Exécution de formatage..."
pnpm run format
echo "Exécution de linting..."
pnpm run lint
echo "--------------------------------------------------"
echo "✅  Formatage et linting terminés"
echo "--------------------------------------------------"

echo "--------------------------------------------------"
echo "Build frontend..."
echo "--------------------------------------------------"
pnpm run build
echo "--------------------------------------------------"
echo "✅  Build terminé"
echo "--------------------------------------------------"

# print de sortie
echo "--------------------------------------------------"
echo "✅  Precommit terminé"
echo "--------------------------------------------------"
