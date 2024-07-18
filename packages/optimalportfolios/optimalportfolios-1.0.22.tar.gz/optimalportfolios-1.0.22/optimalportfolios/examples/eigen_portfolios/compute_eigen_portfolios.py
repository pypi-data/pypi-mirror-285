import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import qis as qis
from typing import Dict, List, Tuple
from enum import Enum
import optimalportfolios.examples.eigen_portfolios.ewm_pca as xpca
from optimalportfolios.utils.filter_nans import filter_covar_and_vectors_for_nans


def set_pca_portfolios_index(n: int) -> List[str]:
    return [f"PC{n+1}" for n in np.arange(n)]


def compute_rolling_ewmpca_eigen_portfolios(prices: pd.DataFrame,
                                            freq: str = 'W-WED',
                                            span: int = 90,
                                            warmup_window: int = 52
                                            ) -> Tuple[Dict[pd.Timestamp, pd.DataFrame], Dict[str, pd.DataFrame], Dict[pd.Timestamp, np.ndarray]]:
    """
    compute pca eigen portfolios using exponential pca or rolling pca
    warmup_window in terms of freq-periods
    """
    returns = qis.to_returns(prices=prices, freq=freq, is_log_returns=True, drop_first=True)
    #ra_returns, weights, ewm_vol = qis.compute_ra_returns(returns=returns, span=span)
    #returns_np = ra_returns.to_numpy()
    returns_np = returns.to_numpy()

    pca_portfolios_index = set_pca_portfolios_index(n=len(prices.columns))
    covar0 = qis.compute_masked_covar_corr(returns_np[:warmup_window, :])
    ewmpca = xpca.EWMPCA(alpha=1.0-2.0/(span+1), W_initial=covar0, max_iter_count=1000)

    # portfolio and weights by assets
    eigen_weights_by_portfolios = {portfolio: {} for portfolio in pca_portfolios_index}
    eigen_weights_by_dates = {}
    sampled_covar = {}
    for t, date in enumerate(returns.index):
        # filter out returns with nans
        returns_t = returns_np[t, :]
        is_nan_return = np.isnan(returns_t)
        # set nan returns to zero
        returns_t[is_nan_return] = 0.0
        eigen_values, eigen_vectors = ewmpca.add(returns_t)
        # print(f"eigen_values=\n{eigen_values}")
        # print(f"eigen_vectors=\n{eigen_vectors}")
        if t > warmup_window:
            scale = np.sqrt(eigen_values)
            scale = np.reciprocal(np.where(np.greater(scale, 0.0), scale, 0.0))
            eigen_vectors = scale * eigen_vectors
            for idx, portfolio in enumerate(pca_portfolios_index):
                eigen_vector = eigen_vectors[idx, :]
                eigen_vector[is_nan_return] = 0.0
                eigen_weights_by_portfolios[portfolio].update({date: eigen_vector})
            eigen_weights_by_dates[date] = pd.DataFrame(eigen_vectors, index=pca_portfolios_index, columns=prices.columns)
            sampled_covar[date] = 52.0*ewmpca.ewmcov.cov

    # map weights to pd.dataframe[dates, weights by asset]
    for key, weights in eigen_weights_by_portfolios.items():
        eigen_weights_by_portfolios[key] = pd.DataFrame.from_dict(eigen_weights_by_portfolios[key],
                                                                  orient='index',
                                                                  columns=prices.columns)
    return eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar


def compute_rolling_pca_eigen_portfolios(prices: pd.DataFrame,
                                         freq: str = 'W-WED',
                                         span: int = 90,
                                         warmup_window: int = 10
                                         ) -> Tuple[Dict[pd.Timestamp, pd.DataFrame], Dict[str, pd.DataFrame], Dict[pd.Timestamp, np.ndarray]]:
    """
    compute pca eigen portfolios using exponential pca or rolling pca
    warmup_window in terms of freq-periods
    """
    returns = qis.to_returns(prices=prices, freq=freq, is_log_returns=True)
    returns_np = returns.to_numpy()
    pca_portfolios_index = set_pca_portfolios_index(n=len(prices.columns))

    covar0 = qis.compute_masked_covar_corr(returns_np[:warmup_window, :])
    ewm_covar = qis.compute_ewm_covar_tensor(a=returns_np, covar0=covar0, span=span)
    eigen_weights_by_dates = {}
    eigen_weights_by_portfolios = {portfolio: {} for portfolio in pca_portfolios_index}
    sampled_covar = {}
    for t, date in enumerate(returns.index):
        # filter out returns with nans
        returns_t = returns_np[t, :]
        is_nan_return = np.where(np.isnan(returns_t))
        # set nan returns to zero
        returns_t[is_nan_return] = 0.0

        if t > warmup_window:
            covar_pd, _ = filter_covar_and_vectors_for_nans(covar=pd.DataFrame(ewm_covar[t], index=prices.columns, columns=prices.columns))
            eigen_values, eigen_vectors = np.linalg.eigh(covar_pd.to_numpy())
            scale = np.sqrt(eigen_values)
            scale = np.reciprocal(np.where(np.greater(scale, 0.0), scale, 0.0))
            eigen_weights = scale * eigen_vectors
            # backfill zeors
            eigen_weights = pd.DataFrame(eigen_weights, columns=covar_pd.index,
                                         index=set_pca_portfolios_index(n=len(covar_pd.index)))
            full_eigen_weights = eigen_weights.reindex(columns=prices.columns) \
                .reindex(index=set_pca_portfolios_index(n=len(prices.columns))).fillna(0.0)  # align with tickers
            eigen_vectors = full_eigen_weights.to_numpy()
            for idx, eigen_vector in enumerate(eigen_vectors):
                eigen_weights_by_portfolios[pca_portfolios_index[idx]].update({date: eigen_vector})

            eigen_weights_by_dates[date] = pd.DataFrame(eigen_vectors, index=pca_portfolios_index, columns=prices.columns)
            sampled_covar[date] = 52.0*ewm_covar[t]

    # map weights to pd.dataframe[dates, weights by asset]
    for key, weights in eigen_weights_by_portfolios.items():
        eigen_weights_by_portfolios[key] = pd.DataFrame.from_dict(eigen_weights_by_portfolios[key],
                                                                  orient='index',
                                                                  columns=prices.columns)
    return eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar


def run_rolling_pca(prices: pd.DataFrame, freq: str = 'W-WED', span: int = 90) -> Dict[str, pd.DataFrame]:
    returns = qis.to_returns(prices=prices, freq=freq, is_log_returns=True, drop_first=True)
    ewm_covar = qis.compute_ewm_covar_tensor(a=returns.to_numpy(), span=span)
    n_assets = len(returns.columns)
    portfolio_weights = {f"PC{n+1}": {} for n in np.arange(n_assets)}
    for t, date in enumerate(returns.index):
        if t > span:
            eigen_values, eigen_vectors = np.linalg.eigh(ewm_covar[t])
            eigen_vectors = np.reciprocal(np.sqrt(eigen_values)) * eigen_vectors  # eigenvectors will be orthonormal
            for n in np.arange(n_assets):
                portfolio_weights[f"PC{n+1}"].update({date: eigen_vectors[n, :]})
            # print(f"eigen_values=\n{eigen_values}")
            # print(f"eigen_vectors=\n{eigen_vectors}")
    for n in np.arange(n_assets):
        portfolio_weights[f"PC{n + 1}"] = pd.DataFrame.from_dict(portfolio_weights[f"PC{n + 1}"], orient='index',
                                                                 columns=prices.columns)

    return portfolio_weights


def run_static_pca_portfolios(prices: pd.DataFrame):
    returns = qis.to_returns(prices=prices, freq='W-WED', is_log_returns=True, drop_first=True)
    covar = qis.compute_masked_covar_corr(returns, is_covar=True)
    eigen_values, eigen_vectors = np.linalg.eigh(covar)
    eigen_vectors = np.reciprocal(np.sqrt(eigen_values)) * eigen_vectors  # eigenvectors will be orthonormal

    portfolios_pnls = returns @ eigen_vectors
    portfolios_pnls = pd.DataFrame(portfolios_pnls, index=returns.index)
    corr = qis.compute_masked_covar_corr(portfolios_pnls, is_covar=False)
    print(f"eigen_values=\n{eigen_values}")
    print(f"eigen_vectors=\n{eigen_vectors}")

    print(f"corr=\n{corr}")
    print(f"vol=\n{np.std(portfolios_pnls, axis=0)}")
    qis.plot_time_series(portfolios_pnls.cumsum(0))


def analyse_pc_portfolios(prices: pd.DataFrame,
                          eigen_weights_by_portfolios: Dict[str, pd.DataFrame]
                          ) -> List[plt.Figure]:

    dates = eigen_weights_by_portfolios[list(eigen_weights_by_portfolios.keys())[0]].index

    returns_f = prices.reindex(index=dates).ffill().pct_change()
    pnls = {}
    for key, weights in eigen_weights_by_portfolios.items():
        pnls[key] = returns_f.multiply(weights.shift(1)).sum(1)
    portfolios_pnls = pd.DataFrame.from_dict(pnls, orient='columns').dropna()

    corr = qis.compute_masked_covar_corr(portfolios_pnls, is_covar=False)
    print(f"corr=\n{corr}")
    print(f"vol=\n{np.std(portfolios_pnls, axis=0)}")

    figs = []
    with sns.axes_style("darkgrid"):
        fig, ax = plt.subplots(1, 1, figsize=(14, 12), tight_layout=True)
        figs.append(fig)
        qis.plot_time_series(portfolios_pnls.cumsum(0), ax=ax)

        for key, weights in eigen_weights_by_portfolios.items():
            fig, ax = plt.subplots(1, 1, figsize=(14, 12), tight_layout=True)
            figs.append(fig)
            qis.plot_time_series(weights, title=key, ax=ax)

    return figs


class UnitTests(Enum):
    RUN_STATIC_PCA = 1
    RUN_ROLLONG_PCA = 2
    RUN_EWM_PCA = 3


def run_unit_test(unit_test: UnitTests):

    import optimalportfolios.local_path as lp
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    tickers = ['SPY', 'TLT', 'GLD', 'HYG', 'LQD', 'USO']
    prices = yf.download(tickers, start=None, end=None)['Adj Close'][tickers]
    prices = prices.loc['2007':, :].dropna()

    is_normalise = True
    if is_normalise:
        np.random.seed(1)
        returns = qis.to_returns(prices, is_first_zero=True)
        rand_returns = np.random.multivariate_normal(mean=np.mean(returns, axis=0),
                                                     cov=qis.compute_masked_covar_corr(returns, is_covar=True),
                                                     size=returns.shape[0])
        prices = pd.DataFrame(np.exp(np.cumsum(rand_returns, axis=0)), columns=returns.columns, index=returns.index)

    print(prices)
    if unit_test == UnitTests.RUN_STATIC_PCA:
        prices = prices.dropna() # need weithout nans
        run_static_pca_portfolios(prices=prices)

    elif unit_test == UnitTests.RUN_ROLLONG_PCA:
        eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar = compute_rolling_pca_eigen_portfolios(prices=prices,
                                                                                                                  freq='ME',
                                                                                                                  span=24)
        analyse_pc_portfolios(prices=prices, eigen_weights_by_portfolios=eigen_weights_by_portfolios)

    elif unit_test == UnitTests.RUN_EWM_PCA:
        eigen_weights_by_dates, eigen_weights_by_portfolios, sampled_covar = compute_rolling_ewmpca_eigen_portfolios(prices=prices,
                                                                                                                     freq='W-FRI',
                                                                                                                     span=52,
                                                                                                                     warmup_window=104)
        figs = analyse_pc_portfolios(prices=prices, eigen_weights_by_portfolios=eigen_weights_by_portfolios)
        qis.save_figs_to_pdf(figs, file_name='ewm_pca', local_path=lp.get_output_path())

    plt.close('all')
    # plt.show()


if __name__ == '__main__':

    unit_test = UnitTests.RUN_EWM_PCA

    is_run_all_tests = False
    if is_run_all_tests:
        for unit_test in UnitTests:
            run_unit_test(unit_test=unit_test)
    else:
        run_unit_test(unit_test=unit_test)
