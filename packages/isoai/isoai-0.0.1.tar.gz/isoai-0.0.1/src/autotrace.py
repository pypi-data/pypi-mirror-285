import os
import json
import re


class Autotrace:
    """A class to search for specific variables in files and save them in a
    JSON-compatible dictionary.
    """

    def __init__(self, search_path):
        """
        Initialize the Autotrace class with a search path.

        Args:
            search_path (str): The file path to search for variables.
        """
        self.search_path = search_path
        self.variables = {
            "dataset_name": None,
            "dataset_path": None,
            "prompt_name": None,
            "prompt_string": None,
            "model_name": None,
            "model_parameters": None,
        }
        self.variable_counter = 1

    def search_variables(self):
        """Search for the specified variables in the given file path and
        update the dictionary.
        """
        pattern = re.compile(r"(dataset_name|dataset_path|prompt_name|prompt_string|model_name|model_parameters)\s*=\s*['\"](.*?)['\"]")

        for root, _, files in os.walk(self.search_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for var, value in matches:
                            if self.variables[var] is None:
                                self.variables[var] = value

        for var in self.variables:
            if self.variables[var] is None:
                self.variables[var] = f"{var}_{self.variable_counter}"
                self.variable_counter += 1

    def check_json_compatibility(self):
        """Ensure the dictionary is JSON-compatible and transform if necessary.
        """
        try:
            json.dumps(self.variables)
        except TypeError:
            # Handle non-serializable values if necessary
            self.variables = {k: str(v) for k, v in self.variables.items()}

    def save_to_json(self, output_file):
        """Save the dictionary to a JSON file.

        Args:
            output_file (str): The path to the output JSON file.
        """
        self.check_json_compatibility()
        with open(output_file, 'w') as f:
            json.dump(self.variables, f, indent=4)

    def run(self, output_file):
        """Execute the variable search and save the result to a JSON file.

        Args:
            output_file (str): The path to the output JSON file.
        """
        self.search_variables()
        self.save_to_json(output_file)

