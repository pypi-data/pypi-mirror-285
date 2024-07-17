import requests

from ob_tuner.util import *
from ob_tuner.functions.button_logic import *

WELCOME_MESSAGE = f"""
# {GRADIO_INFRA_STACK_NAME} AI Workshop

## Introduction
Welcome to the AI Workshop! 
 
## Main Features
- Manage your account's API keys for AI tools that use external APIs.
- Create agent configuration profiles with custom values for:
    - Save and load named agent configuration profiles to/from your account.
    - Interact with your named agents, or community (shared) named agents.
    - Interact with {GRADIO_INFRA_STACK_NAME} with context to simulate the AI interacting with the Lead Momentum SMS Workflow.
    - LLM Type - supported types include
        - function
        - chat
        - completion
    - Tools - List of tools the agent can use. To see tool descriptions, navigate to the Tools tab
    - System Message - Message to display when the agent is first started.
    - Icebreaker - Message to display when the agent is first started.
    - LLM - name of the LLM to use (e.g. gpt-3, gpt-4o, etc.)
    - Temperature - Higher values result in spicier agents with less reliable tool use.
    - Max Execution Time - Maximum time allowed for agent to execute a tool.
    - Max Iterations - Maximum number of iterations allowed for agent to execute a tool.
    - Record Chat - Record chat messages for this agent for later analysis.
    - Record Tool Actions - Record tool actions for this agent for later analysis.
"""

with gr.Blocks(analytics_enabled=False) as landing_page:
    # Read the README file content
    with gr.Row():
        with gr.Column(scale=10):
            if NOAUTH_DEMO_PAGE:
                gr.Markdown(value="# Welcome to OpenBra.in!\n Please enjoy the live demo. Create agents that you can then interact with using the Gradio interface, or programmatically using something a CRM workflow. For example, modify the agent's behavior and see the results on the live website\n(https://www.openbra.in)[OpenBra.in Desert Road]. ")
            else:
                gr.Markdown(value="# Welcome!\n Please sign up or login. ")

        with gr.Column(scale=1) as login_column:
            gr.Button("Login", link="/login", variant="primary", size="sm")
            gr.Button("Signup", link="/signup", variant="secondary", size="sm")

    if NOAUTH_DEMO_PAGE:

        with gr.Tab("Demo"):
            session_state = gr.State(
                value={"session_id": "", "session": requests.Session(), "agent": None, "last_response": None,
                       "username": ""})

            with gr.Tab("Selected Agent Configuration") as submit_tab:
                with gr.Row() as submit_row:
                    with gr.Column(scale=3) as key_text_column:
                        with gr.Row() as key_text_row:
                            client_id = gr.Dropdown(
                                label="Client ID",
                                info="Develop your own AI agents or use a community agent.",
                                choices=["Guest"],
                                value="Guest",
                            )

                            profile_name = gr.Dropdown(
                                allow_custom_value=True,
                                label="Profile Name",
                                info="The name of your AgentConfig. Defaults to 'default'",
                                choices=[str(DEFAULT_PROFILE_NAME)],
                                value=DEFAULT_PROFILE_NAME,
                            )

                    with gr.Column(scale=1) as submit_column:
                        load_agent_profile_button = gr.Button(value="Load", variant="primary")
                        save_agent_profile_button = gr.Button(value="Save", variant="secondary")


            with gr.Accordion("AI Agent Configuration and Tuning", elem_classes="accordion", visible=is_settings_set(),
                              open=False) as prompts_box:
                with gr.Tab("LLM Parameters") as tuning_tab:
                    gr.Markdown(
                        "Changes to these settings are used to set up a conversation using the Reset button and will not "
                        "be reflected until the next 'Reset'"
                    )

                    with gr.Row() as preferences_row1:
                        options = model_agent_config.EXECUTOR_MODEL_TYPES
                        default_llm_types = ["function"]
                        llm_types = gr.CheckboxGroup(
                            choices=options,
                            label="LLM Types",
                            info="List only the types of agents you are interested in.",
                            value=default_llm_types,
                        )
                        original_choices = model_agent_config.FUNCTION_LANGUAGE_MODELS
                        # original_value = openbrain.orm.model_agent_config.FUNCTION_LANGUAGE_MODELS[0]
                        llm = gr.Dropdown(
                            choices=original_choices,
                            # value=original_value,
                            label="LLM",
                            info="The language model to use for completion",
                        )

                        with gr.Column() as extra_options_column:
                            record_tool_actions = gr.Checkbox(
                                label="Record Tool Actions", info="Record tool actions (use 'Actions' box).", interactive=False
                            )
                            record_conversations = gr.Checkbox(label="Record Conversations",
                                                               info="Record conversations.",
                                                               interactive=False)

                        # executor_completion_model = gr.Dropdown( choices=["text-davinci-003", "text-davinci-002",
                        # "text-curie-001", "text-babbage-001", "text-ada-001"], label="Executor Completion Model",
                        # info="This is the model used when Executor Model Type is set to 'completion'" )

                    with gr.Row() as preferences_row2:
                        executor_temp = gr.Slider(
                            minimum=0,
                            maximum=2,
                            label="Temperature",
                            step=0.1,
                            info="Higher temperature for 'spicy' agents.",
                        )
                        max_execution_time = gr.Slider(
                            minimum=0,
                            maximum=120,
                            label="Max Execution Time",
                            step=0.5,
                            info="Maximum agent response time before termination.",
                        )
                        max_iterations = gr.Number(
                            label="Max Iterations",
                            info="Number of steps an agent can take for a response before termination.",
                        )

                with gr.Tab("Tools") as preferences_row3:
                    tools = gr.CheckboxGroup(choices=TOOL_NAMES, value=[], label="Tools",
                                             info="Select tools to enable for the agent", interactive=False)

                    gr.Markdown(
                        value="Tool descriptions as presented to the AI. Confusing text here could lead to inconsistent use of tools."
                    )
                    _tools = discovered_tools
                    with gr.Column() as tool_accordion:
                        for _tool in _tools:
                            with gr.Tab(_tool.name):
                                gr.Markdown(value=get_tool_description(_tool.name))


                with gr.Tab("System Message") as long_text_row1:
                    system_message = gr.TextArea(
                        lines=10,
                        label="System Message",
                        placeholder="Enter your system message here",
                        info="The System Message. This message is a part of every context with "
                             "ChatGPT, and is therefore the most influential, and expensive place to "
                             "add text",
                        show_label=False,
                    )

                with gr.Tab("Icebreaker") as long_text_row2:
                    icebreaker = gr.TextArea(
                        lines=10,
                        label="Icebreaker",
                        placeholder="Enter your icebreaker here",
                        show_label=False,
                        info="The first message to be sent to the user.",
                    )

                with gr.Tab("Documentation") as help_tab:
                    gr.Markdown(value=get_help_text())


            with gr.Accordion("Interact with Agent") as chat_accordian:
                with gr.Row() as chat_row:
                    with gr.Column(scale=2) as chat_container:
                        with gr.Column(scale=2) as chat_column:
                            chatbot = gr.Chatbot(
                                show_share_button=True,
                                show_copy_button=True,
                                # avatar=(user_avatar_path, ai_avatar_path),
                                likeable=True,
                                # layout="panel",
                                layout="bubble",

                            )

                            msg = gr.Textbox()

                    with gr.Column(scale=1) as context_container:
                        initial_value_str = json.loads(json.dumps({
                            "random_word": "Rambutan"
                        }))

                        # context = gr.JSON(
                        #     label="Context",
                        #     value=initial_value_str
                        # )
                        context = gr.Textbox(
                            label="Context",
                            info="Additional context for tools, DISABLED FOR DEMO",
                            show_label=False,
                            show_copy_button=True,
                            lines=4,
                            value=EXAMPLE_CONTEXT,
                            interactive=False,
                        )

                        chat_button = gr.Button("Chat", variant="primary")
                        reset_agent = gr.Button("Reset", variant="secondary")

                        msg.submit(
                            chat,
                            [msg, chatbot, profile_name, session_state, client_id, context],
                            [msg, chatbot, session_state, context],
                        )


            with gr.Row() as bottom_text_row:
                logout_button = gr.Button("Logout", link="/logout", variant="secondary", size="sm", scale=1)
                with gr.Column(scale=10):
                    bottom_text = gr.Markdown(value=get_bottom_text(), rtl=True)

            preferences = [
                icebreaker,
                system_message,
                llm,
                max_iterations,
                max_execution_time,
                executor_temp,
                profile_name,
                client_id,
                record_tool_actions,
                record_conversations,
                tools,
                llm_types,
            ]

            # Refresh Buttons


            save_agent_profile_button.click(fn=lambda:gr.Warning("Saving disabled in the demo, please sign up for an account."))
            load_agent_profile_button.click(load, inputs=[profile_name, client_id], outputs=preferences)

            # Chat Button
            chat_button.click(
                fn=chat,
                inputs=[msg, chatbot, profile_name, session_state, client_id, context],
                outputs=[msg, chatbot, session_state, context],
            )
            dummy_text = gr.Textbox(visible=False)
            chat_button.click(get_aws_cloudwatch_logs, inputs=[session_state], outputs=[dummy_text])

            # Chat Reset Button
            reset_agent.click(
                fn=reset,
                inputs=[client_id, profile_name, chatbot, session_state, context],
                outputs=[msg, chatbot, session_state, context],
            )
            # reset_agent.click(get_bottom_text, inputs=[session_state, profile_name, client_id], outputs=[context])
            reset_agent.click(get_aws_cloudwatch_logs, inputs=[session_state], outputs=[dummy_text])
            reset_agent.click(get_action_events, inputs=[dummy_text, session_state], outputs=[dummy_text])

            # On Change Events
            llm_types.change(get_llm_choices, inputs=[llm_types], outputs=[llm])
            client_id.change(update_available_profile_names, inputs=[client_id], outputs=[profile_name])

    with gr.Tab(f"Welcome to {GRADIO_INFRA_STACK_NAME}"):
        gr.Markdown(WELCOME_MESSAGE)

if __name__ == "__main__":
    if os.getenv("GRADIO_PORT"):
        gradio_host = os.getenv("GRADIO_HOST", '0.0.0.0')
        gradio_port = int(os.getenv("GRADIO_PORT", 7861))
        landing_page.launch(
            debug=True,
            share=False,
            server_name=gradio_host,
            server_port=gradio_port,
        )