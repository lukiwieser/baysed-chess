from typing import TypedDict

from scipy.stats import binomtest

HypothesisTestResult = TypedDict('HypothesisTestResult', {"trials": int, "pvalue": float, "statistic": float})


def hypothesis_test(wins: int, draws: int, losses: int) -> HypothesisTestResult:
    """
    Hypothesis test using Binomial distributions.

    Null Hypothesis: Both engines have the same strength, aka they win on average half of the games.
    Alternative Hypothesis: Both engines have different strength.

    This is a Frequentist Approach.

    :returns: dict of trials, pvalue, test-statistic
    """

    # wins give 1 point, and draws give 1/2 points
    score = wins + draws // 2

    # number of games
    trials = wins + draws + losses

    # due to rounding down "score", if draws are odd, we have to reduce trials by one.
    if draws % 2 != 0:
        trials -= 1

    # we expect that if both engines have the same strength, that they "win" on 50% on average
    expected_success_rate = 0.5

    result = binomtest(score, trials, expected_success_rate, alternative='two-sided')

    return {
        "trials": trials,
        "pvalue": result.pvalue,
        "statistic": result.statistic
    }
