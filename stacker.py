import operator
import ast
from typing import Any, Dict, List
import math as mt

def Warning(func):
    return lambda *args, **kwargs: (print(f"# Warning: {func.__name__} is broken"), None) or func(*args, **kwargs)

class Stack:
    def __init__(self, lunghezza: int = 2**8, librerie: List[str] = []) -> None:
        self.lunghezza = lunghezza
        self.stack: List[str] = []
        self.variables: Dict[str, Any] = {}
        self.librerie = librerie
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow
        }
        self.p = 0
    
    @Warning
    def _load_library(self, libreria: str) -> None:
        """Load a library from a file and append its contents to the stack."""
        with open(libreria, 'r') as f:
            self.stack.append(line.strip() for line in f if line.strip())

    def load_code(self, file_codice: str) -> None:
        """Load code from a specified file into the stack."""
        try:
            with open(file_codice, 'r') as f:
                lines = [line for line in f if line]
                for line in lines:
                    if line.startswith('   '):
                        self.stack.append(line)
                    else:
                        self.stack.append(line.strip())


            if len(self.stack) > self.lunghezza:
                raise ValueError(f"Errore: La lunghezza della pila supera il limite ({self.lunghezza}).")
        except FileNotFoundError:
            raise FileNotFoundError(f"Errore: Il file '{file_codice}' non esiste.")

    def interpret(self) -> None:
        """Interpret and execute the code in the stack."""
        while self.p < len(self.stack):
            token = self.stack[self.p]
            self.p += 1
            if token == '':
                continue
            
            elif token.startswith('if '):

                self._handle_if(token)

            
            else:
                self._handle_token(token)

# Modify _handle_token to remove Python imports
    def _handle_token(self, token: str) -> None:
        """
        Handle different types of tokens, now including 'for' loops.
        """
        match token:
            case _ if token == 'info':
                self._info()
            case _ if token.startswith('def') or token.startswith('py'):
                self._handle_py(token)
            case _ if 'radquand' in token:
                self._handle_sqrt(token)
            case _ if '=' in token:
                self._assign_variable(token)
            case _ if token.startswith('delete'):
                self._delete_variable(token)
            case _ if 'out' in token:
                self._handle_print(token.replace('out', '').strip())
            case 'else':
                self._handle_else()
            case 'end':
                pass
            case 'debug':
                self._debug_info()
            case token if token in {'stop', 'pause'}:
                input("Premi un tasto per continuare...")
            case _ if '#' in token:
                pass  # Ignore comments
            case _ if token.startswith('for'):   # NEW: for loop detection
                self._handle_for(token)          # Call the new method
            case _:
                print(f"Errore: '{token}' non è un'espressione valida.")

    def _handle_for(self, token: str) -> None:
        """
        Handle 'for' loops in the format: for var in start..end.
        The loop body runs until 'end' is encountered.
        """
        try:
            # Parse the for loop structure, e.g., 'for i in 1..10'
            parts = token.replace('for', '').strip().split(' in ')
            var_name = parts[0].strip()
            range_part = parts[1].strip()

            # Extract the start and end of the range (e.g., '1..10')
            start, end = map(int, range_part.split('..'))

            # Accumulate the loop body (lines between 'for' and 'end')
            loop_body = []
            while self.p < len(self.stack):
                line = self.stack[self.p]
                self.p += 1
                if line.strip() == 'end':
                    break
                loop_body.append(line)

            # Execute the loop
            for value in range(start, end + 1):
                self.variables[var_name] = value  # Set the loop variable in the environment
                for line in loop_body:            # Execute each line in the loop body
                    self._handle_token(line)

        except Exception as e:
            print(f"Errore: invalid 'for' loop syntax ({e})")


    def _assign_variable(self, token: str) -> None:
        """Assign a value to a variable, including lambda functions and lambda calls."""
        var_name, expression = map(str.strip, token.split('=', 1))

        if '..' in expression:
            start, end = map(int, expression.split('..'))
            self.variables[var_name] = list(range(start, end + 1))
            
        # Check if it's a list, e.g., x = [1, 2, 3]
        elif '[' and ']' in expression:
            value = eval(expression)
            self.variables[var_name] = value

        # Check if it's a lambda call, e.g., x(5)
        elif '(' in expression and ')' in expression:
            func_name, arg_str = expression.split('(', 1)
            func_name = func_name.strip()
            args = arg_str.replace(')', '').split(',')

            # Resolve the function and its arguments
            if func_name in self.variables and callable(self.variables[func_name]):
                func = self.variables[func_name]
                resolved_args = [self._resolve_name(arg.strip()) for arg in args]
                result = func(*resolved_args)
                self.variables[var_name] = result
            else:
                raise ValueError(f"Errore: '{func_name}' non è una funzione valida.")
        
        # Check if the expression is a lambda function
        elif '->' in expression:
            # Parse the lambda expression
            param, body = expression.split('->', 1)
            param = param.replace('->', ':').strip()
            body = body.strip()

            # Define and store the lambda function
            self.variables[var_name] = eval(f"lambda {param}: {body}")
        
        # Regular variable assignment
        else:
            value = self._safe_eval(expression)
            self.variables[var_name] = value

    def _delete_variable(self, token: str) -> None:
        """Delete a variable from the stack."""
        var_name = token.replace('cancella ', '').strip()
        if var_name in self.variables:
            del self.variables[var_name]
        else:
            print(f"Errore: La variabile '{var_name}' non è presente.")

    def _debug_info(self) -> None:
        """Print debug information."""
        print("=== DEBUG INFO ===")
        print(f"Stack: {self.stack}")
        print(f"Variables and functions: {self.variables}")
        print("==================")

    def _handle_print(self, item: str) -> None:
        """Print the value of a variable or constant."""
        if item in self.variables:
            print(self.variables[item])
        else:
            print(item)

    def include(self, name, value):
        """Include a value from the host Python environment into the stacker environment."""        
        self.variables[name] = value

    def _handle_sqrt(self, token: str) -> None:
        """Calculate the square root and store the result in a variable."""
        parts = token.split(',')
        var_name = parts[0].split()[-1]
        self.variables[var_name] = mt.sqrt(self._resolve_name(parts[1].strip()))

    def _handle_py(self, token: str) -> None:
        """Accumulate lines of code following the 'py' command and execute them as Python code."""

        toval = ''  # Empty string to accumulate lines of code
        if token.startswith('def'):
            toval += token + '\n'
        while self.p < len(self.stack):
            line = self.stack[self.p]
            self.p += 1
            if line == 'end':  # Stop reading lines when 'end' is encountered
                break
            toval += line + '\n'  # Concatenate each line with a newline for proper formatting
        
        
        
        #print(toval)
        exec(toval)  # Execute the accumulated Python code 


    def _info(self) -> None:
        """Print information about Stacker, including the version number and
        copyright/license information."""

        print('Stacker version 1.1')
        print('Copyright (C) 2024 Mario Pisano')
        print('under the MIT License')
    def _execute_function(self, func_name: str) -> None:
        """Execute a previously defined function."""
        func_code = self.functions[func_name]
        original_stack = self.stack.copy()
        original_p = self.p

        self.stack = func_code
        self.p = 0
        self.interpret()

        self.stack = original_stack
        self.p = original_p

    def _handle_if(self, token: str) -> None:
        """Handle if statements with AST evaluation of the condition."""
        try:
            # Extract the condition from the token string (strip 'then' part)
            condition = token.replace('then', '').replace('if', '').strip()
            
            # Safely evaluate the condition using _safe_eval (only condition part)
            if self._safe_eval(condition):
                return  # Condition is true, so continue execution
            
            # Condition is false, skip lines until 'else' or 'end' is found
            while self.p < len(self.stack) and not self.stack[self.p].startswith('else') and not self.stack[self.p].startswith('end'):
                self.p += 1
                
        except Exception as e:
            print(f"Error: invalid if condition '{condition}' ({e})")


    def _handle_else(self) -> None:
        """Handle else statements."""
        while self.p < len(self.stack) and not self.stack[self.p].startswith('end'):
            self.p += 1

    def _resolve_name(self, name: str) -> Any:
        """Resolve a variable or constant name to its value."""
        if name in self.variables:
            return self.variables[str(name)]
        else:
            return float(name)  # Assume it's a number if not found

    def _safe_eval(self, expression: str) -> Any:
        """Safely evaluate an expression."""
        try:
            expr_ast = ast.parse(expression, mode='eval').body
            return self._eval_ast(expr_ast)
        except Exception as e:
            raise ValueError(f"Errore: L'espressione '{expression}' non è valida. ({e})")

    def _eval_ast(self, node: ast.AST) -> Any:
        """Evaluate an AST node."""
        match node:
            case ast.Constant():
                return node.value
            case ast.Name():
                return self._resolve_name(node.id)
            case ast.BinOp():
                left = self._eval_ast(node.left)
                right = self._eval_ast(node.right)
                operator_type = type(node.op)
                if operator_type in self.operators:
                    return self.operators[operator_type](left, right)
                else:
                    raise ValueError(f"Operatore '{operator_type}' non supportato.")
            case ast.Compare():  # Handle comparison operators like ==
                left = self._eval_ast(node.left)
                right = self._eval_ast(node.comparators[0])
                operator_type = type(node.ops[0])
                if operator_type == ast.Eq:
                    return operator.eq(left, right)  # Handle '=='
                elif operator_type == ast.Lt:
                    return operator.lt(left, right)  # Handle '<'
                elif operator_type == ast.Gt:
                    return operator.gt(left, right)  # Handle '>'
                else:
                    raise ValueError(f"Operatore di confronto '{operator_type}' non supportato.")
            case _:
                raise ValueError("Nodo non supportato nel AST.")


with open('stack.conf', 'r') as f:
    exec(f.read())

