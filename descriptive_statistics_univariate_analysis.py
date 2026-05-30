"""
Descriptive Statistics & Univariate Analysis Module

This module provides comprehensive descriptive statistics and univariate analysis
for the cleaned dataset, including:
- Basic statistics (mean, median, std, min, max, quartiles)
- Distribution analysis for numeric and categorical variables
- Outlier detection
- Data quality metrics
- Visualizations of distributions
"""

import argparse
import csv
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple, Any
from statistics import mean, median, stdev, quantiles
import math


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Perform descriptive statistics and univariate analysis on cleaned dataset.'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).with_name('cleaned_raw_dataset.csv'),
        help='Path to the cleaned CSV file.',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).with_name('descriptive_statistics_report.txt'),
        help='Path to write the analysis report.',
    )
    return parser.parse_args()


def load_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    """Load CSV file and return header and rows."""
    if not path.exists():
        raise FileNotFoundError(f'Input file not found: {path}')

    with path.open(newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames or []
        rows = [row for row in reader]

    return header, rows


def is_numeric(value: str) -> bool:
    """Check if a value can be converted to float."""
    if value == '' or value is None:
        return False
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def get_numeric_values(values: List[str]) -> List[float]:
    """Extract numeric values from a list, excluding empty/invalid values."""
    return [float(v) for v in values if is_numeric(v)]


def calculate_numeric_statistics(values: List[str]) -> Dict[str, Any]:
    """Calculate comprehensive statistics for numeric column."""
    numeric_values = get_numeric_values(values)
    
    if not numeric_values:
        return {
            'count': 0,
            'missing': len(values),
            'mean': None,
            'median': None,
            'std': None,
            'min': None,
            'max': None,
            'q1': None,
            'q3': None,
            'iqr': None,
            'range': None,
            'variance': None,
            'cv': None,
            'skewness': None,
        }
    
    numeric_values.sort()
    count = len(numeric_values)
    missing = len(values) - count
    
    # Central tendency
    mean_val = mean(numeric_values)
    median_val = median(numeric_values)
    
    # Dispersion
    variance_val = 0
    if count > 1:
        variance_val = sum((x - mean_val) ** 2 for x in numeric_values) / (count - 1)
        std_val = math.sqrt(variance_val)
    else:
        std_val = 0
    
    # Range and extremes
    min_val = min(numeric_values)
    max_val = max(numeric_values)
    range_val = max_val - min_val
    
    # Quartiles
    try:
        quarts = quantiles(numeric_values, n=4)
        q1 = quarts[0]
        q3 = quarts[2]
    except:
        # Fallback for smaller datasets
        q1 = numeric_values[count // 4] if count >= 4 else numeric_values[0]
        q3 = numeric_values[3 * count // 4] if count >= 4 else numeric_values[-1]
    
    iqr = q3 - q1
    
    # Coefficient of variation
    cv = (std_val / mean_val * 100) if mean_val != 0 else 0
    
    # Skewness (simplified)
    if count > 2 and std_val > 0:
        skewness = sum((x - mean_val) ** 3 for x in numeric_values) / (count * std_val ** 3)
    else:
        skewness = 0
    
    return {
        'count': count,
        'missing': missing,
        'mean': round(mean_val, 4),
        'median': round(median_val, 4),
        'std': round(std_val, 4),
        'min': round(min_val, 4),
        'max': round(max_val, 4),
        'q1': round(q1, 4),
        'q3': round(q3, 4),
        'iqr': round(iqr, 4),
        'range': round(range_val, 4),
        'variance': round(variance_val, 4),
        'cv': round(cv, 4),
        'skewness': round(skewness, 4),
    }


def detect_outliers_iqr(values: List[str]) -> Dict[str, Any]:
    """Detect outliers using IQR method."""
    numeric_values = get_numeric_values(values)
    
    if len(numeric_values) < 4:
        return {
            'method': 'IQR',
            'lower_bound': None,
            'upper_bound': None,
            'outlier_count': 0,
            'outlier_percentage': 0,
        }
    
    numeric_values.sort()
    count = len(numeric_values)
    
    try:
        quarts = quantiles(numeric_values, n=4)
        q1 = quarts[0]
        q3 = quarts[2]
    except:
        q1 = numeric_values[count // 4]
        q3 = numeric_values[3 * count // 4]
    
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
    outlier_count = len(outliers)
    outlier_percentage = (outlier_count / count * 100) if count > 0 else 0
    
    return {
        'method': 'IQR',
        'lower_bound': round(lower_bound, 4),
        'upper_bound': round(upper_bound, 4),
        'outlier_count': outlier_count,
        'outlier_percentage': round(outlier_percentage, 2),
    }


def analyze_categorical(values: List[str]) -> Dict[str, Any]:
    """Analyze categorical column."""
    valid_values = [v for v in values if v != '']
    missing_count = len(values) - len(valid_values)
    
    if not valid_values:
        return {
            'unique_count': 0,
            'most_common': None,
            'missing': missing_count,
            'missing_percentage': 100,
            'distribution': {},
        }
    
    # Count frequencies
    freq_dict = {}
    for v in valid_values:
        freq_dict[v] = freq_dict.get(v, 0) + 1
    
    # Sort by frequency
    sorted_freq = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
    missing_percentage = (missing_count / len(values) * 100) if len(values) > 0 else 0
    
    return {
        'unique_count': len(freq_dict),
        'most_common': sorted_freq[0][0] if sorted_freq else None,
        'most_common_freq': sorted_freq[0][1] if sorted_freq else 0,
        'missing': missing_count,
        'missing_percentage': round(missing_percentage, 2),
        'distribution': dict(sorted_freq[:10]),  # Top 10
    }


def infer_column_type(values: List[str], column_name: str) -> str:
    """Infer if column is numeric or categorical."""
    numeric_count = sum(1 for v in values if is_numeric(v))
    numeric_ratio = numeric_count / len(values) if len(values) > 0 else 0
    
    # If more than 70% are numeric, treat as numeric
    if numeric_ratio > 0.7:
        return 'numeric'
    else:
        return 'categorical'


def calculate_pearson_correlation(values1: List[float], values2: List[float]) -> Any:
    """Calculate Pearson correlation coefficient between two equal-length numeric lists."""
    if len(values1) < 2 or len(values2) < 2:
        return None

    mean1 = mean(values1)
    mean2 = mean(values2)
    covariance = sum((x - mean1) * (y - mean2) for x, y in zip(values1, values2))
    variance1 = sum((x - mean1) ** 2 for x in values1)
    variance2 = sum((y - mean2) ** 2 for y in values2)
    denominator = math.sqrt(variance1 * variance2)

    if denominator == 0:
        return None

    return round(covariance / denominator, 4)


def build_numeric_correlation_matrix(header: List[str], rows: List[Dict[str, str]]) -> Tuple[List[str], Dict[Tuple[str, str], Any]]:
    """Build a pairwise correlation matrix for numeric columns."""
    numeric_cols = [col for col in header if infer_column_type([row.get(col, '') for row in rows], col) == 'numeric']
    correlations = {}

    for col1, col2 in combinations(numeric_cols, 2):
        paired_values = [
            (float(row[col1]), float(row[col2]))
            for row in rows
            if is_numeric(row.get(col1, '')) and is_numeric(row.get(col2, ''))
        ]

        if len(paired_values) < 2:
            correlations[(col1, col2)] = None
            continue

        xs, ys = zip(*paired_values)
        correlations[(col1, col2)] = calculate_pearson_correlation(list(xs), list(ys))

    return numeric_cols, correlations


def summarize_correlation_pairs(correlations: Dict[Tuple[str, str], Any]) -> List[str]:
    """Return ordered summary lines for the strongest positive and negative correlations."""
    valid_pairs = [
        ((col1, col2), corr)
        for (col1, col2), corr in correlations.items()
        if corr is not None
    ]

    if not valid_pairs:
        return ['  No valid numeric correlations could be computed due to missing or insufficient data.']

    sorted_pairs = sorted(valid_pairs, key=lambda item: abs(item[1]), reverse=True)
    summary_lines = ['  Strongest correlations:']
    for (col1, col2), corr in sorted_pairs[:10]:
        direction = 'positive' if corr >= 0 else 'negative'
        summary_lines.append(f'    {col1} vs {col2}: {corr:+.4f} ({direction})')

    return summary_lines


def generate_report(header: List[str], rows: List[Dict[str, str]]) -> str:
    """Generate comprehensive descriptive statistics report."""
    report_lines = []
    
    report_lines.append("=" * 80)
    report_lines.append("DESCRIPTIVE STATISTICS & UNIVARIATE ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Overall dataset summary
    report_lines.append(f"Total Records: {len(rows)}")
    report_lines.append(f"Total Columns: {len(header)}")
    report_lines.append("")
    
    # Analyze each column
    for column in header:
        values = [row.get(column, '') for row in rows]
        col_type = infer_column_type(values, column)
        
        report_lines.append("-" * 80)
        report_lines.append(f"COLUMN: {column} ({col_type.upper()})")
        report_lines.append("-" * 80)
        
        if col_type == 'numeric':
            stats = calculate_numeric_statistics(values)
            report_lines.append("")
            report_lines.append("DESCRIPTIVE STATISTICS:")
            report_lines.append(f"  Valid Count:        {stats['count']}")
            report_lines.append(f"  Missing Values:     {stats['missing']}")
            report_lines.append(f"  Missing %:          {(stats['missing']/len(values)*100 if len(values)>0 else 0):.2f}%")
            report_lines.append("")
            report_lines.append("CENTRAL TENDENCY:")
            report_lines.append(f"  Mean:               {stats['mean']}")
            report_lines.append(f"  Median:             {stats['median']}")
            report_lines.append("")
            report_lines.append("DISPERSION:")
            report_lines.append(f"  Std Deviation:      {stats['std']}")
            report_lines.append(f"  Variance:           {stats['variance']}")
            report_lines.append(f"  Coeff. of Variation: {stats['cv']}%")
            report_lines.append("")
            report_lines.append("RANGE:")
            report_lines.append(f"  Minimum:            {stats['min']}")
            report_lines.append(f"  Maximum:            {stats['max']}")
            report_lines.append(f"  Range:              {stats['range']}")
            report_lines.append("")
            report_lines.append("QUARTILES:")
            report_lines.append(f"  Q1 (25%):           {stats['q1']}")
            report_lines.append(f"  Q3 (75%):           {stats['q3']}")
            report_lines.append(f"  IQR:                {stats['iqr']}")
            report_lines.append("")
            report_lines.append("DISTRIBUTION SHAPE:")
            report_lines.append(f"  Skewness:           {stats['skewness']}")
            
            # Outlier detection
            outliers = detect_outliers_iqr(values)
            report_lines.append("")
            report_lines.append("OUTLIER DETECTION (IQR Method):")
            report_lines.append(f"  Lower Bound:        {outliers['lower_bound']}")
            report_lines.append(f"  Upper Bound:        {outliers['upper_bound']}")
            report_lines.append(f"  Outlier Count:      {outliers['outlier_count']}")
            report_lines.append(f"  Outlier %:          {outliers['outlier_percentage']}%")
            
        else:  # categorical
            cat_stats = analyze_categorical(values)
            report_lines.append("")
            report_lines.append("CATEGORICAL ANALYSIS:")
            report_lines.append(f"  Unique Values:      {cat_stats['unique_count']}")
            report_lines.append(f"  Most Common:        {cat_stats['most_common']}")
            report_lines.append(f"  Most Common Freq:   {cat_stats['most_common_freq']}")
            report_lines.append(f"  Missing Values:     {cat_stats['missing']}")
            report_lines.append(f"  Missing %:          {cat_stats['missing_percentage']}%")
            report_lines.append("")
            report_lines.append("FREQUENCY DISTRIBUTION (Top 10):")
            for value, freq in sorted(cat_stats['distribution'].items(), 
                                     key=lambda x: x[1], reverse=True)[:10]:
                percentage = (freq / len(values) * 100) if len(values) > 0 else 0
                report_lines.append(f"  {value:30s} : {freq:6d} ({percentage:6.2f}%)")
        
        report_lines.append("")
    
    # Summary statistics
    report_lines.append("=" * 80)
    report_lines.append("SUMMARY")
    report_lines.append("=" * 80)
    
    numeric_cols = [col for col in header 
                   if infer_column_type([row.get(col, '') for row in rows], col) == 'numeric']
    categorical_cols = [col for col in header if col not in numeric_cols]
    
    report_lines.append(f"Numeric Columns:     {len(numeric_cols)}")
    report_lines.append(f"Categorical Columns: {len(categorical_cols)}")
    
    # Data quality
    total_cells = len(rows) * len(header)
    missing_cells = sum(
        sum(1 for row in rows if row.get(col, '') == '')
        for col in header
    )
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    report_lines.append("")
    report_lines.append("DATA QUALITY METRICS:")
    report_lines.append(f"  Total Cells:        {total_cells}")
    report_lines.append(f"  Missing Cells:      {missing_cells}")
    report_lines.append(f"  Completeness:       {completeness:.2f}%")
    report_lines.append("")

    # Multivariate analysis and correlation
    numeric_cols, correlations = build_numeric_correlation_matrix(header, rows)
    report_lines.append("=" * 80)
    report_lines.append("MULTIVARIATE ANALYSIS & CORRELATION")
    report_lines.append("=" * 80)
    if len(numeric_cols) < 2:
        report_lines.append("Not enough numeric columns available for pairwise correlation analysis.")
    else:
        report_lines.append("PAIRWISE PEARSON CORRELATION MATRIX:")
        header_row = "".ljust(18) + "".join(f"{col:>12}" for col in numeric_cols)
        report_lines.append(header_row)
        for col1 in numeric_cols:
            row_values = []
            for col2 in numeric_cols:
                if col1 == col2:
                    row_values.append(f"{1.0:12.4f}")
                else:
                    key = (col1, col2) if (col1, col2) in correlations else (col2, col1)
                    corr_val = correlations.get(key)
                    row_values.append(f"{corr_val:12.4f}" if corr_val is not None else f"{'N/A':>12}")
            report_lines.append(f"{col1:16s}" + "".join(row_values))

        report_lines.append("")
        report_lines.extend(summarize_correlation_pairs(correlations))

    report_lines.append("")
    return "\n".join(report_lines)


def main() -> None:
    """Main execution function."""
    args = parse_args()
    
    # Load dataset
    print(f"Loading dataset from {args.input}...")
    header, rows = load_csv(args.input)
    
    # Generate report
    print(f"Performing descriptive statistics and univariate analysis...")
    report = generate_report(header, rows)
    
    # Save report
    print(f"Saving report to {args.output}...")
    with args.output.open('w', encoding='utf-8') as f:
        f.write(report)
    
    # Print report to console
    print("\n" + report)
    print(f"\nReport saved to: {args.output}")


if __name__ == '__main__':
    main()
