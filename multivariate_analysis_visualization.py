"""
Multivariate Analysis & Correlation Visualization

This script produces advanced EDA visualizations for a cleaned dataset.
It generates:
- correlation heatmap
- numeric pair plot
- focused scatter plot for high-correlation numeric pairs
- scatter plot for age vs. a key categorical dimension, if available

Dependencies:
- pandas
- matplotlib
- seaborn

Usage:
    python multivariate_analysis_visualization.py --input cleaned_raw_dataset.csv --output-dir plots
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


def import_plotting_packages():
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as exc:
        raise ImportError(
            "Missing required plotting packages. Install with: pip install pandas matplotlib seaborn"
        ) from exc

    pd.options.mode.chained_assignment = None
    sns.set_theme(style='whitegrid')
    return pd, plt, sns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Generate multivariate visualizations and correlation plots from a cleaned dataset.'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).with_name('cleaned_raw_dataset.csv'),
        help='Path to the cleaned CSV file.',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).with_name('plots'),
        help='Directory to save generated plot images.',
    )
    parser.add_argument(
        '--max-sample',
        type=int,
        default=1000,
        help='Maximum number of rows to sample for pair plots and scatter plots.',
    )
    return parser.parse_args()


def load_data(path: Path, pd) -> 'pd.DataFrame':
    if not path.exists():
        raise FileNotFoundError(f'Input file not found: {path}')

    df = pd.read_csv(path)
    return df


def normalize_column_name(name: str) -> str:
    return name.strip().lower().replace('_', ' ').replace('-', ' ')


def find_column_by_keywords(columns: Iterable[str], keywords: Iterable[str]) -> Optional[str]:
    normalized = {normalize_column_name(c): c for c in columns}
    for keyword in keywords:
        key = normalize_column_name(keyword)
        for norm_name, original in normalized.items():
            if key in norm_name:
                return original
    return None


def numeric_columns(df, pd) -> List[str]:
    numeric = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric:
        numeric = [col for col in df.columns if pd.to_numeric(df[col], errors='coerce').notna().any()]
    return numeric


def categorical_columns(df, pd) -> List[str]:
    return [col for col in df.columns if col not in numeric_columns(df, pd)]


def choose_high_correlation_pairs(corr_matrix, top_n: int = 3) -> List[Tuple[str, str, float]]:
    pairs = []
    for i, col1 in enumerate(corr_matrix.columns):
        for col2 in corr_matrix.columns[i + 1:]:
            value = corr_matrix.loc[col1, col2]
            if value == value:
                pairs.append((col1, col2, float(value)))

    pairs.sort(key=lambda item: abs(item[2]), reverse=True)
    return pairs[:top_n]


def sample_dataframe(df, max_rows: int):
    if len(df) <= max_rows:
        return df.copy()
    return df.sample(n=max_rows, random_state=42).reset_index(drop=True)


def plot_correlation_heatmap(corr_matrix, plt, sns, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='vlag',
        center=0,
        linewidths=0.5,
        cbar_kws={'shrink': 0.8},
        ax=ax,
    )
    ax.set_title('Numeric Feature Correlation Heatmap', fontsize=16)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_pairplot(df, plt, sns, columns: List[str], max_sample: int, output_path: Path) -> None:
    if len(columns) < 2:
        return

    sample = sample_dataframe(df[columns], max_rows=max_sample)
    pair_plot = sns.pairplot(sample, diag_kind='kde', corner=False)
    pair_plot.fig.suptitle('Numeric Pair Plot', y=1.02)
    pair_plot.fig.tight_layout()
    pair_plot.fig.savefig(output_path, dpi=150)
    plt.close(pair_plot.fig)


def plot_scatter(df, plt, sns, x_col: str, y_col: str, hue_col: Optional[str], max_sample: int, output_path: Path) -> None:
    if x_col not in df.columns or y_col not in df.columns:
        return

    columns = [x_col, y_col] + ([hue_col] if hue_col else [])
    plot_df = sample_dataframe(df[columns].dropna(), max_rows=max_sample)
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.scatterplot(
        data=plot_df,
        x=x_col,
        y=y_col,
        hue=hue_col,
        palette='tab10',
        alpha=0.7,
        edgecolor=None,
        ax=ax,
    )
    ax.set_title(f'Scatter Plot: {x_col} vs {y_col}', fontsize=16)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    if hue_col:
        ax.legend(title=hue_col, bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def build_output_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def get_numeric_pair_for_scatter(corr_matrix):
    pairs = choose_high_correlation_pairs(corr_matrix, top_n=1)
    return pairs[0][0], pairs[0][1] if pairs else (None, None)


def run_visualizations(input_path: Path, output_dir: Path, max_sample: int) -> None:
    pd, plt, sns = import_plotting_packages()
    df = load_data(input_path, pd)
    build_output_directory(output_dir)

    numeric_cols = numeric_columns(df, pd)
    if len(numeric_cols) < 2:
        raise ValueError('At least two numeric columns are required to generate the requested visualizations.')

    corr_matrix = df[numeric_cols].corr()
    plot_correlation_heatmap(corr_matrix, plt, sns, output_dir / 'correlation_heatmap.png')

    pairplot_cols = numeric_cols[:5]
    plot_pairplot(df, plt, sns, pairplot_cols, max_sample, output_dir / 'numeric_pairplot.png')

    x_col, y_col = get_numeric_pair_for_scatter(corr_matrix)
    if x_col and y_col:
        plot_scatter(df, plt, sns, x_col, y_col, None, max_sample, output_dir / 'scatter_best_numeric_pair.png')

    age_col = find_column_by_keywords(df.columns, ['age'])
    category_cols = [col for col in categorical_columns(df, pd) if df[col].nunique(dropna=True) <= 12]
    if age_col and category_cols and len(numeric_cols) >= 2:
        second_numeric = [col for col in numeric_cols if col != age_col][0]
        plot_scatter(
            df,
            plt,
            sns,
            age_col,
            second_numeric,
            category_cols[0],
            max_sample,
            output_dir / 'scatter_age_by_category.png',
        )
    elif age_col and len(numeric_cols) >= 2:
        second_numeric = [col for col in numeric_cols if col != age_col][0]
        plot_scatter(df, plt, sns, age_col, second_numeric, None, max_sample, output_dir / 'scatter_age_vs_numeric.png')

    print(f'Generated plots in: {output_dir.resolve()}')
    print(f'  - correlation_heatmap.png')
    print(f'  - numeric_pairplot.png')
    if x_col and y_col:
        print(f'  - scatter_best_numeric_pair.png ({x_col} vs {y_col})')
    if age_col:
        if category_cols:
            print(f'  - scatter_age_by_category.png ({age_col} by {category_cols[0]})')
        else:
            print(f'  - scatter_age_vs_numeric.png ({age_col} vs {second_numeric})')


if __name__ == '__main__':
    args = parse_args()
    try:
        run_visualizations(args.input, args.output_dir, args.max_sample)
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
