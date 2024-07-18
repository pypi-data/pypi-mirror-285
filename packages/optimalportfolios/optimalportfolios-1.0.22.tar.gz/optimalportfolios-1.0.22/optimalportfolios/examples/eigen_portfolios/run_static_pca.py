import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import qis as qis
from typing import Optional, Dict
from enum import Enum
# from bbg_fetch import fetch_field_timeseries_per_tickers
import cvxpy as cvx

from qis.models.linear.pca import compute_eigen_portfolio_weights
from optimalportfolios.optimization.solvers.tracking_error import minimize_tracking_error


class EtfUniverse(Enum):
    LARGE_CAP = 'IVV'
    MID_CAP = 'IJH'
    SMALL_CAP = 'IWM'
    EAFE = 'EFA'
    EM = 'EEM'
    AGG_BOND = 'AGG'
    TREASURY = 'TLT'
    HY = 'HYG'
    CORP = 'LQD'
    REIT = 'IYR'
    COMMODITY = 'DBC'
    GOLD = 'GLD'


def create_price_data():
    tickers = {f"{x.value} US Equity": x.name for x in list(EtfUniverse)}
    price_data = fetch_field_timeseries_per_tickers(tickers=list(tickers.keys()))
    price_data = price_data.rename(tickers, axis=1)
    return price_data


def run_pca_analysis(prices: pd.DataFrame, benchmark_price: pd.Series, freq: str = 'W-WED'):
    returns = qis.to_returns(prices=prices, freq=freq, is_log_returns=True).dropna()
    returns_np = returns.to_numpy()

    covar = qis.compute_masked_covar_corr(data=returns, is_covar=True)

    weights = compute_eigen_portfolio_weights(covar=covar)
    print(f"weights=\n{weights}")

    portfolios_pnls = np.zeros_like(returns_np)
    weights_pd = {}
    for idx, principal_portfolio in enumerate(weights):
        portfolios_pnls[:, idx] = returns_np.dot(principal_portfolio)
        weights_pd[f"Portfolio f{idx}"] = pd.Series(0.015*principal_portfolio, index=prices.columns)
    weights_pd = pd.DataFrame.from_dict(weights_pd, orient='index')
    weights_pd.loc['EigenParity_2', :] = np.nanmean(weights_pd.iloc[:2, :], axis=0)
    weights_pd.loc['EigenParity_3', :] = np.nanmean(weights_pd.iloc[:3, :], axis=0)
    weights_pd.loc['EigenParity_4', :] = np.nanmean(weights_pd.iloc[:4, :], axis=0)
    weights_pd.loc['EigenParity_5', :] = np.nanmean(weights_pd.iloc[:5, :], axis=0)
    print(weights_pd)

    benchmark_weights = weights_pd.loc['EigenParity_2', :].to_numpy()
    lo_weight = minimize_tracking_error(covar=52.0*covar,
                                        benchmark_weights=benchmark_weights,
                                        min_weights=np.zeros_like(benchmark_weights),
                                        max_weights=0.2*np.ones_like(benchmark_weights),
                                        turnover_constraint=None  # todo
                                        )
    weights_pd.loc['LO', :] = lo_weight

    # with alpha
    alpha = compute_momentum_alpha(prices=prices, mom_long_span=252, mom_short_span=21).median(0)
    print(alpha)
    alpha_weight = maximize_alpha_over_tracking_error(covar=52.0*covar,
                                                      alphas=alpha.to_numpy(),
                                                      benchmark_weights=benchmark_weights,
                                                      min_weights=np.zeros_like(benchmark_weights),
                                                      max_weights=0.2*np.ones_like(benchmark_weights),
                                                      tracking_err_vol_constraint=0.5,
                                                      turnover_constraint=None  # todo
                                                      )
    weights_pd.loc['Alpha', :] = alpha_weight

    print(weights_pd)

    portfolios_pnls = pd.DataFrame(portfolios_pnls, index=returns.index)
    corr = qis.compute_masked_covar_corr(portfolios_pnls, is_covar=False)
    print(f"corr=\n{corr}")
    print(f"vol=\n{np.std(portfolios_pnls, axis=0)}")
    qis.plot_time_series(portfolios_pnls.cumsum(0))

    portfolio_datas = []
    for idx in weights_pd.index:
        portfolio_data = qis.backtest_model_portfolio(prices=prices,
                                                      weights=weights_pd.loc[idx, :],
                                                      rebalancing_costs=0.0,
                                                      rebalance_freq=freq,
                                                      is_output_portfolio_data=True,
                                                      ticker=f"{idx}")
        portfolio_datas.append(portfolio_data)

    multi_portfolio_data = qis.MultiPortfolioData(portfolio_datas, benchmark_prices=benchmark_price)
    time_period = qis.TimePeriod(returns.index[0], returns.index[-1])
    figs = qis.generate_multi_portfolio_factsheet(multi_portfolio_data=multi_portfolio_data,
                                                  time_period=time_period,
                                                  **qis.fetch_default_report_kwargs(time_period=time_period))

    return figs


def minimize_tracking_error(covar: np.ndarray,
                            benchmark_weights: np.ndarray = None,
                            min_weights: np.ndarray = None,
                            max_weights: np.ndarray = None,
                            is_long_only: bool = True,
                            max_leverage: float = None,  # for long short portfolios
                            turnover_constraint: Optional[float] = 0.5,
                            weights_0: np.ndarray = None,
                            solver: str = 'ECOS_BB'
                            ) -> np.ndarray:
    """
    max alpha@w
    such that
    w @ Sigma @ w.t <= tracking_err_vol_constraint
    sum(abs(w-w_0)) <= turnover_constraint
    sum(w) = 1 # exposure constraint
    w >= 0  # long only constraint

    subject to linear constraints
         1. weight_min <= w <= weight_max
         2. sum(w) = 1
         3. exposure_budget_eq[0]^t*w = exposure_budget_eq[1]
    """
    n = covar.shape[0]
    w = cvx.Variable(n)
    tracking_error_var = cvx.quad_form(w-benchmark_weights, covar)

    objective_fun = tracking_error_var

    objective = cvx.Minimize(objective_fun)

    # add constraints
    constraints = []
    # gross_notional = 1:
    constraints = constraints + [cvx.sum(w) == 1]

    # tracking error constraint
    # constraints += [tracking_error_var <= tracking_err_vol_constraint ** 2]  # variance constraint

    # turnover_constraint:
    if turnover_constraint is not None:
        if weights_0 is None:
            raise ValueError(f"weights_0 must be given")
        constraints += [cvx.norm(w-weights_0, 1) <= turnover_constraint]

    if is_long_only:
        constraints = constraints + [w >= 0.0]
    if min_weights is not None:
        constraints = constraints + [w >= min_weights]
    if max_weights is not None:
        constraints = constraints + [w <= max_weights]
    #if exposure_budget_eq is not None:
    #    constraints = constraints + [exposure_budget_eq[0] @ w == exposure_budget_eq[1]]
    if max_leverage is not None:
        constraints = constraints + [cvx.norm(w, 1) <= max_leverage]

    problem = cvx.Problem(objective, constraints)
    problem.solve(verbose=True, solver=solver)

    optimal_weights = w.value
    if optimal_weights is None:
        raise ValueError(f"not solved")

    return optimal_weights


def maximize_alpha_over_tracking_error(covar: np.ndarray,
                                       alphas: np.ndarray = None,
                                       benchmark_weights: np.ndarray = None,
                                       min_weights: np.ndarray = None,
                                       max_weights: np.ndarray = None,
                                       is_long_only: bool = True,
                                       max_leverage: float = None,  # for long short portfolios
                                       tracking_err_vol_constraint: float = 0.05,  # annualised sqrt tracking error
                                       turnover_constraint: Optional[float] = 0.5,
                                       weights_0: np.ndarray = None,
                                       solver: str = 'ECOS_BB'
                                       ) -> np.ndarray:
    """
    max alpha@w
    such that
    w @ Sigma @ w.t <= tracking_err_vol_constraint
    sum(abs(w-w_0)) <= turnover_constraint
    sum(w) = 1 # exposure constraint
    w >= 0  # long only constraint

    subject to linear constraints
         1. weight_min <= w <= weight_max
         2. sum(w) = 1
         3. exposure_budget_eq[0]^t*w = exposure_budget_eq[1]
    """

    n = covar.shape[0]
    w = cvx.Variable(n)
    tracking_error_var = cvx.quad_form(w-benchmark_weights, covar)

    objective_fun = alphas.T @ (w - benchmark_weights) - 0.125*tracking_error_var

    objective = cvx.Maximize(objective_fun)

    # add constraints
    constraints = []
    # gross_notional = 1:
    constraints = constraints + [cvx.sum(w) == 1]

    # tracking error constraint
    # constraints += [tracking_error_var <= tracking_err_vol_constraint ** 2]  # variance constraint

    # turnover_constraint:
    if turnover_constraint is not None:
        if weights_0 is None:
            raise ValueError(f"weights_0 must be given")
        constraints += [cvx.norm(w-weights_0, 1) <= turnover_constraint]

    if is_long_only:
        constraints = constraints + [w >= 0.0]
    if min_weights is not None:
        constraints = constraints + [w >= min_weights]
    if max_weights is not None:
        constraints = constraints + [w <= max_weights]
    #if exposure_budget_eq is not None:
    #    constraints = constraints + [exposure_budget_eq[0] @ w == exposure_budget_eq[1]]
    if max_leverage is not None:
        constraints = constraints + [cvx.norm(w, 1) <= max_leverage]

    problem = cvx.Problem(objective, constraints)
    problem.solve(verbose=False, solver=solver)

    optimal_weights = w.value
    if optimal_weights is None:
        raise ValueError(f"not solved")

    return optimal_weights


def compute_momentum_alpha(prices: pd.DataFrame,
                           mom_long_span: int = 12,
                           mom_short_span: Optional[int] = 1
                           ) -> pd.DataFrame:
    """
    compute cross-sectional momentum
    """
    if mom_short_span is not None:
        price1 = prices.shift(mom_short_span)
    else:
        price1 = prices
    momentum = price1.divide(prices.shift(mom_long_span)) - 1.0
    non_nan_cond = np.isfinite(momentum.to_numpy())
    alpha_score = np.divide(np.subtract(momentum, np.nanmean(momentum, keepdims=True, axis=1)),
                            np.nanstd(momentum, keepdims=True, axis=1), where=non_nan_cond)
    return alpha_score


class UnitTests(Enum):
    CREATE_PRICE_DATA = 1
    RUN_PCA = 2


def run_unit_test(unit_test: UnitTests):

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # local_path = "C://Users//uarts//Python//quant_strats//resources//etf_portfolios//"
    local_path = "C://Users//artur//OneDrive//analytics//qdev//resources//etf_portfolios//"
    import quant_strats.local_path as lp

    if unit_test == UnitTests.CREATE_PRICE_DATA:
        price_data = create_price_data()
        print(price_data)
        qis.save_df_to_csv(df=price_data, file_name='etf_prices', local_path=local_path)

    elif unit_test == UnitTests.RUN_PCA:
        prices = qis.load_df_from_csv(file_name='etf_prices', local_path=local_path)
        # prices = prices.iloc[:, 7:]
        n = len(prices.columns)
        benchmark_price = qis.backtest_model_portfolio(prices=prices, weights=np.ones(n)/n,
                                                 rebalance_freq='QE').to_frame('EW')

        figs = run_pca_analysis(prices=prices, benchmark_price=benchmark_price)
        qis.save_figs_to_pdf(figs=figs,
                             file_name=f"eigen_portfolios",
                             orientation='landscape',
                             local_path=lp.get_output_path())

    plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.RUN_PCA

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)

