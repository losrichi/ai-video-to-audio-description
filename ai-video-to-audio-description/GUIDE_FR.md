# Guide français — Projet Video2Audio

Ce dépôt est un **vrai projet exécutable**, prêt à mettre sur GitHub. Il transforme une vidéo en **description écrite, sous-titres SRT et narration audio WAV**. Il existe **deux moteurs distincts** :

1. **`shapes` (démonstration entièrement fonctionnelle, hors ligne)** : détecte uniquement les cercles, carrés, rectangles et triangles colorés dans des vidéos **synthétiques**. Ce moteur utilise OpenCV et des règles de génération de texte, **pas un réseau neuronal**.
2. **`blip` (IA préentraînée, optionnelle)** : extrait des descriptions à partir de véritables images avec le modèle `Salesforce/blip-image-captioning-base`. Il faut installer des dépendances supplémentaires, télécharger les poids du modèle et vérifier manuellement la pertinence des descriptions. **Nous n'avons pas évalué la qualité du modèle BLIP sur des vidéos réelles dans ce dépôt.**

## 1. Ce qui est déjà livré

- **4 vidéos MP4 de démonstration** dans `examples/videos/`.
- **4 narrations audio WAV réelles**, avec description TXT, SRT, aperçu de détection et JSON, dans `examples/results/`.
- **Une évaluation exécutée sur 120 vidéos synthétiques** : 120 WAV effectivement générés pendant l'évaluation, puis supprimés du stockage temporaire pour que le ZIP reste léger. Fichiers de preuves et résultats dans `benchmarks/`.
- **18 tests automatisés réussis** ; un workflow GitHub Actions pour les relancer.
- **Un site de présentation** dans `docs/index.html`, pouvant être publié avec GitHub Pages.
- **Une interface Gradio** pour importer des vidéos et récupérer les fichiers produits.

## 2. Comment ajouter le projet sur GitHub

1. Décompresse le ZIP, **ne mets pas seulement le ZIP sur GitHub**.
2. Va sur `https://github.com/new`, et donne au dépôt le nom **`ai-video-to-audio-description`**.
3. Choisis **Public**. Ne coche pas « Add a README », puisqu'il est fourni.
4. Clique sur **« uploading an existing file »**.
5. Glisse tous les fichiers **et sous-dossiers contenus dans le dossier décompressé** ; `README.md` doit se trouver à la racine du dépôt.
6. Clique sur **Commit changes**. Si le navigateur ne conserve pas l'arborescence, utilise **GitHub Desktop** pour ajouter le dossier et publier le dépôt.

Pour publier la démonstration sur un site public : **Settings → Pages → Build and deployment → Deploy from a branch → main → /docs → Save**. L'URL apparaîtra après le déploiement de GitHub Pages. Le site statique permet seulement de **visionner les démonstrations déjà calculées** : l'analyse de nouveaux fichiers nécessite de lancer Python ou Gradio sur un ordinateur.

## 3. Faire tourner le projet

Sous Windows, installe Python 3.10+ et l'outil eSpeak (ou une voix système compatible `pyttsx3`). Ouvre un terminal dans le dossier du projet :

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,ui]"
video2audio describe --input examples/videos/synthetic_000.mp4 --output outputs/demo
python app.py
```

Sous Linux, installe eSpeak (`sudo apt install espeak`), puis :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,ui]'
video2audio describe --input examples/videos/synthetic_000.mp4 --output outputs/demo
python app.py
```

Le dossier `outputs/demo/` contiendra la narration audio et les résultats d'analyse.

Pour une vidéo réelle avec modèle IA :

```bash
pip install -e '.[ai,ui]'
video2audio describe --input chemin/vers/video.mp4 --output outputs/video_reelle --backend blip --language en
```

*Attention :* le modèle BLIP est en anglais ; son premier téléchargement demande une connexion internet, de l'espace disque et du temps. **Les résultats ne sont pas garantis exacts.**

## 4. Résultats vraiment obtenus

| Mesure | Résultat |
| --- | ---: |
| Vidéos synthétiques analysées | 120/120 |
| WAV effectivement générés et vérifiés | 120/120 |
| Bonne identification de la forme | 100 % |
| Bonne identification de la couleur | 100 % |
| Bonne détection du sens du mouvement | 98,33 % |
| Vidéos naturelles analysées avec BLIP dans ce benchmark | 0 |

Les résultats concernent **uniquement un jeu de vidéos géométriques artificielles**, générées par script, et **ne doivent pas être présentés comme une performance d'IA sur des vidéos réelles**.

Reproduire les chiffres :

```bash
video2audio benchmark --count 120 --seed 2026 --output-dir outputs/benchmark
python -m pytest -q
```

## 5. Formulation possible sur ton CV

En français :

> **Système de description audio de vidéos — Python, OpenCV, NLP, TTS** : Développement d'un pipeline vidéo → analyse visuelle → description textuelle → audio WAV, avec une démonstration interactive et un benchmark reproductible sur **120 vidéos synthétiques** ; intégration d'un modèle BLIP préentraîné en option.

En anglais :

> **Video-to-Audio Description System | Python, OpenCV, NLP, TTS** — Developed a video-to-text-to-speech pipeline with a browsable demo, automated tests, and reproducible processing of 120 **synthetic** video clips; integrated an optional pretrained BLIP captioning backend.

Ne dis pas que tu as entraîné BLIP ou que le benchmark a porté sur des séquences vidéo naturelles : le dépôt ne le prouve pas.
