import json
import os

import numpy as np
import pandas as pd
from tabulate import tabulate


from .utils import compute_max_dd


class Report:
    def __init__(self, pf_values: pd.Series):
        """Generic class for calculating return stream metrics

        Args:
            pf_values (pd.Series): cumulative portfolio values starting at one
        """
        if pf_values.iloc[0] != 1.0:
            raise ValueError(f"Supplied pf_values should start at one got {pf_values.iloc[0]}!")

        self.pf_values = pf_values.copy()
        self.dt_pf_values = pf_values.copy()

        if type(self.pf_values.index) == pd.DatetimeIndex:
            self.pf_values.index = [t.timestamp() for t in self.pf_values.index]

        else:
            self.dt_pf_values.index = [pd.to_datetime(t, unit="s") for t in self.dt_pf_values.index]

        self.pf_returns = self.pf_values.pct_change()
        self.dt_pf_returns = self.dt_pf_values.pct_change()

        self.pf_returns.iloc[0] = 0
        self.dt_pf_returns.iloc[0] = 0

        self.initial_capital = self.pf_values.iloc[0]
        self.final_capital = self.pf_values.iloc[-1]

        self.freq = 31536000 // np.mean(np.diff(self.pf_values.index))

        self.log_dir = "logs"

    @classmethod
    def from_returns(cls, returns: pd.Series):
        """Creates this object using returns instead of portfolio values

        Args:
            returns (pd.Series): series contain the returns of the portfolio
        """
        assert type(returns) == pd.Series

        return cls((returns + 1).cumprod())

    @classmethod
    def from_balances(cls, balances: pd.Series, **kwargs):
        """Creates this object using balances instead of portfolio values

        Args:
            balances (pd.Series): series contain the balances of the portfolio

        Raises:
            ValueError: balances must be a pd.Series object
        """
        if not isinstance(balances, pd.Series):
            raise ValueError("Balances must be a pd.Series object")

        return cls(balances / balances.iloc[0], **kwargs)

    def get_metrics(self):
        """Return all the common metrics"""
        return {
            "final_pnl": self.final_pnl,
            "ytd_performance": self.ytd_performance.iloc[-1],
            "cagr": self.cagr,
            "sharpe": self.sharpe_ratio,
            "sortino": self.sortino_ratio,
            "arithmetic_sharpe": self.arithmetic_sharpe_ratio,
            "annualized_std": self.annualized_standard_deviation,
            "max_dd": self.max_drawdown,
            "calmar": self.calmar_ratio,
            "monthly_win_rate": self.win_rate,
            "monthly_neutral_rate": self.neutral_rate,
            "monthly_loss_rate": self.loss_rate,
            "adj_monthly_win_rate": self.adj_win_rate,
            "avg_monthly_win": self.avg_win,
            "avg_monthly_loss": self.avg_loss,
            "monthly_slugging_ratio": self.slugging_ratio,
            "avg_annual_turnover": self.avg_turnover,
        }

    def print_metrics(self):
        """Print all the common metrics to a table"""
        print(tabulate(pd.DataFrame(self.get_metrics(), index=[0]).T, tablefmt="fancy_grid"))

    def print_annual_returns(self):
        """Print all the annual returns to a table"""
        print(tabulate(self.annual_returns.to_frame(), tablefmt="fancy_grid", headers=["Year", "PnL"]))

    def print_monthly_returns(self, lookback: int = 12):
        """Print the last n monthly returns to a table"""
        print(
            tabulate(self.monthly_returns.iloc[-lookback:].to_frame(), tablefmt="fancy_grid", headers=["Month", "PnL"])
        )

    def print_quarterly_returns(self, lookback: int = 8):
        """Print the last n quarterly returns to a table"""
        print(
            tabulate(
                self.quarterly_returns.iloc[-lookback:].to_frame(), tablefmt="fancy_grid", headers=["Quarter", "PnL"]
            )
        )

    def metrics_to_csv(self, output_dir="", file_name: str = "metrics.csv"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        pd.DataFrame(self.get_metrics(), index=[0]).to_csv(
            os.path.join(self.log_dir, output_dir, file_name), index=None
        )

    def metrics_to_json(self, output_dir="", file_name: str = "metrics.json"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        with open(os.path.join(self.log_dir, output_dir, file_name), "w") as f:
            json.dump(self.get_metrics(), f)

    def annual_returns_to_csv(self, output_dir="", file_name: str = "annual_returns.csv"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        self.annual_returns.sort_index(ascending=False).to_frame().T.to_csv(
            os.path.join(self.log_dir, output_dir, file_name), index_label="year"
        )

    def monthly_returns_to_csv(self, lookback: int = 12, output_dir="", file_name: str = "monthly_returns.csv"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        self.monthly_returns.iloc[-lookback:].sort_index(ascending=False).to_frame().T.to_csv(
            os.path.join(self.log_dir, output_dir, file_name), index_label="month"
        )

    def quarterly_returns_to_csv(self, lookback: int = 8, output_dir="", file_name: str = "quarterly_returns.csv"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        self.quarterly_returns.iloc[-lookback:].sort_index(ascending=False).to_frame().T.to_csv(
            os.path.join(self.log_dir, output_dir, file_name), index_label="quarter"
        )

    def less_performance_fees(self, fee, frequency="M"):
        billing_dates = self.dt_pf_returns.resample(frequency + 'E').last().index

        balance = 1.0
        high_water_mark = balance
        balances = pd.Series(index=self.dt_pf_returns.index)
        fees_paid = pd.Series(index=self.dt_pf_returns.index)
        bill_tomorrow = False
        for index, daily_return in self.dt_pf_returns.items():
            if bill_tomorrow:
                if balance > high_water_mark:
                    billable_profit = balance - high_water_mark
                    fee_bill = fee * billable_profit
                    high_water_mark = balance

                else:
                    fee_bill = 0

                balance -= fee_bill
                fees_paid[index] = fee_bill

            if index in billing_dates:
                bill_tomorrow = True
            else:
                bill_tomorrow = False

            balance *= 1 + daily_return
            balances[index] = balance
                
        return Report.from_balances(balances), fees_paid

    @property
    def final_pnl(self):
        return (self.final_capital - self.initial_capital) / self.initial_capital

    @property
    def sharpe_ratio(self):
        return (self.cagr - 0.0) / (np.sqrt(self.freq) * np.std(self.pf_returns))

    @property
    def arithmetic_sharpe_ratio(self):
        return np.sqrt(self.freq) * np.mean(self.pf_returns) / np.std(self.pf_returns)

    @property
    def sortino_ratio(self):
        return (self.cagr - 0.0) / (np.sqrt(self.freq) * np.nanstd(self.pf_returns[self.pf_returns < 0]))

    @property
    def win_rate(self):
        return (self.monthly_returns > 0).sum() / self.monthly_returns.count()

    @property
    def neutral_rate(self):
        return (self.monthly_returns == 0).sum() / self.monthly_returns.count()

    @property
    def loss_rate(self):
        return (self.monthly_returns < 0).sum() / self.monthly_returns.count()

    @property
    def adj_win_rate(self):
        return (self.monthly_returns > 0).sum() / (self.monthly_returns.count() - (self.monthly_returns == 0).sum())

    @property
    def avg_win(self):
        return self.monthly_returns[self.monthly_returns > 0].mean()

    @property
    def avg_loss(self):
        return self.monthly_returns[self.monthly_returns < 0].mean()

    @property
    def slugging_ratio(self):
        return self.avg_win / abs(self.avg_loss)

    @property
    def avg_turnover(self):
        if hasattr(self, "annual_turnover"):
            avg_turnover = np.mean(self.annual_turnover)
        else:
            avg_turnover = None
        return avg_turnover

    def _monthly_returns(self):
        monthly_returns = self.dt_pf_values.resample("ME").last()
        monthly_returns /= self.dt_pf_values.resample("ME").last().shift(1).fillna(1)
        monthly_returns -= 1
        return monthly_returns

    @property
    def monthly_returns(self):
        monthly_returns = self._monthly_returns()
        monthly_returns.index = [f"{i.year}-{i.month}" for i in monthly_returns.index]
        monthly_returns.name = "return"
        return monthly_returns

    def _quarterly_returns(self):
        quarterly_returns = self.dt_pf_values.resample("QE").last()
        quarterly_returns /= self.dt_pf_values.resample("QE").last().shift(1).fillna(1)
        quarterly_returns -= 1
        return quarterly_returns

    @property
    def quarterly_returns(self):
        quarterly_returns = self._quarterly_returns()
        quarterly_returns.index = [f"{i.year}-{i.month}" for i in quarterly_returns.index]
        quarterly_returns.name = "return"
        return quarterly_returns

    def _annual_returns(self):
        annual_returns = self.dt_pf_values.resample("YE").last()
        annual_returns /= self.dt_pf_values.resample("YE").last().shift(1).fillna(1)
        annual_returns -= 1
        return annual_returns

    @property
    def annual_returns(self):
        annual_returns = self._annual_returns()
        annual_returns.index = [i.year for i in annual_returns.index]
        annual_returns.name = "return"
        return annual_returns

    @property
    def drawdown(self):
        return compute_max_dd(self.pf_returns.values)

    @property
    def max_drawdown(self):
        return compute_max_dd(self.pf_returns.values).min()

    @property
    def cagr(self):
        return (self.final_capital / self.initial_capital) ** (self.freq / self.pf_values.shape[0]) - 1

    @property
    def annualized_standard_deviation(self):
        return np.sqrt(self.freq) * np.std(self.pf_returns)

    @property
    def calmar_ratio(self):
        return self.cagr / abs(self.max_drawdown)

    @property
    def ytd_start(self):
        year_start = self.dt_pf_values.index[-1].replace(month=1, day=1, hour=0, minute=0, second=0) - pd.Timedelta(
            seconds=1
        )

        # find the available year start (whichever is earlier, last date of previous year or the start of the year)
        if self.dt_pf_values.index.min() < year_start:
            available_year_start = self.dt_pf_values.loc[:year_start].index[-1]
        else:
            available_year_start = year_start

        return available_year_start

    @property
    def ytd_performance(self):
        return self.dt_pf_values.loc[self.ytd_start :] / self.dt_pf_values.loc[self.ytd_start :].iloc[0] - 1

    @property
    def mtd_start(self):
        month_start = self.dt_pf_values.index[-1].replace(day=1, hour=0, minute=0, second=0) - pd.Timedelta(seconds=1)

        # find the available month start (whichever is earlier, last date of previous month or the start of the month)
        if self.dt_pf_values.index.min() < month_start:
            available_month_start = self.dt_pf_values.loc[:month_start].index[-1]
        else:
            available_month_start = month_start

        return available_month_start

    @property
    def mtd_performance(self):
        return self.dt_pf_values.loc[self.mtd_start :] / self.dt_pf_values.loc[self.mtd_start :].iloc[0] - 1

    def periodic_returns(self, frequency: str) -> pd.Series:
        """Calculate the returns during a specific period

        Args:
            frequency (str): frequency to reset the returns

        Returns:
            pd.Series: returns during the period
        """
        start_of_period_value = (
            self.dt_pf_values.resample(frequency).last().reindex(self.dt_pf_values.index).ffill().fillna(1)
        )
        returns = self.dt_pf_values / start_of_period_value
        returns -= 1
        returns.name = "return"
        return returns

    def get_recent_performance(self, years=1, months=0, days=0, end_date=None):
        if end_date is None:
            end_date = self.dt_pf_values.index[-1]

        lookback_date = end_date - pd.DateOffset(years=years, months=months, days=days)
        return (
            self.dt_pf_values.loc[lookback_date:end_date] / self.dt_pf_values.loc[lookback_date:end_date].iloc[0] - 1
        )

    def get_recent_cagr(self, years=1, months=0, days=0, end_date=None):
        if end_date is None:
            end_date = self.dt_pf_values.index[-1]

        lookback_date = end_date - pd.DateOffset(years=years, months=months, days=days)
        return (
            self.dt_pf_values.loc[lookback_date:end_date].iloc[-1]
            / self.dt_pf_values.loc[lookback_date:end_date].iloc[0]
        ) ** (self.freq / self.dt_pf_values.loc[lookback_date:end_date].shape[0]) - 1


class ReportComparison(object):
    def __init__(
        self,
        report: Report,
        benchmark_reports: dict[str:Report],
        portfolio_name: str = "Portfolio",
    ):
        """Compare the portfolio to set of benchmarks

        Args:
            report (Report): The portfolio report
            benchmark_reports (dict[str: Report]): A dictionary of benchmark reports
            figsize (tuple): Figure size in matplotlib format, will be converted for plotly
            plot_backend (str): 'matplotlib' or 'plotly' or 'plotly.svg'
        """
        self.pf_report = report
        self.benchmarks = benchmark_reports
        self.portfolio_name = portfolio_name

        self.log_dir = "logs"

    @property
    def batting_averages(self):
        """This metric tell you how frequenty the portfolio has higher returns than the benchmark"""
        output = {}
        for benchmark, bm_report in self.benchmarks.items():
            difference = (self.pf_report.monthly_returns - bm_report.monthly_returns).dropna()
            output[benchmark] = (difference > 0).sum() / difference.count()

        return output

    @property
    def spearman_correlations(self):
        """Calculates Spearman correlations between portfolio returns and benchmark returns for each benchmark"""
        output = {}
        for benchmark, bm_report in self.benchmarks.items():
            corr = self.pf_report.pf_returns.corr(bm_report.pf_returns, method="spearman", min_periods=1)
            output[benchmark] = corr

        return output

    @property
    def pearson_correlations(self):
        """Calculates Pearson correlations between portfolio returns and benchmark returns for each benchmark"""
        output = {}
        for benchmark, bm_report in self.benchmarks.items():
            corr = self.pf_report.pf_returns.corr(bm_report.pf_returns, method="pearson", min_periods=1)
            output[benchmark] = corr

        return output

    @property
    def kendall_correlations(self):
        """Calculates Kendall correlations between portfolio returns and benchmark returns for each benchmark"""
        output = {}
        for benchmark, bm_report in self.benchmarks.items():
            corr = self.pf_report.pf_returns.corr(bm_report.pf_returns, method="kendall", min_periods=1)
            output[benchmark] = corr

        return output

    @property
    def betas(self):
        """Calculates beta values representing the sensitivity of portfolio returns to changes in benchmark returns
        for each benchmark"""
        output = {}
        for benchmark, bm_report in self.benchmarks.items():
            beta = self.pf_report.pf_returns.cov(bm_report.pf_returns, min_periods=1) / bm_report.pf_returns.var()
            output[benchmark] = beta

        return output

    @property
    def alphas(self):
        """Calculates Jensen's alpha between portfolio returns and benchmark returns for each benchmark"""
        output = {}
        for benchmark, bm_report in self.benchmarks.items():
            beta = self.pf_report.pf_returns.cov(bm_report.pf_returns, min_periods=1) / bm_report.pf_returns.var()
            jensen_alpha = self.pf_report.cagr - (beta * bm_report.cagr)
            output[benchmark] = jensen_alpha

        return output

    @staticmethod
    def performance_to_pct(performance):
        return performance * 100

    @staticmethod
    def drawdown_to_pct(drawdown, index):
        return pd.Series(drawdown.flatten() * 100, index=index)

    def get_benchmark_metrics(self):
        """Retrieves various benchmark metrics including batting averages, Pearson correlations, and beta values"""
        return pd.DataFrame(
            [self.batting_averages, self.pearson_correlations, self.alphas, self.betas],
            index=["batting_average", "pearson_correlation", "alpha", "beta"],
        ).T

    def get_benchmark_monthly_returns(self, months=5):
        """Provides monthly returns for the portfolio and benchmarks in recent years

        Args:
            months (int): number of months to show for monthly returns. Default is 5.
        """

        list_output = []
        benchmarks = [self.pf_report] + list(self.benchmarks.values())

        for report in benchmarks:
            monthly_ret = report.monthly_returns.iloc[-months:].to_dict()
            list_output.append(monthly_ret)

        return list_output

    def get_benchmark_annual_returns(self, years=5):
        """Provides annual returns for the portfolio and benchmarks in recent years

        Args:
            years (int): number of years to show for annual returns. Default is 5.
        """

        list_output = []
        benchmarks = [self.pf_report] + list(self.benchmarks.values())

        for report in benchmarks:
            annual_ret = report.annual_returns.iloc[-years:].to_dict()
            list_output.append(annual_ret)

        return list_output

    def get_benchmark_trailing_cagr(self):
        """Calculates the trailing compound annual growth rate (CAGR) for different time periods of portfolio and benchmarks"""
        list_output = []
        benchmarks = [self.pf_report] + list(self.benchmarks.values())

        for report in benchmarks:
            output_benchmark = {
                "10 years returns": report.get_recent_cagr(years=10),
                "5 years returns": report.get_recent_cagr(years=5),
                "3 years returns": report.get_recent_cagr(years=3),
                "1 year returns": report.get_recent_cagr(years=1),
                "6 months returns": report.get_recent_cagr(months=6),
                "3 months returns": report.get_recent_cagr(months=3),
            }
            list_output.append(output_benchmark)

        return list_output

    def get_metrics(self):
        metrics = pd.DataFrame(self.pf_report.get_metrics(), index=[self.portfolio_name])
        metrics = pd.concat(
            [metrics] + [pd.DataFrame(x.get_metrics(), index=[y]) for y, x in self.benchmarks.items()], axis=0
        )
        metrics = pd.concat([metrics, self.get_benchmark_metrics()], axis=1)
        return metrics

    def print_metrics(self):
        """Print the performance metrics for the portfolio and all the benchmarks"""
        print(
            tabulate(
                self.get_metrics().T,
                tablefmt="fancy_grid",
                headers=[self.portfolio_name] + [x for x in self.benchmarks.keys()],
            )
        )

    def metrics_to_csv(self, output_dir="", file_name: str = "metrics.csv"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        self.get_metrics().to_csv(os.path.join(self.log_dir, output_dir, file_name))

    def metrics_to_json(self, output_dir="", file_name: str = "metrics.json"):
        os.makedirs(os.path.join(self.log_dir, output_dir), exist_ok=True)

        with open(os.path.join(self.log_dir, output_dir, file_name), "w") as f:
            json.dump(self.get_metrics(), f)

    def print_benchmark_metrics(self):
        """Prints the benchmark metrics in a formatted table"""
        metrics = pd.DataFrame(self.get_benchmark_metrics(), index=[x for x in self.benchmarks.keys()])

        print(tabulate(metrics.T, tablefmt="fancy_grid", headers=[x for x in self.benchmarks.keys()]))

    def print_benchmark_monthly_returns(self):
        """Prints the benchmark monthly returns for the portfolio and all the benchmarks"""
        metrics = pd.DataFrame(
            self.get_benchmark_monthly_returns(), index=["Portfolio"] + [x for x in self.benchmarks.keys()]
        )

        print(tabulate(metrics.T, tablefmt="fancy_grid", headers=["Portfolio"] + [x for x in self.benchmarks.keys()]))

    def print_benchmark_annual_returns(self):
        """Prints the benchmark annual returns for the portfolio and all the benchmarks"""
        metrics = pd.DataFrame(
            self.get_benchmark_annual_returns(), index=[self.portfolio_name] + [x for x in self.benchmarks.keys()]
        )

        print(
            tabulate(
                metrics.T, tablefmt="fancy_grid", headers=[self.portfolio_name] + [x for x in self.benchmarks.keys()]
            )
        )

    def print_benchmark_trailing_cagr(self):
        """Print the trailing cagr for the portfolio and all the benchmarks"""
        metrics = pd.DataFrame(
            self.get_benchmark_trailing_cagr(), index=[self.portfolio_name] + [x for x in self.benchmarks.keys()]
        )

        print(
            tabulate(
                metrics.T, tablefmt="fancy_grid", headers=[self.portfolio_name] + [x for x in self.benchmarks.keys()]
            )
        )
