import datetime
import unittest
from dailyscheduler.abstract_classes import Task


class TaskSubclassNoMethod(Task):
    booking_id: int
    name: str
    teacher_name: str    
    
    
    def __init__(self, **kwargs):
        super().__init__(id=kwargs.get("booking_id"), from_hour=kwargs.get("from_hour"), to_hour=kwargs.get("to_hour"))
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        
class TaskSubclass(Task):
    booking_id: int
    name: str
    teacher_name: str    
    
    
    def __init__(self, **kwargs):
        super().__init__(id=kwargs.get("id"), from_hour=kwargs.get("from_hour"), to_hour=kwargs.get("to_hour"))
        
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def __str__(self):
        return f"{self.booking_id} {self.name} {self.teacher_name} {self.id} {self.from_hour} {self.to_hour}"
            
## actual tests

class TestTask(unittest.TestCase):
    
    def test_task_init_failure(self):
        """ Test if the Task subclass fails to instantiate correctly """
        with self.assertRaises(TypeError):
            TaskSubclassNoMethod(booking_id=1, name="Math", teacher_name="Mr. A", id=1, from_hour=datetime.time(8), to_hour=datetime.time(9,30))
        with self.assertRaises(ValueError):
            TaskSubclass(booking_id=1, name="Math", teacher_name="Mr. A", id=-1, from_hour=datetime.time(8), to_hour=datetime.time(9,30))
        with self.assertRaises(AssertionError):
            TaskSubclass(booking_id=1, name="Math", teacher_name="Mr. A", from_hour=datetime.time(8), to_hour=datetime.time(9,30))
        with self.assertRaises(AssertionError):
            TaskSubclass(booking_id=1, name="Math", teacher_name="Mr. A", id=1, from_hour=datetime.time(8))
        with self.assertRaises(AssertionError):
            TaskSubclass(booking_id=1, name="Math", teacher_name="Mr. A", id=1)
        
        
        

    def test_task_init_success(self):
        """ Test if the Task class is initialized correctly """ 
        
        TaskSubclass(booking_id=1, name="Math", teacher_name="Mr. A", id=1, from_hour=datetime.time(8), to_hour=datetime.time(9,30), invalid=1)              
        task1 = TaskSubclass(booking_id=1,
                     name="Math",
                     teacher_name="Mr. A",
                     id=1,
                     from_hour=datetime.time(8),
                     to_hour=datetime.time(9,30)
                     )

        self.assertIsInstance(task1, TaskSubclass)
        self.assertIsInstance(task1, Task)
        self.assertIsInstance(task1.from_hour, datetime.time)
        self.assertIsInstance(task1.to_hour, datetime.time)
        self.assertIsInstance(task1.duration, datetime.timedelta)
        self.assertEqual(task1.from_hour, datetime.time(8))
        self.assertEqual(task1.to_hour, datetime.time(9,30))
        self.assertEqual(task1.duration, datetime.timedelta(minutes=90))
        

if __name__ == '__main__':
    unittest.main(verbosity=2)