from collections import defaultdict
from decimal import Decimal, getcontext
from typing import TypeAlias


# Use 20 significant digits for Decimal calculations so the very small link and
# top-event probabilities are not excessively rounded during the analysis.
getcontext().prec = 20

# These aliases describe the basic data structures used by the program: Edge is a directed link represented as a tuple, a network is a list of directed links, and a minimal cut set (MCS) is a frozenset of directed links. 
Edge: TypeAlias = tuple[str, str]
Network: TypeAlias = list[Edge]
MCS: TypeAlias = frozenset[Edge]

def find_minimal_cut_sets(
    network: Network,
    source: str,
    destination: str,
) -> list[MCS]:
    """Derive all minimal cut sets corresponding to the top-event that source-to-destination transmission fails, for the given network.

    Args:
        network: Directed network represented as a list of links. Each link is
            a ``(link_start, link_end)`` tuple indicating the direction of
            transmission.
        source: Node from which frame transmission starts.
        destination: Node to which the frame must be transmitted.

    Returns:
        A list containing all the minimal cut sets. Each MCS contains links whose simultaneous failure causes the top-event. The MCSs must be sorted by increasing cardinality.
    """
    # 1. Fill adjacency list 
    adjacency = defaultdict(list) # using defaultdict to avoid manual init of empty lists
    for start, end in network:
        adjacency[start].append(end)
    
    # 2. Find all paths from source to destination using DFS
    paths_edges = []
    
    # keeping track of global variables to avoid passing copies of the path in recursive calls
    visited = {source} # set of nodes currently in our path (for O(1) checks)
    path_nodes = [source] # list of nodes used in the current path, used to create edges for the path
    
    def dfs(current):
        # base case: when we reach the destination,
        # we can add the path to our list of paths
        if current == destination:
            # zip pairs sequential nodes to create edges for the path
            paths_edges.append(list(zip(path_nodes, path_nodes[1:])))
            return
        # exploring neighbors
        for neighbor in adjacency[current]:
            if neighbor not in visited:
                # record the neighbor as part of our current route
                visited.add(neighbor)
                path_nodes.append(neighbor)
                
                # explore that route
                dfs(neighbor)
                
                # backtrack (pop) for the next branch (loop iteration)
                path_nodes.pop()
                visited.remove(neighbor)
    dfs(source)
    
    # 3. Find all minimal cut sets from the paths
    mcs_list: list[MCS] = [] # list of MCSs found so far
    current_set = set() # set of edges in the current cut set (for O(1) checks)
    
    def fill_mcs(remaining_paths):
        # early pruning (if our set is a superset of a known MCS, we can stop)
        for mcs in mcs_list:
            if mcs.issubset(current_set):
                return
                
        # base case: no remaining paths (we have found a valid cut set)
        if not remaining_paths:
            # remove any existing cut sets that are supersets of the current set
            non_supersets = [mcs for mcs in mcs_list if not current_set.issubset(mcs)]
            non_supersets.append(frozenset(current_set))
            # replacing the list in place to avoid copying
            mcs_list[:] = non_supersets
            return
            
        # branching: try adding each of the first path's edges to the set
        path_to_cut = remaining_paths[0]
        for edge in path_to_cut:
            current_set.add(edge)
            # remove any remaining paths that are already cut by the current edge
            next_remaining = [p for p in remaining_paths[1:] if edge not in p]
            
            # continue cutting the remaining paths recursively
            fill_mcs(next_remaining)
            
            # backtrack to explore other edges in the path
            current_set.remove(edge)

    fill_mcs(paths_edges)
    
    # sort by cardinality 
    return sorted(mcs_list, key=len)


def derive_formula_for_top_event(
    mcs_list: list[MCS],
) -> str:
    """Return a string corresponding to the formula which approximates the top-event probability by summing up the probabilities of all minimal cut sets. You can use 'q' to represent the transmission failure probability on a single link.

    Args:
        mcs_list: Minimal cut sets returned by find_minimal_cut_sets().

    Returns:
        A string representation of the approximated top-event probability.
    """
    raise NotImplementedError

def compute_reliability_metrics(
    mcs_list: list[MCS],
    ber: Decimal,
) -> tuple[Decimal, Decimal]:
    """Compute the required reliability metrics for one BER.

    Compute the approximate top-event probability and the average time between
    packet losses in hours, using PACKET_SIZE_BITS and PACKET_PERIOD_IN_SECONDS.

    Args:
        mcs_list: Minimal cut sets returned by find_minimal_cut_sets().
        ber: Bit error rate used for the reliability calculation.

    Returns:
        A tuple containing the approximate top-event probability and the
        average time between packet losses in hours.
    """
    raise NotImplementedError



if __name__ == '__main__':
    # Each network architecture is represented by all the links that can be used
    # for packet transmission from source to destination.
    network1_baseline = [
        ("MCU-4", "SW_4"),
        ("SW_4", "SW_2"),
        ("SW_2", "SW_B"),
        ("SW_B", "SGA"),
    ]

    network2_CB = [
        ("MCU-4", "SW_4"),
        ("SW_4", "SW_A"),
        ("SW_4", "SW_2"),
        ("SW_A", "SW_B"),
        ("SW_2", "SW_B"),
        ("SW_B", "SGA"),
    ]

    network3_CB_dual_home = [
        ("MCU-4", "SW_4"),
        ("MCU-4", "SW_A"),
        ("SW_4", "SW_A"),
        ("SW_4", "SW_2"),
        ("SW_A", "SW_B"),
        ("SW_2", "SW_B"),
        ("SW_2", "SGA"),
        ("SW_B", "SGA"),
    ]

    network4_unseen = [
        ("MCU-4", "SW_4"),
        ("MCU-4", "SW_A"),
        ("SW_4", "SW_2"),
        ("SW_4", "SW_A"),
        ("SW_4", "SW_B"),
        ("SW_A", "SW_B"),
        ("SW_A", "SW_2"),
        ("SW_2", "SW_B"),
        ("SW_2", "SGA"),
        ("SW_B", "SGA"),
    ]

    networks = [
        network1_baseline,
        network2_CB,
        network3_CB_dual_home,
        network4_unseen,
    ]
    source_node = "MCU-4"
    destination_node = "SGA"

    BERs = [Decimal("1e-10"), Decimal("1e-12")]
    PACKET_SIZE_BITS = 3200
    PACKET_PERIOD_IN_SECONDS = Decimal("0.01")

    # Derive the MCSs and top-event formula for each network, then compute the
    # top-event probability and average time between packet losses for each BER.
    for network in networks:
        mcs_list = find_minimal_cut_sets(network, source_node, destination_node)
        formula = derive_formula_for_top_event(mcs_list)
        
        print("\n------------------------------------------")
        print("Network:")
        for link in network:
            print(f"  {link}")
        print("MCS list:")
        for index, mcs in enumerate(mcs_list, start=1):
            print(f"  MCS {index}: {mcs}")
        print(f"Formula: {formula}")

        for ber in BERs:
            failure_probability, average_time_between_packet_loss = compute_reliability_metrics(mcs_list, ber)
            
            print(f"BER: {ber}")
            print(f"Failure probability: {failure_probability}")
            print(f"Average time between packet losses: {average_time_between_packet_loss} hours")
            
            
