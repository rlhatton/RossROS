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
    Class to allow a single element data bus.
    """

    def __init__(self, initial_message=0, name="Unnamed Bus"):
        self.message = initial_message
        self.name = name

        # Set up the class so that functions can get a lock while working
        self.lock = rwlock.RWLockFairD()

    @log_on_start(DEBUG, "{self.name:s}: Initiating read by {_name:s}")
    @log_on_error(DEBUG, "{self.name:s}: Error on read by {_name:s}")
    @log_on_end(DEBUG, "{self.name:s}: Finished read by {_name:s}")
    def get_message(self, _name):

        with self.lock.gen_rlock():
            message = self.message

        return message

    @log_on_start(DEBUG, "{self.name:s}: Initiating write by {_name:s}")
    @log_on_error(DEBUG, "{self.name:s}: Error on write by {_name:s}")
    @log_on_end(DEBUG, "{self.name:s}: Finished write by {_name:s}")
    def set_message(self, message, _name):

        with self.lock.gen_wlock():
            self.message = message


# Create a set of default input and output busses
default_termination_bus = Bus(False)
default_input_bus = Bus()
default_output_bus = Bus()


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
    the input busses, stores the resulting data into the output busses,
    and watches a set of termination busses for a "True" signal, at which
    point the service shuts down
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create consumer-producer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating consumer-producer")
    @log_on_end(DEBUG, "{name:s}: Finished creating consumer-producer")
    def __init__(self,
                 consumer_producer_function,
                 input_busses=default_input_bus,
                 output_busses=default_output_bus,
                 delay=0,
                 termination_busses=default_termination_bus,
                 name="Unnamed consumer_producer"):

        self.consumer_producer_function = consumer_producer_function
        self.input_busses = ensureTuple(input_busses)
        self.output_busses = ensureTuple(output_busses)
        self.delay = delay
        self.termination_busses = ensureTuple(termination_busses)
        self.name = name

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while executing consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    def __call__(self):

        while True:

            # Check if the loop should terminate
            # termination_value = self.termination_busses[0].get_message(self.name)
            if self.checkTerminationBusses():
                break

            # Collect all of the values from the input busses into a list
            input_values = self.collectBussesToValues(self.input_busses)

            # Get the output value or tuple of values corresponding to the inputs
            output_values = self.consumer_producer_function(*input_values)

            # Deal the values into the output busses
            self.dealValuesToBusses(output_values, self.output_busses)

            # Pause for set amount of time
            time.sleep(self.delay)

    # Take in a bus or a tuple of busses, and store their
    # messages into a list
    @log_on_start(DEBUG, "{self.name:s}: Starting collecting bus values into list")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while collecting bus values")
    @log_on_end(DEBUG, "{self.name:s}: Finished collecting bus values")
    def collectBussesToValues(self, busses):

        # Wrap busses in a tuple if it isn't one already
        busses = ensureTuple(busses)

        # Create a list for storing the values in the busses
        values = []

        # Loop over the busses, recording their values
        for p in busses:
            values.append(p.get_message(self.name))

        return values

    # Take in  a tuple of values and a tuple of busses, and deal the values
    # into the busses
    @log_on_start(DEBUG, "{self.name:s}: Starting dealing values into busses")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while dealing values into busses")
    @log_on_end(DEBUG, "{self.name:s}: Finished dealing values into busses")
    def dealValuesToBusses(self, values, busses):

        # Wrap busses in a tuple if it isn't one already
        busses = ensureTuple(busses)

        # Handle different combinations of bus and value counts

        # If there is only one bus, then the values should be treated as a
        # single entity, and wrapped into a tuple for the dealing process
        if len(busses) == 1:
            values = (values, )
        # If there are multiple busses
        else:
            # If the values are already presented as a tuple, leave them
            if isinstance(values, tuple):
                pass
            # If the values are not already presented as a tuple,
            # Make a tuple with one entry per bus, all of which are the
            # equal to the input values
            else:
                values = tuple([values]*len(busses))

        for idx, v in enumerate(values):
            busses[idx].set_message(v, self.name)

    @log_on_start(DEBUG, "{self.name:s}: Starting to check termination busses")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while checking termination busses")
    @log_on_end(DEBUG, "{self.name:s}: Finished checking termination busses")
    def checkTerminationBusses(self):

        # Look at all of the termination busses
        termination_values = self.collectBussesToValues(self.termination_busses)

        # If any of the termination busses have triggered, signal the loop to end
        return any(termination_values)


class Producer(ConsumerProducer):
    """
    Special case of the consumer-producer class, that sends values to busses
    but does not read them
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create producer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating producer")
    @log_on_end(DEBUG, "{name:s}: Finished creating producer")
    def __init__(self,
                 producer_function,
                 output_busses,
                 delay=0,
                 termination_busses=default_termination_bus,
                 name="Unnamed producer"):

        # Producers don't use an input bus
        input_busses = default_input_bus

        # Match naming convention for this class with its parent class
        # def syntax is necessary because a producer function will not accept
        # input values
        def consumer_producer_function(_input_value): return producer_function()

        # Call the parent class init function
        super().__init__(
            consumer_producer_function,
            input_busses,
            output_busses,
            delay,
            termination_busses,
            name)


class Consumer(ConsumerProducer):
    """
    Special case of the consumer-producer class, that reads values from busses
    but does not send to them
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create consumer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating consumer")
    @log_on_end(DEBUG, "{name:s}: Finished creating consumer")
    def __init__(self,
                 consumer_function,
                 input_busses,
                 delay=0,
                 termination_busses=default_termination_bus,
                 name="Unnamed consumer"):

        # Match naming convention for this class with its parent class
        consumer_producer_function = consumer_function

        # Consumers don't use an output bus
        output_busses = default_output_bus

        # Call the parent class init function
        super().__init__(
            consumer_producer_function,
            input_busses,
            output_busses,
            delay,
            termination_busses,
            name)


class Timer(Producer):
    """
    Timer is a producer that keeps track of time since it was instantiated
    and sets its output busses to True once the elapsed time is longer than its
    "duration" parameter
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create timer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating timer")
    @log_on_end(DEBUG, "{name:s}: Finished creating timer")
    def __init__(self,
                 timer_busses,  # busses that should be set to true when timer triggers
                 duration=5,  # how many seconds the timer should run for (0 is forever)
                 delay=0,  # how many seconds to sleep for between checking time
                 termination_busses=default_termination_bus,
                 name="Unnamed termination timer"):

        super().__init__(
            self.timer,  # Timer class defines its own producer function
            timer_busses,
            delay,
            termination_busses,
            name)

        self.duration = duration
        self.t_start = time.time()

    @log_on_start(DEBUG, "{self.name:s}: Checking current time against starting time")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while checking current time against starting time")
    @log_on_end(DEBUG, "{self.name:s}: Finished checking current time against starting time")
    def timer(self):

        # Trigger the timer if the duration is non-zero and the time elapsed
        # since instantiation is longer than the duration
        if self.duration and (time.time() > (self.t_start + self.duration)):
            print(self.name + ": DING!")
            return True  # Marker that the timer has triggered
        else:
            return False  # Marker that the timer has not yet triggered


class Printer(Consumer):
    """
    Printer is a consumer that reads a value stored in a bus and prints it out at specified intervals
    """

    @log_on_start(DEBUG, "{name:s}: Starting to create printer")
    @log_on_error(DEBUG, "{name:s}: Encountered an error while creating printer")
    @log_on_end(DEBUG, "{name:s}: Finished creating printer")
    def __init__(self,
                 printer_bus,  # bus that should be printed to the terminal
                 delay=0,  # how many seconds to sleep for between printing data
                 termination_busses=default_termination_bus,  # busses to check for termination
                 name="Unnamed termination timer",  # name of this printer
                 print_prefix="Unspecified printer: "):  # prefix for output

        super().__init__(
            self.print_bus,  # Printer class defines its own printing function
            printer_bus,
            delay,
            termination_busses,
            name)

        self.print_prefix = print_prefix

    def print_bus(self, message):
        print(self.print_prefix + str(message))


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
