class Cell:
    """The cell class"""
    def __init__(
        self,
        walls: int = 15,
        static: bool = False,
        visited: bool = False
    ) -> None:
        """initialize the object"""
        self.walls: int = walls
        self.visited: bool = visited
        self.static: bool = static
        self.entrace: bool = False
        self.exit: bool = False
