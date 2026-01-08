# Checkpoints Gallery 🎨

Application PyQt6 pour comparer et noter des images IA générées avec différents checkpoints.

## 🚀 Démarrage Rapide

**Windows :**
```bash
1. Lancez INSTALL.BAT (une seule fois)
2. Lancez START.BAT pour démarrer
```

## ✨ Fonctionnalités

- 📁 Chargement d'images par glisser-déposer ou explorateur
- 🔍 Détection automatique des checkpoints depuis les noms de fichiers
- 📑 Onglets multiples pour organiser vos images
- 🔄 Glisser-déposer pour réorganiser les images
- ⭐ Notation avec 5 critères ou plus (modifiable dans le code)
- 🖼️ Vue plein écran avec comparaison côte à côte
- 💾 Export/import des grilles en JSON
- 🎯 Bordures colorées pour meilleur/pire score

## Utilisation

### 📁 Chargement des images
**Dossier de checkpoints**:
1. Cliquer sur "Checkpoints Folder"
2. Sélectionner le dossier contenant les fichiers `.safetensors`
3. Un fichier `checkpoints.txt` sera créé automatiquement
4. Les noms des checkpoints seront extraits des noms de fichiers

**Fichier checkpoints.txt**:
1. Cliquer sur "Checkpoints.txt"
2. Sélectionner un fichier texte contenant la liste des checkpoints (un par ligne)
3. Les noms seront automatiquement associés aux images importées

### ⏳ Gestion des onglets
- **Ajouter un onglet**: Bouton `+` en haut à droite (max 26 onglets: A-Z)
- **Supprimer tous les onglets**: Bouton `-` (recrée automatiquement l'onglet A)
- **Fermer un onglet**: Bouton `×` dans chaque onglet (le premier onglet ne peut pas être supprimé)

**Méthode Drag & Drop**:
- Glisser-déposer des images (PNG, JPG, JPEG, WEBP) dans la zone dédiée
- Glisser-déposer un fichier JSON pour importer une grille sauvegardée
- Cliquer sur la zone pour ouvrir le sélecteur de fichiers

### ⭐ Évaluation des images
Chaque carte d'image dispose de 3 critères personnalisables:
- **beauty**: Qualité esthétique
- **noErrors**: Absence d'erreurs/artefacts
- **loras**: Qualité des LoRAs appliqués
- **Pos prompt / Neg prompt**: Réactivité aux prompts

**États des boutons**:
- Gris: neutre (0 point)
- Vert: positif (+1 point)
- Rouge: négatif (-1 point)

**Système de notation**:
- Le score total s'affiche en haut à droite de chaque carte
- Meilleures/pires images = bordures vertes/rouges

### Organisation des cartes
- **Redimensionner**: Utiliser le slider "Size" (210-600 pixels)
- **Réorganiser**: Maintenir clic gauche sur une carte et la déplacer
- **Supprimer**: Bouton `×` en haut à gauche de chaque carte
- **Détails**: Clic droit pour afficher les détails d'une image
- **Vue plein écran**: Cliquer sur l'image d'une carte

### 🖼️ Vue plein écran
- **Navigation**: Flèches gauche/droite ou boutons `<` / `>`
- **Comparaison**: Sélectionner un autre onglet dans la liste déroulante pour comparer les images côte à côte
- **Séparateur ajustable**: Glisser la ligne verticale pour ajuster la zone de comparaison
- **Fermer**: Touche `Échap` ou bouton de fermeture

### 💾 Export / Import
 **Export**:
1. Cliquer sur "Export"
2. Le fichier JSON sauvegarde: chemins absolus, noms des checkpoints, critères et scores
3. Nom par défaut: `grid-{ONGLET}_{YYYYMMDD-HHMMSS}.json`

 **Import**:
1. Cliquer sur "Import" ou glisser-déposer un fichier JSON
2. Mode configurable dans Options (Ajouter ou Remplacer)
3. Les images manquantes sont ignorées avec un avertissement

### Autres fonctions
- **Clear**: Supprime toutes les cartes de l'onglet actuel
- **Options**: Ouvre le dialogue de configuration (langue, thème, mode d'import)


## ⚙️ Menu Options
Accessible depuis chaque onglet, avant le bouton "Checkpoints Folder". A la fermeture, l'interface est mise à jour automatiquement.

- **Langue**: FR (Français) ou EN (English).
- **Choix du thème**: Dark / Light
- **Mode d'import de grille**: Ajouter ou Remplacer

## Notes techniques
- Il est possible d'ajouter de nouvelles langues.
- La configuration est chargée au démarrage de l'application
- Les changements s'appliquent sans redémarrer
- Les paramètres sont sauvegardés automatiquement dans `config/settings.json`
- Il est possible de modifier la liste des critères.

## Développement

### Ajouter une nouvelle langue
1. Créer un nouveau fichier dans `config/lang/` (ex: `de.py` pour l'allemand)
2. Copier la structure de `fr.py` ou `en.py`
3. Traduire tous les textes dans le dictionnaire **LANG**
4. Modifier `config/config.py` pour inclure la nouvelle langue
5. Ajouter un checkbox dans `OptionsDialog`

### Ajouter un nouveau texte traduisible
1. Ajouter la clé dans `config/lang/fr.py` et `config/lang/en.py`
2. Utiliser `config.get_text('cle')` dans le code
3. Si nécessaire, ajouter une méthode `refresh_ui_texts()` pour mettre à jour le texte dynamiquement

### Modifier les styles
Tous les styles sont centralisés dans `config/styles.py`:
- Modifier les couleurs dans le dictionnaire **COLORS**
- Modifier les fonctions de style pour ajuster l'apparence

### Modifier les critères
Tous les critères sont centralisés dans `checkpoints_gallery.py` dans la variable **CRITERIA_LIST**


## Structure du projet
```
checkpoints_gallery/
├── checkpoints_gallery.py      # Application principale
├── config/                     # Configuration et internationalisation
│   ├── config.py              # Gestionnaire de configuration
│   ├── settings.json          # Configuration sauvegardée (généré)
│   ├── styles.py              # Styles et couleurs
│   └── lang/                  # Fichiers de langue
│       ├── fr.py              # Textes en français
│       └── en.py              # Textes en anglais
├── INSTALL.BAT                # Installation (Windows)
└── START.BAT                  # Lancement (Windows)
```

## 💡 Notes

- ✅ Les images en double sont automatiquement ignorées
- 🔄 Les noms de checkpoints se mettent à jour automatiquement
- ⏱️ Appui long pour glisser, clic rapide pour plein écran
- 🔒 Le premier onglet ne peut pas être supprimé

---

Créé par Tetsuoo avec Claude Sonnet 4.5 ❤️