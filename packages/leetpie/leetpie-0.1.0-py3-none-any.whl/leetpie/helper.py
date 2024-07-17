import os
import re
import ast


class Solutions:

    DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, file, dir=None):
        if dir is None:
            self.file = os.path.join(self.DIR, file)
        else:
            self.file = os.path.join(dir, file)

    def get_solutions(self) -> list[str]:
        with open(self.file, encoding='utf-8') as f:
            pattern = r'# \d{4}( ----){3}.+?#( ----){4}'
            matches = re.finditer(pattern, f.read(), re.S)
            return [match.group() for match in matches]

    def get_solution(self, id: int) -> str:
        for solution in self.get_solutions():
            if solution.startswith(f'# {id:04}'):
                return solution

    def get_problem(self, id: int) -> str:
        solution = self.get_solution(id)
        match = re.match(r'.+?def solve\(.+?\):', solution, re.S)
        if match is not None:
            return match.group() + f'\n{"pass".rjust(12)}\n\nS_{id}().test()'


def extract_variables(code: str) -> set:
    tree = ast.parse(code)
    res = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            res.add(node.id)

    return res
