import yaml


class IuYAml:
    @staticmethod
    def doLoad(filePath: str) ->dict:
       
        with open(filePath, 'r') as file:
            # Load the YAML content into a Python dictionary
            map = yaml.safe_load(file)

        #print(map)
        return map
    
# Path to your YAML file
