
# LMVM: Modular Function-Calling Agents

LMVM (Language Model Virtual Machine) simplifies building modular agents by allowing developers to use tools created by others, without the need for code re-implementation. By defining simple .lmvm files that specify which tools the agent will use, LMVM lets you get agents up and running in seconds.

### Key Concept

LMVM is driven by the idea of code-sharing, particularly tool-sharing. Developers can create tools (functions) that agents use, and share them with the community via a platform called Tool Hub. This allows others to easily integrate these tools into their own projects using LMVM.

### Example

LMVM's power is best demonstrated through a simple example. In this repository, you'll find two key folders that make LMVM work: `lmvm_files` and `tools`.

- The `lmvm_files` folder contains `.lmvm` files, which define the tools an agent will use. For example, the file `math.lmvm` currently in the `lmvm_files` folder contains:

  ```
  math_tools
  algebra
  ```

  This tells LMVM to run the agent with the tools (functions) found in the `math_tools` and `algebra` folders.

- The `tools` folder is where these tools are stored, including those downloaded from Tool Hub. By running the `math.lmvm` file in LMVM, LMVM will load the specified tools from this folder, allowing the agent to use them immediately.

### LLM Support
As of right now, I aim to start by supporting Cohere because I could not get access to the OpenAI API. However, at the moment, I do have plans to implement Runners for OpenAI, Claude and Cohere. 

### How to Contribute
Since this is an open-source project, contribution is welcome!! To help you guys do so, I am going to write a documentation on LMVM which should detail the inner workings of the system. But that will be for later. As of right now, I am going to finish up the support from Cohere and see if this whole system actually amounts to something.
