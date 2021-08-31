import pandas

class DiscardDestinations(object):
    
    _instance = None

    discard_destinations = None

    def __new__(cls, *args, **kwargs):
        """Singleton catcher

        Returns:
            DiscardDestinations: The singleton DiscardDestinations object
        """
        if cls._instance is None:
            cls._instance = super(DiscardDestinations, cls).__new__(cls)

            val = {'id': [0, 1, 2, 3, 4], 'discard destinations': ['Burned', 'Recycled', 'Composted', 'Landfills', 'Dumps']}

            cls.discard_destinations = pandas.DataFrame(data=val)

        return cls._instance

    
    def UpdateValues(vals: dict) -> None:
        """Update the internal lookup table for discard destinations. This should probably never be used

        Args:
            vals (dict): A dictionary of {'id':List, 'discard destinations':List}

        Returns:
            None
        """
        return None