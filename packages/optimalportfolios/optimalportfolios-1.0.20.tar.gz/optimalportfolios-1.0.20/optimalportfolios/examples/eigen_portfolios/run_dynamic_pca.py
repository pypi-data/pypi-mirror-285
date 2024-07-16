"""
    risk-based methods using EWMA covariance matrix
    implementation of [PortfolioObjective.EQUAL_RISK_CONTRIBUTION,
                       PortfolioObjective.MAX_DIVERSIFICATION,
                       PortfolioObjective.RISK_PARITY_ALT,
                       PortfolioObjective.MIN_VAR]
"""

# packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Optional, List, Tuple
from enum import Enum
import qis as qis
from qis import TimePeriod, PortfolioData
from qis.models.linear.pca import compute_eigen_portfolio_weights

# optimisers
import optimalportfolios.optimization.solvers.nonlinear as ops
import optimalportfolios.optimization.solvers.quadratic as qup
from optimalportfolios.optimization.solvers.tracking_error import minimize_tracking_error
from optimalportfolios.optimization.config import PortfolioObjective, set_min_max_weights, set_to_zero_not_investable_weights
from optimalportfolios.utils.filter_nans import filter_covar_and_vectors_for_nans
from optimalportfolios.examples.eigen_portfolios.compute_eigen_portfolios import (compute_rolling_pca_eigen_portfolios,
                                                                                  compute_rolling_ewmpca_eigen_portfolios)

def set_pca_portfolios_index(n: int) -> List[str]:
    return [f"PC{n+1}" for n in np.arange(n)]


def compute_rolling_eigen_parity_weights(prices: pd.DataFrame,
                                         returns_freq: Optional[str] = 'W-WED',
                                         rebalancing_freq: str = 'YE',
                                         span: int = 52,  # ewma span in periods of returns_freq
                                         is_regularize: bool = False,
                                         is_log_returns: bool = True,
                                         **kwargs
                                         ) -> Tuple[Dict[pd.Timestamp, pd.DataFrame],
                                                    Dict[str, pd.DataFrame],
                                                    Dict[pd.Timestamp, np.ndarray]]:
    """
    compute time series of ewma matrix and solve for optimal weights at rebalancing_freq
    fixed_weights are fixed weights for principal portfolios
    implementation of [PortfolioObjective.EQUAL_RISK_CONTRIBUTION,
                       PortfolioObjective.MAX_DIVERSIFICATION,
                       PortfolioObjective.RISK_PARITY_ALT,
                       PortfolioObjective.MIN_VAR,
                       PortfolioObjective.QUADRATIC_UTILITY]
    asset becomes investable when its price time series is not zero for covariance estimation
    """
    returns = qis.to_returns(prices=prices,
                             is_log_returns=is_log_returns,
                             freq=returns_freq,
                             ffill_nans=True,
                             include_end_date=False)

    # drift adjusted returns
    returns_np = returns.to_numpy()
    x = returns_np - qis.compute_ewm(returns_np, span=span)

    # fill nans using zeros
    covar_tensor_txy = qis.compute_ewm_covar_tensor(a=x, span=span, nan_backfill=qis.NanBackfill.ZERO_FILL)
    rebalancing_schedule = qis.generate_rebalancing_indicators(df=returns, freq=rebalancing_freq, num_warmup_periods=span)

    an_factor = qis.infer_an_from_data(data=returns)
    pca_portfolios_index = set_pca_portfolios_index(n=len(prices.columns))
    eigen_weights_by_portfolios = {portfolio: {} for portfolio in pca_portfolios_index}
    eigen_weights_by_dates = {}
    sampled_covar = {}
    for idx, (date, value) in enumerate(rebalancing_schedule.items()):
        if value:
            covar = an_factor*covar_tensor_txy[idx]
            if is_regularize:
                covar = qis.matrix_regularization(covar=covar)
            sampled_covar[date] = covar
            current_weights = compute_eigen_portfolio_weights_withnans(covar=pd.DataFrame(covar, index=prices.columns, columns=prices.columns))
            eigen_weights_by_dates[date] = current_weights
            for portfolio in pca_portfolios_index:
                eigen_weights_by_portfolios[portfolio].update({date: current_weights.loc[portfolio, :]})

    for portfolio in pca_portfolios_index:
        eigen_weights_by_portfolios[portfolio] = pd.DataFrame.from_dict(eigen_weights_by_portfolios[portfolio], orient='index')

    # weights = pd.DataFrame.from_dict(weights, orient='index', columns=returns.columns)
    return eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar


def compute_eigen_parity_portfolios(prices: pd.DataFrame,
                                    eigen_weights_by_dates: Dict[str, pd.DataFrame],
                                    sampled_covar: Dict[pd.Timestamp, np.ndarray],
                                    rebalancing_freq: str = 'YE',
                                    span: int = 52,  # ewma span in periods of returns_freq
                                    max_portfolios: Tuple[int, int] = (0, 20),
                                    allocation: Optional[pd.DataFrame] = None,
                                    group_loadings: Optional[Dict[str, pd.Series]] = None
                                    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:

    """
    eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar = compute_rolling_eigen_parity_weights(prices=prices,
                                                                                                              rebalancing_freq=rebalancing_freq,
                                                                                                              span=span)
    """
    num_eigens = [n+1 for n in np.arange(start=max_portfolios[0], stop=max_portfolios[1])]
    eigen_portfolios = {f"Eigen-{n}": {} for n in num_eigens}
    long_eigen_portfolios = {f"LO Eigen-{n}": {} for n in num_eigens}

    if allocation is not None:
        group_exposures_min_max = create_group_exposures_min_max(allocation=allocation, group_loadings=group_loadings)
    else:
        group_exposures_min_max = None

    sampled_dates = pd.DatetimeIndex(eigen_weights_by_dates.keys())

    # rebalancing schedule defined on weights dates
    rebalancing_schedule = qis.generate_rebalancing_indicators(index=sampled_dates, freq=rebalancing_freq).index.to_list()

    for date in rebalancing_schedule:
        principal_portfolios = eigen_weights_by_dates[date]
        for n in num_eigens:  # thake the avg from the first n rows
            avg_portfolio = principal_portfolios.iloc[:n, :].mean(0)
            benchmark_weights = avg_portfolio.to_numpy()
            lo_weight = minimize_tracking_error(covar=sampled_covar[date],
                                                benchmark_weights=benchmark_weights,
                                                min_weights=np.zeros_like(benchmark_weights),
                                                max_weights=0.1*np.ones_like(benchmark_weights),   #10.0*np.ones_like(benchmark_weights) / len(benchmark_weights)
                                                turnover_constraint=None,
                                                group_exposures_min_max=group_exposures_min_max
                                                )

            eigen_portfolios[f"Eigen-{n}"].update({date: avg_portfolio})
            long_eigen_portfolios[f"LO Eigen-{n}"].update({date: pd.Series(lo_weight, index=prices.columns)})
    for n in num_eigens:
        eigen_portfolios[f"Eigen-{n}"] = pd.DataFrame.from_dict(eigen_portfolios[f"Eigen-{n}"], orient='index')
        long_eigen_portfolios[f"LO Eigen-{n}"] = pd.DataFrame.from_dict(long_eigen_portfolios[f"LO Eigen-{n}"], orient='index')

    return eigen_portfolios, long_eigen_portfolios


def compute_eigen_portfolio_weights_withnans(covar: pd.DataFrame) -> pd.DataFrame:
    """
    create wrapper accounting for nans in covar matrix
    assets in columns/rows of covar must correspond to alphas.index
    """
    # filter out assets with zero variance or nans
    covar_pd, good_vectors = filter_covar_and_vectors_for_nans(covar=covar, vectors=None)
    # pc weights are in rows
    eigen_weights = compute_eigen_portfolio_weights(covar=covar_pd.to_numpy())
    eigen_weights = pd.DataFrame(eigen_weights, columns=covar_pd.index, index=set_pca_portfolios_index(n=len(covar_pd.index)))
    full_eigen_weights = eigen_weights.reindex(columns=covar.index)\
        .reindex(index=set_pca_portfolios_index(n=len(covar.index))).fillna(0.0)  # align with tickers
    return full_eigen_weights


def load_universe_data(local_path: str, file_name: str = 'etf_universe',
                       is_narrow: bool = True,
                       freq: Optional[str] = 'B',
                       ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dfs = qis.load_df_dict_from_excel(dataset_keys=['universe', 'prices', 'allocation'], file_name=file_name, local_path=local_path)
    prices, universe, allocation = dfs['prices'], dfs['universe'], dfs['allocation']
    prices = prices.drop(['JPCAUS1M Index', 'DBV US Equity', 'DBMF US Equity'], axis=1)
    universe = universe.drop(['JPCAUS1M Index', 'DBV US Equity', 'DBMF US Equity'], axis=0)
    prices = prices[universe.index]
    if is_narrow:
        universe = universe.loc[np.greater(universe['SAA'], 0.0), :]
        prices = prices[universe.index]
    if freq is not None:
        prices = prices.asfreq(freq).ffill()
    # prices = prices.loc['31Dec2007':, :].dropna()
    return prices, universe, allocation


def set_group_min_max_allocation(allocation: pd.DataFrame, universe: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    assign matrix of loadings for group_loadings
    group_loadings = index by instruments, columns = loadings by min max
    """
    group_loadings = {}
    asset_class = universe['Asset Class'].to_numpy(dtype=str)
    for group in allocation.index:
        group_loadings[group] = pd.Series(np.where(asset_class == group, 1.0, 0.0), index=universe.index, name=group)
    return group_loadings


def create_group_exposures_min_max(allocation: pd.DataFrame,
                                   group_loadings: Dict[str, pd.Series]
                                   ) -> List[Tuple[np.ndarray, float, float]]:
    group_exposures_min_max = []
    for group, min, max in zip(allocation.index, allocation['min'], allocation['max']):
        group_exposures_min_max.append((group_loadings[group].to_numpy(), min, max))
    return group_exposures_min_max


class UnitTests(Enum):
    RUN_DYNAMIC_PCA = 1
    RUN_EIGEN_PARITY_PORTFOLIOS = 2
    SET_ALLOCATION = 3


def run_unit_test(unit_test: UnitTests):

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # local_path = "C://Users//uarts//Python//quant_strats//resources//etf_portfolios//"
    local_path = "C://Users//artur//OneDrive//analytics//qdev//resources//etf_portfolios//"
    import optimalportfolios.local_path as lp

    prices, universe, allocation = load_universe_data(file_name='etf_universe', local_path=local_path, is_narrow=True)
    prices = prices.loc['31Dec2004':, :].dropna()
    print(prices)
    group_data = universe['Asset Class']
    group_order = allocation.index.to_list()
    group_loadings = set_group_min_max_allocation(allocation=allocation, universe=universe)
    print(group_loadings)

    n = len(prices.columns)
    benchmark_price = qis.backtest_model_portfolio(prices=prices, weights=np.ones(n) / n,
                                                   rebalance_freq='QE').to_frame('EW')
    time_period = qis.TimePeriod('31Dec2005', prices.index[-1])

    if unit_test == UnitTests.RUN_DYNAMIC_PCA:
        # prices = prices.iloc[:, 7:]
        eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar = compute_rolling_eigen_parity_weights(prices=prices)

        portfolio_datas = []
        for key, df in eigen_weights_by_portfolios.items():
            print(key)
            print(df)
            portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                          weights=0.075*df,
                                                          rebalancing_costs=0.0,
                                                          rebalance_freq=None,
                                                          is_output_portfolio_data=True,
                                                          ticker=f"{key}")
            portfolio_data.set_group_data(group_data, group_order)
            portfolio_datas.append(portfolio_data)
        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas, benchmark_prices=benchmark_price)
        figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                      time_period=time_period,
                                                      add_group_exposures_and_pnl=True,
                                                      **qis.fetch_default_report_kwargs(time_period=time_period))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"eigen_portfolios",
                             orientation='landscape',
                             local_path=lp.get_output_path())

    elif unit_test == UnitTests.RUN_EIGEN_PARITY_PORTFOLIOS:

        is_ewmpca_eigen = True
        if is_ewmpca_eigen:
            eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar = compute_rolling_ewmpca_eigen_portfolios(
                prices=prices,
                freq='W-WED',
                span=52,
                warmup_window=52)
        else:
            eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar = compute_rolling_pca_eigen_portfolios(
                prices=prices,
                freq='W-WED',
                span=52,
                warmup_window=52)

        eigen_portfolios, long_eigen_portfolios = compute_eigen_parity_portfolios(prices=prices, rebalancing_freq='QE',
                                                                                  eigen_weights_by_dates=eigen_weights_by_dates,
                                                                                  sampled_covar=sampled_covar,
                                                                                  max_portfolios=(0, 17),
                                                                                  allocation=allocation,
                                                                                  group_loadings=group_loadings)

        portfolio_datas = []
        for key, df in eigen_weights_by_portfolios.items():
            portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                          weights=0.01*df,
                                                          rebalancing_costs=0.0,
                                                          rebalance_freq=None,
                                                          is_output_portfolio_data=True,
                                                          ticker=f"{key}")
            portfolio_data.set_group_data(group_data, group_order)
            portfolio_datas.append(portfolio_data)
        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas, benchmark_prices=benchmark_price)
        figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                      time_period=time_period,
                                                      add_group_exposures_and_pnl=True,
                                                      **qis.fetch_default_report_kwargs(time_period=time_period))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"principal_portfolios",
                             orientation='landscape',
                             local_path=lp.get_output_path())

        portfolio_datas = []
        for key, df in eigen_portfolios.items():
            portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                          weights=0.01 * df,
                                                          rebalancing_costs=0.0,
                                                          rebalance_freq=None,
                                                          is_output_portfolio_data=True,
                                                          ticker=f"{key}")
            portfolio_data.set_group_data(group_data, group_order)
            portfolio_datas.append(portfolio_data)
        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas, benchmark_prices=benchmark_price)
        figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                      time_period=time_period,
                                                      add_group_exposures_and_pnl=True,
                                                      **qis.fetch_default_report_kwargs(time_period=time_period))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"eigen_parity_portfolios",
                             orientation='landscape',
                             local_path=lp.get_output_path())

        # long on;y
        portfolio_datas = []
        for key, df in long_eigen_portfolios.items():
            portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                          weights=df,
                                                          rebalancing_costs=0.0,
                                                          rebalance_freq=None,
                                                          is_output_portfolio_data=True,
                                                          ticker=f"{key}")
            portfolio_data.set_group_data(group_data, group_order)
            portfolio_datas.append(portfolio_data)
        multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas, benchmark_prices=benchmark_price)
        figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                      time_period=time_period,
                                                      add_group_exposures_and_pnl=True,
                                                      **qis.fetch_default_report_kwargs(time_period=time_period))
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"long_eigen_parity_portfolios",
                             orientation='landscape',
                             local_path=lp.get_output_path())

    plt.close('all')
    # plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.RUN_EIGEN_PARITY_PORTFOLIOS

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)

