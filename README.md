# Mafati: A Functional Interpreted Language

Welcome to **Mafati**, an interpreted functional programming language designed to be simple yet powerful.
It’s perfect for those seeking a minimalistic and functional approach to programming.

Mafati runs through an interpreter called **Stacker**, which is built in Python. Whether you’re creating small utilities or experimenting with functional programming concepts, Mafati offers flexibility and ease of use.

## Installation Guide

To run Mafati, you’ll need Python (version 3.8 or later). Follow these steps:

### Step 1: Install Python
Download and install Python from the official [Python website](https://www.python.org/downloads/). Ensure that Python is added to your system's path during installation.

### Step 2: Install stacker from the repository

### Step 3: Setup
create a folder for your projects
######
create a stack.conf file
######
insert:
```
stack = Stack()
stack.load_code('code.maft')
stack.interpret()
```
create a code.maft file
#### Write your code in there and execute stacker.py to interpret

## Mafati Syntax Overview

### 1. **Arithmetic Operations**
Mafati supports basic arithmetic operations like addition, subtraction, multiplication, and division.

```maf
x = 5 + 3
y = x * 2
out y  
```

### 2. **Variable Assignment**
You can assign variables and use them in expressions.

```maf
x = 10
y = x + 5
out y 
```

### 3. **Inline Functions**
Mafati supports inline functions.

```maf
square = n -> n * n
f = square(4)  
out f
```

### 4. **Control Flow**
Conditional execution is handled using `if` statements, similar to traditional languages.

```maf
x = 10
if x > 5 then
out x is greater than 5
else
out x is less than or equal to 5
end
```

### 5. **Dynamic Python Code Execution**
Mafati allows you to embed Python code for complex operations.

```maf
py
def greet():
    print("Hello from Python!")


greet()
end

```
### 6. **Non-lambda functions**
functions are defined like python but they need an end and need to be added to the global scope with a **include** function (stack.include(<name in the global scope>, <host scope function>):
```maf
def mario(x, y):
    reurn x + y
include('mario', mario)
end
f = mario(5,5)
out f
```

### 7. **For loops**
```maf
for i in 1..50
    out Hello, World!
```
