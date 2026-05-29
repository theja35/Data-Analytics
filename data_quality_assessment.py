import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run a data quality assessment on a CSV file.'
    )
    parser.add_argument(
        '--path',
        type=Path,
        default=Path(__file__).with_name('raw_dataset.csv'),
        help='Path to the CSV file to assess. Defaults to raw_dataset.csv next to this script.',
    )
    return parser.parse_args()


def load_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f'CSV file not found: {path}')

    with path.open(newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames or []
        rows = [row for row in reader]

    return header, rows


def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def infer_type(values: List[str]) -> str:
    non_empty = [value for value in values if value != '']
    if not non_empty:
        return 'empty'

    if all(is_int(value) for value in non_empty):
        return 'int'
    if all(is_float(value) for value in non_empty):
        return 'float'
    return 'string'


def numeric_values(values: List[str]) -> List[float]:
    return [float(value) for value in values if value != '' and is_float(value)]


def detect_outliers(values: List[float]) -> Dict[str, object]:
    if len(values) < 2:
        return {'count': 0, 'outliers': []}

    q1 = sorted(values)[len(values) // 4]
    q3 = sorted(values)[3 * len(values) // 4]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = [value for value in values if value < lower or value > upper]
    return {
        'count': len(outliers),
        'lower_bound': lower,
        'upper_bound': upper,
        'outliers': outliers[:10],
    }


def analyze_quality(header: List[str], rows: List[Dict[str, str]]) -> Dict[str, object]:
    total_rows = len(rows)
    missing_by_column = {}
    uniqueness_by_column = {}
    type_by_column = {}
    invalid_values_by_column = defaultdict(list)
    duplicates = 0

    seen = set()
    for row in rows:
        key = tuple(row.get(col, '') for col in header)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

    for column in header:
        values = [row[column] for row in rows]
        missing_count = sum(1 for value in values if value == '')
        missing_by_column[column] = {
            'missing_count': missing_count,
            'missing_pct': 100 * missing_count / total_rows if total_rows else 0,
        }

        unique_values = set(values)
        uniqueness_by_column[column] = {
            'distinct_count': len(unique_values),
            'unique_pct': 100 * len(unique_values) / total_rows if total_rows else 0,
        }

        inferred_type = infer_type(values)
        type_by_column[column] = inferred_type

        if inferred_type in ('int', 'float'):
            for value in values:
                if value == '':
                    continue
                if not is_float(value):
                    invalid_values_by_column[column].append(value)

    numeric_column_stats = {}
    if rows:
        for column in header:
            values = [row[column] for row in rows]
            if infer_type(values) in ('int', 'float'):
                nums = numeric_values(values)
                if nums:
                    numeric_column_stats[column] = {
                        'count': len(nums),
                        'min': min(nums),
                        'max': max(nums),
                        'mean': mean(nums),
                        'stdev': stdev(nums) if len(nums) > 1 else 0.0,
                        'outliers': detect_outliers(nums),
                    }

    top_values = {
        column: Counter([row[column] for row in rows if row[column] != '']).most_common(10)
        for column in header
    }

    return {
        'total_rows': total_rows,
        'total_columns': len(header),
        'header': header,
        'duplicates': duplicates,
        'missing_by_column': missing_by_column,
        'uniqueness_by_column': uniqueness_by_column,
        'type_by_column': type_by_column,
        'numeric_column_stats': numeric_column_stats,
        'invalid_values_by_column': dict(invalid_values_by_column),
        'top_values': top_values,
    }


def print_report(report: Dict[str, object]) -> None:
    print('Data Quality Assessment Report')
    print('================================')
    print(f"Total rows: {report['total_rows']}")
    print(f"Total columns: {report['total_columns']}")
    print(f"Duplicate rows: {report['duplicates']}\n")

    print('Column quality:')
    for column in report['header']:
        missing = report['missing_by_column'][column]
        unique = report['uniqueness_by_column'][column]
        col_type = report['type_by_column'][column]
        invalid = report['invalid_values_by_column'].get(column, [])
        print(f"- {column}")
        print(f"  Type: {col_type}")
        print(f"  Missing: {missing['missing_count']} ({missing['missing_pct']:.2f}%)")
        print(f"  Distinct: {unique['distinct_count']} ({unique['unique_pct']:.2f}%)")
        if invalid:
            print(f"  Invalid values: {invalid[:10]}")
        print(f"  Top values: {', '.join(f'{value} ({count})' for value, count in report['top_values'][column][:5])}")
        if column in report['numeric_column_stats']:
            stats = report['numeric_column_stats'][column]
            print('  Numeric summary:')
            print(f"    count={stats['count']}, min={stats['min']}, max={stats['max']}, mean={stats['mean']:.4f}, stdev={stats['stdev']:.4f}")
            outlier = stats['outliers']
            print(f"    outlier count={outlier['count']}, lower={outlier['lower_bound']:.4f}, upper={outlier['upper_bound']:.4f}")
            if outlier['outliers']:
                print(f"    sample outliers: {outlier['outliers'][:10]}")
        print('')


if __name__ == '__main__':
    args = parse_args()
    header, rows = load_csv(args.path)
    report = analyze_quality(header, rows)
    print_report(report)
