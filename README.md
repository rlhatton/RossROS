# RossROS

RossROS is:

* A minimal robot operating system
* Written in Python
* Designed to illustrate concepts that appear in ROS, but with less overhead and more accessibility

## Why RossROS?

ROS is powerful, but has a lot of overhead. If you want to actually teach/learn how it works, a simpler system is more desirable. The RossROS kernel is approximately 300 lines of code, extensively commented, and therefore tractable to understand.

In our documentation, we also supply a set of suggested lessons for writing the components of RossROS from scratch in a scaffolded learning approach.

## Core components

### Message bus

Similar to ROS Topic (publish/subscribe model)

Implemented as cached messages -- any bus can be written to or read from by multiple processes, with readers getting the most recently-written message

### Consumer-Producers

Python class that wraps a function to 
* Run on a set frequency
* Take its inputs from a list of message busses
* Deal its outputs to a second list of message busses
