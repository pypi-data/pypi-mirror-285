# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rosys',
 'rosys.analysis',
 'rosys.analysis.legacy',
 'rosys.automation',
 'rosys.driving',
 'rosys.geometry',
 'rosys.hardware',
 'rosys.hardware.communication',
 'rosys.helpers',
 'rosys.pathplanning',
 'rosys.pathplanning.demos',
 'rosys.persistence',
 'rosys.system',
 'rosys.testing',
 'rosys.vision',
 'rosys.vision.camera',
 'rosys.vision.mjpeg_camera',
 'rosys.vision.rtsp_camera',
 'rosys.vision.simulated_camera',
 'rosys.vision.usb_camera']

package_data = \
{'': ['*'], 'rosys.analysis': ['assets/*']}

install_requires = \
['aiocache>=0.11.1,<0.12.0',
 'aioserial>=1.3.0,<2.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'dataclasses-json>=0.5.7,<0.6.0',
 'esptool>=4.3,<5.0',
 'executing>=1.0.0,<2.0.0',
 'httpx>=0.24.0,<0.25.0',
 'humanize>=4.0.0,<5.0.0',
 'idna>=3.7',
 'ifaddr>=0.2.0,<0.3.0',
 'imgsize>=2.1,<3.0',
 'line-profiler>=4.0.3,<5.0.0',
 'matplotlib>=3.7.2,<4.0.0',
 'more-itertools>=8.10.0,<9.0.0',
 'msgpack>=1.0.3,<2.0.0',
 'networkx>=2.6.2,<3.0.0',
 'nicegui>=1.4.29',
 'numpy>=1.20.1,<2.0.0',
 'objgraph>=3.5.0,<4.0.0',
 'opencv-python>=4.5.5,<5.0.0',
 'pillow>=10.3.0',
 'psutil>=5.9.0,<6.0.0',
 'pyloot>=0.1.0,<0.2.0',
 'pyquaternion>=0.9.9,<0.10.0',
 'pyserial>=3.5,<4.0',
 'pyudev>=0.21.0',
 'retry>=0.9.2,<0.10.0',
 'scipy>=1.7.2,<2.0.0',
 'simplejson>=3.17.2,<4.0.0',
 'suntime>=1.2.5,<2.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'ujson==5.4.0',
 'uvicorn!=0.29.0',
 'uvloop>=0.17.0,<0.18.0',
 'yappi>=1.4,<2.0']

entry_points = \
{'console_scripts': ['install-deps = install_opencv:main'],
 'pytest11': ['pytest-rosys = rosys.testing.fixtures']}

setup_kwargs = {
    'name': 'rosys',
    'version': '0.11.0',
    'description': 'Modular Robot System With Elegant Automation Capabilities',
    'long_description': '# RoSys - The Robot System\n\nRoSys provides an easy-to-use robot system.\nIts purpose is similar to [ROS](https://www.ros.org/).\nBut RoSys is fully based on modern web technologies and focusses on mobile robotics.\n\nThe full documentation is available at [rosys.io](https://rosys.io/).\n\n## Principles\n\n### All Python\n\nPython is great to write business logic.\nComputation-heavy tasks are wrapped in processes, accessed through WebSockets or called via C++ bindings.\nLike you would do in any other Python program.\n\n### Modularity\n\nYou can structure your code as you please.\nRoSys provides its magic without assuming a specific file structure, configuration files or enforced naming.\n\n### Event Loop\n\nThanks to [asyncio](https://docs.python.org/3/library/asyncio.html) you can write your business logic without locks and mutexes.\nThe execution is [parallel but not concurrent](https://realpython.com/python-concurrency/) which makes it easier to read, write and debug.\nIn real-case scenarios this is also much faster than [ROS](https://www.ros.org/).\nIts multiprocessing architecture requires too much inter-process communication.\n\n### Web UI\n\nMost machines need some kind of human interaction.\nRoSys is built from the ground up to make sure your robot can be operated fully off the grid with any web browser.\nThis is done by incorporating [NiceGUI](https://nicegui.io/), a wonderful all-Python UI web framework.\nIt is also possible to proxy the user interface through a gateway for remote operation.\n\n### Simulation\n\nRobot hardware is often slower than your own computer.\nTo rapidly test out new behavior and algorithms, RoSys provides a simulation mode.\nHere, all hardware is mocked and can even be manipulated to test wheel blockages and similar.\n\n### Testing\n\nYou can use [pytest](https://docs.pytest.org/) to write high-level integration tests.\nIt is based on the above-described simulation mode and accelerates the robot\'s time for super fast execution.\n\n## Architecture and Features\n\n### Modules\n\nRoSys modules are just Python modules which encapsulate certain functionality.\nThey can hold their own state, register lifecycle hooks, run methods repeatedly and subscribe to or raise [events](#events).\nModules can depend on other modules which is mostly implemented by passing them into the constructor.\n\n### Lifecycle Hooks and Loops\n\nModules can register functions via `rosys.on_startup` or `rosys.on_shutdown` as well as repeatedly with a given interval with `rosys.on_repeat`.\n\n<!-- prettier-ignore-start -->\n!!! note\n    Note that NiceGUI\'s `app` object also provides methods `app.on_startup` and `app.on_shutdown`, but it is recommended to use RoSys\' counterparts:\n    `rosys.on_startup` ensures the callback is executed _after_ persistent modules have been loaded from storage.\n    If you, e.g., set the `rosys.config.simulation_speed` programmatically via `app.on_startup()` instead of `rosys.on_startup`,\n    the change is overwritten by RoSys\' `persistence.restore()`.\n<!-- prettier-ignore-end -->\n\n### Events\n\nModules can provide events to allow connecting otherwise separated modules of the system.\nFor example, one module might read sensor data and raise an event `NEW_SENSOR_DATA`, without knowing of any consumers.\nAnother module can register on `NEW_SENSOR_DATA` and act accordingly when being called.\n\n### Automations\n\nRoSys provides an `Automator` module for running "automations".\nAutomations are coroutines that can not only be started and stopped, but also paused and resumed, e.g. using `AutomationControls`.\nHave a look at our [Click-and-drive](examples/click-and-drive.md) example.\n\n### Persistence\n\nModules can register backup and restore methods to read and write their state to disk.\n\n### Time\n\nRoSys uses its own time which is accessible through `rosys.time`.\nThis way the time can advance much faster in simulation and tests if no CPU-intensive operation is performed.\nTo delay the execution of a coroutine, you should invoke `await rosys.sleep(seconds: float)`.\nThis creates a delay until the provided amount of _RoSys time_ has elapsed.\n\n### Threading and Multiprocessing\n\nRoSys makes extensive use of [async/await](#async) to achieve parallelism without threading or multiprocessing.\nBut not every piece of code you want to integrate is offering an asyncio interface.\nTherefore RoSys provides two handy wrappers:\n\nIO-bound:\nIf you need to read from an external device or use a non-async HTTP library like [requests](https://requests.readthedocs.io/),\nyou should wrap the code in a function and await it with `await rosys.run.io_bound(...)`.\n\nCPU-bound:\nIf you need to do some heavy computation and want to spawn another process,\nyou should wrap the code in a function and await it with `await rosys.run.cpu_bound(...)`.\n\n### Safety\n\nPython (and Linux) is fast enough for most high-level logic, but has no realtime guarantees.\nSafety-relevant behavior should therefore be put on a suitable microcontroller.\nIt governs the hardware of the robot and must be able to perform safety actions like triggering emergency hold etc.\n\nWe suggest to use an industrial PC with an integrated controller like the [Zauberzeug Robot Brain](https://www.zauberzeug.com/products/robot-brain).\nIt provides a Linux system to run RoSys, offers AI acceleration via NVidia Jetson, two integrated [ESP32](https://www.espressif.com/en/products/socs/esp32) microcontrollers and six I/O sockets with up to 24 GPIOs for digital I/Os, CAN, RS485, SPI, I2C, etc.\nIt also has two hardware ENABLE switches and one which is controllable via software.\n\nTo have flexible configuration for the microcontroller we created another open source project called [Lizard](https://lizard.dev/).\nIt is a domain-specific language interpreted by the microcontroller which enables you to write reactive hardware behavior without recompiling and flashing.\n\n### User Interface\n\nRoSys builds upon the open source project [NiceGUI](https://nicegui.io/) and offers many robot-related UI elements.\nNiceGUI is a high-level UI framework for the web.\nThis means you can write all UI code in Python and the state is automatically reflected in the browser through WebSockets.\nSee any of our [examples](examples/steering.md).\n\nRoSys can also be used with other user interfaces or interaction models if required, for example a completely app-based control through Bluetooth Low Energy with Flutter.\n\n### Notifications\n\nModules can notify the user through `rosys.notify(\'message to the user\')`.\nWhen using NiceGUI, the notifications will show as snackbar messages.\nThe history of notifications is stored in the list `rosys.notifications`.\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/zauberzeug/rosys',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
