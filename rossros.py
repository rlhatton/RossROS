#! /usr/bin/python3
import concurrent.futures
import time
import logging
from readerwriterlock import rwlock
from logdecorator import log_on_start, log_on_end, log_on_error

DEBUG = logging.DEBUG
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO,
                    datefmt="%H:%M:%S")


class Bus:
    """
    Class for passing broadcast messages between processes.
    """

    def __init__(self,
                 initial_message=0,
                 name="Unnamed Bus"):

        self.message = initial_message
        self.name = name

        # Set up the class so that functions can get a lock while working
        self.lock = rwlock.RWLockFairD()

    @log_on_start(DEBUG, "{self.name:s}: Initiating read by {_name:s}")
    @log_on_error(DEBUG, "{self.name:s}: Error on read by {_name:s}")
    @log_on_end(DEBUG, "{self.name:s}: Finished read by {_name:s}")
    def get_message(self, _name='Unspecified function'):

        with self.lock.gen_rlock():
            message = self.message

        return message

    @log_on_start(DEBUG, "{self.name:s}: Initiating write by {_name:s}")
    @log_on_error(DEBUG, "{self.name:s}: Error on write by {_name:s}")
    @log_on_end(DEBUG, "{self.name:s}: Finished write by {_name:s}")
    def set_message(self, message, _name='Unspecified function'):

        with self.lock.gen_wlock():
            self.message = message


def ensureTuple(value):
    """
    Function that wraps an input value in a tuple if it is not already a tuple
    """
    
    if isinstance(value, tuple):
        value_tuple = value
    else:
        value_tuple = (value,)  # comma creates the tuple

    return value_tuple


class ConsumerProducer:
    """
    Class that turns a provided function into a service that reads from
    the input buses, stores the resulting data into the output buses,
    and watches a set of termination buses for a "True" or non-negative signal, at which
    point the service shuts down
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create consumer-producer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating consumer-producer")
    @log_on_end(DEBUG, "{name:s}: Finished creating consumer-producer")
    def __init__(self,
                 consumer_producer_function,
                 input_buses,
                 output_buses,
                 delay=0,
                 termination_buses=Bus(False, "Default consumer_producer termination bus"),
                 name="Unnamed consumer_producer"):

        self.consumer_producer_function = consumer_producer_function
        self.input_buses = ensureTuple(input_buses)
        self.output_buses = ensureTuple(output_buses)
        self.delay = delay
        self.termination_buses = ensureTuple(termination_buses)
        self.name = name

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while executing consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    def __call__(self):

        while True:

            # Check if the loop should terminate
            # termination_value = self.termination_buses[0].get_message(self.name)
            if self.checkTerminationbuses():
                break

            # Collect all of the values from the input buses into a list
            input_values = self.collectbusesToValues(self.input_buses)

            # Get the output value or tuple of values corresponding to the inputs
            output_values = self.consumer_producer_function(*input_values)

            # Deal the values into the output buses
            self.dealValuesTobuses(output_values, self.output_buses)

            # Pause for set amount of time
            time.sleep(self.delay)

    # Take in a bus or a tuple of buses, and store their
    # messages into a list
    @log_on_start(DEBUG, "{self.name:s}: Starting collecting bus values into list")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while collecting bus values")
    @log_on_end(DEBUG, "{self.name:s}: Finished collecting bus values")
    def collectbusesToValues(self, buses):

        # Wrap buses in a tuple if it isn't one already
        buses = ensureTuple(buses)

        # Create a list for storing the values in the buses
        values = []

        # Loop over the buses, recording their values
        for p in buses:
            values.append(p.get_message(self.name))

        return values

    # Take in  a tuple of values and a tuple of buses, and deal the values
    # into the buses
    @log_on_start(DEBUG, "{self.name:s}: Starting dealing values into buses")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while dealing values into buses")
    @log_on_end(DEBUG, "{self.name:s}: Finished dealing values into buses")
    def dealValuesTobuses(self, values, buses):

        # Wrap buses in a tuple if it isn't one already
        buses = ensureTuple(buses)

        # Handle different combinations of bus and value counts

        # If there is only one bus, then the values should be treated as a
        # single entity, and wrapped into a tuple for the dealing process
        if len(buses) == 1:
            values = (values, )
        # If there are multiple buses
        else:
            # If the values are already presented as a tuple, leave them
            if isinstance(values, tuple):
                pass
            # If the values are not already presented as a tuple,
            # Make a tuple with one entry per bus, all of which are the
            # equal to the input values
            else:
                values = tuple([values]*len(buses))

        for idx, v in enumerate(values):
            buses[idx].set_message(v, self.name)

    @log_on_start(DEBUG, "{self.name:s}: Starting to check termination buses")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while checking termination buses")
    @log_on_end(DEBUG, "{self.name:s}: Finished checking termination buses")
    def checkTerminationbuses(self):

        # Look at all of the termination buses
        termination_bus_values = self.collectbusesToValues(self.termination_buses)

        # If any of the termination buses have triggered (gone true or non-negative), signal the loop to end
        for tbv in termination_bus_values:
            if tbv and tbv >= 0:
                return True


class Producer(ConsumerProducer):
    """
    Special case of the consumer-producer class, that sends values to buses
    but does not read them
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create producer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating producer")
    @log_on_end(DEBUG, "{name:s}: Finished creating producer")
    def __init__(self,
                 producer_function,
                 output_buses,
                 delay=0,
                 termination_buses=Bus(False, "Default producer termination bus"),
                 name="Unnamed producer"):

        # Producers don't use an input bus
        input_buses = Bus(0, "Default producer input bus")

        # Match naming convention for this class with its parent class
        # def syntax is necessary because a producer function will not accept
        # input values
        def consumer_producer_function(_input_value): return producer_function()

        # Call the parent class init function
        super().__init__(
            consumer_producer_function,
            input_buses,
            output_buses,
            delay,
            termination_buses,
            name)


class Consumer(ConsumerProducer):
    """
    Special case of the consumer-producer class, that reads values from buses
    but does not send to them
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create consumer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating consumer")
    @log_on_end(DEBUG, "{name:s}: Finished creating consumer")
    def __init__(self,
                 consumer_function,
                 input_buses,
                 delay=0,
                 termination_buses=Bus(False, "Default consumer termination bus"),
                 name="Unnamed consumer"):

        # Match naming convention for this class with its parent class
        consumer_producer_function = consumer_function

        # Consumers don't use an output bus
        output_buses = Bus(0, "Default consumer output bus")

        # Call the parent class init function
        super().__init__(
            consumer_producer_function,
            input_buses,
            output_buses,
            delay,
            termination_buses,
            name)


class Timer(Producer):
    """
    Timer is a producer that keeps track of time since it was instantiated
    Time is instantiated with a duration value, and writes a "countdown" value (time before or after the
    specified duration) to its output bus. The output bus can be used as the termination bus for other
    consumer-producers (and for the timer itself); these consumer producers will terminate when the timer reaches zero
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create timer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating timer")
    @log_on_end(DEBUG, "{name:s}: Finished creating timer")
    def __init__(self,
                 output_buses,  # buses that receive the countdown value
                 duration=5,  # how many seconds the timer should run for (0 is forever)
                 delay=0,  # how many seconds to sleep for between checking time
                 termination_buses=Bus(False, "Default timer termination bus"),
                 name="Unnamed termination timer"):

        super().__init__(
            self.timer,  # Timer class defines its own producer function
            output_buses,
            delay,
            termination_buses,
            name)

        self.duration = duration
        self.t_start = time.time()

    @log_on_start(DEBUG, "{self.name:s}: Checking current time against starting time")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while checking current time against starting time")
    @log_on_end(DEBUG, "{self.name:s}: Finished checking current time against starting time")
    def timer(self):

        # Trigger the timer if the duration is non-zero and the time elapsed
        # since instantiation is longer than the duration
        if self.duration:
            time_relative_to_end_time = time.time() - self.t_start - self.duration
            return time_relative_to_end_time
        else:
            return False


class Printer(Consumer):
    """
    Printer is a consumer that reads a value stored in a bus and prints it out at specified intervals
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create printer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating printer")
    @log_on_end(DEBUG, "{name:s}: Finished creating printer")
    def __init__(self,
                 printer_bus,  # bus or tuple of buses that should be printed to the terminal
                 delay=0,  # how many seconds to sleep for between printing data
                 termination_buses=Bus(False, "Default printer termination bus"),  # buses to check for termination
                 name="Unnamed termination timer",  # name of this printer
                 print_prefix="Unspecified printer: "):  # prefix for output

        super().__init__(
            self.print_bus,  # Printer class defines its own printing function
            printer_bus,
            delay,
            termination_buses,
            name)

        self.print_prefix = print_prefix

    def print_bus(self, *messages):
        output_string = self.print_prefix                  # Start the output string with the print prefix
        for msg in messages:                               # Append bus messages to the output

            if isinstance(msg, str):                       # If the message is a string, leave it as it is
                msg_str = msg
            else:                                          # If it's not a string, assume it's a number and convert it
                msg_str = str("{0:.4g}".format(msg))       # Convert to string with 4 significant figures
                if msg >= 0:                               # Append a space before the value if it is not negative
                    msg_str = " " + msg_str

            output_string = output_string + " " + msg_str  # Append the message string to the output string

            for i in range(1, 12 - len(msg_str)):          # Add spacing to put the outputs into columns
                output_string = output_string + " "

        print(output_string)                               # Print the formatted output


@log_on_start(DEBUG, "runConcurrently: Starting concurrent execution")
@log_on_error(DEBUG, "runConcurrently: Encountered an error during concurrent execution")
@log_on_end(DEBUG, "runConcurrently: Finished concurrent execution")
def runConcurrently(producer_consumer_list):
    """
    runConcurrently is aFunction that uses a concurrent.futures ThreadPoolExecutor to concurrently
    execute a set of ConsumerProducer functions
    """

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(producer_consumer_list)) as executor:

        # Create a list to hold the executors created from the provided functions
        executor_list = []

        # Loop over the list of provided functions, turning each into an executor for the thread pool
        for cp in producer_consumer_list:
            executor_list.append(executor.submit(cp))

    # Loop over the executors that were created above, running their result methods
    for e in executor_list:
        e.result()
