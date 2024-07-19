import math
import networkx as nx
import numpy as np
from itertools import combinations, chain

from typing import Callable 

from tqdm import tqdm
import logging


class MyersonCalculator():
    r"""Calculates the exact Myerson values. 
        For a game described by a coalition function :math:`v` the Myerson values
        attribute the individual players contribution to the payoff of the game. For
        a complete graph (every node connected to every other node) the Myerson
        value is equal to the Shapley value (:math:`S`: coalition of players,
        :math:`N`: grand coalition of all players):

        .. math::

            \text{Sh}_i\,({v}) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|! \: (|N| - |S| - 1)!}{|N|!}\big( {v}\,(S \cup \{i\}) - {v}\,(S) \big)

        Else, the additional gain players can obthain through coalition is
        restricted only to players which are connected by edges in the graph. 

    Args:
        graph (nx.classes.graph.Graph): The coalition structure of the game.
        coalition_function (Callable): The coalition for which to calculate
            the payoff of the game. Expects a coalition (tuple of node
            indices) and a graph which contains additional information on
            the players to decide on the payoff. 

        disable_tqdm (bool, optional): Disables progress bar. Defaults to
            True.
    """

    def __init__(self,
                 graph: nx.classes.graph.Graph,
                 coalition_function: Callable,
                 disable_tqdm: bool=True) -> None:
        """Instantiate the class.
        """

        self.disable_tqdm = disable_tqdm
        self.log = logging.getLogger("MyersonCalculator")
        self.nx_graph = graph
        self.grand_coalition = list(graph.nodes()) # alias: set of players / set of nodes / F
        self.coalition_function = coalition_function

    def calculate_coalitions(self, grand_coalition: list) -> list:
        r"""Calculate all possible coalitions for a set of players / all nodes in
        a graph.

        Args:
            grand_coalition (list): Set of players / grand coalition / atoms in
                graph as a list of tupels.

        Returns:
            list: All :math:`2^N` coalitions.
        """
        self.log.info(f"Calculating number of coalitions.")
        coalitions = [combinations(grand_coalition, len(grand_coalition)-x) for x in \
                      tqdm(range(len(grand_coalition)), desc="Calculate coalitions", disable=self.disable_tqdm)]
        coalitions = list(chain.from_iterable(coalitions)) # chaining removes empty set
        coalitions.append(())
        self.log.info(f"Number of coalitions: {len(coalitions)}")
        return coalitions

    def calculate_graph_restricted_coalitions(self, coalitions: list, 
                                  nx_graph: nx.classes.graph.Graph) -> tuple[set, dict]:
        """Calculate the graph restricted coalitions for each coalition. The 
        graph restricted coalitions are tuples of nodes which are connected.

        Args:
            coalitions (list): All coalitions.
            nx_graph (nx.classes.graph.Graph): NetworkX Graph for which to
            calculate the Myerson values.

        Returns:
            tuple[set, dict]: Set of all possible graph restricted coalitions as
                a tuple of nodes, dictionary mapping each coalition to its
                graph restricted coalitions.
        """
        self.log.info(f"Calculating number of graph restricted coalitions.")
        graph_restricted_coalitions = [self.restrict(coalition, nx_graph) \
                                       for coalition in tqdm(coalitions,
                                           desc="Calculate graph restricted coalitions",
                                           disable=self.disable_tqdm)]
        coalitions_to_graph_restricted_coalitions = dict(zip(coalitions, graph_restricted_coalitions))
        graph_restricted_coalitions = list(chain.from_iterable(graph_restricted_coalitions))
        self.log.info(f"Removing dublicates from {len(graph_restricted_coalitions)} graph restricted coalitions.")
        graph_restricted_coalitions = set(x for x in tqdm(graph_restricted_coalitions, desc="Remove duplicates", disable=self.disable_tqdm))
        self.log.info(f"Number of graph restricted coalitions: {len(graph_restricted_coalitions)}")
        return graph_restricted_coalitions, coalitions_to_graph_restricted_coalitions

    def calculate_worth_of_single_graph_restricted_coalition(self,
        graph_restricted_coalition: tuple,
        nx_graph: nx.classes.graph.Graph) -> float:
        """Calculate the worth of a graph restricted coalition, i. e. a single
        connected component.

        Args:
            graph_restricted_coalition (tuple): Graph restricted coalition as
                node indices.
            nx_graph (nx.classes.graph.Graph): Additional information for the
                coalition function, i.e. the entire graph with node parameters. 
                The result of the coalition function should depend only on the
                coalition, however the node parameters might contain necessary 
                information.

        Returns:
            float: Worth, the output of the coalition function for the connected
            subgraph. 
        """
        return self.coalition_function(graph_restricted_coalition, nx_graph)

    def calculate_worth_of_graph_restricted_coalitions(self,
        graph_restricted_coalitions: set) -> dict:
        """Calculate the worth of every graph restricted coalition and map it to
        its worth. 

        Args:
            graph_restricted_coalitions (set): Set of connected components as
                tuples of node indices.

        Returns:
            dict: Dictionary mapping each connected component to its worth.
        """
        self.log.info(f"Calculating worth of graph restricted coalitions.")
        graph_restricted_coalitions_to_worth = {}
        for coalition in tqdm(graph_restricted_coalitions,
                              desc="Calculating worth of graph restricted coalitions",
                              disable=self.disable_tqdm):
            worth = self.calculate_worth_of_single_graph_restricted_coalition(coalition,
                                                                              self.nx_graph)
            graph_restricted_coalitions_to_worth.update({coalition: worth})
        return graph_restricted_coalitions_to_worth

    def map_coalition_to_worth(self, coalitions: list[tuple], 
                       coalitions_to_graph_restricted_coalitions: dict,
                       graph_restricted_coalitions_to_worth: dict) -> dict:
        """Map every coalition to its worth.

        Args:
            coalitions (list): List of all coalitions (2^{num_nodes}). 
            coalitions_to_graph_restricted_coalitions (dict): Dictionary mapping
                the coalitions to the corresponding graph restricted coalitions.
            graph_restricted_coalitions_to_worth (dict): Dictionary mapping the 
                graph restricted coalitions to their worth.

        Returns:
            dict: Dictionary mapping each coalition to its worth.
        """
        self.log.info(f"Mapping coalitions to worth.")
        coalition_to_worth = {}
        for coalition in tqdm(coalitions, desc="Mapping coalitions to worth", disable=self.disable_tqdm):
            worth = 0.
            for graph_restricted_coalition in coalitions_to_graph_restricted_coalitions[coalition]:
                worth += graph_restricted_coalitions_to_worth[graph_restricted_coalition]
            coalition_to_worth.update({coalition: worth})
        return coalition_to_worth

    def calculate_worth_of_grand_coalition(self, nx_graph: nx.classes.graph.Graph) -> float:
        """Calculate payoff of the game, i.e. the payoff of all players / the
        grand coalition.

        Args:
            coalition_function (Callable): The coalition function associating a
                coalition with a payoff.
            nx_graph (nx.classes.graph.Graph): Coalition structure of the game
                as a graph.

        Returns:
            float: Payoff of the game / worth of grand coalition.
        """
        restricted_grand_coalition = self.restrict(self.grand_coalition, nx_graph)
        worth = sum([self.calculate_worth_of_single_graph_restricted_coalition(S, nx_graph) \
                     for S in restricted_grand_coalition])
        return worth 

    def restrict(self, coalition: tuple, nx_graph: nx.classes.graph.Graph) -> list[tuple]:
        """Restricts a graph through a (sub)set of nodes / players. Generate a
        list of graph restricted coalitions, i. e. a list of node indices of
        connected nodes in the subgraph.

        Args:
            coalition (tuple): Nodes that remain in the graph.
            nx_graph (nx.classes.graph.Graph): Graph from which to generate
                subgraphs.

        Returns:
            list[tuple]: Graph restricted coalitions as tuples of node indices.
        """
        remove_nodes = set(nx_graph.nodes)-set(coalition)
        if remove_nodes == set(nx_graph.nodes):
            return [()] # empty_graph 
        else:
            G_reduced = nx_graph.copy()
            G_reduced.remove_nodes_from(remove_nodes)
            result = [tuple(comp) for comp in nx.connected_components(G_reduced)]
            return result

    def subgraph_from_coalition(self, graph_restricted_coalition: tuple,
                               nx_graph: nx.classes.graph.Graph) -> nx.classes.graph.Graph:
        """Generates a subgraph from a graph restricted coalition (a subset of
        nodes / players) and a graph.

        Args:
            graph_restricted_coalition (tuple): Nodes / players which form the
                subgraph.
            nx_graph (nx.classes.graph.Graph): Subgraph induced in this graph by
                the nodes_set.

        Returns:
            nx.classes.graph.Graph: The new subgraph.
        """
        if len(graph_restricted_coalition) == 0:
            return nx.Graph()
        else:
            return nx_graph.subgraph(graph_restricted_coalition)

    def calculate_single_myerson_value(self, node: int, grand_coalition: tuple,
                                  coalitions: list[tuple], coalition_to_worth: dict) -> float:
        """Calculate a single Myerson value.

        Args:
            node (int): Node index for which to calculate the Myerson value.
            grand_coalition (tuple): Set of all players.
            coalitions (list[tuple]): List of all coalitions.
            coalition_to_worth (dict): Mapping of every coalition to its worth.

        Returns:
            float: Myerson value.
        """
        my = 0
        size_grand_coalition = len(grand_coalition)
        factorial_size_grand_coalition = math.factorial(size_grand_coalition)
        for coalition in [S for S in coalitions if node not in S]:
            size_coalition = len(coalition)
            prefactor = ((math.factorial(size_coalition)
                         *math.factorial(size_grand_coalition-size_coalition-1))
                         /factorial_size_grand_coalition)
            worth_of_coalition = coalition_to_worth[coalition]
            worth_of_coalition_with_node = coalition_to_worth[tuple(sorted(coalition+(node,)))]
            my += prefactor * (worth_of_coalition_with_node - worth_of_coalition)
        return my

    def calculate_all_myerson_values(self) -> dict:
        """Calculate the Myerson values for every node / player in the graph.

        Returns:
            dict: Mapping of each node index to the Myerson value.
        """
        self.calculate_all_mappings()
        self.log.info(f"Calculating Myerson values.")
        my_values = {}
        for node in tqdm(self.grand_coalition, desc="Calculating Myerson values.", disable=self.disable_tqdm):
            my_val = self.calculate_single_myerson_value(node, self.grand_coalition,
                                                  self.coalitions, self.coalitions_to_worth)
            my_values.update({node: my_val})
        log_string = "".join([f"\t{k}: {v:.4f}\n" for k, v in my_values.items()])
        self.log.info(f"Myerson Values:\n{log_string}")
        return my_values

    def calculate_all_mappings(self) -> None:
        """Calculates all coalitions, graph restricted coalitions, and their
        associated worths as class attributes:

            * `self.coalitions` (list[tuple])
            * `self.graph_restricted_coalitions` (set[tuple])
            * `self.coalitions_to_graph_restricted_coalitions` (dict)
            * `self.graph_restricted_coalitions_to_worth` (dict)
            * `self.coalitions_to_worth` (dict)
        """
        self.coalitions = self.calculate_coalitions(self.grand_coalition)

        self.graph_restricted_coalitions, self.coalitions_to_graph_restricted_coalitions \
            = self.calculate_graph_restricted_coalitions(self.coalitions, self.nx_graph)

        self.graph_restricted_coalitions_to_worth \
            = self.calculate_worth_of_graph_restricted_coalitions(self.graph_restricted_coalitions)

        self.coalitions_to_worth \
            = self.map_coalition_to_worth(self.coalitions, 
                                          self.coalitions_to_graph_restricted_coalitions,
                                          self.graph_restricted_coalitions_to_worth)

class MyersonSampler(MyersonCalculator):
    r"""A class approximating the Myerson value using Monte Carlo sampling.
        The Myerson values are approximated by randomly sampling from all  
        permutations needed to calculate the Shapley value:

        .. math::

            \text{Sh}_i\,({v}) = \frac{1}{|N|!}\; \sum_R \big({v}\,(P_i^R \cup \{i\}) - {v}(P_i^R)\big)

        For efficiencies sake, the sampled permutations are transformed into
        the corresponding coalitions.

    Args:
        graph (nx.classes.graph.Graph): The coalition structure of the game.
        coalition_function (Callable): The coalition for which to calculate
            the payoff of the game. Expects a coalition (tuple of node
            indices) and a graph which contains additional information on
            the players to decide on the payoff. 
        seed (None | int, optional): Seed for randomness. Defaults to None.
        number_of_samples (int, optional): Number of sampling steps. Defaults to 1000.
        disable_tqdm (bool, optional): Disables progress bar. Defaults to True.
    """
    def __init__(self,
                 graph: nx.classes.graph.Graph,
                 coalition_function: Callable,
                 seed: None | int = None, 
                 number_of_samples: int = 1000,
                 disable_tqdm: bool=True) -> None:

        self.disable_tqdm = disable_tqdm
        self.log = logging.getLogger("MyersonSampler")
        self.nx_graph = graph
        self.grand_coalition = list(graph.nodes()) # alias: set of players / set of nodes / F
        self.coalition_function = coalition_function
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.number_of_samples = number_of_samples
        """Instantiates the class.
        """

    @staticmethod
    def _replace_in_array(array: np.ndarray, value_to_replace, value_to_replace_with) -> np.ndarray:
        """Replace a value in an array with a different value.

        Args:
            array (np.ndarray): The array.
            value_to_replace (int): The value to replace.
            value_to_replace_with (int): The value to replace with.

        Returns:
            np.ndarray: The array with the replace value if it was found, else
                the original array.
        """
        # Convert to a flat array to work with a single loop for any dimension
        flat_array = array.ravel().copy()
        # Find the index of the first occurrence of value_to_replace
        index = np.where(flat_array == value_to_replace)[0]
        if index.size > 0:  # Check if the value was found
            flat_array[index[0]] = value_to_replace_with  # Replace the first occurrence
        # Reshape back to original array's shape
        return flat_array.reshape(array.shape)

    def reset_rng(self):
        """Reset random number generator to seed.
        """
        self.rng = np.random.default_rng(self.seed)

    def sample_permutations(self, number_of_samples: int):
        """Uniformly sample permutations from all possible permutations. Samples
        `number_of_samples`*2*`number_of_nodes` permutations in total.

        Args:
            number_of_samples (int): How many sample steps should be carried out.

        Returns:
            tuple(int, list[np.ndarray], list[np.ndarray]): A randomly chosen 
                node, the sampled permutations without the random node, all the
                sampled permutations.
        """
        nodes_array = np.array(self.grand_coalition)
        random_node = self.rng.choice(nodes_array)

        self.log.info(f"Sampling {number_of_samples} steps.")
        permutations_without_random_node = []
        for i in tqdm(range(number_of_samples),
                      desc="Sample permutations without random node",
                      disable=self.disable_tqdm):
            random_permutation_size: int = self.rng.integers(0, len(nodes_array))  
            nodes_array_without_random_node = nodes_array.copy()
            indices_to_delete = np.where(nodes_array_without_random_node == random_node)
            nodes_array_without_random_node = np.delete(nodes_array_without_random_node,
                                                        indices_to_delete)
            sampled_permutation_without_random_node = self.rng.choice(nodes_array_without_random_node,
                                                        size=random_permutation_size,
                                                        replace=False)
            self.rng.shuffle(sampled_permutation_without_random_node)
            permutations_without_random_node.append(sampled_permutation_without_random_node)

        all_sampled_permutations = []
        for permutation in tqdm(permutations_without_random_node,
                         desc="Sample permutations containing random node",
                         disable=self.disable_tqdm):
            for node_idx, node in enumerate(nodes_array):
                sampled_permutation_with_current_swapped_in_random_node = permutation.copy()
                sampled_permutation_with_current_swapped_in_random_node = \
                self._replace_in_array(sampled_permutation_with_current_swapped_in_random_node,
                                       node, random_node)
                all_sampled_permutations.append(sampled_permutation_with_current_swapped_in_random_node)
                all_sampled_permutations.append(np.append(sampled_permutation_with_current_swapped_in_random_node, node))
        # len(all_sampled_permutations): steps*2*len(self.grand_coalition)
        self.log.info(f"Sampled {len(all_sampled_permutations)} of {math.factorial(len(self.grand_coalition))} permutations.")

        return random_node, permutations_without_random_node, all_sampled_permutations

    def get_coalitions_from_permutations(self, permutations: list[np.ndarray]):
        """Get the set of coalitions from the different (sampled) permutations.

        Args:
            permutations (list[np.ndarray]): The permutations.

        Returns:
            list[tuple]: The sampled coalitions.
        """
        all_sampled_coalitions = list(set([tuple(np.sort(x)) for x in permutations]))
        self.log.info(f"Sampled {len(all_sampled_coalitions)} of {2**len(self.grand_coalition)} coalitions.")
        return all_sampled_coalitions

    def sample_all_mappings(self) -> None:
        """Samples permutations, corresponding coalitions, graph restricted
        coalitions, and their associated worths as class attributes:

            * `self.random_node` (int) 
            * `self.permutations_without_random_node` (list[np.ndarray])
            * `self.all_sampled_permutations` (list[np.ndarray])
            * `self.coalitions` (list[tuple])
            * `self.graph_restricted_coalitions` (set[tuple])
            * `self.coalitions_to_graph_restricted_coalitions` (dict)
            * `self.graph_restricted_coalitions_to_worth` (dict)
            * `self.coalitions_to_worth` (dict)
        """
        self.random_node, self.permutations_without_random_node, self.all_sampled_permutations \
            = self.sample_permutations(self.number_of_samples)

        self.coalitions = self.get_coalitions_from_permutations(self.all_sampled_permutations)

        self.graph_restricted_coalitions, self.coalitions_to_graph_restricted_coalitions \
            = self.calculate_graph_restricted_coalitions(self.coalitions, self.nx_graph)

        self.graph_restricted_coalitions_to_worth \
            = self.calculate_worth_of_graph_restricted_coalitions(self.graph_restricted_coalitions)

        self.coalitions_to_worth \
            = self.map_coalition_to_worth(self.coalitions, 
                                          self.coalitions_to_graph_restricted_coalitions,
                                          self.graph_restricted_coalitions_to_worth)

    def sample_all_myerson_values(self) -> dict:
        """Use Monte Carlo sampling to approximate the Myerson values for every
        node / player in the graph.

        Returns:
            dict: Mapping of each node index to the sampled Myerson value.
        """
        self.sample_all_mappings()
        nodes_array = np.array(self.grand_coalition)
        my_values = np.zeros(len(nodes_array), dtype=float)
        self.log.info(f"Calculating sampled Myerson values.")
        for permutation in tqdm(self.permutations_without_random_node,
                              disable=self.disable_tqdm,
                              desc="Calculate sampled Myerson values"):
            for node_idx, node in enumerate(nodes_array):

                sampled_permutation_with_current_swapped_in_random_node = permutation.copy()
                sampled_permutation_with_current_swapped_in_random_node \
                    = self._replace_in_array(sampled_permutation_with_current_swapped_in_random_node,
                                             node,
                                             self.random_node)

                worth_with_node = self.coalitions_to_worth[tuple(np.sort(np.append(sampled_permutation_with_current_swapped_in_random_node, node)))]
                worth_without_node = self.coalitions_to_worth[tuple(np.sort(sampled_permutation_with_current_swapped_in_random_node))]
                my_values[node_idx] = (my_values[node_idx] + worth_with_node - worth_without_node)

        my_values = my_values / self.number_of_samples
        my_values = {i: float(my_i) for i, my_i in enumerate(my_values)}
        log_string = "".join([f"\t{k}: {v:.4f}\n" for k, v in my_values.items()])
        self.log.info(f"Sampled Myerson Values:\n{log_string}")
        return my_values

    def calculate_all_myerson_values(self) -> None:
        """Not implemented for sampling class.

        Raises:
            NotImplementedError: The MyersonSampler only has the
                `sample_all_myerson_values()` method. To accuratly calculate the
                Myerson values, please use the `MyersonCalculator` class.
        """
        raise NotImplementedError("""The MyersonSampler only has the `sample_all_myerson_values()` method.
                     To accuratly calculate the Myerson values,
                     please use the `MyersonCalculator` class.""")