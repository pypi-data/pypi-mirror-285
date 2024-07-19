# acq


### What it is?!

This library provides a simple and convenient way to
automatically search packages for modules and import them
without needing project files to manually import them, which
allows for automatic configuration and other useful mechanics
within projects.


### Installation

You can install this module via pip or your preferred dependency management
tool(s):

    pip install acq


### Usage

In standard Python applications, the tool can be used in the following ways:

```python
from acq import discover

# Import modules 'a' and 'b' from packages "example1" and "example2"
discover('a', 'b', package_names=['example1', 'example2'])
```

In Django applications, you can automatically import from INSTALLED_APPS via:

```python
from acq.django import discover

# Import views.py for all packages in the INSTALLED_APPS setting
discover('views')

# Import views.py for all packages in an AUTOSEARCH_MODULES setting
discover('views', packages_setting_name='AUTOSEARCH_MODULES')

```


### Contributing

Thank you for considering use of this project, and please feel
free to provide any suggestions in pull requests if you have
any!
