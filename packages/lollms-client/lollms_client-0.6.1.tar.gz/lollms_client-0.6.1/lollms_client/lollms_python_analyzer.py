import ast
import argparse
from pathlib import Path
from typing import List, Dict, Union, Optional, Any

class MethodInfo:
    def __init__(self, node: ast.FunctionDef):
        self.name = node.name
        self.args = self._parse_args(node)
        self.returns = self._get_type_annotation(node.returns)

    def _parse_args(self, node: ast.FunctionDef) -> List[str]:
        args = []
        for i, arg in enumerate(node.args.args):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {self._get_type_annotation(arg.annotation)}"
            
            if i >= len(node.args.args) - len(node.args.defaults):
                default_value = node.args.defaults[i - (len(node.args.args) - len(node.args.defaults))]
                arg_str += f" = {ast.unparse(default_value)}"
            
            args.append(arg_str)
        return args

    def _get_type_annotation(self, annotation: Optional[ast.AST]) -> str:
        if annotation is None:
            return "Any"
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_type_annotation(annotation.value)}[{self._get_type_annotation(annotation.slice)}]"
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_type_annotation(annotation.value)}.{annotation.attr}"
        else:
            return ast.unparse(annotation)

    def __str__(self) -> str:
        return f"def {self.name}({', '.join(self.args)}) -> {self.returns}"

class ClassInfo:
    def __init__(self, node: ast.ClassDef):
        self.name = node.name
        self.methods = self._parse_methods(node)

    def _parse_methods(self, node: ast.ClassDef) -> List[MethodInfo]:
        return [MethodInfo(child) for child in node.body if isinstance(child, ast.FunctionDef)]

    def __str__(self) -> str:
        return f"class {self.name}:\n" + "\n".join(f"    {method}" for method in self.methods)

class ClassAnalyzer:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.classes: List[ClassInfo] = []

    def analyze(self) -> None:
        tree = self._parse_file()
        self.classes = self._analyze_classes(tree)

    def _parse_file(self) -> ast.AST:
        with self.file_path.open('r') as file:
            content = file.read()
        return ast.parse(content)

    def _analyze_classes(self, tree: ast.AST) -> List[ClassInfo]:
        return [ClassInfo(node) for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def generate_markdown(self) -> str:
        markdown = f"# Class Information for {self.file_path.name}\n\n"
        markdown += f"File: `{self.file_path}`\n\n"
        markdown += "## Classes\n\n"
        
        for class_info in self.classes:
            markdown += f"### {class_info.name}\n\n"
            markdown += "```python\n"
            markdown += str(class_info) + "\n"
            markdown += "```\n\n"
        
        return markdown

    def save_markdown(self, output_path: Optional[Path] = None) -> None:
        if output_path is None:
            output_path = self.file_path.with_name(f"{self.file_path.stem}_classes.md")
        
        markdown = self.generate_markdown()
        output_path.write_text(markdown)
        print(f"Markdown file generated: {output_path}")

def main(file_path: Path) -> None:
    analyzer = ClassAnalyzer(file_path)
    analyzer.analyze()
    analyzer.save_markdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Python file and extract class information.")
    parser.add_argument("file", nargs="?", default="example.py", type=Path,
                        help="Path to the Python file to analyze (default: example.py)")
    args = parser.parse_args()
    
    file_path = args.file
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        exit(1)
    
    main(file_path)