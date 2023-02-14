#! /usr/bin/env python3

"""Module cesim  (Cache Effect Simulator) simulates 
   the cache effect on throughput"""

import math

###############################################################################
# Primitive Parameters
###############################################################################

# Input Parameters (from the experiment on the EIVU platform)
T_0    = 172   # Maximum throughput [Mpps]
N_0    = 163   # L1 access times (hits + misses) [times/packet]
R2     = 0.70  # L2 hit ratio
R3     = 0.79  # L3 hit ratio

# Server spec. Parameters
CPU    = 3.5   # CPU clock rate [GHz]
C_L1   = 4     # L1 access latency [cycles]
C_L2   = 14    # L2 access latency [cycles]
C_L3   = 68    # L3 access latency [cycles]
_C_MEM = 79    # Memory access latency (part) [cycles]
_L_MEM = 50    # Memory access latency (part) [ns]

# Other Parameters
A      = 0.5   # Processing rate (0 <= A <= 1)


###############################################################################
# Global Variables
###############################################################################

# Global variables
C_MEM  = None  # Memory access latency [cycles]
N      = None  # Apparent L1 access times [times/packet]
L_PROC = None  # Processing latency w/o memory (cache) accesses [ns]
L_L1   = None  # L1 access latency [ns]
L_L2   = None  # L2 access latency [ns]
L_L3   = None  # L3 access latency [ns]
L_MEM  = None  # Memory access latency [ns]
B      = None  # Acceleration factor (1 <= B)


##############################################################################
# Processing
##############################################################################

def validate():
    """Validates the important constans and variables"""

    if C_L1 < 1 or L_L1 < 0:
        raise ValueError(f'Invalid L1 access cost: {C_L1} ({L_L1:.2f})')
    if C_L2 < C_L1 or L_L2 < L_L1:
        raise ValueError(f'Invalid L2 access cost: {C_L2} ({L_L2:.2f})')
    if C_L3 < C_L2 or L_L3 < L_L2:
        raise ValueError(f'Invalid L3 access cost: {C_L3} ({L_L3:.2f})')
    if C_MEM < C_L3 or L_MEM < L_L3:
        raise ValueError(f'Invalid memory access cost: {C_MEM} ({L_MEM:.2f})')
    if T_0 <= 0:
        raise ValueError(f'Invalid maximum throughput: {T_0}')
    if N_0 <= 0:
        raise ValueError(f'Invalid L1 access times: {N_0}')
    if CPU <= 0:
        raise ValueError(f'Invalid CPU clock rate: {CPU:.2f}')
    if A < 0 or 1 < A:
        raise ValueError(f'Invalid processing rate: {A:.2f}')
    if B < 1:
        raise ValueError(f'Invalid acceleration factor: {B:.2f}')


def calc_throughput(R1):
    """Calculates the throughput when L1 hit ratio is 'R1'"""

    l3_miss = (1.0 - R3) * L_MEM
    l3_hit  = R3 * L_L3
    l3_latency = l3_hit + l3_miss

    l2_miss = (1.0 - R2) * l3_latency
    l2_hit  = R2 * L_L2
    l2_latency = l2_hit + l2_miss

    l1_miss = (1.0 - R1) * l2_latency
    l1_hit  = R1 * L_L1
    l1_latency = l1_hit + l1_miss

    _N_STAR = math.pow(R1, B) * N + (1 - math.pow(R1, B)) * N_0
    _L_ACCESS = _N_STAR * l1_latency

    return 1000.0 / (L_PROC + _L_ACCESS)


def plot():
    """Plots the throughputs in the range of L1 hit ratio"""

    _START_PER = 99 # [%]
    _STOP_PER = 100 # [%]
    _RESOLUTION = 10000

    start = int(_START_PER / 100.0 * _RESOLUTION)
    stop  = int(_STOP_PER / 100.0 * _RESOLUTION)

    for _r in range(start, stop + 1):
        r_1 = float(_r) / _RESOLUTION
        thr = calc_throughput(r_1)
        print(f'{r_1:.4f},{thr:.4f}')


if __name__ == "__main__":

    # Initialize the global variables

    C_MEM = (CPU * _L_MEM)  + _C_MEM

    _NS_PER_CLOCK = 1.0 / CPU

    L_L1 = C_L1 * _NS_PER_CLOCK
    L_L2 = C_L2 * _NS_PER_CLOCK
    L_L3 = C_L3 * _NS_PER_CLOCK
    L_MEM = C_MEM * _NS_PER_CLOCK

    _NS_PER_PACKET = 1000.0 / T_0

    L_PROC = _NS_PER_PACKET * A
    _L_ACCESS = _NS_PER_PACKET - L_PROC

    N = _L_ACCESS / L_L1
    B = float(N_0) / N  # B = 1 (the acceleration factor is disabled)


    # Validates the variables and constants
    validate()

    # Start the simulation
    plot()
