Please email richardmckenzie@protonmail.com if you have further questions.

Alternatively, this project may be handed to someone else if necessary, if they take over this then this should change

### Data extraction TL;DR:
If you want to reprod. the results, good luck, you will want the tests stored in /tests (although the graphs and random seeds are both stored in the h5 which is available on request)

If you want to do analysis on the data, the summaries will have everything. The _all column will generally be the entire range (and what you want) after the 1k burn-in, so it might be means of t=~~10000~~ 9000 or t=~~5000~~ 4000 depending on if you're looking at the _10000.pkl/csv or the _allk and _sync (both are 5000 simulated units).

### Summary information:
Each summary row contains a different test run, `c` is the coupling strength (a multiplier for coupled effects), `k` is the nearest neighbour coupling for the Watts-Strogatz graph during that run, `n` is the amount of nodes in the network, `p` is the probability for an edge to be rewired, `zeta` is the strength of the stochastic noise, `analytical_sigma_cont` is the analytically derived relative synchrony, `kuramoto_euler_sigma_squared_all` is the empircally-meaned relative synchrony for the kuramoto model, and `ou_euler_sigma_squared_all` is the empirically-meaned relative synchrony for the linear model, as stated in the above paragraph, the `_all` generally indicates a mean for about `t=4000` steps.


.pkl is designed to be opened with [numpy.load][https://numpy.org/doc/stable/reference/generated/numpy.load.html]
the actual data (available on request via email, 50 GB) is stored in .h5 is designed to be opened with the hdf5 python library [h5py][https://docs.h5py.org/en/stable/index.html] (although other hdf5 readers are *probabily* compatable).






### Synchronised Stability Results:
Results for experiments that were initialised in sync, aka stability results. (These are the strongest results to prove and probably the ones you want if you're doing an EDA)
Tests are in data/tests.zip/tests_synced 
Summaries are in gathered_data_sync.csv and gathered_data_sync.pkl

### Onset of Synchrony Results:
Results for experiments that were not initially in sync, or that measured if such systems would synchronise/the "onset" of synchrony.
tests are in the tests.zip archive and labelled tests_k4_10k/2, and tests_k6/k8/k10
Summaries are split between the gathered_data_onset_allk.csv/pkl and need to be merged with the gathered_data_10000.csv/pkl

### Width Estimation results:
Results for experiments that were not initially in sync, but also ran for 10,000 timeunits instead of the typical 5000 to determine if the runtime was correct.
Tests are in tests_k4_10k/2
Summaries are in gathered_data_10000.csv/gathered_data_10000.pkl
