"""Run all Python notebook cells headlessly and record execution evidence."""
import ast
import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')


def main():
    root = Path(__file__).resolve().parent
    required = ['storm.xlsx', 'storm_summary.sas7bdat', 'storm_2017.sas7bdat', 'storm_detail.sas7bdat']
    missing = [name for name in required if not (root/'data/raw'/name).is_file()]
    if missing:
        raise FileNotFoundError('Missing data/raw inputs: ' + ', '.join(missing))
    notebook = root/'notebooks/python-storm-data-analysis.ipynb'
    document = json.loads(notebook.read_text())
    cells = [c for c in document['cells'] if c['cell_type']=='code' and ''.join(c['source']).strip()]
    for cell in cells:
        cell['execution_count'] = None
        cell['outputs'] = []
    code_hash = hashlib.sha256('\n'.join(''.join(c['source']) for c in cells).encode()).hexdigest()
    report = {
        'status':'running', 'executed_code_cells':0,
        'execution_mode':'Sequential Python cell execution with Agg and display shim; no Jupyter kernel',
        'python':platform.python_version(),
        'packages':{name:importlib.metadata.version(name) for name in ['pandas','numpy','matplotlib','openpyxl']},
        'started_utc':datetime.now(timezone.utc).isoformat(), 'code_sha256':code_hash,
        'input_sha256':{name:hashlib.sha256((root/'data/raw'/name).read_bytes()).hexdigest() for name in required}
    }
    output = root/'output/tables/notebook_execution.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report,indent=2))
    namespace = {'__name__':'__main__', 'display':lambda *args:print(*(str(a) for a in args),sep='\n')}
    previous = Path.cwd()
    started = time.monotonic()
    try:
        os.chdir(notebook.parent)
        for number, cell in enumerate(cells,1):
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                tree = ast.parse(''.join(cell['source']))
                tail = tree.body.pop() if tree.body and isinstance(tree.body[-1],ast.Expr) else None
                exec(compile(tree,f'notebook-cell-{number}','exec'),namespace)
                if tail:
                    value = eval(compile(ast.Expression(tail.value),f'notebook-cell-{number}','eval'),namespace)
                    if value is not None: print(value)
            cell['execution_count'] = number
            cell['outputs'] = [{'output_type':'stream','name':'stdout','text':capture.getvalue().splitlines(keepends=True)}]
            report['executed_code_cells'] = number
        report['status'] = 'passed'
    except Exception as error:
        report.update(status='failed',failed_cell=report['executed_code_cells']+1,error=f'{type(error).__name__}: {error}')
        raise
    finally:
        os.chdir(previous)
        report['elapsed_seconds'] = round(time.monotonic()-started,2)
        output.write_text(json.dumps(report,indent=2))
        notebook.write_text(json.dumps(document,indent=1))
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
