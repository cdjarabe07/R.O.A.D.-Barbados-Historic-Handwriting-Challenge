"""
Script d'analyse rapide pour le challenge R.O.A.D. Barbados Handwriting (Zindi).

Ce script :
1. Vérifie que les images matchent bien les ID des CSV (Train/Test)
2. Analyse les dimensions des images (largeur/hauteur/ratio)
3. Détecte les images corrompues ou introuvables
4. Génère un montage d'échantillons aléatoires pour inspection visuelle
5. Affiche des stats sur les longueurs de texte (Train)

Usage :
    python analyze_data.py
"""

import os
import random
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# CONFIG - adapte ces chemins si besoin
# ---------------------------------------------------------------------------
IMAGES_DIR = "images_extracted/images"   # dossier contenant les .jpg/.png
TRAIN_CSV = "Train.csv"
TEST_CSV = "Test.csv"
IMAGE_EXT_CANDIDATES = [".jpg", ".jpeg", ".png"]  # extensions à essayer

# ---------------------------------------------------------------------------

def find_image_path(image_id, images_dir):
    """Essaie de trouver le fichier image correspondant à un ID, quelle que soit l'extension."""
    for ext in IMAGE_EXT_CANDIDATES:
        candidate = os.path.join(images_dir, image_id + ext)
        if os.path.exists(candidate):
            return candidate
    return None


def main():
    print("=" * 70)
    print("ANALYSE DES DONNEES - R.O.A.D. Barbados Handwriting Challenge")
    print("=" * 70)

    # --- 1. Charger les CSV ---
    train = pd.read_csv(TRAIN_CSV)
    test = pd.read_csv(TEST_CSV)
    print(f"\nTrain.csv : {len(train)} lignes")
    print(f"Test.csv  : {len(test)} lignes")

    # --- 2. Vérifier le matching image <-> CSV ---
    print("\n--- Vérification des correspondances image <-> ID ---")
    missing_train = []
    sizes = []
    ratios = []
    sample_paths = []

    all_ids = list(train["ID"]) + list(test["ID"])
    random.seed(42)
    sample_ids = random.sample(all_ids, min(12, len(all_ids)))

    n_checked = 0
    n_missing = 0
    widths, heights = [], []

    for img_id in all_ids:
        path = find_image_path(img_id, IMAGES_DIR)
        n_checked += 1
        if path is None:
            n_missing += 1
            if n_missing <= 5:
                missing_train.append(img_id)
            continue
        try:
            with Image.open(path) as im:
                w, h = im.size
                widths.append(w)
                heights.append(h)
        except Exception as e:
            print(f"  [ERREUR lecture] {img_id}: {e}")

    print(f"Images vérifiées : {n_checked}")
    print(f"Images manquantes/introuvables : {n_missing}")
    if missing_train:
        print(f"  Exemples d'ID manquants : {missing_train}")

    # --- 3. Stats dimensions ---
    if widths:
        w_series = pd.Series(widths)
        h_series = pd.Series(heights)
        ratio_series = w_series / h_series
        print("\n--- Dimensions des images ---")
        print(f"Largeur  -> min={w_series.min()} max={w_series.max()} moyenne={w_series.mean():.1f}")
        print(f"Hauteur  -> min={h_series.min()} max={h_series.max()} moyenne={h_series.mean():.1f}")
        print(f"Ratio L/H -> min={ratio_series.min():.2f} max={ratio_series.max():.2f} moyenne={ratio_series.mean():.2f}")

    # --- 4. Stats sur les longueurs de texte (Train) ---
    print("\n--- Longueur des transcriptions (Train) ---")
    char_lens = train["Target"].astype(str).str.len()
    word_lens = train["Target"].astype(str).str.split().str.len()
    print(f"Caractères -> min={char_lens.min()} max={char_lens.max()} moyenne={char_lens.mean():.1f}")
    print(f"Mots       -> min={word_lens.min()} max={word_lens.max()} moyenne={word_lens.mean():.1f}")

    # --- 5. Montage d'échantillons aléatoires ---
    print("\n--- Génération d'un montage d'échantillons (sample_grid.png) ---")
    fig, axes = plt.subplots(4, 3, figsize=(15, 10))
    for ax, img_id in zip(axes.flat, sample_ids):
        path = find_image_path(img_id, IMAGES_DIR)
        if path is None:
            ax.set_title(f"{img_id} (introuvable)", fontsize=8, color="red")
            ax.axis("off")
            continue
        try:
            with Image.open(path) as im:
                ax.imshow(im)
                # Cherche le label si dispo (train)
                match = train.loc[train["ID"] == img_id, "Target"]
                label = match.values[0][:40] if len(match) else "(test - pas de label)"
                ax.set_title(f"{img_id}\n{label}", fontsize=7)
                ax.axis("off")
        except Exception as e:
            ax.set_title(f"{img_id} (erreur)", fontsize=8, color="red")
            ax.axis("off")

    plt.tight_layout()
    plt.savefig("sample_grid.png", dpi=150)
    print("Montage sauvegardé : sample_grid.png (ouvre-le dans VS Code pour l'inspecter)")

    print("\n" + "=" * 70)
    print("ANALYSE TERMINEE")
    print("=" * 70)


if __name__ == "__main__":
    main()