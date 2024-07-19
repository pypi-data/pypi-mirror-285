def lazy(clazz, init, *initbefore):
    from threading import Lock
    initlock = Lock()
    init = [init]
    def overridefactory(name):
        orig = getattr(clazz, name)
        def override(*args, **kwargs):
            with initlock:
                if init:
                    init[0](obj)
                    del init[:]
            return orig(*args, **kwargs)
        return override
    Lazy = type('Lazy', (clazz, object), {name: overridefactory(name) for name in initbefore})
    obj = Lazy()
    return obj

# FIXME: The idea was to defer anything Cython/numpy to pyximport time, but this doesn't achieve that.
def cythonize(extensions):
    def init(ext_modules):
        ordinary = []
        cythonizable = []
        for e in extensions:
            (cythonizable if any(s.endswith('.pyx') for s in e.sources) else ordinary).append(e)
        if cythonizable:
            from Cython.Build import cythonize
            ordinary += cythonize(cythonizable)
        ext_modules[:] = ordinary
    return lazy(list, init, '__getitem__', '__iter__', '__len__')
