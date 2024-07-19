class SourceInfo:

    class PYXPath:

        suffixes = '.pyx', '.c'

        def __init__(self, module, path):
            self.module = module
            self.path = path

        def buildrequires(self):
            if self.path.endswith('.pyx'):
                yield 'Cython<3'

        def make_ext(self):
            g = {}
            with open(self.path + 'bld') as f: # Assume project root.
                exec(f.read(), g)
            return g['make_ext'](self.module, self.path)

    def __init__(self, rootdir):
        import os, setuptools, subprocess
        self.packages = setuptools.find_packages(rootdir)
        extpaths = {}
        def addextpaths(dirpath, moduleprefix):
            names = sorted(os.listdir(os.path.join(rootdir, dirpath)))
            for suffix in self.PYXPath.suffixes:
                for name in names:
                    if name.endswith(suffix):
                        module = "%s%s" % (moduleprefix, name[:-len(suffix)])
                        if module not in extpaths:
                            extpaths[module] = self.PYXPath(module, os.path.join(dirpath, name))
        addextpaths('.', '')
        for package in self.packages:
            addextpaths(package.replace('.', os.sep), "%s." % package)
        extpaths = extpaths.values()
        if extpaths and os.path.isdir(os.path.join(rootdir, '.git')): # We could be an unpacked sdist.
            check_ignore = subprocess.Popen(['git', 'check-ignore'] + [p.path for p in extpaths], cwd = rootdir, stdout = subprocess.PIPE)
            ignoredpaths = set(check_ignore.communicate()[0].decode().splitlines())
            assert check_ignore.wait() in [0, 1]
            self.extpaths = [path for path in extpaths if path.path not in ignoredpaths]
        else:
            self.extpaths = extpaths
