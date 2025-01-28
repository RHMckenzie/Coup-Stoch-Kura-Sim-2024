# Linear OU process simulator, should be fairly straightforward
# Most of work done in linear_runtime and single_linear_vec

import numpy as np
import math
import tqdm

#produces matrix K for linear matrices:

# see errata for eq. (55) from arenas et. al 2008, sync in complex networks
# Can also use laplacian, but will not be equivalent.
# Also existant in eq. [14] of Supplementary material in Lizier et. al.

#K = -(I - C), presuming uniform coupling that sums to 1
#aka Graph laplacian
def linear_coupling_matrix(X):
    #presume X is already pre-unweighted
    N = X.shape[0]
    row_sum_X = np.array(np.round(X.T @ np.ones(N), 5))
    # Forms identity usually*, otherwise puts the column sum in a diagonal matrix
    X_diag = np.diag(row_sum_X[0])
    return -(X_diag - X)


#Performs a single discrete instance of linearised O-U model

# K is the coupling matrix
# phi is the vector of phases of each oscillator
# o is the vector of natural frequencies for each oscillator
# dt is the time differential of the update.
# noise is the variance of the perbetuation
def single_linear_vec(K, phi, dt, o, noise, rng = None):
    N = len(phi)
    phi_updated = phi.copy()
    # Extract inbound column on coupling matrix
    dx_mat = phi @ K
    dx_mat = np.asarray(dx_mat).reshape(-1)
    # Construct Noise term 
    if rng is None:
        noise_term = (noise * np.random.normal(size = N))
    else:
        noise_term = noise * rng.normal(size = N)

    phi_updated += (dx_mat * dt) + (noise_term * math.sqrt(dt))
    return phi_updated

def single_linear_old(K, phi, dt, o, noise, rng = None):
    N = len(phi)
    phi_updated = phi.copy()
    for i in range(N):
        # Extract inbound column on coupling matrix
        k_i = np.take(K, i, axis=1)[0]
        # construct update term
        dx = phi @ k_i.T
        # Construct Noise term 
        if rng is None:
            noise_term = (noise * np.random.normal())
        else:
            noise_term = noise * rng.normal()
        phi_updated[i] += (dt * dx) + (noise_term * math.sqrt(dt))
    return phi_updated



# Runs t iterations of the Linear model
# Comments pending
def linear_runtime(C, t, zeta, dt = 1, seed = None, prog_bar = False, vectorised = False, synchronised_start = False):
    #K = -(I - C)
    K = linear_coupling_matrix(C)
    N = K.shape[0]
    rng = np.random.default_rng(seed = seed)
    if synchronised_start:
        starting_state = np.ones(N) * ((rng.random() * 2 * np.pi) - np.pi)
    else:
        starting_state = np.array((rng.random(size = N) * (2 * np.pi)) - np.pi)
    state_list = [starting_state]
    sigma_squared = []

    # A simple progress bar as part of TQDM
    iter = range(math.floor(t * 1/dt))
    if prog_bar:
        iter = tqdm(iter)
    #C = normalise_graph_linear(K, dt)
    prev_state = state_list[0]
    for i in iter:

        linear_func = single_linear_old
        if vectorised:
            linear_func = single_linear_vec

        new_state = linear_func(K, prev_state, dt, np.zeros((N)), zeta, rng = rng)
        mean = np.mean(new_state)
        # Only record statistics when descretised time is non-fractional
        if (i % math.floor(1 / dt) == 0):
            # Calculate Sigma Squared
            current_sigma_squared = ((np.sum((new_state - mean) ** 2)) / N)
            state_list.append(new_state)
            sigma_squared.append(current_sigma_squared)
        prev_state = new_state - mean
    return {
        "all_states": state_list, 
        "initial_state": state_list[0], 
        "sigma_squared": sigma_squared,
        "final_state": state_list[-1]
            } 
