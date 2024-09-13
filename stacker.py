import operator
import ast

class Stack:
    def __init__(self, lunghezza):
        self.lunghezza = lunghezza
        self.stack = []
        self.variables = {}  # Dizionario per memorizzare le variabili
        self.const = {}      # Dizionario per memorizzare le costanti
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

    def carica_codice(self, file_codice):
        with open(file_codice, 'r') as f:
            for line in f:
                self.stack.append(line.strip())  # Rimuove i caratteri di fine riga
            for buffer in range(self.lunghezza - len(self.stack)):
                self.stack.append('')

            if len(self.stack) > self.lunghezza:
                print("Errore: La lunghezza della pila è troppo grande.")
                raise ValueError("Errore: La lunghezza della pila è troppo grande.")

            self.p = 0

    def info(self):
        info = {'lunghezza': self.lunghezza, 'stack': self.stack, 'variables': self.variables, 'const': self.const}
        print(info)
        return info

    def interpreta(self):
        while self.p < self.lunghezza:
            self.p_val = self.stack[self.p]
            token = self.p_val
            self.p += 1

            # Gestione dell'assegnazione delle variabili e delle costanti
            if '=' in token:
                var_name, expression = token.split('=')
                var_name = var_name.strip()
                expression = expression.strip()

                if var_name.startswith('const_'):
                    # Se la variabile inizia con 'const_', è una costante
                    if var_name in self.const:
                        print(f"Errore: La costante '{var_name}' non può essere modificata.")
                        continue
                    self.const[var_name] = self.eval_expr(expression)
                else:
                    try:
                        value = self.eval_expr(expression)
                    except Exception as e:
                        print(f"Errore nell'interpretazione dell'espressione: {e}")
                        continue
                    self.variables[var_name] = value

            elif token == '':
                continue

            elif '#' in token:
                continue

            # Stampa di variabili o stringhe
            elif 'stampa' in token:
                parts = token.split(',')
                for part in parts:
                    value_to_print = part.replace('stampa', '').strip()

                    if value_to_print in self.variables:
                        print(self.variables[value_to_print])
                    elif value_to_print in self.const:
                        print(self.const[value_to_print])
                    else:
                        print(value_to_print)

            # Otherwise, it's not a valid expression
            else:
                print(f"Errore: '{token}' non è un'espressione valida.")

    def eval_expr(self, expression):
        """Safely evaluate an arithmetic expression using AST."""
        try:
            # Parse the expression to AST
            expr_ast = ast.parse(expression, mode='eval').body
            return self._eval_ast(expr_ast)
        except Exception as e:
            raise ValueError(f"Errore: L'espressione '{expression}' non è valida. ({e})")

    def _eval_ast(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):  # Updated for Python 3.8+
            return node.value
        elif isinstance(node, ast.Name):  # Variables or constants
            if node.id in self.variables:
                return self.variables[node.id]
            elif node.id in self.const:
                return self.const[node.id]
            else:
                raise ValueError(f"Variabile '{node.id}' non trovata.")
        elif isinstance(node, ast.BinOp):  # Binary operations
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            operator_type = type(node.op)
            if operator_type in self.operators:
                return self.operators[operator_type](left, right)
            else:
                raise ValueError(f"Operatore '{operator_type}' non supportato.")
        else:
            raise ValueError(f"Tipo di nodo AST '{type(node)}' non supportato.")







# MIT License
#
# Copyright (c) 2024 Mario Pisano
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

