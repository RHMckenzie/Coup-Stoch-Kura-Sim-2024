import math
import numpy as np
import tqdm


# Normalises X into a value between -Pi and Pi
def norm_circular(x):
    return ((x + np.pi) % (2 * np.pi)) - np.pi

#norm_circ_vec = np.vectorize(norm_circular)
norm_circ_vec = norm_circular

# Turns a value between -pi and pi into a point around the unit circle with its value as the argument:
def arg_convert(x):
    return complex(math.cos(x), math.sin(x))

def vec_arg_convert_np(x):
    return np.dstack((np.cos(x), np.sin(x)))[0]

# produces the "mean" of a set of phases, in that the different complex phases are meaned together and the result is the argument of that mean
# The tuple returned is a pair that contains the angle of this mean and the mean itself respectively.  
# This is effectively the same as taking the cos and sine means for all the phases 
# (which is how Pikovsky, Rosenblaum and Kurths [Cambridge textbook] does it)
def angular_mean_vec(x):
    x = vec_arg_convert_np(x)
    vec = np.mean(x, axis = 0)
    vec = norm_circular(vec)
    m = complex(vec[0], vec[1])
    return (np.angle(m), m)    

def angular_mean(x):
    x = np.array(list(map(arg_convert, map(norm_circular, x))))
    m = np.mean(x)
    return (np.angle(m), m)    


# Vector friendly of above function
def angular_mean_vec_old(x):
    _vec_norm_circular = np.vectorize(norm_circular)
    _vec_arg_convert = np.vectorize(arg_convert)
    x = _vec_arg_convert(_vec_norm_circular(x))
    m = np.mean(x)
    return (np.angle(m), m)    

# Based off of the cosine angular difference
# The angle between two vectors is theta where cos(theta) = A dot B / ||A|| * ||B||
# As the magnitude of the phases across the unit circle is equal to 1, then this is just A dot B where A is (cos(x),sin(x)) and B is similar
def angular_difference(x, y):
    #return math.acos(math.cos(x) * math.cos(y) + math.sin(x) * math.sin(y))
    val = np.cos(x) * np.cos(y) + np.sin(x) * np.sin(y)
    old_val = val.copy()
    val = np.clip(val, a_min = -1, a_max = 1)
    if (old_val != val).any():
        obl = old_val != val
        print("WARNING! ERROR! A errornous correction was made, turning:")
        print(old_val[obl])
        print("Into:")
        print(val[obl])
    val = np.arccos(val)
    return val


 


#Performs a single discrete instance of kuraomoto model

# K is the coupling matrix
# phi is the vector of phases of each oscillator
# o is the vector of natural frequencies for each oscillator
# dt is the time differential of the update.
# noise is the variance of the perbetuation
def single_kuramoto_old(K, phi, dt, o, noise, rng = None):
    phi_updated = phi.copy()
    for i in range(len(phi)):
        # get sine offsets
        sine = np.array(list(map(lambda x: math.sin(x - phi[i]), phi)))
        # Extract inbound column on coupling matrix
        k = np.take(K, i, axis = 1)[0]
        # construct update term
        dx = np.mean(sine @ k.T) + o[i]
        # Construct Noise term 
        if rng is None:
            noise_term = (noise * np.random.normal())
        else:
            noise_term = noise * rng.normal()
        phi_updated[i] += (dx * dt) + (noise_term * math.sqrt(dt)) # an issue with this is that larger time values may be sampled incorrectly
        phi_updated[i] = norm_circular(phi_updated[i])
    return phi_updated


def single_kuramoto_old_vectorised(K, phi, dt, o, noise, rng = None, mean = False):
    phi_updated = phi.copy()
    N = phi.shape[0]
    sine_mat = np.stack([phi - np.take(phi,i) for i in range(N)], axis=1).reshape((N, N))
    #prefilter non-existant values before performing costly operation (sine)
    sine_mat = np.where(K != 0, sine_mat, 0)

    #get sine values of sparse K matrix
    sine_func = np.vectorize(math.sin)
    sine_mat = sine_func(sine_mat)
    #multiply by coupling
    sine_vec = np.multiply(sine_mat, K)
    
    #Arenas says no mean for node degree!!! sigma_ij = K/k_i, section 3.1.2, EQ 11, Arenas 2008, Syncrhonisation in Complex Networks
    if mean:
        #take fast mean
        mean_vec = np.ones(N) * 1/N #Check if this should be matrix degree instead, or even included at all????
        dx_vec = mean_vec @ sine_vec
    else:
        #Take sum
        sum_vec = np.ones(N)
        dx_vec = sum_vec @ sine_vec

    
    if rng is None:
        noise_term = (noise * np.random.normal(size = N))
    else:
        noise_term = noise * rng.normal(size = N)

    phi_updated = phi_updated + (dx_vec * dt) + (noise_term * math.sqrt(dt))
    phi_updated = norm_circ_vec(phi_updated)
    phi_updated = np.asarray(phi_updated).reshape(-1)
    return phi_updated


def single_kuramoto_old_modern(K, phi, dt, o, noise, rng = None, mean = False):
    phi_updated = phi.copy()
    N = phi.shape[0]
    sine_mat = phi[:, np.newaxis] - phi[np.newaxis, :]
    #prefilter non-existant values before performing costly operation (sine)
    sine_mat = np.where(K != 0, sine_mat, 0)

    #get sine values of sparse K matrix
    sine_mat = np.sin(sine_mat)
    #multiply by coupling
    sine_vec = np.multiply(sine_mat, K)
    
    #Arenas says no mean for node degree!!! sigma_ij = K/k_i, section 3.1.2, EQ 11, Arenas 2008, Syncrhonisation in Complex Networks
       #Take sum
    sum_vec = np.ones(N)
    dx_vec = sum_vec @ sine_vec

    
    if rng is None:
        noise_term = (noise * np.random.normal(size = N))
    else:
        noise_term = noise * rng.normal(size = N)

    phi_updated = phi_updated + (dx_vec * dt) + (noise_term * math.sqrt(dt))
    phi_updated = norm_circ_vec(phi_updated)
    phi_updated = np.asarray(phi_updated).reshape(-1)
    return phi_updated


def kuramoto_derivative(phi, K, o, debug_value = None):
    N = len(phi)
    if debug_value is not None:
        print("phi %s:" % debug_value, np.round(phi,4))
        print("phi_shape %s" % debug_value, phi.shape)
    # Create a matrix of phase differences
    phi_diff = phi[:, np.newaxis] - phi[np.newaxis, :]
    if debug_value is not None:
        print("phi_diff prefilter %s:" % debug_value, np.round(phi_diff,4))
    # We don't care about non-coupled phase values
    phi_diff = np.where(K != 0, phi_diff, 0)
    if debug_value is not None:
        print("phi_diff %s:" % debug_value, np.round(phi_diff,4))    
    sine_mat = np.sin(phi_diff)
    sine_vec = np.multiply(sine_mat, K)
    if debug_value is not None:
        print("coupled_sin %s:" % debug_value, np.round(sine_vec,4))
    #sum for node degree section 3.1.2, EQ 11, Arenas 2008, Syncrhonisation in Complex Networks
    sum_sin = np.sum(sine_vec, axis=0)
    if debug_value is not None:
        print("sum_sin %s:" % debug_value, np.round(sum_sin,4))
    dphi = o + sum_sin
    return np.asarray(dphi).reshape(-1)



def single_kuramoto_rk1(K, phi, dt, o, noise, rng = None, mean = False, debug = False):
    N = phi.shape[0]
    #couple with derivative    
    dx_vec = kuramoto_derivative(phi, K, o)
    
    if rng is None:
        noise_term = (noise * np.random.normal(size = N))
    else:
        noise_term = noise * rng.normal(size = N)

    phi_updated = phi \
        + (dx_vec * dt) \
        + (noise_term * math.sqrt(dt))
    phi_updated = norm_circ_vec(phi_updated)
    phi_updated = np.asarray(phi_updated).reshape(-1)
    return phi_updated

def single_kuramoto_rk4(K, phi, dt, o, noise, rng = None, mean = False, debug = False):
    if debug:
        debug_values = ("k1", "k2", "k3", "k4")
    else:
        debug_values = (None,) * 4
    N = phi.shape[0]
    #couple with derivative    
    k1 = kuramoto_derivative(phi, K, o, debug_value = debug_values[0])
    k2 = kuramoto_derivative(norm_circ_vec(phi + 0.5 * dt * k1), K, o, debug_value = debug_values[1])
    k3 = kuramoto_derivative(norm_circ_vec(phi + 0.5 * dt * k2), K, o, debug_value = debug_values[2])
    k4 = kuramoto_derivative(norm_circ_vec(phi + dt * k3), K, o, debug_value = debug_values[3])

    
    if rng is None:
        noise_term = (noise * np.random.normal(size = N))
    else:
        noise_term = noise * rng.normal(size = N)

    phi_updated = phi \
        + ((dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)) \
        + (noise_term * math.sqrt(dt))
    phi_updated = norm_circ_vec(phi_updated)
    phi_updated = np.asarray(phi_updated).reshape(-1)
    return phi_updated



SIM_METHODS = {
    "rk1": single_kuramoto_rk1,
    "rk4": single_kuramoto_rk4,
    "old": single_kuramoto_old_modern
}


# Runs t iterations of the Kuramoto model
# Comments pending
def kuramoto_runtime(K, t, zeta, dt = 0.1, seed = None, prog_bar = False, sim_method = "old", synchronised_start = False):
    difference_func = angular_difference
    N = K.shape[0]
    rng = np.random.default_rng(seed = seed)
    if synchronised_start:
        starting_state = np.ones(N) * ((rng.random() * 2 * np.pi) - np.pi)
    else:
        starting_state = np.array((rng.random(size = N) * (2 * np.pi)) - np.pi)
    
    state_list = [starting_state]
    sigma_squared = []
    order_parameters = []

    # A simple progress bar as part of TQDM
    iter = range(math.floor(t * 1/dt))
    if prog_bar:
        iter = tqdm.tqdm(iter)
    prev_state = state_list[0]
    single_kuramoto = SIM_METHODS[sim_method]
    for i in iter:
        new_state = single_kuramoto(K, prev_state, dt, np.zeros(N), zeta, rng = rng)

        if (i % math.floor(1/dt) == 0):
            state_list.append(new_state)
            mean_angle, mean_vector = angular_mean_vec(new_state)
            current_sigma_squared = np.sum((difference_func(new_state, mean_angle) ** 2) / N)
            sigma_squared.append(current_sigma_squared)
            order_parameter_strength = math.sqrt(np.real(mean_vector) ** 2 + np.imag(mean_vector) ** 2)
            order_parameters.append(order_parameter_strength)
        prev_state = new_state
    return {
        "all_states": state_list, 
        "initial_state": state_list[0], 
        "order_parameters": order_parameters, 
        "sigma_squared": sigma_squared,
        "final_state": state_list[-1]
            } 

def kuramoto_euler(*args, **kwargs):
    if "sim_method" in kwargs:
        del kwargs["sim_method"]
    kwargs["sim_method"] = "rk1"
    return kuramoto_runtime(*args, **kwargs)

def kuramoto_rk4(*args, **kwargs):
    if "sim_method" in kwargs:
        del kwargs["sim_method"]
    kwargs["sim_method"] = "rk4"
    return kuramoto_runtime(*args, **kwargs)


def kuramoto_old(*args, **kwargs):
    if "sim_method" in kwargs:
        del kwargs["sim_method"]
    kwargs["sim_method"] = "old"
    return kuramoto_runtime(*args, **kwargs)

#def linear_runtime():
