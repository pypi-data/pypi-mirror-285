import importlib
import inspect
import os
import json
import yaml
from typing import Dict, List, Any, Callable, Optional, Tuple
from enum import Enum, auto
import re
import tiktoken

import colorama
from colorama import Fore, Back, Style
import random

from .Agent import Agent
from .JSONManager import JSONManager
from .LLMConfig import LLMConfig
from .LLMManager import LLMManager
from .rag_system import RAGSystem

colorama.init(autoreset=True)


class LogLevel(Enum):
    USER = auto()
    SYSTEM = auto()
    DEBUG = auto()


class PhaseType(Enum):
    THOUGHT = "THOUGHT"
    DRY_RUN = "DRY_RUN"
    FIND_BOTTLENECK = "FIND_BOTTLENECK"
    CORRECT = "CORRECT"


class MultiAgentFramework:
    _instance = None

    def __new__(cls, base_path: str, verbosity: LogLevel = LogLevel.USER):
        if cls._instance is None:
            cls._instance = super(MultiAgentFramework, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_path: str, verbosity: LogLevel = LogLevel.USER):
        if self._initialized:
            return
        self.base_path = base_path
        self.config = LLMConfig(os.path.join(base_path, "config.yaml")).get_config()
        self.agents: Dict[str, Agent] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.json_manager = JSONManager(base_path)
        self.llm_manager = LLMManager(self.config)
        self.examples: Dict[str, str] = {}
        self.verbosity = verbosity
        self.agent_colors = {}
        self.loaded_tool_names = set()  # Add this line
        self._initialize_agent_colors()
        self._initialized = True
        self.global_rag_config = self.config['framework'].get('rag', {})
        self.current_agent = None
        self.global_rag_config = self.config['framework'].get('rag', {})
        self.rag_system = None
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.initial_prompt = ""  # Add this line to initialize the initial_prompt attribute
        if self.global_rag_config.get('enabled', False):
            self.rag_system = RAGSystem(self.global_rag_config)
        self.load_components()

    def _log(self, level: LogLevel, agent_name: str, message: str, message_type: str = "INFO"):
        if level.value <= self.verbosity.value:
            color = self.agent_colors.get(agent_name, Fore.WHITE)
            level_color = {
                LogLevel.USER: Fore.GREEN,
                LogLevel.SYSTEM: Fore.YELLOW,
                LogLevel.DEBUG: Fore.CYAN
            }.get(level, Fore.WHITE)

            print(
                f"{level_color}[{level.name}] {color}[{agent_name}] {Style.BRIGHT}{message_type}: {Style.NORMAL}{message}{Style.RESET_ALL}")

    def _log_agent_action(self, agent: Agent, action: str, details: str):
        color = self.agent_colors.get(agent.name, Fore.WHITE)
        print(f"\n{color}{'=' * 50}")
        print(f"{color}Agent: {agent.name} ({agent.role})")
        print(f"{color}Action: {action}")
        print(f"{color}Details: {details}")
        print(f"{color}{'=' * 50}{Style.RESET_ALL}")

    def _log_llm_io(self, agent: Agent, input_data: str, output_data: str):
        if self.verbosity == LogLevel.DEBUG:
            color = self.agent_colors.get(agent.name, Fore.WHITE)
            print(f"\n{color}{'*' * 50}")
            print(f"{color}LLM Input/Output for {agent.name}")
            print(f"{color}{'*' * 50}")
            print(f"{color}Input:")
            print(f"{Fore.CYAN}{input_data}{Style.RESET_ALL}")
            print(f"\n{color}Output:")
            print(f"{Fore.MAGENTA}{output_data}{Style.RESET_ALL}")
            print(f"{color}{'*' * 50}{Style.RESET_ALL}")

    def _initialize_agent_colors(self):
        available_colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
        for agent_name, agent in self.agents.items():
            if 'color' in agent.llm_config:
                self.agent_colors[agent_name] = getattr(Fore, agent.llm_config['color'].upper(), Fore.WHITE)
            else:
                self.agent_colors[agent_name] = random.choice(available_colors)
                available_colors.remove(self.agent_colors[agent_name])
                if not available_colors:
                    available_colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

    def _debug_print(self, agent_name: str, message: str, message_type: str = "INFO"):
        if self.debug_mode:
            color = self.agent_colors.get(agent_name, Fore.WHITE)
            print(f"{color}[{agent_name}] {Style.BRIGHT}{message_type}: {Style.NORMAL}{message}{Style.RESET_ALL}")

    def _load_config(self):
        config_path = os.path.join(self.base_path, "config.yaml")

        with open(config_path, 'r') as f:
            config_str = f.read()

        # Replace environment variables
        config_str = re.sub(r'\$\{([^}^{]+)\}', lambda m: os.environ.get(m.group(1), m.group(0)), config_str)

        # Parse the YAML after environment variable substitution
        config = yaml.safe_load(config_str)

        return config

    def start_conversation(self, initial_prompt: str) -> Dict[str, Any]:
        """
        Start a new conversation with the multi-agent system.

        :param initial_prompt: The initial prompt or query to start the conversation.
        :return: The final result of the conversation.
        """
        print(f"Starting new conversation with prompt: {initial_prompt}")

        current_agent = self._determine_starting_agent(initial_prompt)
        current_data = initial_prompt

        while True:
            print(f"\nProcessing with agent: {current_agent.name}")
            result = self._process_agent(current_agent, current_data)
            current_data = result.get('input_data', result.get('output', current_data))  # Use input_data if available

            print(f"Agent {current_agent.name} output: {result['output']}")

            next_agent = self._determine_next_agent(result)
            if next_agent is None:
                print("\nConversation finished.")
                break
            current_agent = next_agent

        return result

    def load_components(self):
        try:
            self.load_tools()
            self.load_agents()
            self.load_examples()
            self.validate_and_update_agent_connections()
            self.load_role_knowledge()
        except ValueError as e:
            print(f"Error during component loading: {str(e)}")
            raise SystemExit(1)

    def load_examples(self):
        examples_path = os.path.join(self.base_path, "Examples")
        for root, _, files in os.walk(examples_path):
            for file in files:
                if file.endswith(".txt"):
                    example_name = os.path.splitext(file)[0]
                    with open(os.path.join(root, file), 'r') as f:
                        self.examples[example_name] = f.read().strip()

    def load_tools(self):
        # Load tools from "./DefaultTools" directory from this file not from self.base_path
        default_tools_path = os.path.join(os.path.dirname(__file__), "DefaultTools")
        self._load_tools_from_directory(default_tools_path, is_default=True)

        # Load custom tools
        custom_tools_path = os.path.join(self.base_path, "Tools")
        self._load_tools_from_directory(custom_tools_path, is_default=False)

    def _load_tools_from_directory(self, directory_path, is_default=False):
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    tool_name = os.path.splitext(file)[0]
                    if tool_name not in self.loaded_tool_names:
                        module_path = os.path.join(root, file)

                        try:
                            spec = importlib.util.spec_from_file_location(tool_name, module_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)

                            if hasattr(module, 'main'):
                                full_tool_name = f"{tool_name}" if is_default else tool_name
                                self.tools[full_tool_name] = {
                                    "function": module.main,
                                    "description": module.main.__doc__ or "No description available",
                                    "is_default": is_default
                                }
                                self.loaded_tool_names.add(tool_name)
                                print(f"Loaded tool: {full_tool_name} ({'default' if is_default else 'custom'})")
                        except Exception as e:
                            print(f"Error loading tool {tool_name}: {str(e)}")

    def load_agents(self):
        agents_path = os.path.join(self.base_path, "Agents")
        for root, _, files in os.walk(agents_path):
            for file in files:
                if file.endswith(".yaml"):
                    agent_name = os.path.splitext(file)[0]
                    with open(os.path.join(root, file), 'r') as f:
                        agent_config = yaml.safe_load(f)

                    raw_system_prompt = agent_config.get('system_prompt', '')
                    raw_validation_prompt = agent_config.get('validation_prompt', None)

                    role = agent_config.get('role', '')
                    tool_names = agent_config.get('tools', [])
                    llm_config = agent_config.get('llm_config', {})
                    rag_config = agent_config.get('rag_config')
                    extracts = agent_config.get('extracts',{})
                    transition_prompts = agent_config.get('transition_prompts', {})

                    agent = Agent(agent_name, raw_system_prompt, raw_validation_prompt, role, llm_config, tool_names, rag_config, extracts, transition_prompts)
                    agent.initialize_rag_system(self.config['framework'].get('rag', {}))
                    agent.agent_connections = agent_config.get('agentConnections', [])
                    self.agents[agent_name] = agent
                    self._log(LogLevel.DEBUG, "SYSTEM", f"Loaded agent: {agent_name}", "AGENT_LOAD")

    # def update_agent_system_prompts(self):
    #     for agent_name, agent in self.agents.items():
    #         replacements = self._get_replacements(agent)
    #         agent.system_prompt = self._apply_replacements(agent.system_prompt, replacements)
    #         if agent.validation_prompt:
    #             agent.validation_prompt = self._apply_replacements(agent.validation_prompt, replacements)
    #         else:
    #             self._log(LogLevel.DEBUG, agent_name, "No validation prompt specified", "PROMPT_UPDATE")

    @staticmethod
    def _apply_replacements(prompt: str, replacements: Dict[str, str]) -> str | None:
        if prompt is None:
            return None
        for key, value in replacements.items():
            prompt = prompt.replace(key, str(value))  # Convert value to string to ensure it's replaceable
        return prompt

    def _get_tool_info(self, tool):
        description = tool.get('description', 'No description available')
        if 'params' in tool:
            params = tool['params']
        else:
            func = tool['function']
            signature = inspect.signature(func)
            params = str(signature)
        return f"({description}, {params})"

    def _get_replacements(self, agent: Agent) -> Dict[str, str]:
        replacements = {
            "$otherAgents": json.dumps({name: a.role for name, a in self.agents.items() if a != agent}, indent=2),
            "$tools": json.dumps({name: self._get_tool_info(tool) for name, tool in self.tools.items()}, indent=2),
            "{agent.name}": agent.name,
            "{agent.role}": agent.role,
            "{agent.role_knowledge}": json.dumps(agent.role_knowledge, indent=2),
        }

        # Add replacements for other agents' thoughts, history, and extracts
        for other_agent_name, other_agent in self.agents.items():
            replacements[f"${other_agent_name}.THOUGHTS"] = "\n".join(other_agent.thought_process)
            replacements[f"${other_agent_name}.HISTORY"] = other_agent.get_history_as_string()
            for extract_key in other_agent.extracts:
                replacements[f"${other_agent_name}.{extract_key}"] = self._get_latest_extract(other_agent, extract_key)

        replacements["$USER_PROMPT"] = self.initial_prompt

        return replacements

    def _get_latest_extract(self, agent: Agent, key: str) -> str:
        for message in reversed(agent.conversation_history):
            if message['role'] == 'assistant':
                extract = self._extract_information(message['content'], key, agent.extracts[key])
                if extract:
                    return extract
        return ""

    def validate_agent_output(self, agent: Agent, llm_output: str) -> Dict[str, Any]:
        if not agent.validation_prompt:
            return {'valid': True, 'output': llm_output}  # Skip validation if no validation prompt is provided

        validation_input = agent.validation_prompt.format(agent=agent, llm_output=llm_output)
        validation_result = self.llm_manager.call_llm(agent.llm_config, validation_input)

        result = {}
        if "VALIDATION_RESULT: VALID" in validation_result:
            result['valid'] = True
            result['output'] = llm_output
        else:
            result['valid'] = False
            corrected_output_match = re.search(r'CORRECTED_OUTPUT:(.*)', validation_result, re.DOTALL)
            if corrected_output_match:
                result['output'] = corrected_output_match.group(1).strip()
            else:
                result['output'] = llm_output  # Fallback to original output if no correction provided

        # Ensure NEXT_AGENT instructions are preserved
        next_agent_match = re.search(r'NEXT_AGENT:\s*(\w+)', result['output'], re.IGNORECASE)
        if next_agent_match:
            result['next_action'] = {"type": "NEXT_AGENT", "agent": next_agent_match.group(1)}

        return result
    def validate_and_update_agent_connections(self):
        undefined_agents = set()
        undefined_tools = set()

        for agent_name, agent in self.agents.items():
            # Validate agent connections
            for connection in agent.agent_connections:
                if connection not in self.agents:
                    undefined_agents.add(connection)

            # Validate tools
            for tool in agent.tools:
                if isinstance(tool, str):
                    if tool not in self.tools:
                        undefined_tools.add(tool)
                elif isinstance(tool, dict):
                    tool_name = tool.get('name')
                    if tool_name not in self.tools:
                        undefined_tools.add(tool_name)

        # If any undefined agents or tools are found, raise an error
        if undefined_agents or undefined_tools:
            error_message = "Validation failed. The following components are undefined:\n"
            if undefined_agents:
                error_message += f"Agents: {', '.join(undefined_agents)}\n"
            if undefined_tools:
                error_message += f"Tools: {', '.join(undefined_tools)}\n"
            raise ValueError(error_message)

        # If validation passes, update agent tools with actual tool functions
        for agent in self.agents.values():
            updated_tools = []
            for tool in agent.tools:
                if isinstance(tool, str):
                    if tool in self.tools:
                        updated_tools.append(self.tools[tool])
                elif isinstance(tool, dict):
                    tool_name = tool.get('name')
                    if tool_name in self.tools:
                        updated_tools.append(self.tools[tool_name])
            agent.tools = updated_tools

    # def update_agent_prompts(self):
    #     other_agents_info = {name: agent.role for name, agent in self.agents.items()}
    #
    #     def get_tool_info(tool):
    #         description = tool.get('description', 'No description available')
    #         if 'params' in tool:
    #             params = tool['params']
    #         else:
    #             # Get the function signature if 'params' is not available
    #             func = tool['function']
    #             signature = inspect.signature(func)
    #             params = str(signature)
    #         return f"({description}, {params})"
    #
    #     tools_info = {name: get_tool_info(tool) for name, tool in self.tools.items()}
    #
    #     for agent in self.agents.values():
    #         updated_prompt = agent.prompt.replace("$otherAgents", json.dumps(other_agents_info, indent=2))
    #         updated_prompt = updated_prompt.replace("$tools", json.dumps(tools_info, indent=2))
    #
    #         # Replace #ExampleFile placeholders
    #         for example_name, example_content in self.examples.items():
    #             placeholder = f"#{example_name}"
    #             if placeholder in updated_prompt:
    #                 updated_prompt = updated_prompt.replace(placeholder, example_content)
    #             else:
    #                 print(f"Warning: Example file '{example_name}' not used in any prompt.")
    #
    #         # Check for any remaining #ExampleFile placeholders
    #         remaining_placeholders = re.findall(r'#(\w+)', updated_prompt)
    #         if remaining_placeholders:
    #             print(f"Warning: The following example files were not found: {', '.join(remaining_placeholders)}")
    #
    #         agent.prompt = updated_prompt

    def load_role_knowledge(self):
        knowledge_path = os.path.join(self.base_path, "RoleKnowledge")
        for root, _, files in os.walk(knowledge_path):
            for file in files:
                if file.endswith(".json"):
                    role = os.path.splitext(file)[0]
                    with open(os.path.join(root, file), 'r') as f:
                        role_knowledge = json.load(f)
                    for agent in self.agents.values():
                        if agent.role == role:
                            agent.set_role_knowledge(role_knowledge)

    def run_system(self, initial_input: str):
        self.initial_prompt = initial_input  # Update this line to set the initial_prompt
        self._log(LogLevel.SYSTEM, "SYSTEM", f"Starting system with initial input: {initial_input}", "START")
        current_agent = self._determine_starting_agent(initial_input)
        current_data = initial_input
        conversation_step = 1

        while True:
            self._log_agent_action(current_agent, "Processing", f"Step {conversation_step}")
            self._log(LogLevel.USER, current_agent.name, f"Processing input: {current_data[:100]}...", "INPUT")

            result = self._process_agent(current_agent, current_data)
            self._log_agent_action(current_agent, "Output", result['output'][:100] + "...")

            for thought in result['thoughts']:
                self._log(LogLevel.SYSTEM, current_agent.name, f"Thought: {thought}", "THOUGHT")

            next_action = result.get('next_action', {})

            if next_action.get('type') == "FINISH":
                self._log(LogLevel.SYSTEM, "SYSTEM", "Task completed.", "END")
                break
            elif next_action.get('type') == "NEXT_AGENT":
                next_agent_name = next_action.get('agent')
                next_agent = self.agents.get(next_agent_name)
                if next_agent:
                    self._log(LogLevel.USER, "SYSTEM", f"Handing over to agent: {next_agent.name}", "TRANSITION")
                    current_agent = next_agent
                    # if result.get('last_tool_result'):
                    #     current_data = f"Previous agent used tool: {result['last_tool_result']}\n\n{result['output']}"
                    # else:
                    current_data = result['output']
                else:
                    self._log(LogLevel.SYSTEM, "SYSTEM", f"Warning: Specified next agent '{next_agent_name}' does not exist. Continuing with current agent.", "WARNING")
                    current_data = result['output']
            else:
                current_data = result['output']

            conversation_step += 1

            if self.verbosity == LogLevel.USER:
                human_input = input(f"\n{Fore.WHITE}{Back.BLUE}Press Enter to continue or type 'stop' to end: {Style.RESET_ALL}")
                if human_input.lower() == 'stop':
                    self._log(LogLevel.SYSTEM, "SYSTEM", "Conversation finished by user request.", "END")
                    break

        return current_data

    def _print_step_header(self, step: int, agent: Agent):
        color = self.agent_colors.get(agent.name, Fore.WHITE)
        print(f"\n{color}{'=' * 50}")
        print(f"{color}Step {step}: {agent.name} ({agent.role})")
        print(f"{color}{'=' * 50}{Style.RESET_ALL}")

    def _print_step_result(self, result: Dict[str, Any]):
        color = self.agent_colors.get(result['agent'], Fore.WHITE)
        print(f"\n{color}--- Agent Output ---")
        print(f"{color}Output: {result['output']}")
        print(f"\n{color}--- Agent Thoughts ---")
        for thought in result['thoughts']:
            print(f"{color}- {thought}")
        print(f"\n{color}Next Action: {result['next_action']}{Style.RESET_ALL}")

    def _determine_starting_agent(self, initial_input: str) -> Agent:
        # Logic to determine the starting agent based on initial inputexe
        # For simplicity, we'll start with a default agent
        return self.agents.get("InitialAgent", next(iter(self.agents.values())))

    def _process_agent(self, agent: Agent, input_data: Any, max_iterations: int = 5) -> Dict[str, Any]:
        self.current_agent = agent
        iteration_count = 0
        tool_summary = None

        if agent.rag_system:
            rag_results = agent.rag_system.retrieve_info(input_data)
            if rag_results:
                rag_context = "\n".join([f"Relevant info: {result['content']}" for result in rag_results])
                input_data = f"{rag_context}\n\nCurrent input: {input_data}"

        agent.add_to_history("user", input_data)

        while iteration_count < max_iterations:
            iteration_count += 1
            self._log(LogLevel.DEBUG, agent.name, f"Processing iteration {iteration_count}", "ITERATION")

            llm_input = self._prepare_llm_input(agent)
            self._log(LogLevel.DEBUG, agent.name, f"LLM input prepared: \n {llm_input}", "LLM_INPUT")

            llm_output = self.llm_manager.call_llm(agent.llm_config, llm_input)
            if not agent.llm_config.get('stream', False):
                self._log(LogLevel.DEBUG, agent.name, f"LLM output received: {llm_output}", "LLM_OUTPUT")

            # Validate the LLM output
            validation_result = self.validate_agent_output(agent, llm_output)
            if not validation_result['valid']:
                self._log(LogLevel.DEBUG, agent.name, f"Invalid output detected. Using corrected output.", "VALIDATION")
                llm_output = validation_result['output']

            # Extract thoughts and update JSON
            thoughts = self._extract_thoughts(llm_output)
            for thought in thoughts:
                agent.add_thought(thought)
                self._log(LogLevel.DEBUG, agent.name, f"Thought: {thought}", "THOUGHT")

            # Extract other information based on agent's 'extracts' configuration
            extracted_info = {}
            for extract_key, extract_pattern in agent.extracts.items():
                extracted_info[extract_key] = self._extract_information(llm_output, extract_key, extract_pattern)


            json_updates = self._extract_json_updates(llm_output)
            for file_path, update_data in json_updates.items():
                self.json_manager.update_json(file_path, update_data)
                self._log(LogLevel.DEBUG, agent.name, f"Updated JSON file: {file_path}", "JSON_UPDATE")

            # Process tool usage and next action
            tool_info = self._extract_tool_to_use(llm_output)
            next_action = self._extract_next_action(llm_output)

            if tool_info:
                tool_name, tool_params = tool_info
                self._log(LogLevel.DEBUG, agent.name, f"Using tool: {tool_name}", "TOOL")
                self._log(LogLevel.DEBUG, agent.name, f"Tool parameters: {tool_params}", "TOOL_PARAMS")
                tool_result = self._execute_tool(tool_name, tool_params, self.tools)

                if isinstance(tool_result, str) and tool_result.startswith("Error:"):
                    self._log(LogLevel.DEBUG, agent.name, f"Tool execution failed: {tool_result}", "TOOL_ERROR")
                    tool_summary = f"TOOL_FAILED: {tool_name} - {tool_result}"
                else:
                    self._log(LogLevel.DEBUG, agent.name, f"Tool result: {tool_result}", "TOOL_RESULT")
                    tool_summary = f"TOOL_USED: {tool_name} - Result: {tool_result}"

                agent.add_to_history("tool", tool_summary)

                # Safe replacement of USE_TOOL with TOOL_USED
                def replace_use_tool(match):
                    return tool_summary

                llm_output = re.sub(r'USE_TOOL:.*', replace_use_tool, llm_output, flags=re.DOTALL)

                if next_action.get('type') == "NEXT_AGENT":
                    next_agent = next_action.get('agent')
                    agent_handover_summary = f"AGENT_HANDOVER_TO: {next_agent} with tool result: {tool_summary}"
                    agent.add_to_history("system", agent_handover_summary)

                    # Safe replacement of NEXT_AGENT with AGENT_HANDOVER_TO
                    def replace_next_agent(match):
                        return agent_handover_summary

                    llm_output = re.sub(r'NEXT_AGENT:.*', replace_next_agent, llm_output, flags=re.IGNORECASE)
                    break
                elif next_action.get('type') == "FINISH":
                    agent.add_to_history("system", "TASK_COMPLETED")
                    break
                else:
                    input_data = f"Previous action: {llm_output}\nTool result: {tool_summary}\nBased on this information, what's the next step?"
                    break;

            # If no tool was used, process next action
            if next_action.get('type') == "NEXT_AGENT":
                next_agent = next_action.get('agent')
                agent_handover_summary = f"AGENT_HANDOVER_TO: {next_agent}"
                agent.add_to_history("system", agent_handover_summary)
                # Replace NEXT_AGENT with AGENT_HANDOVER_TO in llm_output
                llm_output = re.sub(r'NEXT_AGENT:.*', agent_handover_summary, llm_output, flags=re.IGNORECASE)
                break
            elif next_action.get('type') == "FINISH":
                agent.add_to_history("system", "TASK_COMPLETED")
                break
            else:
                agent.add_to_history("assistant", llm_output)
                break  # Exit the loop if no clear next action is specified

        if iteration_count == max_iterations:
            self._log(LogLevel.SYSTEM, agent.name, f"Reached maximum iterations ({max_iterations}). Forcing completion.", "MAX_ITERATIONS")
            next_action = {"type": "FINISH"}

        agent.summarize_history()

        result = {
            'agent': agent.name,
            'role': agent.role,
            'output': llm_output,
            'thoughts': agent.thought_process,
            'next_action': next_action,
            'last_tool_result': tool_summary if tool_info else None
        }
        self._log(LogLevel.SYSTEM, agent.name, f"Processing complete. Next action: {next_action}", "END")
        return result

    def _execute_tool(self, tool_name: str, tool_params: Dict[str, Any],
                      available_tools: Dict[str, Dict[str, Any]]) -> Any:
        if tool_name in available_tools:
            tool = available_tools[tool_name]['function']
            try:
                return tool(tool_params, self, self.current_agent)
            except Exception as e:
                self._log(LogLevel.SYSTEM, "SYSTEM", f"Error executing tool {tool_name}: {str(e)}", "ERROR")
                return f"Error: {str(e)}"
        else:
            self._log(LogLevel.SYSTEM, "SYSTEM", f"Tool {tool_name} not found in available tools.", "WARNING")
            return f"Error: Tool {tool_name} not found"

    def _parse_json_tool(self, json_str: str) -> dict | None:
        try:
            tool_dict = json.loads(json_str)

            if isinstance(tool_dict, dict):
                return tool_dict
            else:
                self._log(LogLevel.SYSTEM, "SYSTEM", f"Unexpected JSON format: {json_str}", "WARNING")
                return None
        except json.JSONDecodeError as e:
            self._log(LogLevel.SYSTEM, "SYSTEM", f"Failed to parse JSON: {json_str}", "WARNING")
            self._log(LogLevel.DEBUG, "SYSTEM", f"JSON decode error: {str(e)}", "ERROR")
            return None

    def _parse_json_with_name_tool(self, tool_name: str, json_str: str) -> dict[Any, Any] | None:
        try:
            params = json.loads(json_str)
            return {tool_name: params}
        except json.JSONDecodeError:
            self._log(LogLevel.SYSTEM, "SYSTEM", f"Failed to parse JSON with name: {json_str}", "WARNING")
            return None

    def _parse_key_value_with_name_tool(self, tool_name: str, params_str: str) -> Dict[str, Any]:
        params = self._parse_key_value_pairs(params_str)
        return {tool_name: params}

    @staticmethod
    def _parse_key_value_pairs(params_str: str) -> Dict[str, Any]:
        params = {}
        pairs = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', params_str)
        for pair in pairs:
            match = re.match(r'(\w+)\s*[:=]\s*(.+)', pair.strip())
            if match:
                key, value = match.groups()
                value = value.strip('"')
                params[key] = value
        return params

    def _extract_tool_to_use(self, llm_output: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        # Flatten the input by replacing newlines with spaces
        flattened_output = re.sub(r'\s+', ' ', llm_output)

        extract_methods = self.config['framework'].get('tool_extract_methods', [])
        for method in extract_methods:
            self._log(LogLevel.DEBUG, "SYSTEM", f"Attempting to extract tool using method: {method['name']}",
                      "TOOL_EXTRACTION")
            regexp = method['regexp']
            parse_method = method['parse_method']
            tool_name_extractor = method['tool_name_extractor']
            params_extractor = method['params_extractor']

            match = re.search(regexp, flattened_output, re.IGNORECASE)
            if match:
                full_match = match.group(1)
                self._log(LogLevel.DEBUG, "SYSTEM", f"Full match: {full_match}", "TOOL_EXTRACTION")

                tool_name_match = re.search(tool_name_extractor, full_match)
                params_match = re.search(params_extractor, full_match, re.DOTALL)

                if tool_name_match and params_match:
                    tool_name = tool_name_match.group(1)
                    params_str = params_match.group(1)
                    self._log(LogLevel.DEBUG, "SYSTEM", f"Extracted tool name: {tool_name}", "TOOL_EXTRACTION")
                    self._log(LogLevel.DEBUG, "SYSTEM", f"Extracted params: {params_str}", "TOOL_EXTRACTION")

                    params = None
                    if parse_method == 'json':
                        params = self._parse_json_tool(params_str)
                    elif parse_method == 'json_with_name':
                        params = self._parse_json_with_name_tool(tool_name, params_str)
                    elif parse_method == 'key_value_with_name':
                        params = self._parse_key_value_with_name_tool(tool_name, params_str)

                    if params:
                        self._log(LogLevel.SYSTEM, "SYSTEM",
                                  f"Tool successfully extracted using method: {method['name']}", "INFO")
                        return tool_name, params
                    else:
                        self._log(LogLevel.DEBUG, "SYSTEM",
                                  f"Method {method['name']} matched but failed to parse parameters.", "WARNING")
                else:
                    self._log(LogLevel.DEBUG, "SYSTEM",
                              f"Failed to extract tool name or params using method: {method['name']}", "WARNING")
            else:
                self._log(LogLevel.DEBUG, "SYSTEM", f"Regexp didn't match for method: {method['name']}", "INFO")

        self._log(LogLevel.SYSTEM, "SYSTEM", "No matching tool extraction method found.", "WARNING")
        return None

    def _extract_next_action(self, llm_output: str) -> Dict[str, Any]:
        next_agent_match = re.search(r'NEXT_AGENT:\s*(\w+)', llm_output, re.IGNORECASE)
        if next_agent_match:
            next_agent = next_agent_match.group(1)
            if next_agent.lower() != "none":
                return {"type": "NEXT_AGENT", "agent": next_agent}
        if "FINISH" in llm_output.upper():
            return {"type": "FINISH"}
        return {"type": "CONTINUE"}

    def _prepare_llm_input(self, agent: Agent, max_attempts: int = 3, additional_context: str = "") -> str:
        system_prompt = agent.system_prompt
        max_tokens = agent.llm_config.get('max_tokens', 4096)  # Default to 4096 if not specified

        # Get pre_prompt and post_prompt from the framework config
        pre_prompt = self.config.get('framework', {}).get('pre_prompt', '')
        post_prompt = self.config.get('framework', {}).get('post_prompt', '')

        # Get replacements
        replacements = self._get_replacements(agent)

        for attempt in range(max_attempts):
            conversation_history = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in agent.conversation_history[1:]  # Skip the initial system message
            ])

            # Apply replacements to pre_prompt, post_prompt, and system_prompt
            pre_prompt_replaced = self._apply_replacements(pre_prompt, replacements) if agent.llm_config.get('pre_prompt', True) else ''
            post_prompt_replaced = self._apply_replacements(post_prompt, replacements) if agent.llm_config.get('post_prompt', True) else ''
            system_prompt_replaced = self._apply_replacements(system_prompt, replacements)

            # Construct the full prompt with replaced pre_prompt and post_prompt
            prompt = f"""
            {pre_prompt_replaced}
    
            {system_prompt_replaced}
    
            Conversation History:
            {conversation_history}
    
            {additional_context}
    
            Assistant: Based on the conversation history, including any tool results, and your role, please provide the next response or action.
    
            {post_prompt_replaced}
            """

            encoded_prompt = self.tokenizer.encode(prompt)

            if len(encoded_prompt) <= max_tokens:
                return prompt

            # If we exceed token limit, summarize the conversation history
            summary_tokens = max_tokens // 2  # Use half of max_tokens for summary
            agent.summarize_history(summary_tokens)

        # If we still can't fit within token limit after max attempts, truncate
        self._log(LogLevel.DEBUG, agent.name, f"Unable to fit conversation within {max_tokens} tokens after {max_attempts} summarization attempts. Truncating.", "TOKEN_LIMIT")

        truncated_history = agent.conversation_history[-10:]  # Keep only the last 10 messages
        conversation_history = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in truncated_history
        ])

        # Construct the truncated prompt with replaced pre_prompt and post_prompt
        prompt = f"""
        {pre_prompt_replaced}
    
        {system_prompt_replaced}
    
        Conversation History (Truncated):
        {conversation_history}
    
        {additional_context}
    
        Assistant: Based on this truncated conversation history, including any tool results, and your role, please provide the next response or action.
    
        {post_prompt_replaced}
        """

        return prompt

    def _extract_information(self, text: str, key: str, pattern: str) -> str:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""


    def _extract_thoughts(self, llm_output: str) -> List[str]:
        thoughts_section = re.search(r'THOUGHTS:(.*?)(?:JSON_UPDATES:|NEXT_ACTION:|$)', llm_output, re.DOTALL)
        if thoughts_section:
            return [thought.strip() for thought in thoughts_section.group(1).split('\n') if thought.strip()]
        return []

    def _extract_json_updates(self, llm_output: str) -> Dict[str, Dict]:
        updates = {}
        json_pattern = r'UPDATE_JSON\(([^)]+)\):\s*(\{[\s\S]+?\})'
        matches = re.findall(json_pattern, llm_output, re.DOTALL)
        for file_path, json_str in matches:
            try:
                # Remove any leading/trailing whitespace
                json_str = json_str.strip()

                # Replace any single quotes with double quotes
                json_str = json_str.replace("'", '"')

                # Handle potential line breaks and formatting issues
                json_str = re.sub(r'\s+', ' ', json_str)

                # Parse the JSON string
                json_data = json.loads(json_str)
                updates[file_path.strip()] = json_data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for {file_path}: {str(e)}")
                print(f"Problematic JSON string: {json_str}")
        return updates

    def _determine_next_agent(self, result: Dict[str, Any]) -> Agent:
        next_action = result.get('next_action', {})
        if next_action.get('type') == "NEXT_AGENT":
            next_agent_name = next_action.get('agent')
            current_agent = self.agents[result['agent']]
            next_agent = self.agents.get(next_agent_name)
            if next_agent:
                transition_prompt = current_agent.get_transition_prompt(next_agent_name)
                replacements = self._get_replacements(current_agent)
                transition_prompt = self._apply_replacements(transition_prompt, replacements)
                next_agent.add_to_history("system", transition_prompt)
                return next_agent
            else:
                print(f"Warning: Specified next agent '{next_agent_name}' does not exist.")
                return self._handle_human_intervention(result)
        elif next_action.get('type') == "FINISH":
            return None
        else:
            return self._handle_human_intervention(result)

    def _handle_human_intervention(self, result: Dict[str, Any]) -> Agent:
        print("\n--- Human Intervention Required ---")
        # print(f"Current Agent: {result.get('agent')}")
        # print(f"Current Output: {result.get('output')}")
        print("\nAvailable Agents:")
        for idx, (agent_name, agent) in enumerate(self.agents.items(), 1):
            print(f"{idx}. {agent_name} ({agent.role})")

        while True:
            try:
                choice = int(input(
                    "\nPlease select the next agent number, 0 to finish the conversation, or -1 to continue with the current agent: "))
                if choice == 0:
                    return None  # Finish the conversation
                elif choice == -1:
                    return self.agents[result.get('agent')]  # Continue with current agent
                elif 1 <= choice <= len(self.agents):
                    return list(self.agents.values())[choice - 1]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    def _get_human_input(self, agent_name: str, current_data: Any) -> Any:
        print(f"\n--- Human Input Required for Agent: {agent_name} ---")
        print(f"Current Data: {current_data}")
        return input("Please provide your input or press Enter to continue: ")
