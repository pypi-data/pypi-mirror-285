
# ANSI code for colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

#dielectric properties
DDX = 0.01 # spatial discretization
SPEED_C = 299792458 # speed of light [m/s]
DT = DDX/int(2*SPEED_C ) # temporal discretization
EPSZ = 8.8541e-12