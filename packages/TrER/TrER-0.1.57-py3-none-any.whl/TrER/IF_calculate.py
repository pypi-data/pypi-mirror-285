import numpy as np


class IF:
    def __init__(
        self,
        tau: np.array,
        mu1: np.array,
        mu0: np.array,
        A: np.array,
        ipw: np.array,
        Y: np.array,
    ) -> None:
        self.tau = tau
        self.mu1 = mu1
        self.mu0 = mu0
        self.A = A
        self.ipw = ipw
        self.Y = Y

        self.mu = mu1 - mu0
        # weidhted_difference
        self.wD = (2 * A - 1) * ipw * (Y - A * mu1 - (1 - A) * mu0)

    def base(self, p, q) -> np.array:

        condition = self.tau <= q
        mu = self.mu
        wD = self.wD

        cvar_base = q + (mu + wD - q) * condition / p

        return cvar_base

    def plugin(self, p, q) -> np.array:

        condition = self.tau <= q
        cvar_plugin = q + (self.tau - q) * (condition) / p
        return cvar_plugin

    def bad(self, p, q) -> np.array:
        condition = self.tau <= q
        wD, mu = self.wD, self.mu
        cvar_bad = q + (mu + wD - q) * condition / p
        return cvar_bad

    def tau_ate(self, p, q) -> np.array:
        tau = self.tau

        condition = tau <= q
        q_cnd_p = condition / p - 1
        q_condition_p = q * condition / p

        cvar_tau_ate = q + (self.mu + self.wD) * (q_cnd_p) - q_condition_p
        return cvar_tau_ate

    def bboond_ate(
        self, p, q, varsum01: np.array, rho: np.array, sdprod01: np.array
    ) -> np.array:
        wD = self.mu

        tau = self.tau
        tau_q = tau - q

        tau_q2 = tau_q**2 + varsum01 - 2 * rho * sdprod01
        sqrt_term = sqrt_term(tau_q2)

        mu1 = -wD
        tau_sqrt = (tau - q - sqrt_term) / (2 * p)
        tau_mu = (1 - tau_q / sqrt_term) * wD / (2 * p)

        cvar_bbound = mu1 + q + tau_sqrt + tau_mu
        return cvar_bbound

    def bbound_mate(self, p, q, b) -> np.array:
        condition = self.tau - b <= q

        mu, wD = self.mu, self.wD

        mu_wd = mu + wD

        cvar_bbound_mate = (
            -mu_wd
            + q
            + (mu_wd - q - b) * condition / (2 * p)
            + (mu_wd - q + b) * condition / (2 * p)
        )
        return cvar_bbound_mate
