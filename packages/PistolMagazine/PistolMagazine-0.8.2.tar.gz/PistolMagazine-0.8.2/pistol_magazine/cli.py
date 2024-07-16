import click
import os


TEMPLATES = {
    "Simple Template": '''
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

''',
    "Postman Template": '''
from pistol_magazine import *


@hook('final_generate', order=1, hook_set="SET1")
def final_generate_second_hook(data):
    json_exporter = JSONExporter()
    json_exporter.export(data, 'output.json')


class RequestBody(DataMocker):
    create_time: Timestamp = Timestamp(Timestamp.D_TIMEE10, days=2)
    user_name: Str = Str(data_type="name")
    user_email: Str = Str(data_type="email")
    user_age: Int = Int(byte_nums=6, unsigned=True)

    def gen_body(self):
        return self.mock(single_item=True, to_json=True)


@provider
class CreateUserItemProvider:
    def generate_user_item(self):
        return {
            "name": "Create User",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": RequestBody().gen_body()
                },
                "url": "https://api.example.com/users"
            }
        }

    def gen_item_list(self, num_items: int = 1):
        return [self.generate_user_item() for _ in range(num_items)]


class PostmanRESTfulAPITemplate(DataMocker):
    info = {
        "name": "Simple Collection",
        "description": "This is a sample Postman collection"
    }
    item: ProviderField = ProviderField(CreateUserItemProvider().gen_item_list, num_items=2)

    def get_template(self):
        return self.mock(single_item=True, to_json=True, hook_set="SET1")


if __name__ == '__main__':
    print(PostmanRESTfulAPITemplate().get_template())

    '''
}


@click.command()
@click.option('--template', type=click.Choice(['a', 'b']),
              prompt='Select a template to generate (a: Simple Template, b: Postman Template):',
              help="Select a template to generate")
@click.option('--output', type=click.Path(), prompt=True, help="Output file path")
def generate_template(template, output):

    template_mapping = {'a': 'Simple Template', 'b': 'Postman Template'}
    selected_template = template_mapping[template]

    if not output.endswith('.py'):
        output += '.py'

    output_dir = os.path.dirname(output)
    if output_dir and not os.path.exists(output_dir):
        click.echo(f"Directory {output_dir} not exist. Creating it...")
        os.makedirs(output_dir)

    template_content = TEMPLATES.get(selected_template)
    if not template_content:
        click.echo(f"Template '{selected_template}' not found.")
        return

    with open(output, 'w') as f:
        f.write(template_content)

    click.echo(f"Template '{selected_template}' has been generated to {os.path.abspath(output)}")


if __name__ == '__main__':
    generate_template()
