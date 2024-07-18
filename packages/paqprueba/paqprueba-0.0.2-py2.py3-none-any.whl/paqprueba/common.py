"""The common module contains common functions and classes used by the other modules.
"""

def hello_world():
    """Prints "Hello World!" to the console.
    """
    print("Hello World!")
    
    
    
    
def get_version():
    """Returns the version of the paqprueba package.
    
    Returns:
        str: The version of the paqprueba package.
    """
    
    return "0.0.1"


def random_number():
    """Return a random number between 0 and 1.

    Returns:
        float: A random number between 0 and 1.
    """
    
    import random
    return random.random()
  