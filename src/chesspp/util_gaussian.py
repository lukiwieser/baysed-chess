import math

import torch
import torch.distributions as dist
from torch import exp

F1: dict[float, float] = {}
F2: dict[float, float] = {}
CDF: dict[float, float] = {}
lookup_count = 0


def max_gaussian_numeric(mu1, sigma1, mu2, sigma2) -> (float, float):
    pass


def max_gaussian(mu1, sigma1, mu2, sigma2) -> (float, float):
    global lookup_count
    global F1
    global F2
    global CDF

    """
    Returns the combined max gaussian of two Gaussians represented by mu1, sigma1, mu2, simga2
    :param mu1: mu of the first Gaussian
    :param sigma1: sigma of the first Gaussian
    :param mu2: mu of the second Gaussian
    :param sigma2: sigma of the second Gaussian
    """
    # we assume independence of the two gaussians
    try:
        #print(mu1, sigma1, mu2, sigma2)
        normal = dist.Normal(0, 1)
        sigma_m = math.sqrt(sigma1 ** 2 + sigma2 ** 2)
        alpha = (mu1 - mu2) / sigma_m

        if alpha in CDF:
            cdf_alpha = CDF[alpha]
            lookup_count += 1
        else:
            cdf_alpha = normal.cdf(torch.tensor(alpha)).item()
            CDF[alpha] = cdf_alpha

        pdf_alpha = exp(normal.log_prob(torch.tensor(alpha))).item()

        if alpha in F1:
            f1_alpha = F1[alpha]
            lookup_count += 1
        else:
            f1_alpha = alpha * cdf_alpha + pdf_alpha
            F1[alpha] = f1_alpha

        if alpha in F2:
            f2_alpha = F2[alpha]
            lookup_count += 1
        else:
            f2_alpha = alpha ** 2 * cdf_alpha * (1 - cdf_alpha) + (
                        1 - 2 * cdf_alpha) * alpha * pdf_alpha - pdf_alpha ** 2
            F2[alpha] = f2_alpha

        mu = mu2 + sigma_m * f1_alpha
        #sigma_old = sigma2 ** 2 + (sigma1 ** 2 - sigma2 ** 2) * cdf_alpha + sigma_m ** 2 * f2_alpha
        sigma = math.sqrt((mu1**2 + sigma1**2) * cdf_alpha + (mu2**2 + sigma2**2) * (1 - cdf_alpha) + (mu1 + mu2) * sigma_m * pdf_alpha - mu**2)

        return mu, sigma
    except ValueError:
        print(mu1, sigma1, mu2, sigma2)
        exit(1)


def beta_mean(alpha, beta):
    return alpha / (alpha + beta)


def beta_std(alpha, beta):
    try:
        return math.sqrt((alpha * beta) / ((alpha * beta)**2 * (alpha + beta + 1)))
    except ZeroDivisionError:
        print(alpha, beta)


def gaussian_ucb1(mu, sigma, N) -> float:
    return mu + math.sqrt(2 * math.log(N) * sigma)
