import os
import ast
import subprocess
#This reads the lmvm files
#lmvm files contain names of tools that will be used for the agent
#the first line specifies the LLM to use:[openai, claude, cohere,...]
class Reader:
    def __init__(self, lmvm_file_path):
        self.lmvm_file_path = lmvm_file_path

    def read(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        relative_folder_path = os.path.join(script_dir, 'lmvm_files/'+self.lmvm_file_path)
        print(relative_folder_path)
        #read in the file contents (tool names)
        tool_names=None
        with open(relative_folder_path,"r") as file:
            tool_names = [line.strip() for line in file if line.strip()]
            print(tool_names)
        return tool_names

#this extracts functions from the required tool files allowing them to be called by the LLM
#it also installs necessary dependencies
class Extractor:
    def __init__(self,tool_names):
        self.tool_names=tool_names
        self.code_string=''
    
    def read(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        for t in self.tool_names:
            # Get the tool folder
            relative_folder_path = os.path.join(script_dir, 'tools', t)
            
            # Install dependencies from requirements.txt if it exists
            requirements_path = os.path.join(relative_folder_path, 'requirements.txt')
            if os.path.isfile(requirements_path):
                subprocess.check_call(['pip', 'install', '-r', requirements_path])
            
            # Read in all the Python files into self.code_string
            for root, _, files in os.walk(relative_folder_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            self.code_string += f.read() + '\n'

    def extract(self):
        self.read()
        #compile strings and setup exec environment
        functions,imports=self.extract_components()
        #get the function source code and correspond
        func_details={}
        for func in functions:
            func_code=self.get_function_source(func)
            func_details[func.name]={"source_code":func_code}
        import_statements = [self.get_import_source(imp) for imp in imports]
        
        return func_details,import_statements
                
    def extract_components(self):
        # Parse the code into an AST
        tree = ast.parse(self.code_string)
        # Extract function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        return functions,imports

    def get_function_source(self,node):
        # Get the starting and ending lines of the function
        start_line = node.lineno - 1  # lineno is 1-based
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        
        # Get the function code from the source code
        function_code = self.code_string.splitlines()[start_line:end_line]
        
        return '\n'.join(function_code)
    
    def get_import_source(self,node):
        return ast.unparse(node)

#this is the base class that interfaces with the llm and calls the tools
class Runner:
    def __init__(self,func_details,sys_prompt,api_key=''):
        self.func_details=func_details
        self._exec_environment={}
        self.sys_prompt=sys_prompt
        self.api_key=api_key
    
    def set_up_environ(self):
        #execute imports and function definitions
        for func_name,details in self.func_details.items():
            exec(details['source_code'],self._exec_environment)
    
    def create_tool_dict(self):
        pass
    
    def run(self,prompt):
        pass
    

class OpenAIRunner(Runner):
    def create_tool_dict(self):
        return super().create_tool_dict()

class ClaudeRunner(Runner):
    def create_tool_dict(self):
        return super().create_tool_dict()
    

class CohereRunner(Runner):
    def create_tool_dict(self):
        return super().create_tool_dict()

if __name__=="__main__":
    r=Reader("math.lmvm")
    tool_names=r.read()
    c=Extractor(tool_names)
    c.extract()
    








