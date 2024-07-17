# metrics-logger

[![Downloads](https://static.pepy.tech/personalized-badge/sailing-log?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/sailing-log)
[![License: GPL v3](https://img.shields.io/badge/License-GPL_v3+-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%20-blue)
[![Documentation Status](https://readthedocs.org/projects/sailing-log/badge/?version=latest)](https://sailing-log.readthedocs.io/en/latest/?badge=latest)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![PyPI - Version](https://img.shields.io/pypi/v/sailing-log.svg)](https://pypi.org/project/sailing-log)


A small python logging configuration used in deep learning and reinforcement learning, or other mission critical setups. 

I tend to use it for APIs, too. It is up to you, however, I found it easiser to manage one configuration that works decoupled from all applications that use it. 


# Minimal Example

It is really simple to use 

```python
from sailing_log import MetricsLogger

log_dir = "path_to_dir"
logger = MetricsLogger(log_dir)
```