# MicroSignal

## Description
MicroSignal provides a lightweight library for handling custom signals with synchronous and asynchronous callbacks in Python. It supports both function-based and method-based callbacks, allowing for flexible signal handling in various contexts.

The library was born out of the need for a very simple event subscription model functionality, similar to the systems used in QT or PyPubSub (inspired by these libraries), but without being overloaded with unnecessary functionality and features. It also needed to work with both synchronous and asynchronous functions and class methods, something that was sorely lacking in PyPubSub.

Or as Michael Abrash said in his book "[Graphics Programming Black Book](https://www.jagregory.com/abrash-black-book/)": "No code runs faster than no code."


## Features
- Synchronous and asynchronous callback support
- Function and class method callback support
- Easy-to-use decorator and method for subscribing to signals

## Installation

To install MicroSignal, you can use pip:

```sh
pip install microsignal
```


