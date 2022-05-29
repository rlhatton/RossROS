# RossROS

RossROS is a minimal robot operating system designed to teach principles of concurrent interactions between sensing, processing and acting elements of a system.

## Why Use RossROS?

RossROS is a lightweight means of constructing a set of multitasked processes, passing messages with a publish-subscribe model (conceptually similar to the "topics" model used in ROS). Its design is targeted at two main educational use-cases:

* Direct use in an educational setting: RossROS allows programs written as monolithic sense-think-act loops (e.g., basic line following algorithms) to be easily converted into pre-emptive or cooperative multitasked programs. This conversion then supports further instruction in more complex control architectures using a simpler syntax and less implementation overhead than would be required for a full ROS install.

* An introduction to multitasked programming itself: "Implement a basic version of RossROS" is a feasible assignment that exposes students to the core concepts of how multitasked systems work. Within a "system stack" robotics class, this provides students with a mental model for multitasking and some "hands-on" experience with such code, but without requiring the depth and extent of coverage typically seen when multitasking is covered in a traditional "programming" class.

## Provided Files

The core RossROS functionality is provided in rossros.py, with an example of code using the library provided in rossros_demo.py. An alternative implementation (using cooperative multitasking) is provided as rossros_asyncio.py, and demonstrated in rossros_asyncio_demo.py. 

Documentation for RossROS is provided in:
* This Readme
* Comments in the Python files
* RossROS_Design_and_Teaching.pdf, which contains notes on the principles which motivated the design of the code and suggested programming tasks for implementing RossROS from scratch as a learning exercise



## Components

The core components of RossROS are two python classes -- message buses and consumer-producers. 

* Message buses are data containers with read-write locking, designed to allow processes running in separate threads to safely exchange data.

* Consumer-producers are function wrappers that set up their enclosed functions to run periodically in their own threads, drawing their inputs from a set of message buses, and writing their outputs to a second set of buses. Each consumer producer monitors a list of "termination buses", and stops running if any of these buses takes on a True or non-negative numeric value.

RossROS additionally provides several additional classes derived from the consumer-producer class:

* Producers wrap functions that take no input but generate output.

* Consumers wrap functions that that take in input but do not generate output.

* Timers are producers that count down to a future time. Tying their output to the termination bus monitored by another consumer-producer is a convenient way to set the consumer-producer to run for a fixed length of time.

* Printers are consumers that display the current values held by a bus or set of buses.

## Using RossROS

To set up a system using RossROS:

* Create a set of functions for the tasks you want to execute (e.g., read sensor data, interpret sensor data, send motor commands).
* Create a set of buses for passing data between the tasks.
* Wrap the functions into consumer-producer objects linked by the appropriate buses.
* Pass the list of consumer-producer objects into the runConcurrently function provided by RossROS.

It is often useful to additionally:
* Create a termination bus so that all of the consumer-producers can be shut down cleanly.
* Create a timer whose output is the termination bus, to limit the time that the system runs for.
* Create a printer tied to the data and termination buses, to monitor the state of the system.

The file rr_demo.py provides a commented example of this process.


## Pre-emptive and cooperative multitasking

The core rossros.py library uses pre-emptive multitasking, implemented via the concurrent.futures Python package.

An alternative library, rossros_asyncio.py, instead uses cooperative multitasking, implemented via the asyncio Python package.

Systems set up with rossros.py should be able to seamlessly transition to using rossros_asyncio.py simply by changing the relevant "import" line in the code, and it can be instructive to compare the behavior of the system under the two approaches to multitasking.

Note that when using cooperative multitasking, the default behavior for a consumer-producer is to retain control of the processor for the complete "collect input data, execute the function, and deal output data" operation. For a function that takes a significant length of time to complete, you can let the function release the processor at intermediate points by including calls to "await.sleep" within the functions (but note that any such calls will stack with the loop delay time, so that you should decrease the loop delay to keep the same overall execution frequency).

