import operator
import ast
from typing import Any, Dict, List
import math as mt
import time



class Stack:
    def __init__(self, lunghezza: int = 256, librerie: List[str] = []) -> None:
        self.lunghezza = lunghezza
        self.stack: List[str] = []
        self.variables: Dict[str, Any] = {}
        self.const: Dict[str, Any] = {}
        self.functions: Dict[str, List[str]] = {}
        self.librerie = librerie
        self.libstack: List[str] = []  # Stores library contents
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,          # Modulo
            ast.FloorDiv: operator.floordiv, # Divisione intera
            ast.USub: operator.neg          # Negazione unaria
        }
        self.p = 0


    def _load_library(self, libreria: str) -> None:
        """Load a library from a file and append its contents to libstack."""
        with open(libreria, 'r') as f:
            self.libstack.extend(line.strip() for line in f if line.strip())

    def load_code(self, file_codice: str) -> None:
        """Load code from a specified file into the stack."""
        try:
            with open(file_codice, 'r') as f:
                self.stack += [line.strip() for line in f if line.strip()]
            if len(self.stack) > self.lunghezza:
                raise ValueError(f"Errore: La lunghezza della pila supera il limite ({self.lunghezza}).")
        except FileNotFoundError:
            raise FileNotFoundError(f"Errore: Il file '{file_codice}' non esiste.")

    def interpreta(self) -> None:
        """Interpret and execute the code in the stack."""
        self.stack.extend(self.libstack)  # Merge library code into the main stack
        
        while self.p < len(self.stack):
            token = self.stack[self.p]
            self.p += 1

            if token.startswith('se '):
                self._handle_if(token)
            elif 'carica' in token:
                self._load_library(token.replace('carica', '').strip() + '.mlib')
            elif 'var' in token:
                for var in token.replace('var', '').replace(',', '').strip().split():
                    self.variables[var] = 0
            elif '#' in token:
                continue
            else:
                self._handle_token(token)

    def _handle_token(self, token):
        """Handle a single token in the stack."""
        actions = {
            'radquand': self._handle_sqrt,
            'quad': self._handle_quad,
            '=': self._assign_variable,
            'cancella ': self._delete_variable,
            'stampa': lambda t: self._handle_print(t.replace('stampa', '').strip()),
            'aggiungi': self._handle_generic_operation,
            'moltiplica': lambda t: self._handle_operation(t, operator.mul),
            'somma': lambda t: self._handle_operation(t, sum),
            'public ': self._define_function,
            'altrimenti': self._handle_else,
            'end': lambda t: None,
            'debug': self._debug_info,
        }

        for key, action in actions.items():
            if key in token:
                action(token)
                return

        if token in self.functions:
            self._execute_function(token)
        elif token in {'aspetta', 'pause'}:
            input("Premi un tasto per continuare...")
        elif '#' in token:
            pass  # Ignore comments
        else:
            print(f"Errore: '{token}' non è un'espressione valida.")


    def _assign_variable(self, token: str) -> None:
        """Assign a value to a variable, including lambda functions and lambda calls."""
        var_name, expression = map(str.strip, token.split('=', 1))

        # Check if it's a lambda call, e.g., x(5)
        if '(' in expression and ')' in expression:
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
        elif 'lambda' in expression:
            # Parse the lambda expression
            param, body = expression.split(':', 1)
            param = param.replace('lambda', '').strip()
            body = body.strip()

            # Define and store the lambda function
            self.variables[var_name] = eval(f"lambda {param}: {body}")
        
        # Regular variable assignment
        else:
            value = self._safe_eval(expression)
            if var_name.startswith('const_'):
                if var_name in self.const:
                    print(f"Errore: La costante '{var_name}' non può essere modificata.")
                else:
                    self.const[var_name] = value
            else:
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
        print(f"Variables: {self.variables}")
        print(f"Constants: {self.const}")
        print(f"Functions: {self.functions}")
        print("==================")

    def _handle_print(self, item: str) -> None:
        """Print the value of a variable or constant."""
        if item in self.variables:
            print(self.variables[item])
        elif item in self.const:
            print(self.const[item])
        else:
            print(item)

    def _handle_operation(self, token: str, op: Any) -> None:
        """Perform an operation and store the result in a variable."""
        parts = token.split(',')
        var_name = parts[0].split()[-1]
        operands = [self._resolve_name(part.strip()) for part in parts[1:]]

        if op == sum:
            result = sum(operands)
        else:
            result = operands[0]
            for operand in operands[1:]:
                result = op(result, operand)

        self.variables[var_name] = result
        print(f"{var_name} = {result}")

    def _handle_sqrt(self, token: str) -> None:
        """Calculate the square root and store the result in a variable."""
        parts = token.split(',')
        var_name = parts[0].split()[-1]
        self.variables[var_name] = mt.sqrt(self._resolve_name(parts[1].strip()))

    def _handle_quad(self, token: str) -> None:
        parts = token.split(',')
        if len(parts) < 2:
            print(f"Errore: token '{token}' non contiene abbastanza parti per il quadrato.")
            return

        var_name = parts[0].split()[-1]  # Extract var_name from the first token part
        self.variables[var_name] = mt.pow(self._resolve_name(parts[1].strip()), 2)

    def _handle_generic_operation(self, token: str) -> None:
        """Handle generic operations like addition."""
        parts = token.split()
        command = parts[1]
        var_name = parts[2].rstrip(',')
        operands = [self._resolve_name(part.strip().rstrip(',')) for part in parts[3:]]

        if command == 'somma':
            result = sum(operands)
        else:
            raise ValueError(f"Operazione '{command}' non riconosciuta.")

        self.variables[var_name] = result
        print(f"{var_name} = {result}")

    def _define_function(self, token: str) -> None:
        """Define a new function."""
        func_name = token.split()[1]
        func_code = []

        while self.p < len(self.stack):
            line = self.stack[self.p]
            self.p += 1
            if line == 'end':
                break
            func_code.append(line)

        self.functions[func_name] = func_code

    def _execute_function(self, func_name: str) -> None:
        """Execute a previously defined function."""
        func_code = self.functions[func_name]
        original_stack = self.stack.copy()
        original_p = self.p

        self.stack = func_code
        self.p = 0
        self.interpreta()

        self.stack = original_stack
        self.p = original_p

    def _handle_if(self, token: str) -> None:
        """Handle if statements."""
        condition = token.split('se ')[1].split(' allora')[0].strip()
        if self._safe_eval(condition):
            return
        else:
            while self.p < len(self.stack) and not self.stack[self.p].startswith('altrimenti') and not self.stack[self.p].startswith('end'):
                self.p += 1

    def _handle_else(self) -> None:
        """Handle else statements."""
        while self.p < len(self.stack) and not self.stack[self.p].startswith('end'):
            self.p += 1

    def _resolve_name(self, name: str) -> Any:
        """Resolve a variable or constant name to its value."""
        if name in self.variables:
            return self.variables[name]
        elif name in self.const:
            return self.const[name]
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
            case ast.Compare():
                left = self._eval_ast(node.left)
                right = self._eval_ast(node.comparators[0])
                operator_type = type(node.ops[0])
                return operator_type(left, right)  # Assuming operator_type can be called directly
            case _:
                raise ValueError("Nodo non supportato nel AST.")



stacker = Stack()
stacker.load_code('code.maft')
stacker.interpreta()