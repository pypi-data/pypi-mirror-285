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


def test_postman_restful_api():
    print(PostmanRESTfulAPITemplate().get_template())
