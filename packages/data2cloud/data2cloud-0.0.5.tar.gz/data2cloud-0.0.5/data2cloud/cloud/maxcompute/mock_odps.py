# 模拟odps的函数和类，用于测试
import os


class MockODPS:
    def __init__(self, base_dir="mock_odps_resources"):
        """Initialize the mock ODPS with a base directory for resources."""
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def create_resource(self, name, type, file_obj, comment=None):
        """Create a resource file in the mock environment."""
        resource_path = os.path.join(self.base_dir, name)
        with open(resource_path, "w") as file:
            file.write(file_obj)
        if comment:
            print(f"Resource {name} created with comment: {comment}")
        else:
            print(f"Resource {name} created without any comments.")

    def open_resource(
        self,
        name,
        project=None,
        mode="r+",
        encoding="utf-8",
        schema=None,
        type="file",
        stream=False,
        comment=None,
    ):
        """Open a resource file in the mock environment."""
        resource_path = os.path.join(self.base_dir, name)
        if mode == "r" and not os.path.exists(resource_path):
            raise FileNotFoundError(f"No resource named {name} found.")
        return open(resource_path, mode)

    def exist_resource(self, name):
        """Check if a resource exists in the mock environment."""
        resource_path = os.path.join(self.base_dir, name)
        return os.path.exists(resource_path)

    def create_function(self, func, class_type, resources):
        pass

    def exist_function(self, name, project=None, schema=None):
        return True

    def delete_resource(self, name, project=None, schema=None):
        pass
