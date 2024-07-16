from areport import Report
from tests.deterministic_data import geometric_daily

# Create a report
pf_values = geometric_daily(start_price=1, end_price=2, n_days=31)
report = Report(pf_values)

report.print_metrics()
report.metrics_to_csv(file_name='report_metrics.csv')