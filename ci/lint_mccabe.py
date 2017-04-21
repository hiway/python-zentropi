# coding=utf-8

import ast
import path
import sys

import mccabe

def ignore(p):
    """ Ignore hidden and test files """
    parts = p.splitall()
    if any(x.startswith(".") for x in parts):
        return True
    if 'test' in parts:
        return True
    return False


def collect_sources(ignore_func):
    top_path = path.Path(".")
    for py_path in top_path.walkfiles("*.py"):
        py_path = py_path.normpath()  # get rid of the leading '.'
        if not ignore_func(py_path):
            yield py_path


def process(py_source, max_complexity):
    code = py_source.text()
    tree = compile(code, py_source, "exec", ast.PyCF_ONLY_AST)
    visitor = mccabe.PathGraphingAstVisitor()
    visitor.preorder(tree, visitor)
    for graph in visitor.graphs.values():
        if graph.complexity() > max_complexity:
            text = "{}:{}:{} {} {}"
            return text.format(py_source, graph.lineno, graph.column, graph.entity,
                               graph.complexity())


def main():
    max_complexity = int(sys.argv[1])
    ok = True
    for py_source in collect_sources(ignore_func=ignore):
        error = process(py_source, max_complexity)
        if error:
            ok = False
            print(error)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
