"""
Deprecated
"""


# from pistol_magazine import DataMocker
#
#
# class FixedValueProvider(DataMocker):
#     def __init__(self, fixed_value=None):
#         """
#         This class always returns a fixed value.
#         If no value is provided, it uses a default fixed value.
#
#         Args:
#         fixed_value: The fixed value to return. If None, a default value is used.
#         """
#         super().__init__()
#         if fixed_value is None:
#             fixed_value = "default_fixed_value"
#         self.value = fixed_value
#
#     def get_fixed_value(self):
#         return self.value
