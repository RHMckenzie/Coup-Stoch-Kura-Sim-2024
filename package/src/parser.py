import json
import networkx as nx
import numpy as np
import graphs as gg
import kuramoto
import linear
import sigma
import datetime
import os
import sys
import time
import traceback


##############################################################
#   Misc & Helper Functions:
#
#   Just a list of small Misc/Helper functions for this task   
#
##############################################################


def list_partial(func, args, kwargs):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = []
    return func(*args,**kwargs)



##############################################################
#   Parsing:
#   
#   List of processes
#   Each process is run and data output is stored in appropriate file
#   
#   Graph -> Store Graph -> (Process -> Store Process Data) -> Graphing
#
##############################################################

def dummy_parse(json_file):
    d = None
    with open(json_file) as j_data:
        d = json.load(j_data)
    return parse_graph(d["graph"])

def parse_loop(json_file, return_value = False):
    if return_value:
        out = []
    data = None
    with open(json_file) as j_data:
        data = json.load(j_data)
    if data is None:
        raise Exception("JSON Data not found!")
    data, settings = parse_settings(data, data.get("settings", None))
    batch_data = data.copy()
    batch_settings = settings.copy()
    run_times = settings.get("n_batch", 1)

    if settings["debug_prints"]:
        print("Running Simulation: %s" % json_file)
        time_graph = []
        time_graph.append(time.perf_counter())

    for i in range(run_times):
        if settings["debug_prints"]:
            print("Iteration: %d" % (i + 1))
        data, settings = modify_settings(batch_data, batch_settings)
        if settings["save_json"]:
            save_json(data, settings)
        graph = parse_graph(data.get("graph", None), settings = settings)
        if graph is None:
            raise Exception("Graph not found!")
        #Save graph here!
        save_graph(graph, settings = settings)
        p_list = data.get("processes", None)
        if p_list is None:
            raise Exception("No Processes!")
        
        # Run processes here!
        for p in p_list:
            if settings["debug_prints"]:
                process_start = time.perf_counter()
            results = parse_process(graph, p, settings)
            # save processes here
            save_process(results, p, settings)

            if settings["debug_prints"]:
                process_end = time.perf_counter()
                print(time_format("Process %s elapsed: {0}:{1:02}" % p["function"], process_end, process_start))
                
        
        if settings.get("seed", None) is not None:
            with open(settings["save_folder"] + '/' + "seed.dat", "w") as f:
                f.write(str(settings.get("seed")))
        if settings["debug_prints"]:
            time_graph.append(time.perf_counter())
            print("Data saved to: %s" % settings["save_folder"])
            print(time_format("Time elapsed for this run: {0}:{1:02}", time_graph[-1], time_graph[-2]))
        if return_value:
            out.append(settings["save_folder"])
    if settings["debug_prints"]:
        print(time_format("Time elapsed for this Simulation: {0}:{1:02}", time_graph[-1], time_graph[0]))
    if return_value:
        return out

def time_format(string, time1, time2):
    return string.format(
        int((time1 - time2) // 60),
        int((time1 - time2) % 60)
    )


##############################################################
#   Settings:
#   
#   Currently does little, can be expanded at a later date 
#                      (hopefully)...
#   
##############################################################

def parse_settings(data, settings):
    d = settings
    if d is None:
        d = []
    if d.get("save_folder", None) is None:
        d["save_folder"] = "unnamed_run"
    d["debug_prints"] = d.get("debug_prints", False)
    d["save_json"] = d.get("save_json", False)

    return data, d


def modify_settings(data, settings):
    settings = settings.copy()
    data = data.copy()

    if settings.get("force_seed", False):
        seed = int(np.random.randint(1e8))
        recc_search_replace(data, "seed", seed)
        settings["seed"] = seed

    if settings.get("time_stamp", True):
        rhs = settings["save_folder"].split('/')[-1]
        lhs = '/'.join(settings["save_folder"].split('/')[:-1])
        if len(lhs) > 1:
            lhs = lhs + '/'
        settings["save_folder"] = lhs + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S_%f_") + rhs
    
    #setup save_folder
    try:
        os.mkdir(settings["save_folder"])
    except FileExistsError:
        pass
    return data, settings



def recc_search_replace(a, val, new_val):
    if type(a) is dict:
        for k in a.keys():
            if type(a[k]) is dict or type(a[k]) is list:
                recc_search_replace(a[k], val, new_val)
                continue
            if k == val:
                a[k] = new_val
    elif type(a) is list:
        for l in a:
            if type(l) is dict or type(l) is list:
                recc_search_replace(l, val, new_val)
             
             


##############################################################
#   Graph Generation/Parsing:
#   
#   Graphs are generated and stored in adjacency matrix form as an np array
#   A networkX diagram can be generated at a later time, but experiments shouldn't generate these
#   
#   The graph name and argument list comes from the provided parsed json file 
#
##############################################################

GRAPH_FUNCTIONS = {

    "watts_strogatz_unconnected" : gg.watts_strogatz_directed,
    "weak_watts_strogatz" : gg.weak_connected_ws_directed,
    "strong_watts_strogatz" : gg.strong_connected_ws_directed,
    "watts_strogatz_undirected_unconnected" : nx.watts_strogatz_graph,
    "watts_strogatz_undirected" : nx.connected_watts_strogatz_graph,
    "random": nx.random_regular_graph,
    "barabas_albert" : nx.barabasi_albert_graph,
    "erdos_renyi" : nx.erdos_renyi_graph,
}


def generate_graph(graph_func, graph_args, graph_settings):
    graph = list_partial(graph_func, None, graph_args)
    adjacency_matrix = nx.to_numpy_array(graph)
    adjacency_matrix = np.matrix(adjacency_matrix).astype(np.float32)
    if graph_settings.get("normalise",True):
        adjacency_matrix = gg.in_degree_normalisation(adjacency_matrix)
    ccv = graph_settings.get("cross_couple_value", 1)
    adjacency_matrix = gg.cross_couple(adjacency_matrix, ccv)
    #print(adjacency_matrix) 
    return adjacency_matrix

def parse_graph(graph_object, settings):
    if graph_object is None:
        return None
    #parse graph from file
    if "file" in graph_object:
        #not implemented
        return None
    
    #Otherwise construct new graph
    func = GRAPH_FUNCTIONS[graph_object["function"]]
    args = graph_object["arguments"]
    graph_settings = graph_object.get("settings", dict())
    return generate_graph(func, args, graph_settings)

def graph_settings_apply():
    #TODO!
    pass


##############################################################
#   Graph Saving/Initial Plotting:
#   
#   
#
##############################################################
    

def save_graph(adjacency_matrix, settings):
    #Perhaps store this in an actual graph object?

    filename = settings["save_folder"] + '/' + "graph_matrix"
    np.save(filename, adjacency_matrix)
    #TODO Graph images!
    #Not yet implemented!
    pass


def save_json(data, settings):

    settings = settings.copy()
    settings["n_batch"] = 1
    settings["force_seed"] = False
    settings["time_stamp"] = False


    new_json = settings["save_folder"] + "/settings.json"
    data = data.copy()
    data["settings"] = settings
    with open(new_json, "w") as f:
        json.dump(data, f, indent=4)

##############################################################
#   Processes:
#   
#   Empirical and Analytical modelling processes for calculating parameters
#   Currently:
#       Kuramoto (Euler), stored in kuramoto.py
#       Ornstein-Uhlenbeck (Euler), Stored in linear.py
#       Lizier's Sigma^2 (Continuous), stored in sigma.py
#   To Add:
#       Kuramoto (Heun/Taylor)
#       O-U (Heun/Taylor)
#       time-lagged analyitcal sigma (not necessary)
#   Also to add:
#       O-U w/ Cholseky Decomoposed Noise around the Zero mode, see: linsync code and barnett/buckley paper about this thoughie
#
#   Additionally, all processes presume that the graph is the first function parameter for each of these process functions
#
##############################################################

#These each produce different results under the assumption that the first argument is the normalised coupling matrix
PROCESS_LIST = {
    "kuramoto_euler": kuramoto.kuramoto_euler,
    "kuramoto_old": kuramoto.kuramoto_old,
    "kuramoto_rk4": kuramoto.kuramoto_rk4,
    "ou_euler": linear.linear_runtime,
    "analytical_sigma_cont": sigma.calculate_analytical_variance_cont,
    "analytical_sigma_discrete": sigma.calculate_analytical_variance_disc,
    "analytical_sigma_discrete_approx": sigma.calculate_analytical_variance_disc_approx
}


def parse_process(graph, process_data, settings):

    # settings here:

    arguments = process_data.get("arguments", [])
    process = process_data.get("function", None)
    if process is None:
        raise Exception("Invalid process data in JSON")
    return run_process(process, graph, arguments) 

def run_process(process, graph, arguments):
    results = list_partial(PROCESS_LIST[process], [graph,], arguments)
    return results

def save_process(results, process_data, settings):
    filename = settings["save_folder"] + '/' + process_data["function"]
    #print(results)
    filter = process_data.get("settings",dict()).get("filter",list())
    if hasattr(results, '__len__') and len(results) > 1:
        #results is a tuple of matricies
        if type(results) is dict:
            for k in results:
                #filter here:
                if k in filter:
                    continue
                np.save(filename + "_" + k, results[k])
        else:
            for r_i in range(len(results)):
                m = np.matrix(results[r_i])
                np.save(filename + str(r_i), m)
        
    else:
        with open(filename + ".dat", "w") as f:
            f.write(str(results))




##############################################################
#   
#   Main loop
#
##############################################################


def main_loop(argv, return_value = False):
    names = []
    try:
        start = time.perf_counter()
        if len(sys.argv) < 2:
            print("Usage: python3 parser.py filename.json")
        print("Running for " + str(len(argv) - 1) +" Files")
        for i in range(1, len(argv)):
            print("Simulating: " + str(i))
            x = parse_loop(argv[i], return_value = return_value)
            if return_value:
                names = names + x
        end = time.perf_counter()
        n = len(range(1, len(argv)))
        print("SUCCESSFULLY COMPLETED ALL " + str(n) + " FILES IN " + time_format("{0}:{1:02}",end, start) + "!")
        if return_value:
            return names
    except Exception as e:
        print("WARNING! FAILED:")
        print(traceback.format_exc())
        if return_value:
            return names


if __name__ == "__main__":
    main_loop(sys.argv)