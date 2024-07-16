from pistol_magazine.hooks.hook_manager import hook_manager


def hook(hook_point, order=0, hook_set='default'):
    """
    :param hook_point:
    pre_generate: Executes operations before generating all data. Suitable for tasks like logging or starting external services.

    after_generate: Executes operations after generating each data entry but before final processing. Suitable for tasks like data validation or conditional modifications.

    final_generate: Executes operations after generating and processing all data entries. Suitable for final data processing, sending data to message queues, or performing statistical analysis.

    :param order:
    :param hook_set:
    :return:
    """
    def decorator(func):
        hook_manager.register_hook(hook_point, func, order, hook_set)
        return func
    return decorator
