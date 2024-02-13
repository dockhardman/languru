import socket
from typing import Text


def check_port(port: int, host: Text = "0.0.0.0"):
    """Check if a port is available.

    Parameters
    ----------
    port : int
        The port number to check.
    host : str, optional
        The host address to bind to. Defaults to '0.0.0.0'.

    Returns
    -------
    bool
        True if the port is available, False otherwise.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except socket.error:
            return False


# Get available port starting from a port number and incrementing by 1
def get_available_port(start_port: int, host: Text = "0.0.0.0") -> int:
    """Get an available port starting from a port number and incrementing by 1.

    Parameters
    ----------
    start_port : int
        The port number to start from.
    host : str, optional
        The host address to bind to. Defaults to '0.0.0.0'.

    Returns
    -------
    int
        The available port number.
    """

    port = start_port
    while not check_port(port=port, host=host):
        port += 1
    return port
