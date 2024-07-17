import typer
from typing import Annotated, Optional
import os
import json
from . import *
from .helper import Solutions, extract_variables
from .utils import print_iterable

LEETPIE_FILE = 'leetpie.json'
PRACTICE_FILE = 'practice.py'

app = typer.Typer()
sol = Solutions('problems.py')


def load_leetpie_file():
    if os.path.exists(LEETPIE_FILE):
        with open(LEETPIE_FILE, encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(LEETPIE_FILE, 'w', encoding='utf-8') as f:
            data = {'todo': {}, 'variables': []}
            json.dump(data, f, indent=2)
            return data


def generate_markdown_file(filename, lst):
    BLANK_LINES = '\n\n'
    with open(filename, 'w', encoding='utf-8') as f:
        for i in lst:
            sol_ = sol.get_solution(i)
            idx1 = sol_.index(')\n')
            idx2 = sol_.index('class ')
            f.write(f'#{sol_[22:idx1+1]}{BLANK_LINES}')
            f.write(f'```python\n{sol_[idx2:-21]}```{BLANK_LINES}')


def generate_practice_file(lst, solution):
    with open(PRACTICE_FILE, 'w', encoding='utf-8') as f:
        BLANK_LINES = '\n\n\n'
        f.write('from leetpie import *' + BLANK_LINES)
        for i in lst:
            if solution:
                f.write(sol.get_solution(i) + BLANK_LINES)
            else:
                f.write(sol.get_problem(i) + BLANK_LINES)


@app.command()
def review(
    tag: Annotated[Optional[str], typer.Argument()] = None,
    solution: Annotated[bool, typer.Option('--solution', '-s', help='show solution')] = False,
    markdown: Annotated[bool, typer.Option('--markdown', '-m', help='generate markdown')] = False
):
    todo = load_leetpie_file()['todo']

    if tag is None:
        print_iterable(todo.keys(), n=4)
        return

    if markdown:
        if tag in todo:
            generate_markdown_file(f'{tag}.md', todo[tag])
        else:
            print(f'Tag "{tag}" doesn\'t exist.')
        return

    if tag in todo:
        generate_practice_file(todo[tag], solution)
    else:
        print(f'Tag "{tag}" doesn\'t exist.')


@app.command()
def test(problem_id: int):
    if (code := sol.get_solution(problem_id)) is None:
        print(f'Solution "{problem_id}" doesn\'t exist.')
    else:
        code = f'from leetpie import *\n{code}\nS_{problem_id}().test()'
        exec(code)


@app.command()
def check():
    variables = set(load_leetpie_file()['variables'])

    with open(sol.file, encoding='utf-8') as f:
        code = f.read()

    print_iterable(sorted(extract_variables(code) - variables), n=4)


if __name__ == '__main__':

    app()
