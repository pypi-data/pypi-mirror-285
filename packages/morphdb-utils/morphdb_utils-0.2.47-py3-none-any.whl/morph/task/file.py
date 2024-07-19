import os
import shutil
import sys

from morph.cli.flags import Flags
from morph.task.base import BaseTask


class CreateFileTask(BaseTask):
    def __init__(self, args: Flags):
        super().__init__(args)
        self.args = args

        self.filename = args.FILENAME
        self.content = args.CONTENT

    def run(self):
        if os.path.exists(self.filename):
            print(f"File {self.filename} already exists.", file=sys.stderr)
            sys.exit(1)

        with open(self.filename, "w") as f:
            f.write("" if self.content is None else self.content)


class UpdateFileTask(BaseTask):
    def __init__(self, args: Flags):
        super().__init__(args)
        self.args = args

        self.filename = args.FILENAME
        self.content = args.CONTENT

    def run(self):
        if not os.path.exists(self.filename):
            print(f"File {self.filename} does not exist.", file=sys.stderr)
            sys.exit(1)

        with open(self.filename, "w") as f:
            f.write(self.content)


class DeleteFileTask(BaseTask):
    def __init__(self, args: Flags):
        super().__init__(args)
        self.args = args

        self.filename = args.FILENAME

    def run(self):
        if not os.path.exists(self.filename):
            print(f"File {self.filename} does not exist.", file=sys.stderr)
            sys.exit(1)

        if os.path.exists(self.filename):
            if os.path.isdir(self.filename):
                shutil.rmtree(self.filename)
            else:
                os.remove(self.filename)
