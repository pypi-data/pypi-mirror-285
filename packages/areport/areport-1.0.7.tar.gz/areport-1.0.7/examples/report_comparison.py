from areport import Report, ReportComparison
from tests.deterministic_data import geometric_daily

# Create a report
portfolio_pf_values = geometric_daily(start_price=1, end_price=1.5, n_days=31)
benchmark_pf_values = geometric_daily(start_price=1, end_price=1.3, n_days=31)
comparison = ReportComparison(report=Report(portfolio_pf_values), benchmark_reports={'bm_1': Report(benchmark_pf_values)})

comparison.print_metrics()
comparison.metrics_to_csv(file_name='report_comparison_metrics.csv')