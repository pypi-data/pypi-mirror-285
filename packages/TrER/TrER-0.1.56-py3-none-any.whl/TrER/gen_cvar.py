import pandas as pd, numpy as np
from .CVaR_calculate import (
    IF_bbound_mate,
    IF_cvar_bbouns_ate,
    cvar_calculate,
    cvar_if_plugin,
    cvar_if_tauate,
)
from .utils import goldsectmax, rearrange_cvar, wtdquantile


def cvar_tau(data, ps, tau_col="tau"):
    result = pd.DataFrame()
    for p in ps:
        r = cvar_calculate(data, p, tau=tau_col)
        result = pd.concat((result, r), ignore_index=True)
    return result


def cvar_plugin(data, ps, tau_col="tau"):
    results = pd.DataFrame()
    for p in ps:
        r = cvar_calculate(data, p, tau=tau_col, method_if=cvar_if_plugin)
        results = pd.concat([results, r], ignore_index=True)
    return results


def cvar_mate(data, ps, tau_col="tau"):
    result = pd.DataFrame()
    for x in ps:
        r = cvar_calculate(data, x, tau=tau_col, method_if=cvar_if_tauate)
        result = pd.concat([result, r], ignore_index=True)
    return result


def cvar_bbound_mate(data, ps, bs, tau_col="tau", sw_col="sw", sort_cvar=True):
    tau = data[tau_col]
    sw = data[sw_col]

    sw1 = np.concatenate((sw, sw))
    results = pd.DataFrame()

    for b in bs:
        tau1 = np.concatenate((tau + b, tau - b))
        for p in ps:
            q = wtdquantile(tau1, sw1, p)
            IF = IF_bbound_mate(q, p, b, data)
            cvar = IF * sw
            CVaR = np.nanmean(cvar)
            CVaR_se = np.nanstd(cvar) / np.sqrt(len(sw))
            result = pd.DataFrame({"CVaR": [CVaR], "CVaR_se": [CVaR_se], "p": [p]})

            if b is not None:
                result["b"] = [b]

            results = pd.concat((results, result))
    results["b"] = np.round(results["b"], 3)
    if sort_cvar:
        n_results = results.copy()
        n_results["CVaR"] = n_results.groupby("b")["CVaR"].transform(rearrange_cvar)
        return n_results
    return results


def cvar_bbounded(cvar_mate, cvar_bbound_mate, bs):
    c1 = cvar_mate.assign(b=np.nan, type="CATE-CVaR")
    c2 = cvar_bbound_mate.assign(type="Thm. 3.2").query("b > 0")
    c3_temp = []

    for b in bs:
        temp_df = cvar_mate.copy()
        temp_df["CVaR"] = (temp_df["CVaR"] - b) * (temp_df["p"] < 1)
        temp_df["b"] = b
        temp_df["type"] = "Thm. 3.3"
        c3_temp.append(temp_df)
    c3 = pd.concat(c3_temp, ignore_index=True).query("b > 0")
    c3["b"] = np.round(c3["b"], 3)
    df_bounded = pd.concat((c1, c2, c3))
    df_bounded["Type"] = df_bounded["type"]
    for i_group, (btype, group) in enumerate(df_bounded.groupby(["b", "type"])):
        group["CVaR"] = rearrange_cvar(group["CVaR"])
    return df_bounded


def cvar_bbounds_ate(
    data: pd.DataFrame,
    ps: np.array,
    rhos: np.array,
    totvar: float,
    tau_col="tau",
    sw_col="sw",
    var_col="varsum01",
    sd_col="sdprod01",
):
    sw = data[sw_col]
    results = []
    for p in ps:
        for rho in rhos:

            def objective_function(beta):
                return data.assign(
                    tmp=lambda x: (
                        beta
                        + np.mean(
                            x[sw_col]
                            * (
                                x[tau_col]
                                - beta
                                - np.sqrt(
                                    (x[tau_col] - beta) ** 2
                                    + x[var_col]
                                    - 2 * rho * x[sd_col]
                                )
                            )
                        )
                        / (2 * p)
                    )
                )["tmp"].mean()

            # Minimizar la función objetivo usando goldsectmax
            q = goldsectmax(
                objective_function,
                min(data[tau_col]) - 5 * totvar / max(p, 0.01),
                max(data[tau_col]) + 5 * totvar / max(1.0 - p, 0.01),
                tol=1e-4,
                m=1000,
            )
            IF = IF_cvar_bbouns_ate(data, p, q, rho)
            cvar = IF * sw

            # Agregar resultados a la lista
            results.append(
                {
                    "p": p,
                    "q": q,
                    "rho": rho,
                    "CVaR": np.nanmean(cvar),
                    "CVaR_se": np.nanstd(cvar) / np.sqrt(len(sw)),
                }
            )
    return pd.DataFrame(results)


def prep_bbounds_ate(
    df,
    sw_col="sw",
    y_col="Y",
    A_col="A",
    mu1_col="mu1",
    mu0_col="mu0",
    var0_col="var0",
    var1_col="var1",
):
    data = df.copy()
    data["condvar"] = (
        data[sw_col]
        * (
            data[y_col]
            - data[A_col] * data[mu1_col]
            - (1 - data[A_col]) * data[mu0_col]
        )
        ** 2
    )

    data["marvar"] = data[sw_col] * data[y_col]

    Rsquared = (
        data.groupby(A_col)
        .agg(condvar=("condvar", "mean"), marvar=("marvar", "mean"))
        .reset_index()
    )
    # print(Rsquared)
    totvar = Rsquared["condvar"].sum()

    correction2 = np.sum(np.sqrt(Rsquared["condvar"]))

    oi = data["sw"] * (np.sqrt(data[var0_col]) + np.sqrt(data[var1_col]))
    correction1 = np.mean(oi)

    data["sdprod01"] = data.apply(
        lambda row: np.sqrt(row[var0_col] * row[var1_col]), axis=1
    )
    data["varsum01"] = data[var0_col] + data[var1_col]

    return data, totvar, correction1, correction2


def job_condvar_gen(cvar_mate, sbound_mate, correction1, correction2):

    df1 = cvar_mate.assign(type="CATE-CVaR")
    df2 = cvar_mate.assign(
        type="Eq. (9) bound",
        CVaR=cvar_mate["CVaR"] - correction1 / (2 * cvar_mate["p"]),
    )
    df3 = cvar_mate.assign(
        type="Eq. (10) bound",
        CVaR=cvar_mate["CVaR"] - correction2 / (2 * cvar_mate["p"]),
    )
    df4 = sbound_mate.assign(type="Thm. 3.4 bound")

    job_condvar = pd.concat((df1, df2, df3, df4)).query("p > .7").fillna("NaN")
    job_condvar["Type"] = job_condvar["type"]
    return job_condvar
