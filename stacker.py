import operator
import ast
from typing import Any, Dict, List
import math as mt

class Stack:
    def __init__(self, lunghezza: int) -> None:
        self.lunghezza = lunghezza
        self.stack: List[str] = []
        self.variables: Dict[str, Any] = {}
        self.const: Dict[str, Any] = {}
        self.functions: Dict[str, List[str]] = {}  # Store functions
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        self.p = 0

    def carica_codice(self, file_codice: str) -> None:
        try:
            with open(file_codice, 'r') as f:
                self.stack = [line.strip() for line in f if line.strip()]
            if len(self.stack) > self.lunghezza:
                raise ValueError(f"Errore: La lunghezza della pila supera il limite ({self.lunghezza}).")
        except FileNotFoundError:
            raise FileNotFoundError(f"Errore: Il file '{file_codice}' non esiste.")

    def interpreta(self) -> None:
        while self.p < len(self.stack):
            token = self.stack[self.p]
            self.p += 1

            if token.startswith('se '):
                self._handle_if(token)
            
            elif 'radquad' in token:
                self._handle_sqrt(token)
            elif '=' in token:
                var_name, expression = map(str.strip, token.split('=', 1))
                value = self._safe_eval(expression)
                if var_name.startswith('const_'):
                    if var_name in self.const:
                        print(f"Errore: La costante '{var_name}' non può essere modificata.")
                    else:
                        self.const[var_name] = value
                else:
                    self.variables[var_name] = value

            elif token.startswith('stampa'):
                self._handle_print(token.replace('stampa', '').strip())

            elif token.startswith('aggiungi'):
                self._handle_generic_operation(token)

            elif token.startswith('moltiplica'):
                self._handle_operation(token, operator.mul)

            elif token.startswith('somma'):
                self._handle_operation(token, sum)

            elif token.startswith('def '):
                self._define_function(token)

            elif token in self.functions:
                self._execute_function(token)



            elif token == 'altrimenti':
                self._handle_else()
            
            elif token == 'end':
                continue

            elif token == 'debug':
                print("=== DEBUG INFO ===")
                print(f"Stack: {self.stack}")
                print(f"Variables: {self.variables}")
                print(f"Constants: {self.const}")
                print(f"Functions: {self.functions}")
                print("==================")

            elif token in {'aspetta', 'pause'}:
                input("Premi un tasto per continuare...")

            elif 'cancella' in token:
                variable_to_cancel = token.replace('cancella', '').strip()
                if variable_to_cancel in self.variables:
                    del self.variables[variable_to_cancel]
                else:
                    print(f"Errore: La variabile '{variable_to_cancel}' non è presente.")

            elif '#' in token:
                continue

            else:
                print(f"Errore: '{token}' non è un'espressione valida.")

    def _handle_print(self, item: str) -> None:
        if item in self.variables:
            print(self.variables[item])
        elif item in self.const:
            print(self.const[item])
        else:
            print(item)

    def _handle_operation(self, token: str, op: Any) -> None:
        parts = token.split(',')
        var_name = parts[0].split()[-1]  # Extract var_name from the first token part
        operands = [self._resolve_name(part.strip()) for part in parts[1:]]

        if op == sum:
            result = sum(operands)
        else:  # Assume it's a binary operation like multiplication
            result = operands[0]
            for operand in operands[1:]:
                result = op(result, operand)

        self.variables[var_name] = result
        print(f"{var_name} = {result}")
    
    def _handle_sqrt(self, token: str) -> None:
        parts = token.split(',')
        var_name = parts[0].split()[-1]  # Extract var_name from the first token part
        self.variables[var_name] = mt.sqrt(self._resolve_name(parts[1].strip()))
    def _handle_generic_operation(self, token: str) -> None:
        # Token example: 'aggiungi somma c, a, b'
        parts = token.split()  # Split by spaces
        command = parts[1]     # 'somma' is the operation
        var_name = parts[2].rstrip(',')  # Variable to store the result, remove trailing commas

        # Extract operands from the rest of the parts, and ensure they are properly trimmed
        operands = [self._resolve_name(part.strip().rstrip(',')) for part in parts[3:]]  

        if command == 'somma':  # Summing up all operands
            result = sum(operands)

        
        else:
            raise ValueError(f"Operazione '{command}' non riconosciuta.")

        self.variables[var_name] = result
        print(f"{var_name} = {result}")


    def _define_function(self, token: str) -> None:
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
        func_code = self.functions[func_name]
        original_stack = self.stack.copy()
        original_p = self.p

        self.stack = func_code
        self.p = 0
        self.interpreta()

        self.stack = original_stack
        self.p = original_p

    def _handle_if(self, token: str) -> None:
        condition = token.split('se ')[1].split(' allora')[0].strip()
        if self._safe_eval(condition):
            return  # Continue execution if true
        else:
            # Skip lines until 'else' or 'end if'
            while self.p < len(self.stack) and not self.stack[self.p].startswith('altrimenti') and not self.stack[self.p].startswith('end'):
                self.p += 1

    def _handle_else(self) -> None:
        # Skip until 'end if'
        while self.p < len(self.stack) and not self.stack[self.p].startswith('end'):
            self.p += 1

    def _resolve_name(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        elif name in self.const:
            return self.const[name]
        else:
            return float(name)  # Assume it's a number if not found

    def _safe_eval(self, expression: str) -> Any:
        try:
            expr_ast = ast.parse(expression, mode='eval').body
            return self._eval_ast(expr_ast)
        except Exception as e:
            raise ValueError(f"Errore: L'espressione '{expression}' non è valida. ({e})")

    def _eval_ast(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return self._resolve_name(node.id)
        elif isinstance(node, ast.BinOp):
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            operator_type = type(node.op)
            if operator_type in self.operators:
                return self.operators[operator_type](left, right)
            else:
                raise ValueError(f"Operatore '{operator_type}' non supportato.")
        elif isinstance(node, ast.Compare):  # Handle comparisons
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.comparators[0])  # Assumes simple comparison
            operator_type = type(node.ops[0])
            if operator_type == ast.Gt:
                return left > right
            elif operator_type == ast.Lt:
                return left < right
            elif operator_type == ast.GtE:
                return left >= right
            elif operator_type == ast.LtE:
                return left <= right
            elif operator_type == ast.Eq:
                return left == right
            elif operator_type == ast.NotEq:
                return left != right
            else:
                raise ValueError(f"Operatore di confronto '{operator_type}' non supportato.")
        else:
            raise ValueError(f"Tipo di nodo AST '{type(node)}' non supportato.")


# Example usage
stack = Stack(25)
stack.carica_codice('test.mafati')
stack.interpreta()
