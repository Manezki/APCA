from scipy.stats import beta
import scipy
import numpy as np
from collections import namedtuple
from matplotlib import pyplot as plt

Sample = namedtuple( "Sample" , [ "Participants" , "ReEngaged" ])
control = Sample( 12 , 7 )
experiment = Sample( 5 , 13 )


def resample_compare(distributions , n_samples = 1000 ):
    assert all((isinstance(dist, scipy.stats._distn_infrastructure.rv_frozen)
                for dist in distributions))
    
    random_samples = np.zeros(( len(distributions), n_samples))
    for idx, dist in enumerate(distributions):
        random_samples[idx, :] = dist.rvs(n_samples)
    
    compared = np.subtract(random_samples[0, :], random_samples[1:] )
    
    return np.sort(compared)

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

ax.set_title("Re-engagement ratios (Beta-distribution)")
ax.set_xlabel("Re-engagement ratio")
ax.set_ylabel("Pdf")

ax.legend()

fig.savefig("Re-engagement-beta.png")

compared = resample_compare([dist_first, dist_second])
#print(compared)