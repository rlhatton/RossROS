from rossros import *
import asyncio

class Bus:
    """
    Class for passing broadcast messages between processes.
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



@log_on_start(DEBUG, "runConcurrently: Starting concurrent execution")
@log_on_error(DEBUG, "runConcurrently: Encountered an error during concurrent execution")
@log_on_end(DEBUG, "runConcurrently: Finished concurrent execution")
async def gather(producer_consumer_list):
    """
    Function that uses asyncio.gather to concurrently
    execute a set of ConsumerProducer functions
    """
    await asyncio.gather(*producer_consumer_list)


def runConcurrently(producer_consumer_list):
    """
    Function that uses asyncio.run to tell asyncio.gather to run a list of
    ConsumerProducers
    """
    asyncio.run(gather(producer_consumer_list))
