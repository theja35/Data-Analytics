# Static Dashboard Mock-up

## Dashboard Purpose
A static KPI dashboard for the cleaned dataset should highlight overall data quality, the most important numeric metrics, and the strongest relationships between variables. This mock-up is designed for a stakeholder who needs fast insight from exploratory data analysis.

---

## Recommended Key Performance Indicators (KPIs)

1. **Dataset Coverage**
   - Total records
   - Total columns
   - Completeness (%)
   - Missing cell count

2. **Core Numeric Metrics**
   - Average value for the most important numeric features
   - Median value for the most important numeric features
   - Standard deviation for key numeric features
   - Outlier count and percent for important numeric columns

3. **Category Quality**
   - Top categorical values and their share
   - Number of unique categories
   - Missing percentage for categorical fields

4. **Multivariate Insights**
   - Pairwise correlation strength between numeric columns
   - Top 3 positively correlated variable pairs
   - Top 3 negatively correlated variable pairs

5. **Data Health and Risk Signals**
   - Most problematic columns by missingness
   - Columns with the highest number of outliers
   - Skewness for each numeric column

---

## Suggested Dashboard Layout

### 1. Header + Summary Cards
- **Total Records**
- **Completeness (%)**
- **Numeric Columns**
- **Categorical Columns**
- **Missing Cells**

### 2. KPI Cards (Top row)
- **Average / Median** for selected numeric fields
- **Standard Deviation** for selected numeric fields
- **Outlier %** for selected numeric fields
- **Top Category** for important categorical columns

### 3. Visual Blocks
- **Distribution Snapshot**
  - Histogram or bar chart for one or two key numeric variables
- **Category Distribution**
  - Bar chart for top categorical values
- **Correlation Heatmap**
  - Display numeric correlation matrix using strong positive/negative color coding

### 4. Insights Panel
- **Top 3 positive correlations**
- **Top 3 negative correlations**
- **Columns with highest missingness**
- **Columns with highest outlier rates**

---

## Example Static Mock-up Content

### Overview Section
| KPI | Value | Comment |
|---|---|---|
| Total Records | 1000 | Dataset size after cleaning |
| Completeness | 94% | Percentage of non-missing values |
| Numeric Columns | 10 | Columns treated as numeric |
| Categorical Columns | 5 | Columns treated as categorical |
| Missing Cells | 420 | Total missing values |

### Core Numeric KPI Cards
- `Average Order Value`: 73.45
- `Median Delivery Time`: 2.6
- `Std Dev - Transaction Amount`: 15.2
- `Outlier Rate - Revenue`: 7.8%

### Category Quality Cards
- `Top Category - Region`: North America (34%)
- `Unique Product Types`: 18
- `Missing % - Customer Segment`: 3.2%

### Multivariate Insights
- `Strongest Positive Correlation`: OrderAmount vs DiscountAmount (+0.82)
- `Strongest Negative Correlation`: DeliveryTime vs CustomerSatisfaction (-0.67)
- `High-risk Column`: Revenue (15% outlier rate)

---

## Notes for the Presenter
- Use a clean 2x2 grid for the main dashboard tile layout.
- Reserve one panel for overall data health and one panel for correlation insight.
- Keep the dashboard static by using text boxes and simple charts rather than interactive elements.
- Focus on the top 5 metrics that business stakeholders care about most: completeness, average values, outlier risk, top categories, and correlation strength.

---

## Recommended Implementation
If converting this mock-up into PowerPoint / Google Slides or Excel:
- Create one slide or worksheet with a title block and four sections: Summary, Top Metrics, Data Quality, Correlation.
- Use chart placeholders for distributions and category share bars.
- Use a small heatmap table to show correlation intensity.
- Add a short insight box with the top 3 correlations and data quality risks.
