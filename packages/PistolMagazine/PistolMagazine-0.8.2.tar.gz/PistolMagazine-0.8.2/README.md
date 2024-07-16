# PistolMagazine 🎯
[![PyPI - Version](https://img.shields.io/pypi/v/PistolMagazine)](https://pypi.org/project/PistolMagazine/)


PistolMagazine is a data mocking tool designed to help you generate realistic data for testing and development purposes.

## Features ✨

- **Flexible Data Types** 📊: Supports various data types including integers, floats, strings, timestamps, and more.
- **Custom Providers** 🛠️: Easily create and integrate custom data providers.
  - **Built-in Providers** 🏗️: Provides several built-in providers for common use cases.
- **Random Data Generation** 🎲: Generates realistic random data for testing.
- **Hook Functions** 🪝: Support for hook functions, allowing users to execute custom operations before or after generating mock data. These hooks can be utilized for:
  - **Logging**: Record relevant operations or data before or after data generation.
  - **Starting External Services**: Initiate external services or resources before generating data.
  - **Dynamic Data Modification**: Perform data validation or sanitization before generating mock data.
  - **Sending Data to Message Queues**: Transmit generated data to message queues for integration with other systems.
  - **Data Profiling**: Perform statistical analysis or monitoring post data generation.
- **Data Export** 📤: Supports exporting to CSV, JSON, XML, and MySQL. Can be used in conjunction with hook functions.

## Installation 📦

Install PistolMagazine using pip:

```bash
pip install PistolMagazine
```

## Quick Start 🚀

Here’s a quick example to get you started:


You can use the `pistol-gen` command to interactively select a sample code template and specify the path for the generated code within your project directory.

Run the following command:

```bash
pistol-gen
```

The tool will then generate the file with the chosen template at the specified location.

```python
from random import choice
from pistol_magazine import *


# Create a custom provider
@provider
class MyProvider:
    def my_provider(self):
        return choice(["ACTIVE", "INACTIVE"])


"""
Define hook functions
pre_generate: Executes operations before generating all data. Suitable for tasks like logging or starting external services.
after_generate: Executes operations after generating each data entry but before final processing. Suitable for tasks like data validation or conditional modifications.
final_generate: Executes operations after generating and processing all data entries. Suitable for final data processing, sending data to message queues, or performing statistical analysis.
"""
@hook('pre_generate', order=1, hook_set='SET1')
def pre_generate_first_hook():
    print("Start Mocking User Data")


@hook('pre_generate', order=2, hook_set='SET1')
def pre_generate_second_hook():
    """
    Perform some preprocessing operations, such as starting external services.
    """

@hook('after_generate', order=1, hook_set="SET1")
def after_generate_first_hook(data):
    data['customized_param'] = 'ACTIVE' if data['int_param'] >= 18 else 'INACTIVE'
    return data


@hook('final_generate', order=1, hook_set="SET1")
def final_generate_second_hook(data):
    """
    Suppose there is a function send_to_message_queue(data) to send data to the message queue
    Or use built-in data exporters to export data, like the code below⬇️.
    """
    json_exporter = JSONExporter()  # Also support csv, db, xml export
    json_exporter.export(data, 'output.json')


class Temp(DataMocker):
    timestamp_param: Timestamp = Timestamp(Timestamp.D_TIMEE10, days=2)
    str_param1: Str = Str(data_type="name")
    str_param2: Str = Str(data_type="email")
    int_param: Int = Int(byte_nums=6, unsigned=True)
    customized_param: ProviderField = ProviderField(MyProvider().my_provider)
    bool_param: Bool = Bool()
    dict_param: Dict = Dict(
        {
            "a": Float(left=2, right=4, unsigned=True),
            "b": Timestamp(Timestamp.D_TIMEE10, days=2)
        }
    )
    list_param: List = List(
        [
            Datetime(Datetime.D_FORMAT_YMD_T, weeks=2),
            StrInt(byte_nums=6, unsigned=True)
        ]
    )
    built_in_provider_param1: ProviderField = ProviderField(
        CyclicParameterProvider(parameter_list=["x", "y", "z"]).gen
    )
    built_in_provider_param2: ProviderField = ProviderField(
        RandomFloatInRangeProvider(start=0.00, end=4.00, precision=4).gen
    )
    built_in_provider_param3: ProviderField = ProviderField(
        IncrementalValueProvider(start=0, step=-2).gen
    )
    built_in_provider_param4: ProviderField = ProviderField(
        RegexProvider(pattern=r"\d{3}-[a-z]{2}").gen
    )
    fixed_value_str = "fixed_value"
    fixed_value_dict = {"key": "value"}

    def gen_data(self):
        return self.mock(
            num_entries=3,
            as_list=False,
            to_json=True,
            hook_set='SET1',
            key_generator=lambda: RegexProvider(pattern=r"^[A-Z]{4}-\d{3}$").gen()
        )


if __name__ == '__main__':
    print(Temp().gen_data())

```

If you want more detailed instructions, you can refer to the examples and documentation in the [wiki](https://github.com/miyuki-shirogane/PistolMagazine/wiki).


## Help PistolMagazine

If you find PistolMagazine useful, please ⭐️ Star it at GitHub

[Feature discussions](https://github.com/miyuki-shirogane/PistolMagazine/discussions) and [bug reports](https://github.com/miyuki-shirogane/PistolMagazine/issues) are also welcome!

**Happy Mocking!** 🎉🎉🎉