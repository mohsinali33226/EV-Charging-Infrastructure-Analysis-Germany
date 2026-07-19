# EV Charging Infrastructure Analysis in Germany

This project analyzes public EV charging infrastructure in Germany using Python and Power BI.

The main goal is not only to count charging points, but to understand charging infrastructure quality, installed power, HPC readiness, operator strategy, rollout trends, and charging supply compared with BEV stock.

## Project Objective

The project answers these questions:

1. Which German states have strong charging infrastructure quality?
2. Are some states quantity-heavy while others are power-focused?
3. How much of the charging network is AC, DC fast, or HPC / ultra-fast?
4. Which operators focus on high-power charging?
5. How does charging infrastructure compare with BEV demand by state?
6. Is the rollout shifting toward high-power charging over time?

## Dashboard Preview

### State Strategy Matrix
[State Strategy Matrix](assets/state_strategy_matrix.png)

### Executive Overview
[Executive Overview](assets/executive_overview.png)

### Operator Strategy
[Operator Strategy](assets/operator_strategy.png)

### Rollout Trend
[Rollout Trend](assets/rollout_trend.png)

## Data Sources

- Bundesnetzagentur charging station register
- KBA electric vehicle stock by German federal state

## Tools Used

- Python
- pandas
- NumPy
- Power BI
- Excel

## Main Analysis Steps

1. Cleaned the raw charging station register.
2. Aggregated charging infrastructure by German state.
3. Created a charging infrastructure quality index.
4. Classified charging stations into power classes:
   - AC / Destination
   - Urban fast
   - DC Fast
   - HPC / Ultra-fast
5. Analyzed operator strategies.
6. Compared infrastructure supply with BEV stock.
7. Analyzed yearly rollout trend.
8. Built an interactive Power BI dashboard.

## Key Findings

### 1. Charging point count alone is misleading

AC / Destination chargers dominate by number of charging points, but HPC / Ultra-fast chargers contribute a much larger share of installed charging power.

### 2. State strategies are different

Some states are quantity-heavy, while others are more power-focused. This means infrastructure should be judged by both number of points and installed power.

### 3. BEV demand changes the picture

After adjusting for BEV stock, some smaller states show stronger relative charging supply, while some urban or high-demand states show more pressure.

### 4. Operators follow different strategies

Some operators focus on large network size, while others focus on high-power charging and HPC infrastructure.

### 5. Rollout is becoming more power-capacity focused

In recent usable rollout years, HPC / Ultra-fast charging contributes a much larger share of newly installed power.

## Power BI Dashboard Pages

The dashboard includes:

- State Strategy Matrix
- Executive Overview
- Supply vs Demand
- Operator Strategy
- Rollout Trend
- Methodology

## Project Limitation

This project analyzes installed infrastructure capacity. It does not include real charging session data, utilization rates, waiting times, pricing, grid constraints, or charger availability.

Therefore, the results show infrastructure readiness and capacity, not actual charging usage.

## Files and Folders

```text
data_raw/       Raw downloaded datasets
data_clean/     Cleaned analysis-ready data
outputs/        KPI tables and final Power BI dataset
scripts/        Python analysis scripts
.pbix           Power BI dashboard file