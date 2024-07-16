# 禔 礽 祉 禛 禩 禟 䄉 祥 禵
import uuid

from pistol_magazine import *


class Param(DataMocker):
    a: ProviderField = ProviderField(
        CyclicParameterProvider(parameter_list=[1000, 1031, 1001, 1002, 1009]).gen
    )
    c: ProviderField = ProviderField(
        RandomFloatInRangeProvider(start=0.00, end=4.00, precision=4).gen
    )
    d: ProviderField = ProviderField(
        IncrementalValueProvider(start=0, step=-2).gen
    )
    e: ProviderField = ProviderField(
        RegexProvider(pattern=r"\d{3}-[a-z]{2}").gen
    )
    g = "s"
    f = {"key": "value"}
    create_time: Timestamp = Timestamp(Timestamp.D_TIMEE10, days=2)
    user_name: Str = Str(data_type="name")
    user_email: Str = Str(data_type="email")
    user_age: Int = Int(byte_nums=6, unsigned=True)
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

    def param_info(self):
        return self.mock(to_json=False, as_list=False, num_entries=3, key_generator=lambda: str(uuid.uuid4()))


def test_gen_data():
    data = Param().param_info()
    print(data)


