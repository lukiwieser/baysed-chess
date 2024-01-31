import math
from functools import cache

import torch
import torch.distributions as dist
from torch import exp

total_count = 0
calculation_count = 0


def get_lookup_count():
    global total_count, calculation_count
    return total_count - calculation_count


@cache
def calc_cdf(alpha: float) -> tuple[float, float, float]:
    """
    Returns the calculated CDF and parameters f1,f2 from the input alpha
    """
    global calculation_count
    calculation_count += 1

    normal = dist.Normal(0, 1)
    cdf_alpha = normal.cdf(torch.tensor(alpha)).item()
    pdf_alpha = exp(normal.log_prob(torch.tensor(alpha))).item()
    f1 = alpha * cdf_alpha + pdf_alpha
    f2 = alpha ** 2 * cdf_alpha * (1 - cdf_alpha) + (
            1 - 2 * cdf_alpha) * alpha * pdf_alpha - pdf_alpha ** 2
    return cdf_alpha, f1, f2


def max_gaussian(mu1, sigma1, mu2, sigma2) -> tuple[float, float]:
    """
    Returns the combined max gaussian of two Gaussians represented by mu1, sigma1, mu2, simga2
    :param mu1: mu of the first Gaussian
    :param sigma1: sigma of the first Gaussian
    :param mu2: mu of the second Gaussian
    :param sigma2: sigma of the second Gaussian
    :return: mu and sigma maximized
    """
    global total_count
    total_count += 1

    # we assume independence of the two gaussians
    # print(mu1, sigma1, mu2, sigma2)
    # normal = dist.Normal(0, 1)
    sigma_m = math.sqrt(sigma1 ** 2 + sigma2 ** 2)

    # round to two significant digits to enable float lookup
    alpha = round((mu1 - mu2) / sigma_m, 2)

    cdf_alpha, f1_alpha, f2_alpha = calc_cdf(alpha)

    mu = mu2 + sigma_m * f1_alpha
    sigma = math.sqrt(sigma2 ** 2 + (sigma1 ** 2 - sigma2 ** 2) * cdf_alpha + sigma_m ** 2 * f2_alpha)
    # sigma = math.sqrt((mu1**2 + sigma1**2) * cdf_alpha + (mu2**2 + sigma2**2) * (1 - cdf_alpha) + (mu1 + mu2) * sigma_m * pdf_alpha - mu**2)

    return mu, sigma


def min_gaussian(mu1, sigma1, mu2, sigma2) -> tuple[float, float]:
    """
    Returns the combined min gaussian of two Gaussians represented by mu1, sigma1, mu2, simga2
    :param mu1: mu of the first Gaussian
    :param sigma1: sigma of the first Gaussian
    :param mu2: mu of the second Gaussian
    :param sigma2: sigma of the second Gaussian
    :return: mu and sigma minimized
    """
    try:
        normal = dist.Normal(0, 1)
        sigma_m = math.sqrt(sigma1 ** 2 + sigma2 ** 2)
        alpha = (mu1 - mu2) / sigma_m

        cdf_alpha = normal.cdf(torch.tensor(alpha)).item()
        pdf_alpha = exp(normal.log_prob(torch.tensor(alpha))).item()
        pdf_alpha_neg = exp(normal.log_prob(torch.tensor(-alpha))).item()

        mu = mu1 * (1 - cdf_alpha) + mu2 * cdf_alpha - pdf_alpha_neg * sigma_m
        sigma = math.sqrt((mu1 ** 2 + sigma1 ** 2) * (1 - cdf_alpha) + (mu2 ** 2 + sigma2 ** 2) * cdf_alpha - (
                    mu1 + mu2) * sigma_m * pdf_alpha - mu ** 2)
        return mu, sigma
    except ValueError:
        print(mu1, sigma1, mu2, sigma2)


def beta_mean(alpha, beta):
    return alpha / (alpha + beta)


def beta_std(alpha, beta):
    try:
        return math.sqrt((alpha * beta) / ((alpha * beta) ** 2 * (alpha + beta + 1)))
    except ZeroDivisionError:
        print(alpha, beta)


def gaussian_ucb1(mu, sigma, N) -> float:
    return mu + math.sqrt(2 * math.log(N) * sigma)
