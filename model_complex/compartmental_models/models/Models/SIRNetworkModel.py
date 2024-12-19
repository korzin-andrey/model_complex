import numpy as np
import networkx as nx
import EoN
import random
from collections import defaultdict
from .ModelParams import ModelParams


def _simple_test_transmission_(u, v, p):
    r'''
    A simple test for whether u transmits to v assuming constant probability p

    From figure 6.8 of Kiss, Miller, & Simon.  Please cite the book if
    using this test_transmission function for basic_discrete_SIR.

    This handles the simple case where transmission occurs with
    probability p.

    :Arguments:

        u (node)
            the infected node
        v : node
            the susceptible node
        p : number between 0 and 1
            the transmission probability

    :Returns:



            True if u will infect v (given opportunity)
            False otherwise
    '''

    return random.random() < p


def discrete_SIR_immune_param(G, test_transmission=_simple_test_transmission_, args=(),
                              initial_infecteds=None, initial_recovereds=None, initial_susceptible=None,
                              rho=None, alpha=None, tmin=0, tmax=float('Inf'),
                              return_full_data=False, sim_kwargs=None):
    # tested in test_discrete_SIR
    r'''
    Simulates an SIR epidemic on G in discrete time, allowing user-specified transmission rules

    From figure 6.8 of Kiss, Miller, & Simon.  Please cite the book
    if using this algorithm.

    Return details of epidemic curve from a discrete time simulation.

    It assumes that individuals are infected for exactly one unit of
    time and then recover with immunity.

    This is defined to handle a user-defined function
    ``test_transmission(node1,node2,*args)``
    which determines whether transmission occurs.

    So elaborate rules can be created as desired by the user.

    By default it uses
    ``_simple_test_transmission_``
    in which case args should be entered as (p,)

    :Arguments:

    **G** NetworkX Graph (or some other structure which quacks like a
                           NetworkX Graph)
        The network on which the epidemic will be simulated.

    **test_transmission** function(u,v,*args)
        (see below for args definition)
        A function that determines whether u transmits to v.
        It returns True if transmission happens and False otherwise.
        The default will return True with probability p, where args=(p,)

        This function can be user-defined.
        It is called like:
        test_transmission(u,v,*args)
        Note that if args is not entered, then args=(), and this call is
        equivalent to
        test_transmission(u,v)

    **args** a list or tuple
        The arguments of test_transmission coming after the nodes.  If
        simply having transmission with probability p it should be
        entered as
        args=(p,)

        [note the comma is needed to tell Python that this is really a
        tuple]

    **initial_infecteds** node or iterable of nodes
        if a single node, then this node is initially infected

        if an iterable, then whole set is initially infected

        if None, then choose randomly based on rho.

        If rho is also None, a random single node is chosen.

        If both initial_infecteds and rho are assigned, then there
        is an error.

    **initial_recovereds** as for initial_infecteds, but initially
            recovered nodes.

    **rho** number  (default is None)
        initial fraction infected. initial number infected
        is int(round(G.order()*rho)).

        The default results in a single randomly chosen initial infection.

    **tmin** start time

    **tmax** stop time (default Infinity).

    **return_full_data** boolean (default False)
        Tells whether a Simulation_Investigation object should be returned.

    **sim_kwargs** keyword arguments
        Any keyword arguments to be sent to the Simulation_Investigation object
        Only relevant if ``return_full_data=True``


    :Returns:


    **t, S, I, R** numpy arrays

    Or ``if return_full_data is True`` returns

    **full_data**  Simulation_Investigation object
        from this we can extract the status history of all nodes
        We can also plot the network at given times
        and even create animations using class methods.

    :SAMPLE USE:

    ::

        import networkx as nx
        import EoN
        import matplotlib.pyplot as plt
        G = nx.fast_gnp_random_graph(1000,0.002)
        t, S, I, R = EoN.discrete_SIR(G, args = (0.6,),
                                            initial_infecteds=range(20))
        plt.plot(t,I)


    Because this sample uses the defaults, it is equivalent to a call to
    basic_discrete_SIR
    '''
    if rho is not None and initial_infecteds is not None:
        raise EoN.EoNError("cannot define both initial_infecteds and rho")

    if initial_infecteds is None:  # create initial infecteds list if not given
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(G.order()*rho))
        initial_infecteds = random.sample(list(G), initial_number)
    elif G.has_node(initial_infecteds):
        initial_infecteds = [initial_infecteds]

    if initial_susceptible is None:  # create initial susceptible list if not given
        if alpha is None:
            initial_number = 1
        else:
            filtered_nodes = [node for node in list(G.nodes)
                              if node not in initial_infecteds]
            initial_number = int(round(G.order()*alpha))
            # if initial_number >= len(filtered_nodes):
            #     initial_number = len(filtered_nodes) - 1
            assert initial_number < len(filtered_nodes)
        initial_susceptible = random.sample(filtered_nodes, initial_number)
    # else it is assumed to be a list of nodes.

    if return_full_data:
        node_history = defaultdict(lambda: ([tmin], ['S']))
        transmissions = []
        for node in initial_infecteds:
            node_history[node] = ([tmin], ['I'])
            transmissions.append((tmin-1, None, node))
        if initial_recovereds is not None:
            for node in initial_recovereds:
                node_history[node] = ([tmin], ['R'])

    N = G.order()
    t = [tmin]
    S = [len(initial_susceptible)]
    I = [len(initial_infecteds)]
    R = [0]

    susceptible = defaultdict(lambda: False)
    # above line is equivalent to u.susceptible=True for all nodes.

    # for u in initial_infecteds:
    #     susceptible[u] = False
    for u in initial_susceptible:
        susceptible[u] = True
    # if initial_recovereds is not None:
    #     for u in initial_recovereds:
    #         susceptible[u] = False

    infecteds = set(initial_infecteds)

    while t[-1] < tmax-1:
        new_infecteds = set()

        infector = {}  # used for returning full data.  a waste of time otherwise
        for u in infecteds:
            for v in G.neighbors(u):
                if susceptible[v] and test_transmission(u, v, *args):
                    new_infecteds.add(v)
                    susceptible[v] = False
                    infector[v] = [u]
                elif return_full_data and v in new_infecteds and test_transmission(u, v, *args):
                    # if ``v`` already infected on this round, consider if it is
                    # multiply infected this round.
                    infector[v].append(u)

        if return_full_data:
            for v in infector.keys():
                transmissions.append((t[-1], random.choice(infector[v]), v))
            next_time = t[-1]+1
            if next_time <= tmax:
                for u in infecteds:
                    node_history[u][0].append(next_time)
                    node_history[u][1].append('R')
                for v in new_infecteds:
                    node_history[v][0].append(next_time)
                    node_history[v][1].append('I')

        infecteds = new_infecteds

        R.append(R[-1]+I[-1])
        I.append(len(infecteds))
        S.append(S[-1]-I[-1])
        t.append(t[-1]+1)
    if not return_full_data:
        return np.array(t), np.array(S), np.array(I), \
            np.array(R)
    else:
        if sim_kwargs is None:
            sim_kwargs = {}
        return EoN.Simulation_Investigation(G, node_history, transmissions,
                                            possible_statuses=['S', 'I', 'R'],
                                            **sim_kwargs)

#############################################
##### ##### ALL ABOVE IS BULLSHIT ##### #####
##### #####   USE fast_SIR model  ##### #####
#############################################


def fast_SIR_immune(G, alpha, beta, initial_infecteds_number=None, initial_recovereds=None,
                    rho=None, tmin=0, tmax=float('Inf'), transmission_weight=None,
                    recovery_weight=None, return_full_data=False, sim_kwargs=None):
    gamma = 1
    nodes = list(G.nodes)
    assert (alpha > 0) and (alpha < 1), "Incorrect alpha value!"
    initial_infecteds = random.sample(
        nodes, min(initial_infecteds_number, len(nodes)))
    initial_immune_number = int(G.order()*(1-alpha))
    initial_recovereds = random.sample(
        list(set(nodes) - set(initial_infecteds)),
        min(initial_immune_number, len(nodes) - len(initial_infecteds)))
    return EoN.fast_SIR(G, tau=beta, gamma=gamma, initial_infecteds=initial_infecteds,
                        initial_recovereds=initial_recovereds, tmax=100)


class SIRNetworkModel():
    def __init__(self, population_size: int, m_vertices: int):
        """
        SIR network model with immune fraction added.
        :param: population_size: number of vertices in network
        :param m_vertices: number of vertices to link with new one according
        to preferential attachment (see A. L. Barabási and R. Albert “Emergence of
        scaling in random networks”, Science 286, pp 509-512, 1999.)
        """
        assert isinstance(
            population_size, int), "Population type should be int."
        assert population_size > 10**2, "Too small population size!"
        self.population_size = population_size
        self.m_vertices = m_vertices
        # TODO: decide which type of network to use
        self.G = nx.barabasi_albert_graph(population_size, m_vertices)
        self.alpha_dim = 1
        self.beta_dim = 1
        self.is_calibrated = False
        self.ready_for_ci = False
        self.best_calibration_params: ModelParams = None
        self.ci_params: list[ModelParams] = None

    def simulate(
        self,
        model_params: ModelParams,
        modeling_duration: int
    ):
        """
        Simulate disease propagation using SIR on network.

        :return:
        """
        time, susceptible, total_infected, recovered = \
            fast_SIR_immune(self.G, beta=model_params.beta[0],
                            initial_infecteds_number=model_params.initial_infectious[0],
                            alpha=model_params.alpha[0], tmax=modeling_duration)
        # TODO: check equation for calculating newly_infected from
        # total_infected and recovered
        newly_infected = [total_infected[0] if index == 0 else
                          total_infected[index] - (total_infected[index-1] -
                          abs(recovered[index] - recovered[index-1]))
                          for index in range(len(total_infected))]
        # assert len(newly_infected) == modeling_duration
        self.newly_infected = newly_infected

    def get_daily_newly_infected(self):
        return self.newly_infected

    def pad_array_to_multiple_of_seven(self, arr):
        '''
        Auxiliary function used for padding array of daily data by zeroes for converting
        to weekly data
        '''
        current_size = len(arr)
        new_size = (current_size + 6) // 7 * 7
        padding_needed = new_size - current_size
        padded_array = np.pad(arr, (0, padding_needed),
                              mode='constant', constant_values=0)
        return padded_array

    def get_weekly_newly_infected(self):
        daily_newly_infected_padded = self.pad_array_to_multiple_of_seven(
            self.newly_infected)
        return daily_newly_infected_padded.reshape(-1, 7).sum(axis=1)

    def set_best_params_after_calibration(self, best_params: ModelParams):
        self.best_calibration_params = best_params
        self.is_calibrated = True

    def set_ci_params(self, ci_params: ModelParams):
        self.ci_params = ci_params
        self.ready_for_ci = True

    def get_best_params(self) -> ModelParams:
        if self.is_calibrated:
            return self.best_calibration_params
        else:
            raise Exception('Model is not calibrated!')

    def get_ci_params(self) -> list[ModelParams]:
        if self.ready_for_ci:
            return self.ci_params
        else:
            raise Exception(
                'Model does not have set of parameters for CI construction!')
