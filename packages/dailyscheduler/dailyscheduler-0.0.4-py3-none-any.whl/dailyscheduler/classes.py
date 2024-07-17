import datetime
from typing import Optional
from dailyscheduler.abstract_classes import Task


class WorkingDay():

    """
    A class representing a working day.
    
    Attributes:
        start (int): Start hour of the day (included).
        end (int): End hour of the day (excluded).
        hours (int): Total hours of the day.
        slot_duration (int): Duration of a slot in minutes.
        slot_number_in_hour (int): Number of slots in an hour.
        slots (list[int]): List of slots representing the availability of each hour.
    """

    ## FIXME: implement with datetime.time and not int to have better control over time

    start: int
    end: int
    hours: int
    slot_duration: int ## minutes per slot
    slot_number_in_hour: int ## numebr of slots in an hour
    slots: list[int]

    def __init__(self, start: int = 8, end: int = 16, slot_duration: int = 5):
        """
        Initialize a working day

        Args:
            start (int, optional): Start hour of the day (included). Defaults to 8.
            end (int, optional): End hour of the day (excluded). Defaults to 16.
            slot_duration (int, optional): Duration of a slot in minutes. Defaults to 5.

        """

        ## set the start and end hours of the day
        self.start = start
        self.end = end
        self.slot_duration = slot_duration
        
        if 60 % self.slot_duration != 0:
            raise ValueError("Slot duration must be a divisor of 60")

        ## integrity checks
        if self.start < 0 or self.start >= 24:
            raise ValueError("Start hour must be between 0 and 24")
        if self.end <= 0 or self.end > 24:
            raise ValueError("End hour must be between 1 and 24")
        if self.start >= self.end:
            raise ValueError("Start hour must be before end hour")

        self.hours = self.end - self.start # Total hours of the day
        self.slot_number_in_hour = 60//self.slot_duration # Duration of a slot in minutes
        self.slots = [0] * (self.hours * self.slot_number_in_hour)  # Each hour has slot_number_in_hour slots #slot_duration of minutes

    def __str__(self):
        return f"Working day from {self.start} to {self.end}. Number of hours: {self.hours}. Number of slots: {len(self.slots)}"
    
    def __len__(self):
        return len(self.slots)
    
    def __getitem__(self, index):
        return self.slots[index]
    
    ## properties
    
    
    ## MISC methods
    
    def debug(self):
        ## TODO: can be a good idea to make a config attribute to customize debug output and other stuff
            
        # declare variables for loops
        j = self.start
        n = 0

        # print header of calendar

        print("      |", end=" ")
        for i in range(self.slot_number_in_hour):
            print(f":{n:02}", end=" | ")
            n+=self.slot_duration
        print()
    
        # print first hour of calendar
        print(f"{j:02}:00", end=" | ")
        j += 1

        # print calendar slots
        for i in range(len(self.slots)):
            print(f"{self.slots[i]:03}", end=" | ")

            if (i + 1) % self.slot_number_in_hour == 0:
                print()
                print(f"{j:02}:00", end=" | ")
                j += 1

        print("\n\n")

    # SLOTS methods

    def get_hour_index(self, time: datetime.time):
        """
        Get the index of the hour in the time slots list.

        Args:
            time (datetime.time): The time to get the hour index for.

        Returns:
            int: The index of the hour in the time slots list, or None if the hour is not within the working day range.
        """

        if time.hour < self.start or time.hour >= self.end:
            raise ValueError(f"Hour {time.hour} is not in the working day range")
        
        return (time.hour - self.start) * self.slot_number_in_hour + time.minute // self.slot_duration

    def is_available(self, time: datetime.time):
        """
        Check if a time slot is available for a given hour.

        Args:
            time (datetime.time): The hour to check.

        Returns:
            bool: True if the time slot is available, False otherwise.
        """

        # Get the index of the hour in the time slots list
        index = self.get_hour_index(time)

        # Check if the hour is in the working day range
        if index is None:
            return False

        # Check if the slot is available
        if self.slots[index] == 0:
            return True
        else:
            return False

    def is_slot_available(self, from_hour: datetime.time, to_hour: datetime.time):
        """
        Check if a time slot is available for a given time range.

        Args:
            from_hour (datetime.time): The start hour of the time range.
            to_hour (datetime.time): The end hour of the time range.

        Returns:
            bool: True if the time slot is available, False otherwise.
        """

        # Get the index of the hours in the time slots list
        from_index = self.get_hour_index(from_hour)
        to_index = self.get_hour_index(to_hour)

        # Check if the hour is in the working day range
        if from_index is None or to_index is None:
            return False

        # Check if the from hour is before the to hour
        if from_index >= to_index:
            print("From hour must be before to hour")
            return False

        # Check if the slot is available
        for i in range(from_index, to_index):
            if self.slots[i] != 0:
                return False

        return True

    def is_slot_available_with_overlap(self, from_hour: datetime.time, to_hour: datetime.time, id: int):
        """
        Check if a time slot is available for a given time range, allowing overlap onto itself.

        Args:
            from_hour (datetime.time): The start hour of the time range.
            to_hour (datetime.time): The end hour of the time range.
            id (int): The ID of the task.

        Returns:
            bool: True if the time slot is available, False otherwise.
        """

        # Get the index of the hours in the time slots list
        from_index = self.get_hour_index(from_hour)
        to_index = self.get_hour_index(to_hour)

        # Check if the hour is in the working day range
        if from_index is None or to_index is None:
            return False

        # Check if the from hour is before the to hour
        if from_index >= to_index:
            print("From hour must be before to hour")
            return False

        # Check if the slot is available
        for i in range(from_index, to_index):
            if self.slots[i] != 0 and self.slots[i] != id:
                print(f"Slot {i} is not available")
                return False

        return True

    def book_slot(self, from_hour: datetime.time, to_hour: datetime.time, id: int = 1):
        """
        Book a time slot for a given time range.

        Args:
            from_hour (datetime.time): The start hour of the time range.
            to_hour (datetime.time): The end hour of the time range.
            id (int, optional): The ID of the task. Defaults to 1.

        Returns:
            bool: True if the time slot is successfully booked, False otherwise.
        """

        # Get the index of the hours in the time slots list
        from_index = self.get_hour_index(from_hour)
        to_index = self.get_hour_index(to_hour)

        # Check if the hour is in the working day range
        if from_index is None or to_index is None:
            return False

        # Check if the from hour is before the to hour
        if from_index >= to_index:
            raise ValueError("From hour must be before to hour")

        # Check if the slot is already booked
        for i in range(from_index, to_index):
            if self.slots[i] != 0:
                print(f"Slot {i} is already booked")
                raise RuntimeError(f"Slot {i} is already booked")

        # Book the slot
        for i in range(from_index, to_index):
            self.slots[i] = id

        return True

    def cancel_slot(self, from_hour: datetime.time, to_hour: datetime.time):
        """
        Cancel a booked time slot.

        Args:
            from_hour (datetime.time): The start hour of the time range.
            to_hour (datetime.time): The end hour of the time range.

        Returns:
            bool: True if the time slot is successfully canceled, False otherwise.
        """

        # Get the index of the hours in the time slots list
        from_index = self.get_hour_index(from_hour)
        to_index = self.get_hour_index(to_hour)

        # Check if the hour is in the working day range
        if from_index is None or to_index is None:
            return False

        # Check if the from hour is before the to hour
        if from_index >= to_index:
            print("From hour must be before to hour")
            return False

        # Check if the slot is already available
        for i in range(from_index, to_index):
            if self.slots[i] == 0:
                print(f"Slot {i} is already available")
                return False

        # Cancel the slot
        for i in range(from_index, to_index):
            self.slots[i] = 0

        return True

    def get_available_slots(self):
        """
        Get all available time slots.

        Returns:
            list[int]: A list of indices representing the available time slots.
        """

        slots = []

        for i in range(len(self.slots)):
            if self.slots[i] == 0:
                slots.append(i)

        return slots

    def get_available_slots_for_range(self, from_hour: datetime.time, to_hour: datetime.time):
        """
        Get all available time slots for a given time range.

        Args:
            from_hour (datetime.time): The start hour of the time range.
            to_hour (datetime.time): The end hour of the time range.

        Returns:
            list[int]: A list of indices representing the available time slots.
        """

        slots = []

        # Get the index of the hours in the time slots list
        from_index = self.get_hour_index(from_hour)
        to_index = self.get_hour_index(to_hour)

        # Check if the hour is in the working day range
        if from_index is None or to_index is None:
            return False

        # Check if the from hour is before the to hour
        if from_index >= to_index:
            print("From hour must be before to hour")
            return False

        # Check if the slot is already booked
        for i in range(from_index, to_index):
            if self.slots[i] == 0:
                slots.append(i)

        return slots

    def get_booked_slots(self):
        """
        Get all booked time slots.

        Returns:
            list[int]: A list of indices representing the booked time slots.
        """

        slots = []

        for i in range(len(self.slots)):
            if self.slots[i] != 0:
                slots.append(i)

        return slots

    def move_slot(self, before_start_hour: datetime.time, before_end_hour: datetime.time, after_start_hour: datetime.time):
        """
        Move a booked time slot to a new time range.

        Args:
            before_start_hour (datetime.time): The start hour of the original time range.
            before_end_hour (datetime.time): The end hour of the original time range.
            after_start_hour (datetime.time): The start hour of the new time range.

        Returns:
            bool: True if the time slot is successfully moved, False otherwise.
        """

        general_date = datetime.date(1, 1, 1)

        # calculate the duration between before_start_hour and before_end_hour
        before_duration = datetime.datetime.combine(general_date, before_end_hour) - datetime.datetime.combine(general_date, before_start_hour)

        # calculate after_end_hour by adding the duration to after_start_hour
        after_end_hour = (datetime.datetime.combine(general_date, after_start_hour) + before_duration).time()

        # Get Task id
        task_id = self.slots[self.get_hour_index(before_start_hour)]

        if self.is_slot_available(after_start_hour, after_end_hour):
            self.cancel_slot(before_start_hour, before_end_hour)
            self.book_slot(after_start_hour, after_end_hour, task_id)

            return True
        else:
            return False

    def move_slot_with_overlap(self, before_start_hour: datetime.time, before_end_hour: datetime.time, after_start_hour: datetime.time, id: int):
        """
        Move a booked time slot to a new time range, allowing overlap onto itself.

        Args:
            before_start_hour (datetime.time): The start hour of the original time range.
            before_end_hour (datetime.time): The end hour of the original time range.
            after_start_hour (datetime.time): The start hour of the new time range.
            id (int): The ID of the task.

        Returns:
            bool: True if the time slot is successfully moved, False otherwise.
        """

        general_date = datetime.date(1, 1, 1)

        # calculate the duration between before_start_hour and before_end_hour
        before_duration = datetime.datetime.combine(general_date, before_end_hour) - datetime.datetime.combine(general_date, before_start_hour)

        # calculate after_end_hour by adding the duration to after_start_hour
        after_end_hour = (datetime.datetime.combine(general_date, after_start_hour) + before_duration).time()
        after_end_hour = (datetime.datetime.combine(general_date, after_start_hour) + before_duration).time()

        # Get Task id
        task_id = self.slots[self.get_hour_index(before_start_hour)]

        if self.is_slot_available_with_overlap(after_start_hour, after_end_hour, id=id):
            self.cancel_slot(before_start_hour, before_end_hour)
            self.book_slot(after_start_hour, after_end_hour, task_id)       
        
            return True
        else:
            return False

    def delay_slot_by(self, from_hour: datetime.time, to_hour: datetime.time, minutes: int):
        """
        Delay a slot by a given number of minutes
        """

        outcome = self.move_slot_with_overlap(from_hour, to_hour, from_hour + datetime.timedelta(minutes=minutes), id=self.slots[self.get_hour_index(from_hour)])

        return outcome

    def slot_to_hour(self, slot: int):
        """
        Convert a slot index to an hour
        """
        
        if slot < 0 or slot >= len(self.slots):
            raise ValueError(f"Slot {slot} is not in the working day range")

        hour = self.start + slot // self.slot_number_in_hour
        minute = (slot % self.slot_number_in_hour) * self.slot_duration

        return datetime.time(hour, minute)

    def get_unavailable_slots(self):
        """
        Get all unavailable slots of the day
        """
        ## TODO: to implement
        
        unavailable_slots = []
        for slot in range(len(self.slots)):
            if self.slots[slot] != 0:
                unavailable_slots.append(self.slots[slot])
                
        return unavailable_slots
    
    ## TASK methods

    def book_task(self, task: Task):
        """
        Book a task
        """
        
        ## FIXME: always check if hour and duration etc of the task is updated after every change
        assert isinstance(task, Task)
        outcome = self.book_slot(task.from_hour, task.to_hour, id=task.id)

        return outcome
        
    def move_task(self, task: Task, new_from_hour: datetime.time):
        """
        Move a task
        """
        ## datetime.date(1, 1, 1) is just a dummy date to be able to use datetime.combine and set the desired time
        assert isinstance(task, Task)
        outcome = self.move_slot_with_overlap(task.from_hour, task.to_hour, new_from_hour, id=task.id)

        if outcome:
            # convert new_from_hour to a datetime, add task.duration, and extract the time
            new_to_hour = (datetime.datetime.combine(datetime.datetime.today(), new_from_hour) + task.duration).time()

            task.from_hour = new_from_hour
            task.to_hour = new_to_hour

        return outcome

    def cancel_task(self, task: Task):
        """
        Cancel a task
        """
        assert isinstance(task, Task)
        outcome = self.cancel_slot(task.from_hour, task.to_hour)

        return outcome
    
    def delay_task_by(self, task: Task, minutes: int):
        """
        Delay a task by a given number of minutes
        """
        assert isinstance(task, Task)
        ## TODO: check that task does not go after end of working day

        outcome = self.delay_slot_by(task.from_hour, task.to_hour, minutes)
        task.from_hour = task.from_hour + datetime.timedelta(minutes=minutes)
        task.to_hour = task.to_hour + datetime.timedelta(minutes=minutes)

        return outcome

    def get_available_slots_for_task_duration(self, task: Task):
        """
        Get all available slots for a given task, this function considers only the duration of the task, not the actual hour range
        """
        assert isinstance(task, Task)

        # calculate the number of slots required for the task (60 sec * 5 min = 300 sec)
        n_slots_required = task.duration.seconds // (self.slot_duration * 60)

        print(task.duration.seconds)
        print(n_slots_required)

        all_slots = self.get_available_slots()
        consecutive_slots = []

        print(all_slots)
        print(n_slots_required)
        
        # check if there are enough consecutive slots and then append them to list
        for i in range(len(all_slots) - n_slots_required + 1):
            ## take a slice of the list of slots and check if they are consecutive by comparing it to a list of consecutive numbers given by range()
            if all_slots[i:i+n_slots_required] == list(range(all_slots[i], all_slots[i] + n_slots_required)):
                ## if they are consecutive, append the first slot to the list of consecutive slots
                consecutive_slots.append(all_slots[i])
        
        return consecutive_slots
        
    def move_task_to_nearest_slot(self,task):
        """
        Move a task to the nearest available slot
        """
        assert isinstance(task, Task)

        # get all available slots for the task
        available_slots = self.get_available_slots_for_task(task)

        # get the index of the hour of the task
        task_hour_index = self.get_hour_index(task.from_hour)

        # get the index of the hour of the nearest available slot
        nearest_available_slot_index = min(available_slots, key=lambda x:abs(x-task_hour_index))

        # convert the index of the nearest available slot to an hour
        nearest_available_slot_hour = self.slot_to_hour(nearest_available_slot_index)

        # move the task to the nearest available slot
        outcome = self.move_task(task, nearest_available_slot_hour)

        return outcome
    
    def get_task_index_from_hour(self, hour: datetime.time) -> Optional[int]:
        """
        Get the task from a given hour if present
        """

        index = self.get_hour_index(hour)

        if self.slots[index] != 0:
            return self.slots[index]
        else:
            return None
        
    def get_all_tasks_indexes(self) -> set[int]:
        """
        Get the indexes of all tasks of the day
        """
        
        tasks = set()
        for slot in range(len(self.slots)):
            if self.slots[slot] != 0:
                tasks.add(self.slots[slot])
                
        return tasks