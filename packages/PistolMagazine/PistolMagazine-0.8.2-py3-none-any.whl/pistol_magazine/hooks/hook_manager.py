class HookManager:
    def __init__(self):
        """
        pre_generate: Executes operations before generating all data. Suitable for tasks like logging or starting external services.
        after_generate: Executes operations after generating each data entry but before final processing. Suitable for tasks like data validation or conditional modifications.
        final_generate: Executes operations after generating and processing all data entries. Suitable for final data processing, sending data to message queues, or performing statistical analysis.
        """
        self.hooks = {
            'default': {
                'pre_generate': [],
                'after_generate': [],
                'final_generate': [],
            }
        }

    def register_hook(self, hook_point, func, order=0, hook_set='default'):
        if hook_set not in self.hooks:
            self.hooks[hook_set] = {
                'pre_generate': [],
                'after_generate': [],
                'final_generate': [],
            }

        if hook_point in self.hooks[hook_set]:
            self.hooks[hook_set][hook_point].append((func, order))
            self.hooks[hook_set][hook_point].sort(key=lambda x: x[1])
        else:
            raise ValueError(f"Hook point {hook_point} not recognized.")

    def trigger_hooks(self, hook_point, data, hook_set='default'):
        for func, _ in self.hooks.get(hook_set, {}).get(hook_point, []):
            if data is not None:
                func(data)
            else:
                func()
        return data


hook_manager = HookManager()

