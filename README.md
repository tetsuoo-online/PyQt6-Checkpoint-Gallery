# Checkpoints Gallery - Architecture mise à jour

## Structure du projet

```
checkpoints_gallery/
├── checkpoints_gallery.py      # Application principale
├── config/                     # Configuration et internationalisation
│   ├── __init__.py
│   ├── config.py              # Gestionnaire de configuration
│   ├── settings.json          # Configuration sauvegardée (généré)
│   ├── styles.py              # Styles et couleurs
│   └── lang/                  # Fichiers de langue
│       ├── __init__.py
│       ├── fr.py              # Textes en français
│       └── en.py              # Textes en anglais
├── INSTALL.BAT                # Installation (Windows)
└── START.BAT                  # Lancement (Windows)
```


## Utilisation
<A remplir>

### Installation
```bash
INSTALL.BAT
```

### Lancement
```bash
START.BAT
```
### Menu Options (⚙️ Options)
Accessible depuis chaque onglet, avant le bouton "Checkpoints Folder". A la fermeture, l'interface est mise à jour automatiquement.

- ⏳ **Langue**: FR (Français) ou EN (English).
- ⏳ **Choix du thème**: Dark / Light
- ⏳ **Mode d'import de grille**: Ajouter ou Remplacer

## Notes techniques
- Il est possible d'ajouter de nouvelles langues.
- La configuration est chargée au démarrage de l'application
- Les changements s'appliquent sans redémarrer
- Les paramètres sont sauvegardés automatiquement dans `config/settings.json`


## Développement

### Ajouter une nouvelle langue
1. Créer un nouveau fichier dans `config/lang/` (ex: `de.py` pour l'allemand)
2. Copier la structure de `fr.py` ou `en.py`
3. Traduire tous les textes dans le dictionnaire `LANG`
4. Modifier `config/config.py` pour inclure la nouvelle langue
5. Ajouter un checkbox dans `OptionsDialog`

### Ajouter un nouveau texte traduisible
1. Ajouter la clé dans `config/lang/fr.py` et `config/lang/en.py`
2. Utiliser `config.get_text('cle')` dans le code
3. Si nécessaire, ajouter une méthode `refresh_ui_texts()` pour mettre à jour le texte dynamiquement

### Modifier les styles
Tous les styles sont centralisés dans `config/styles.py`:
- Modifier les couleurs dans le dictionnaire `COLORS`
- Modifier les fonctions de style pour ajuster l'apparence


## 💡 Notes

- ✅ Les images en double sont automatiquement ignorées
- 🔄 Les noms de checkpoints se mettent à jour automatiquement
- ⏱️ Appui long pour glisser, clic rapide pour plein écran
- 🔒 Le premier onglet ne peut pas être supprimé

---

Créé par Tetsuoo avec Claude Sonnet 4.5 ❤️