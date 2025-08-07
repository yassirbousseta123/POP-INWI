#!/bin/bash

echo "🚀 Lancement du tableau de bord BGU-ONE..."
echo ""
echo "📦 Installation des dépendances si nécessaire..."
pip install -r requirements.txt --quiet

echo ""
echo "🏃 Démarrage de l'application..."
echo ""
echo "📊 Le tableau de bord sera accessible à l'adresse:"
echo "   👉 http://localhost:8501"
echo ""
echo "Pour arrêter l'application, appuyez sur Ctrl+C"
echo ""

streamlit run app.py