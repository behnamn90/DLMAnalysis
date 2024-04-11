
class Helix:
    """
    Represents a helix in a DNA origami structure.

    Attributes:
        _index (int): The index of the helix.
        _nucs (list): The nucleotides in the helix.
        _domains (list): The domains associated with the helix.
    """

    def __init__(self, index, nucs):
        self._index = index
        self._nucs = nucs
        self._domains = []

    def __str__(self):
        """
        Returns a string representation of the helix.
        """
        result = 'Helix '+str(self.ind)
        return result

    ### Getters ###
    @property
    def ind(self):
        """
        Get the index of the helix.

        Returns:
            int: The index of the helix.
        """
        return self._index

    @property
    def nucs(self):
        """
        Get the nucleotides in the helix.

        Returns:
            list: The nucleotides in the helix.
        """
        return self._nucs

    @property
    def domains(self):
        """
        Get the domains associated with the helix.

        Returns:
            list: The domains associated with the helix.
        """
        return self._domains

    ### Setters ###
    def add_domain(self, domain):
        """
        Add a domain to the helix.

        Args:
            domain (Domain): The domain to add.
        """
        self._domains.append(domain)

    def set_domains(self, domains):
        """
        Set the domains associated with the helix.

        Args:
            domains (list): The domains to set.
        """
        self._domains = domains
