from scipy.stats import beta
import scipy
import math
import numpy as np
from os import path as op
from collections import namedtuple
from matplotlib import pyplot as plt

Sample = namedtuple( "Sample" , [ "Participants" , "ReEngaged" ])
control = Sample( 12 , 7 )
experiment = Sample( 5 , 13 )

CUR_DIR = op.dirname(__file__)

def resample_compare(distributions , n_samples = 1000 ):
    assert all((isinstance(dist, scipy.stats._distn_infrastructure.rv_frozen)
                for dist in distributions))
    
    random_samples = np.zeros(( len(distributions), n_samples))
    for idx, dist in enumerate(distributions):
        random_samples[idx, :] = dist.rvs(n_samples)
    
    compared = np.subtract(random_samples[0, :], random_samples[1:] )
    
    return np.sort(compared.squeeze())

# Use uniform prior for both
dist_first = beta(control.Participants + 1 , control.ReEngaged + 1 )
dist_second = beta(experiment.Participants + 1 , experiment.ReEngaged + 1 )

x = np.linspace(0, 1, 100)

plt.rc("font", size=16)
fig, ax = plt.subplots(1, 1, figsize=(16, 9.6))

ax.plot(x, dist_first.pdf(x), label="Control group", color="b")
ax.plot(x, dist_second.pdf(x), color="r", label="Experiment group")

ax.plot((dist_first.ppf(0.025), dist_first.ppf(0.025)), (0.0, 4.0), color="b", linestyle="--", label="95% confidence interval")
ax.plot((dist_first.ppf(0.975), dist_first.ppf(0.975)), (0.0, 4.0), color="b", linestyle="--")

ax.plot((dist_second.ppf(0.025), dist_second.ppf(0.025)), (0.0, 4.0), color="r", linestyle="--", label="95% confidence interval")
ax.plot((dist_second.ppf(0.975), dist_second.ppf(0.975)), (0.0, 4.0), color="r", linestyle="--")

ax.set_title("Likelihood of re-engagement probability (Beta-distribution)")
ax.set_xlabel("Probability of re-engagement")
ax.set_ylabel("Probability")

ax.legend()

fig.savefig(op.join(CUR_DIR, "Re-engagement-betas.png"))
plt.close(fig=fig)

compared = resample_compare([dist_second, dist_first], n_samples=100_000)

fig, ax = plt.subplots(1, 1, figsize=(16, 9.6))

ax.set_title("Change in re-engagement probability, when switching from control to experiment.\nEstimated using resampling with 100,000 samples")

ax.set_xlim((-1, 1))
n, bins, patches = ax.hist(compared, 100, density=True, alpha=0.8)

max_y = np.max([p.get_height() for p in patches])

lower_idx = math.floor(len(compared) * 0.025)
upper_idx = math.ceil(len(compared) * 0.975)

ax.plot((compared[lower_idx], compared[lower_idx]), (0.0, max_y), color="r", linestyle="--", label="95% Confidence interval")
ax.plot((compared[upper_idx], compared[upper_idx]), (0.0, max_y), color="r", linestyle="--")
ax.plot((compared[int(len(compared)/2)], compared[int(len(compared)/2)]), (0.0, max_y), color="g", linestyle="--", label="Median change")

ax.text(compared[lower_idx] + 0.015, max_y - 0.25, "{:.2}".format(compared[lower_idx]), color="r")
ax.text(compared[upper_idx] + 0.015, max_y - 0.25, "{:.2}".format(compared[upper_idx]), color="r")
ax.text(compared[int(len(compared)/2)] + 0.015, 2.75, "{:.2}".format(compared[int(len(compared)/2)]), color="g")

ax.set_xlabel("Difference in re-engagement probability")
ax.set_ylabel("Approximate probability")

ax.legend()

fig.savefig(op.join(CUR_DIR, "Re-engage-Experiment-vs-Control.png"))