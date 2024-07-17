**thoughtful** is a collection of open-source libraries and tools for Robot Process
Automation (RPA) development. The goal of this project is to provide a set of
for supervising bot execution, and enabling these bots to do more.

[![PyPi version](https://badgen.net/pypi/v/thoughtful/)](https://pypi.org/project/thoughtful/)
![Main Branch Tests](https://github.com/Thoughtful-Automation/supervisor/actions/workflows/main-push.yml/badge.svg?branch=main)
[![Supported Versions](https://img.shields.io/pypi/pyversions/thoughtful.svg)](https://pypi.org/project/thoughtful)
[![Downloads](https://pepy.tech/badge/thoughtful/month)](https://pepy.tech/project/thoughtful)

[//]: # ([![GitHub release]&#40;https://img.shields.io/github/release/Thoughtful-Automation/supervisor.svg&#41;]&#40;https://GitHub.com/Naereen/StrapDown.js/releases/&#41;)


This project is:
* Open-source: [GitHub][url:gh]
* Owned by [thoughtful][url:ta]
* Licensed under the [Apache License 2.0][url:al]

Links:
* [Homepage][url:gh]
* [Documentation][url:readthedocs]
* [PyPI][url:pypi]

**thoughtful** is available on [PyPI][url:pypi] and can be installed using pip:

```sh
pip install thoughtful
```

---

**thoughtful** officially supports Python 3.7+.

---

# Libraries

This is a list of the available libraries in this project. API Reference
and User Guide available on [docs][url:readthedocs].

## Supervisor

Supervisor is a Workflow Engine for Digital Workers that constructs
and broadcasts a detailed and structured telemetric log, called the Run Report.

```python
from thoughtful.supervisor import step, step_scope, supervise, set_step_status


# using the step decorator
@step("2")
def step_2(name: str) -> bool:
    print(f'Hello {name}')
    return True  # some condition

def main() -> None:
    # using the step_scope context manager
    with step_scope('1') as step_context:
        try:
            print("Getting credentials")
            # ...
        except Exception as e:
            # set step status using method
            step_context.set_status("warning")

    if not step_2():
        # set step status using function
        set_step_status("2", "fail")

if __name__ == '__main__':
    with supervise():
        main()
```

## Contributing

Contributions to **thoughtful** are welcome!

To get started, see the [contributing guide](CONTRIBUTING.md).

---

  Made with ❤️ by

  [![Thoughtful](https://user-images.githubusercontent.com/1096881/141985289-317c2e72-3c2d-4e6b-800a-0def1a05f599.png)][url:ta]

---

This project is open-source and licensed under the terms of the [Apache License 2.0][url:al].


<!--  Link References -->

[url:ta]: https://www.thoughtful.ai/
[url:gh]: https://github.com/Thoughtful-Automation/supervisor
[url:pypi]: https://pypi.org/project/thoughtful/
[git:issues]: https://github.com/Thoughtful-Automation/supervisor/issues
[url:readthedocs]: https://thoughtful-supervisor.readthedocs-hosted.com/en/latest/
[url:al]: http://www.apache.org/licenses/LICENSE-2.0
