import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Dict, List, Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Clean and transform raw_dataset.csv for modeling or analysis.'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).with_name('raw_dataset.csv'),
        help='Path to the raw input CSV file.',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).with_name('cleaned_raw_dataset.csv'),
        help='Path to write the cleaned output CSV file.',
    )
    parser.add_argument(
        '--no-encode',
        action='store_true',
        help='Do not apply label encoding to Sex/Embarked columns.',
    )
    return parser.parse_args()


def load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f'Input file not found: {path}')

    with path.open(newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]


def save_csv(path: Path, rows: List[Dict[str, Any]], header: List[str]) -> None:
    with path.open('w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def infer_median(values: List[str]) -> float:
    numeric = [float(value) for value in values if value != '']
    if not numeric:
        return 0.0
    return median(numeric)


def mode_or_default(values: List[str], default: str = '') -> str:
    non_empty = [value for value in values if value != '']
    if not non_empty:
        return default
    return Counter(non_empty).most_common(1)[0][0]


def extract_title(name: str) -> str:
    if ',' in name and '.' in name:
        title = name.split(',')[1].split('.')[0].strip()
        return title
    return 'Unknown'


def map_title(title: str) -> str:
    common_titles = {
        'Mr': 'Mr',
        'Mrs': 'Mrs',
        'Miss': 'Miss',
        'Master': 'Master',
    }
    if title in common_titles:
        return common_titles[title]
    if title in {'Mlle', 'Ms'}:
        return 'Miss'
    if title in {'Mme'}:
        return 'Mrs'
    if title in {'Don', 'Rev', 'Dr', 'Major', 'Lady', 'Sir', 'Col', 'Capt', 'Countess', 'Jonkheer'}:
        return 'Rare'
    return 'Rare'


def clean_row(row: Dict[str, str], medians: Dict[str, float], modes: Dict[str, str]) -> Dict[str, Any]:
    cleaned = dict(row)

    # Impute simple numeric values
    cleaned['Age'] = cleaned['Age'] or str(medians['Age'])
    cleaned['Fare'] = cleaned['Fare'] or str(medians['Fare'])
    cleaned['Embarked'] = cleaned['Embarked'] or modes['Embarked']

    # Cabin: use deck letter or U for unknown
    cleaned['Cabin'] = cleaned['Cabin'].strip()
    cleaned['Cabin'] = cleaned['Cabin'][0] if cleaned['Cabin'] else 'U'

    # Make numeric fields explicit
    cleaned['Age'] = float(cleaned['Age'])
    cleaned['Fare'] = float(cleaned['Fare'])
    cleaned['Pclass'] = int(cleaned['Pclass']) if cleaned['Pclass'] != '' else 0
    cleaned['SibSp'] = int(cleaned['SibSp']) if cleaned['SibSp'] != '' else 0
    cleaned['Parch'] = int(cleaned['Parch']) if cleaned['Parch'] != '' else 0
    cleaned['Survived'] = int(cleaned['Survived']) if cleaned['Survived'] != '' else 0

    # Feature engineering
    cleaned['Title'] = map_title(extract_title(cleaned['Name']))
    cleaned['FamilySize'] = cleaned['SibSp'] + cleaned['Parch'] + 1
    cleaned['IsAlone'] = 1 if cleaned['FamilySize'] == 1 else 0

    # Clean text fields
    cleaned['Sex'] = cleaned['Sex'].lower()
    cleaned['Embarked'] = cleaned['Embarked'].upper()
    cleaned['Name'] = cleaned['Name'].strip()
    cleaned['Ticket'] = cleaned['Ticket'].strip()

    return cleaned


def encode_columns(rows: List[Dict[str, Any]]) -> None:
    sex_map = {'male': 0, 'female': 1}
    embarked_map = {'S': 0, 'C': 1, 'Q': 2, '': 3}
    title_map = {'Mr': 0, 'Mrs': 1, 'Miss': 2, 'Master': 3, 'Rare': 4, 'Unknown': 5}

    for row in rows:
        row['Sex'] = sex_map.get(str(row['Sex']).lower(), 0)
        row['Embarked'] = embarked_map.get(str(row['Embarked']).upper(), 3)
        row['Title'] = title_map.get(str(row['Title']), title_map['Unknown'])


def build_clean_dataset(rows: List[Dict[str, str]], encode: bool = True) -> List[Dict[str, Any]]:
    medians = {
        'Age': infer_median([row['Age'] for row in rows]),
        'Fare': infer_median([row['Fare'] for row in rows]),
    }
    modes = {
        'Embarked': mode_or_default([row['Embarked'] for row in rows], 'S'),
    }

    cleaned_rows = [clean_row(row, medians, modes) for row in rows]
    if encode:
        encode_columns(cleaned_rows)

    return cleaned_rows


def get_output_header(cleaned_rows: List[Dict[str, Any]]) -> List[str]:
    if not cleaned_rows:
        return []
    header = list(cleaned_rows[0].keys())
    # preserve a sensible ordering, dropping raw text columns if desired
    preferred = [
        'PassengerId', 'Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Parch',
        'FamilySize', 'IsAlone', 'Title', 'Cabin', 'Embarked', 'Fare',
        'Name', 'Ticket',
    ]
    ordered = [col for col in preferred if col in header]
    ordered.extend([col for col in header if col not in ordered])
    return ordered


def main() -> None:
    args = parse_args()
    raw_rows = load_csv(args.input)
    cleaned_rows = build_clean_dataset(raw_rows, encode=not args.no_encode)
    header = get_output_header(cleaned_rows)
    save_csv(args.output, cleaned_rows, header)

    print(f'Cleaned {len(cleaned_rows)} rows from {args.input} and wrote output to {args.output}')
    print('Example transformed row:')
    print(cleaned_rows[0])


if __name__ == '__main__':
    main()
