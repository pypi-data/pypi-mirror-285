import datetime
import unittest
from dailyscheduler.abstract_classes import Task
from dailyscheduler.classes import WorkingDay


class TaskSubclass(Task):
    id = None
    additional_1 = None
    additional_2 = None
    
    def __init__(self, from_hour: datetime.time, to_hour: datetime.time, id: int, additional_1=None, additional_2=None):
        super().__init__(id, from_hour, to_hour)
        self.id = id
        self.additional_1 = additional_1
        self.additional_2 = additional_2
    
    def __str__(self):
        return "TaskSubclass"

class TestDay(unittest.TestCase):
    
    def test_correct_init(self):
        """ Test if the Day class is initialized correctly """ 
        WorkingDay(start=8, end=16, slot_duration=5)
        
    def test_incorrect_init(self):
        pass
    
    def test_hours(self):
        """ Test if the hours property returns the correct value """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(day.hours, 8)

    def test_length(self):
        """ Test if the __len__ method returns the correct value """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(len(day), 96)

    def test_get_hour_index(self):
        """ Test if the get_hour_index method returns the correct index """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(day.get_hour_index(datetime.time(8, 0)), 0)
        self.assertEqual(day.get_hour_index(datetime.time(13, 30)), 66)
        self.assertEqual(day.get_hour_index(datetime.time(15, 30)), 90)

    def test_slot_to_hour(self):
        """ Test if the slot_to_hour method returns the correct hour """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(day.slot_to_hour(0), datetime.time(8, 0))
        self.assertEqual(day.slot_to_hour(11), datetime.time(8, 55))
        self.assertEqual(day.slot_to_hour(15), datetime.time(9, 15))
        
    def test_get_hour_index_outside_working_hours(self):
        """ Test if the get_hour_index method raises ValueError for hours outside working hours """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        with self.assertRaises(ValueError):
            day.get_hour_index(datetime.time(7, 0))
        with self.assertRaises(ValueError):
            day.get_hour_index(datetime.time(17, 0))

    def test_slot_to_hour_outside_working_hours(self):
        """ Test if the slot_to_hour method raises ValueError for slots outside working hours """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        with self.assertRaises(ValueError):
            day.slot_to_hour(-1)
        with self.assertRaises(ValueError):
            day.slot_to_hour(96)

    def test_get_hour_index_seconds_time(self):
        """ Test if the get_hour_index method raises ValueError for time with seconds """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        day.get_hour_index(datetime.time(8, 30, 15))
        self.assertEqual(day.get_hour_index(datetime.time(8, 33, 15)), 6) ## 8:30:00 - 8:34:59 is 6th slot

    def test_slot_to_hour_invalid_slot(self):
        """ Test if the slot_to_hour method raises ValueError for invalid slot """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        with self.assertRaises(ValueError):
            day.slot_to_hour(100)

    def test_get_hour_index_exact_end_time(self):
        """ Test if the get_hour_index method returns the correct index for the exact end time """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(day.get_hour_index(datetime.time(15, 55)), 95) ## beacause last hour (16:00) is not included

    def test_slot_to_hour_exact_end_slot(self):
        """ Test if the slot_to_hour method returns the correct hour for the exact end slot """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(day.slot_to_hour(95), datetime.time(15, 55))
        
    def test_base_methods_fails(self):
        day = WorkingDay(start=8, end=16, slot_duration=5)
        with self.assertRaises(ValueError):
            day.get_hour_index(datetime.time(7, 0))

    def test_get_task_index_from_hour(self):
        """ Test if the get_task_index_from_hour method returns the correct index """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        task1 = TaskSubclass(from_hour=datetime.time(8, 0), to_hour=datetime.time(9, 0), id=1)
        task2 = TaskSubclass(from_hour=datetime.time(9, 0), to_hour=datetime.time(10, 0), id=2)
        task3 = TaskSubclass(from_hour=datetime.time(10, 0), to_hour=datetime.time(11, 0), id=3)
        day.book_task(task1)
        day.book_task(task2)
        day.book_task(task3)
        
        self.assertEqual(day.get_task_index_from_hour(datetime.time(8, 30)), 1)
        self.assertEqual(day.get_task_index_from_hour(datetime.time(9, 15)), 2)
        self.assertEqual(day.get_task_index_from_hour(datetime.time(10, 45)), 3)
        self.assertEqual(day.get_task_index_from_hour(datetime.time(11, 30)), None)  # No task at this hour

    def test_get_all_tasks_indexes(self):
        """ Test if the get_all_tasks_indexes method returns the correct indexes """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        task1 = TaskSubclass(from_hour=datetime.time(8, 0), to_hour=datetime.time(9, 0), id=1)
        task2 = TaskSubclass(from_hour=datetime.time(9, 0), to_hour=datetime.time(10, 0), id=2)
        task3 = TaskSubclass(from_hour=datetime.time(10, 0), to_hour=datetime.time(11, 0), id=3)
        day.book_task(task1)
        day.book_task(task2)
        day.book_task(task3)

        self.assertEqual(day.get_all_tasks_indexes(), {1, 2, 3})

    def test_get_all_tasks_indexes_empty_day(self):
        """ Test if the get_all_tasks_indexes method returns an empty list for an empty day """
        day = WorkingDay(start=8, end=16, slot_duration=5)
        self.assertEqual(day.get_all_tasks_indexes(), set([]))

    def test_get_available_slots_for_task_duration(self):
        """ Test if the get_available_slots_for_task method returns the correct available slots """
        day = WorkingDay(start=8, end=16, slot_duration=30)
        task1 = TaskSubclass(from_hour=datetime.time(8, 0), to_hour=datetime.time(9, 0), id=1)
        task2 = TaskSubclass(from_hour=datetime.time(9, 0), to_hour=datetime.time(10, 0), id=2)
        task3 = TaskSubclass(from_hour=datetime.time(10, 0), to_hour=datetime.time(11, 0), id=3)
        day.book_task(task1)
        day.book_task(task2)
        day.book_task(task3)

        # Test for a task that can be scheduled in the available slots
        task4 = TaskSubclass(from_hour=datetime.time(11, 0), to_hour=datetime.time(12, 0), id=4)
        available_slots = day.get_available_slots_for_task_duration(task4)
        self.assertEqual(available_slots, [i for i in range(6, 15)])

        # Test for a task that cannot be scheduled due to exceeding the working hours
        task6 = TaskSubclass(from_hour=datetime.time(15, 0), to_hour=datetime.time(16, 30), id=6)
        available_slots = day.get_available_slots_for_task_duration(task6)
        self.assertEqual(available_slots, [i for i in range(6, 14)])
    
if __name__ == '__main__':
    unittest.main(verbosity=2)