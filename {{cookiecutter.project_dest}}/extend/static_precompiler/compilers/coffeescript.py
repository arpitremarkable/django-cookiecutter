import os

# third party
from static_precompiler import exceptions, utils
from static_precompiler.compilers import CoffeeScript as BaseCoffeeScript


__all__ = (
    "CoffeeScript",
)


class CoffeeScript(BaseCoffeeScript):
    def __init__(self, transpile=False, header=True, *args, **kwargs):
        self.transpile = transpile
        self.header = header
        return super().__init__(*args, **kwargs)

    def compile_file(self, source_path):
        full_output_path = self.get_full_output_path(source_path)
        args = [
            self.executable,
            "-c",
        ]
        if self.is_sourcemap_enabled:
            args.append("-m")
        if self.transpile:
            args.append("-t")
        if not self.header:
            args.append("--no-header")
        args.extend([
            "-o", os.path.dirname(full_output_path),
            self.get_full_source_path(source_path),
        ])
        return_code, out, errors = utils.run_command(args)

        if return_code:
            raise exceptions.StaticCompilationError(errors)

        if self.is_sourcemap_enabled:
            utils.fix_sourcemap(os.path.splitext(full_output_path)[0] + ".map", source_path, full_output_path)

        return self.get_output_path(source_path)

    def compile_source(self, source):
        args = [
            self.executable,
            "-c",
            "-s",
            "-p",
        ]
        if self.transpile:
            args.append("-t")
        if not self.header:
            args.append("--no-header")
        return_code, out, errors = utils.run_command(args, source)
        if return_code:
            raise exceptions.StaticCompilationError(errors)

        return out
