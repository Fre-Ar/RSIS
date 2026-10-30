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
        link_start: Node from which frame transmission starts.
        link_end: Node to which the frame must be transmitted.

    Returns:
        A list containing all the minimal cut sets. Each MCS contains links whose simultaneous failure causes the top-event. The MCSs must be sorted by increasing cardinality.
    """
    raise NotImplementedError


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
            
            
