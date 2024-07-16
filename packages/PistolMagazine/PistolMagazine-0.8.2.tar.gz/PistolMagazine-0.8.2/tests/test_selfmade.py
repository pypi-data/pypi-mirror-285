from pprint import pprint
from random import choice, randint
from pistol_magazine import *


def test_model_data_conversion():
    """
    Use it when your mock requirements are not that precise.
    In this case, you cannot use `kwargs` to pass custom arguments such as instances of the `Timestamp` class.
    Only the default rules for keyword arguments can be used.
    If you want to use `kwargs`, refer to the test functions in files like `test_dict` and `test_list` for guidance.
    :return:
    """
    # data = {
    #     "a": {
    #         "1": "2022-01-01T00:00:00",
    #         "2": "20.22",
    #         "3": 20.22,
    #         "4": 100,
    #     },
    #     "b": 1680441525,
    #     "c": 1680441525000,
    #     "d": "i am strong",
    #     "e": ["1680441525000000", "2022-01-01T00:00:001",
    #           {
    #               "f": 1000,
    #               "g": "10000"
    #           }]
    # }
    models = {
        'a': {'1': 'Datetime_%Y-%m-%dT%H:%M:%S', '2': 'StrFloat', '3': 'Float', '4': 'Int'},
        'b': 'Timestamp_10', 'c': 'Timestamp_13', 'd': 'Str',
        'e': ['StrTimestamp_13', 'Str', {'f': 'Int', "g": "StrInt"}]
    }
    # data_mocker1 = DataMocker.data_to_model(data)
    data_mocker2 = DataMocker.model_to_data(models)
    # Input raw data ---------> Data format
    # pprint(data_mocker1.get_datatype())
    # # Input raw data ---------> New mock data in the same format
    # pprint(data_mocker1.mock())
    # Input model data ---------> Mock data in the given format
    pprint(data_mocker2.mock())


@provider
class MyProvider:
    def user_status(self):
        return choice(["ACTIVE", "INACTIVE"])


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
    data['user_status'] = 'ACTIVE' if data['user_age'] >= 18 else 'INACTIVE'
    return data


@hook('final_generate', order=1, hook_set="SET1")
def final_generate_second_hook(data):
    """
    Suppose there is a function send_to_message_queue(data) to send data to the message queue
    """
    json_exporter = JSONExporter()
    json_exporter.export(data, 'output.json')


class UserInfo(DataMocker):
    create_time: Timestamp = Timestamp(Timestamp.D_TIMEE10, days=2)
    user_name: Str = Str(data_type="name")
    user_email: Str = Str(data_type="email")
    user_age: Int = Int(byte_nums=6, unsigned=True)
    user_status: ProviderField = ProviderField(MyProvider().user_status)
    user_marriage: Bool = Bool()
    user_dict: Dict = Dict(
        {
            "a": Float(left=2, right=4, unsigned=True),
            "b": Timestamp(Timestamp.D_TIMEE10, days=2)
        }
    )
    user_list: List = List(
        [
            Datetime(Datetime.D_FORMAT_YMD_T, weeks=2),
            StrInt(byte_nums=6, unsigned=True)
        ]
    )


def test_gen_data():
    UserInfo().mock(num_entries=3, as_list=False, to_json=True, hook_set='SET1')
