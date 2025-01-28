import numpy as np
# U^T covariance matrix U
EPSILON = 1.19e-07

def centering_matrix(C):
    return np.eye(C.shape[0]) - (np.ones(C.shape) * 1/(C.shape[0]))


# Eq 49/50, PNAS appendix
def calculate_covariance_matrix(C, err = EPSILON * 1e4, max_iter = 10000):
    U = centering_matrix(C)
    diff = U * 0.5
    projected_covariance = U * 0.5
    i = 0
    while np.any(abs(diff) >= err) and i < max_iter:
        diff = ((U @ C.T @ diff) + (diff @ C @ U)) / 2
        projected_covariance += diff
        i += 1
    if i == max_iter or np.any(projected_covariance == np.nan) or np.any(projected_covariance == np.inf):
        pass
        #print("Convergence failure!")
    return projected_covariance

#variance * trace of covariance * 1/N

def calculate_analytical_variance_cont(C, zeta, err = EPSILON * 1e4, max_iter = 10000):
    N = C.shape[0]
    m = calculate_covariance_matrix(C, err = err, max_iter = max_iter)
    return (zeta ** 2) * np.trace(m) * 1/N


#EQ 64, PNAS appendix


def calculate_covariance_matrix_discrete(C, err = EPSILON * 1e4, max_iter = 10000):
    U = centering_matrix(C)
    projected_covariance = U
    left_term = (C @ U).T
    right_term = (C @ U)
    diff = left_term @ U @ right_term
    i = 0
    while np.any(abs(diff - projected_covariance) >= err) and i < max_iter:
        projected_covariance += diff
        diff = (left_term @ diff @ right_term) 
        i += 1
    if i == max_iter or np.any(projected_covariance == np.nan) or np.any(projected_covariance == np.inf):
        pass
        #print("Convergence failure!")
    return projected_covariance



def calculate_analytical_variance_disc(C, zeta, err = EPSILON * 1e4, max_iter = 10000):
    N = C.shape[0]
    m = calculate_covariance_matrix_discrete(C, err = err, max_iter = max_iter)
    return (zeta ** 2) * np.trace(m) * 1/N



#modified descritisation that approximates the continuous
#EQ 64, PNAS appendix


def calculate_analytical_variance_disc_approx(C, zeta, dt=0.1, err = EPSILON * 1e4, max_iter = 10000, include_dt_final = True):
    N = C.shape[0]
    C_mod = np.eye(N) - (dt * (np.eye(N) - C))
    m = calculate_covariance_matrix_discrete(C_mod, err = err, max_iter = max_iter)
    if include_dt_final:
        zeta *= np.sqrt(dt)
    return (zeta ** 2) * np.trace(m) * 1/N
