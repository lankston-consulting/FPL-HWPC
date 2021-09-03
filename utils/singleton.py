class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        """Singleton catcher

        Returns:
            Singleton: The a singleton object
        """
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)

        return cls._instance