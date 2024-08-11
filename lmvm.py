import os
import ast
import subprocess
import inspect

import cohere

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
            func_details[func.name]={"source_code":func_code,"description":ast.get_docstring(func)}
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

    def __init__(self,func_details,sys_prompt='',chat_history=[],api_key=''):
        self.func_details=func_details
        self._exec_environment={}
        self.sys_prompt=sys_prompt
        self.api_key=api_key
        self.chat_history=chat_history
        self._tools=[]
        self.set_up_environ()
    def set_up_environ(self):
        #execute imports and function definitions
        for func_name,details in self.func_details.items():
            exec(details['source_code'],self._exec_environment)
    
    def create_tool_dicts(self):
        pass
    
    def run(self,prompt):
        pass
    

class OpenAIRunner(Runner):
    def create_tool_dicts(self):
        return super().create_tool_dicts()

class ClaudeRunner(Runner):
    def create_tool_dicts(self):
        return super().create_tool_dicts()
    

class CohereRunner(Runner):
    def __init__(self, func_details, sys_prompt='',chat_history=[], api_key=''):
        super().__init__(func_details, sys_prompt,chat_history, api_key)
        self.co=cohere.Client(self.api_key)
    def create_tool_dicts(self):
        for func_name in self._exec_environment:
            if(func_name!="__builtins__"):
                tool={
                    "name":func_name,
                    "description": self.func_details[func_name]['description'],
                    "parameter_definitions":{
                    }
                }
                #add parameters of the function to parameter_definitions
                function=self._exec_environment[func_name]
                signature=inspect.signature(function)
                parameters=signature.parameters
                for param_name,param in parameters.items():
                    tool["parameter_definitions"].update(
                        {param_name:{
                        "description":"",
                        "type":param.annotation.__name__,
                        "required": True}}
                        )
                print(tool)
                self._tools.append(tool)
    def run(self,prompt):
        #create the tool dicts
        self.create_tool_dicts()
        response=self.co.chat(
            model="command-r-plus",
            chat_history=self.chat_history,
            message=prompt,
            force_single_step=False,
            tools=self._tools,
            preamble=self.sys_prompt,
            temperature=0
        )
        self.chat_history.append(response.chat_history[-1])
        while response.tool_calls:
            print(response.text)
            tool_results=[]
            current_call_result={'call':response.tool_calls[0],'outputs':self._exec_environment[response.tool_calls[0].name](**response.tool_calls[0].parameters)}
            tool_results.append(current_call_result)
            response = self.co.chat(
            model="command-r-plus",
            chat_history=self.chat_history,
            message="",
            force_single_step=False,
            tools=self._tools,
            tool_results=tool_results,
            preamble=self.sys_prompt,
            temperature=0
            )
            self.chat_history.append(response.chat_history[-1])
        print(response.text)
        
        
        

if __name__=="__main__":
    r=Reader("math.lmvm")
    tool_names=r.read()
    e=Extractor(tool_names)
    func_details,import_statements=e.extract()
    cr=CohereRunner(func_details,sys_prompt='''
    ## Task & Context
    You will help answer math questions. Your job is to use tools to answer them. Use the tools one by one to figure out the answer.
    ## IMPORTANT
    -Follow PEDMAS
    -Make a list for the solution plan.
    -For each step choose EXACTLY ONE TOOL that executes the step.
    -Do not assume anything that does not come as a result from tool usage.
    ## Style Guide
    Be friendly and recheck your work.
    
''',api_key='anrMxWD8pmfgasIwxNcQx3yGZgPxrapijbntnz2W')
    cr.run("4-5/125+6?")

    








