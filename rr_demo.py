#!/usr/bin/python3
"""
This file demonstrates the basic operation of a RossROS program.

First, it defines two signal-generator functions (a +/-1 square wave and a saw-tooth wave) and a
function for multiplying two scalar values together.

Second, it generates buses to hold the most-recently sampled values for the signal-generator functions,
the product of the two signals, and a countdown timer determining how long the program should run

Third, it wraps the signal-generator functions into RossROS Producer objects, and the multiplication
function into a RossROS Consumer-Producer object.

Fourth, it creates a RossROS Printer object to periodically display the current bus values, and a RossROS Timer
object to terminate the program after a fixed number of seconds

Fifth and finally, it makes a list of all of the RossROS objects and sends them to the runConcurrently function
for simultaneous execution

"""

import rossros as rr
import logging
import time
import math

# logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)


""" First Part: Signal generation and processing functions """

# Create two signal-generation functions


# This function outputs a square wave that steps between +/- 1
# every second
def square():
    return (2 * math.floor(time.time() % 2)) - 1


# This function counts up from zero to 1 every second
def sawtooth():
    return time.time() % 1  # "%" is the modulus operator


# This function multiplies two inputs together
def mult(a, b):
    return a * b


""" Second Part: Create buses for passing data """

# Initiate data and termination busses
bSquare = rr.Bus(square(), "Square wave bus")
bSawtooth = rr.Bus(sawtooth(), "Sawtooth wave Bus")
bMultiplied = rr.Bus(sawtooth() * square(), "Multiplied wave bus")
bTerminate = rr.Bus(0, "Termination Bus")

""" Third Part: Wrap signal generation and processing functions into RossROS objects """

# Wrap the square wave signal generator into a producer
readSquare = rr.Producer(
    square,  # function that will generate data
    bSquare,  # output data bus
    0.05,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read square wave signal")

# Wrap the sawtooth wave signal generator into a producer
readSawtooth = rr.Producer(
    sawtooth,  # function that will generate data
    bSawtooth,  # output data bus
    0.05,  # delay between data generation cycles
    bTerminate,  # bus to watch for termination signal
    "Read sawtooth wave signal")

# Wrap the multiplier function into a consumer-producer
multiplyWaves = rr.ConsumerProducer(
    mult,  # function that will process data
    (bSquare, bSawtooth),  # input data buses
    bMultiplied,  # output data bus
    0.05,  # delay between data control cycles
    bTerminate,  # bus to watch for termination signal
    "Multiply Waves")

""" Fourth Part: Create RossROS Printer and Timer objects """

# Make a printer that returns the most recent wave and product values
printBuses = rr.Printer(
    (bSquare, bSawtooth, bMultiplied, bTerminate),  # input data buses
    # bMultiplied,      # input data buses
    0.25,  # delay between printing cycles
    bTerminate,  # bus to watch for termination signal
    "Print raw and derived data",  # Name of printer
    "Data bus readings are: ")  # Prefix for output

# Make a timer (a special kind of producer) that turns on the termination
# bus when it triggers
terminationTimer = rr.Timer(
    bTerminate,  # Output data bus
    3,  # Duration
    0.01,  # Delay between checking for termination time
    bTerminate,  # Bus to check for termination signal
    "Termination timer")  # Name of this timer

""" Fifth Part: Concurrent execution """

# Create a list of producer-consumers to execute concurrently
producer_consumer_list = [readSquare,
                          readSawtooth,
                          multiplyWaves,
                          printBuses,
                          terminationTimer]

# Execute the list of producer-consumers concurrently
rr.runConcurrently(producer_consumer_list)
