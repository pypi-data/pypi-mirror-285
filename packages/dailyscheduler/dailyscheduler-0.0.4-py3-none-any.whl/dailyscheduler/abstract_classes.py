import datetime
from abc import ABC, abstractmethod
import datetime


class Task(ABC):
    """
    Abstract base class representing a task. Must be subclassed to be used.
    
    Subclasses must have all this attributes and call super() constructor. 

    Attributes:
        __id (int): The ID of the task.
        __from_hour (datetime.time): The starting hour of the task.
        __to_hour (datetime.time): The ending hour of the task.
        __duration (datetime.timedelta): The duration of the task.

    Methods:
        __init__(self, **kwargs): Initializes the task object.
        __str__(self): Returns a string representation of the task.

    """

    __id: int
    __from_hour: datetime.time
    __to_hour: datetime.time
    __duration: datetime.timedelta

    def __init__(self, id: int, from_hour: datetime.time, to_hour: datetime.time) -> None:
        """
        Initializes an instance of the class.

        Args:
            id (int): The ID of the instance.
            from_hour (datetime.time): The starting hour of the task.
            to_hour (datetime.time): The ending hour of the task.
        """
        assert isinstance(id, int)
        assert isinstance(from_hour, datetime.time)
        assert isinstance(to_hour, datetime.time)
        
        self.id = id
        self.from_hour = from_hour
        self.to_hour = to_hour

        self.duration = datetime.timedelta(minutes=(self.__to_hour.hour * 60) + self.__to_hour.minute - (self.__from_hour.hour * 60) - self.__from_hour.minute)

    @property
    def id(self) -> int:
        """
        Returns the ID of the task.

        Returns:
            int: The ID of the task.

        """
        return self.__id
    
    @id.setter
    def id(self, value: int) -> None:
        """
        Sets the ID of the task.

        Args:
            value (int): The ID of the task.

        """
        if value <= 0:
            raise ValueError("ID must be greater than 0")
        
        self.__id = value

    @property
    def from_hour(self) -> datetime.time:
        """
        Returns the starting hour of the task.

        Returns:
            datetime.time: The starting hour of the task.

        """
        return self.__from_hour
    
    @from_hour.setter
    def from_hour(self, value: datetime.time) -> None:
        """
        Sets the starting hour of the task.

        Args:
            value (datetime.time): The starting hour of the task.

        """
        self.__from_hour = value

    @property
    def to_hour(self) -> datetime.time:
        """
        Returns the ending hour of the task.

        Returns:
            datetime.time: The ending hour of the task.

        """
        return self.__to_hour
    
    @to_hour.setter
    def to_hour(self, value: datetime.time) -> None:
        """
        Sets the ending hour of the task.

        Args:
            value (datetime.time): The ending hour of the task.

        """
        self.__to_hour = value

    @property
    def duration(self) -> datetime.timedelta:
        """
        Returns the duration of the task.

        Returns:
            datetime.timedelta: The duration of the task.
            
        """
        return self.__duration
    
    @duration.setter
    def duration(self, value: datetime.timedelta) -> None:
        """
        Sets the duration of the task.

        Args:
            value (datetime.timedelta): The duration of the task.

        """
        self.__duration = value

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns a string representation of the task.

        Returns:
            str: A string representation of the task.

        """
        pass