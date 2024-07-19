import acq
import setuptools

# setup.cfg is a new-ish standard, so we need to check this for now
if int(setuptools.__version__.split('.', 1)[0]) < 38:
    raise EnvironmentError(
        'Please upgrade setuptools. This package uses setup.cfg, which requires '
        'setuptools version 38 or higher. If you use pip, for instance, you can '
        'upgrade easily with ` pip install -U setuptools `'
    )

setuptools.setup(
    description=acq.short_description(),
    long_description=acq.long_description(),
    name=acq.name(),
    version=acq.version_string(),
)
