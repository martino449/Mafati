import operator
import ast
from typing import Any, Dict, List

class Stack:
    def __init__(self, lunghezza: int) -> None:
        self.lunghezza = lunghezza
        self.stack: List[str] = []
        self.variables: Dict[str, Any] = {}
        self.const: Dict[str, Any] = {}
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

            if '=' in token:
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

            elif token.startswith('moltiplica'):
                self._handle_operation(token, operator.mul)

            elif token.startswith('somma'):
                self._handle_operation(token, sum)

            elif token == 'debug':
                print("=== DEBUG INFO ===")
                print(f"Stack: {self.stack}")
                print(f"Variables: {self.variables}")
                print(f"Constants: {self.const}")
                print("==================")

            elif token in {'aspetta', 'pause'}:
                input("Premi un tasto per continuare...")


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
            result = operands[0] * operands[1]
        
        self.variables[var_name] = result
        print(f"{var_name} = {result}")

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
        else:
            raise ValueError(f"Tipo di nodo AST '{type(node)}' non supportato.")

# Example usage
stack = Stack(256)
stack.carica_codice('test.mafati')
stack.interpreta()
