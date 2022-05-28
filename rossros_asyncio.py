#!/usr/bin/python3
"""
This file modifies RossROS to use cooperative multitasking (via the asyncio package)
rather than preemptive multitasking (via concurrent.futures)

--

The RossROS AsyncIO package acts as a transparent wrapper on top of RossROS:
The user syntax for both the base RossROS package and this modification are the same, and you can replace

import rossros

with

import rossros_asyncio

and expect your code to run as before (assuming that you haven't incorporated any extra dependencies on
the threading architecture from concurrent.futures).

While running RossROS AsyncIO, you can include calls to "await.sleep" within the consumer and producer functions
(but note that any such calls will stack with the loop delay time, so that you should decrease the loop delay
to keep the same overall execution frequency).

--

Under the hood, RossROS AsyncIO makes three changes to RossROS:

First, it replaces the Bus class with a version that does not use locking code (which is no longer necessary
because switching behavior is explicitly handled by the code structure).

Second, it replaces the __call__ method for all ConsumerProducers with a version that is aware of the asyncio
task-switching architecture.

Third, it replaces the runConcurrently function with a version that uses the asyncio paradigm.
"""

from rossros import *
import asyncio


""" First Change: For asyncio, locking is handled manually, so the Bus class does not the the RWLock code"""


class Bus:
    """
    Redefined bus class that removes the RW lock code
    """

    def __init__(self, initial_message=0, name="Unnamed Bus"):
        self.message = initial_message
        self.name = name

    @log_on_start(DEBUG, "{self.name:s}: Initiating read by {_name:s}")
    @log_on_error(DEBUG, "{self.name:s}: Error on read by {_name:s}")
    @log_on_end(DEBUG, "{self.name:s}: Finished read by {_name:s}")
    def get_message(self, _name):
        message = self.message
        return message

    @log_on_start(DEBUG, "{self.name:s}: Initiating write by {_name:s}")
    @log_on_error(DEBUG, "{self.name:s}: Error on write by {_name:s}")
    @log_on_end(DEBUG, "{self.name:s}: Finished write by {_name:s}")
    def set_message(self, message, _name):
        self.message = message


""""
Second Change: the __call__ method for ConsumerProducer and its child classes needs to be an async function
and have an "await asyncio.sleep" call instead of time.sleep.

The "from rossros import *" call at the beginning of the file brings all items in the rossros namespace into the
rossros_asyncio namespace. Declaring classes in rossros_asyncio that inherit from their same-named classes in rossros
then allows us to redefine the __call__ method to be asyncio-aware.
"""


class ConsumerProducer(ConsumerProducer):

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while closing down consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    async def __call__(self):

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
            await asyncio.sleep(self.delay)


class Producer(Producer):

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while closing down consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    async def __call__(self):

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
            await asyncio.sleep(self.delay)


class Consumer(Consumer):

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while closing down consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    async def __call__(self):

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
            await asyncio.sleep(self.delay)


class Printer(Printer):

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while closing down consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    async def __call__(self):

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
            await asyncio.sleep(self.delay)


class Timer(Timer):

    @log_on_start(DEBUG, "{self.name:s}: Starting consumer-producer service")
    @log_on_error(DEBUG, "{self.name:s}: Encountered an error while closing down consumer-producer")
    @log_on_end(DEBUG, "{self.name:s}: Closing down consumer-producer service")
    async def __call__(self):

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
            await asyncio.sleep(self.delay)


"""
Third change: Replace the runConcurrently function with a version that calls asyncio.run. This function requires
a helper function (gather) to set up the execution calls
"""

@log_on_start(DEBUG, "runConcurrently: Starting concurrent execution")
@log_on_error(DEBUG, "runConcurrently: Encountered an error during concurrent execution")
@log_on_end(DEBUG, "runConcurrently: Finished concurrent execution")
async def gather(producer_consumer_list):
    """
    Function that uses asyncio.gather to concurrently
    execute a set of ConsumerProducer functions
    """

    # Make a new list of producer_consumers by evaluating the input list
    # (this evaluation matches syntax with rossros.py)
    producer_consumer_list2 = []
    for pc in producer_consumer_list:
        producer_consumer_list2.append(pc())

    await asyncio.gather(*producer_consumer_list2)


def runConcurrently(producer_consumer_list):
    """
    Function that uses asyncio.run to tell asyncio.gather to run a list of
    ConsumerProducers
    """
    asyncio.run(gather(producer_consumer_list))
