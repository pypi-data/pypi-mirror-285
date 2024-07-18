import logging

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr
from tueplots import markers

from kronfluence.analyzer import Analyzer


def main():
    logging.basicConfig(level=logging.INFO)

    # Load the scores. You might need to modify the path.
    full_scores = Analyzer.load_file("influence_results/imagenet/scores_ekfac/pairwise_scores.safetensors")[
        "all_modules"
    ]
    lr_scores = Analyzer.load_file("influence_results/imagenet/scores_ekfac_qlr32/pairwise_scores.safetensors")[
        "all_modules"
    ]
    # lr_scores = Analyzer.load_file("influence_results/imagenet/scores_ekfac_half_qlr32/pairwise_scores.safetensors")[
    #     "all_modules"
    # ].float()

    # Only plot first 5000 points to avoid clutter.
    plt.rcParams.update({"figure.dpi": 150})
    plt.rcParams.update(markers.with_edge())
    plt.rcParams["axes.axisbelow"] = True
    plt.scatter(lr_scores[0][:5000], full_scores[0][:5000], edgecolor="k")
    plt.grid()
    plt.xlabel("Full Rank Score")
    plt.ylabel("Low Rank (32) Score")
    plt.show()

    # Compute the averaged spearman correlation.
    all_corr = []
    for i in range(100):
        all_corr.append(spearmanr(full_scores[i], lr_scores[i])[0])
    logging.info(f"Averaged Spearman Correlation: {np.array(all_corr).mean()}")

    # Compute the averaged pearson correlation.
    all_corr = []
    for i in range(100):
        all_corr.append(pearsonr(full_scores[i], lr_scores[i])[0])
    logging.info(f"Averaged Spearman Correlation: {np.array(all_corr).mean()}")


if __name__ == "__main__":
    main()
