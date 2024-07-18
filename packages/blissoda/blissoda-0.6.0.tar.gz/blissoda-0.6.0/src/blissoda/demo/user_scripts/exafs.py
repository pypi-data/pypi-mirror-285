from blissoda.demo.exafs import exafs_plotter


def exafs_demo(*args, nrepeats=3, **kw):
    for _ in range(nrepeats):
        exafs_plotter.run(*args, **kw)
