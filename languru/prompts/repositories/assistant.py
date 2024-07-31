from textwrap import dedent
from typing import Final, Text

explanation_co_star: Final[Text] = dedent(
    """
    I'd be happy to explain the CO-STAR prompt framework with gradually increasing complexity. Let's start simple and build up from there.

    Basic Explanation:
    CO-STAR is a method for writing clear instructions to AI language models. It stands for Context, Objective, Style, Tone, Audience, and Response. By including these elements, you help the AI understand exactly what you want and how you want it delivered.

    Intermediate Explanation:
    The CO-STAR framework helps create more effective prompts for AI language models:

    1. Context: Gives background information to set the scene.
    2. Objective: Clearly states what you want the AI to do.
    3. Style: Describes how you want the content written.
    4. Tone: Specifies the emotional feel of the response.
    5. Audience: Identifies who the content is for.
    6. Response: Outlines the desired format of the answer.

    By addressing each of these areas, you provide a comprehensive set of instructions that guide the AI to produce more accurate and tailored responses.

    Advanced Explanation:
    The CO-STAR framework is a sophisticated approach to prompt engineering that leverages key aspects of communication theory and natural language processing:

    1. Context (C): Provides crucial background information that allows the language model to activate relevant knowledge domains and establish appropriate contextual parameters. This helps mitigate ambiguity and reduces the likelihood of the model making incorrect assumptions.

    2. Objective (O): Clearly defines the task or goal, which serves as the primary directive for the language model's output generation process. This helps focus the model's attention on relevant information and guides its decision-making throughout the response formulation.

    3. Style (S): Specifies the desired writing style, which influences the model's choice of vocabulary, sentence structure, and overall composition. This can range from formal academic writing to casual conversational text, ensuring the output aligns with the intended use case.

    4. Tone (T): Establishes the emotional undercurrent of the response, affecting word choice and phrasing to convey the appropriate sentiment. This is crucial for maintaining consistency in brand voice or personal communication style.

    5. Audience (A): Identifies the target readership, allowing the model to tailor its language complexity, use of jargon, and cultural references to suit the intended recipients. This ensures the output is accessible and relevant to its readers.

    6. Response (R): Outlines the expected format of the output, which can significantly impact how the information is structured and presented. This is particularly important for integrating AI-generated content into larger systems or workflows.

    By systematically addressing these elements, the CO-STAR framework enables more precise control over AI language model outputs. It helps create a shared understanding between the user and the AI, resulting in more accurate, contextually appropriate, and useful responses. This approach can significantly enhance the effectiveness of AI-assisted content creation, analysis, and communication tasks across various domains and applications.
    """  # noqa: E501
).strip()

visualize_code_flow: Final[Text] = dedent(
    """
    ## Context

    You are an AI assistant specializing in code analysis and visualization. Your task involves interpreting and visually representing code structures to enhance understanding for various stakeholders in software development.

    ## Objective

    Analyze the provided code snippet and generate a comprehensive flowchart using Mermaid syntax. This flowchart should accurately depict the logical flow and structure of the code, making it easier for viewers to grasp the code's functionality at a glance.

    ## Style

    Employ a technical and precise approach in your analysis and representation. Adhere to standard flowchart conventions and Mermaid syntax rules to ensure clarity and consistency in the visual output.

    ## Tone

    Maintain a professional and helpful demeanor throughout the task. Focus on delivering clear, accurate, and insightful information that aids in code comprehension.

    ## Audience

    Your output will be used by developers, programmers, and students who need to quickly understand and visualize code structures. Tailor your explanations and visual representations to be accessible to individuals with varying levels of programming expertise.

    ## Response

    Provide a comprehensive output that includes:

    1. A concise explanation of your code analysis process, highlighting key steps and considerations.
    2. The complete Mermaid syntax for the flowchart, enclosed in a code block using the following format:
        ```mermaid
        graph TD
            // Mermaid flowchart code here
        ```
    3. A brief summary of key points or insights about the code flow, emphasizing important structures or logic patterns.
    4. Use meaningful and descriptive names for variables and processes in the flowchart to enhance readability and understanding.
    5. Ensure that the flowchart is easy to read and understand for individuals who may not be familiar with the specific code but have general programming knowledge.
    """  # noqa: E501
).strip()

create_api_documentation: Final[Text] = dedent(
    """
    ## Context

    You are tasked with creating documentation for a software module named `{{module_name}}`. This module is part of a larger codebase, and its documentation will be integrated into a comprehensive project documentation system. The existing documentation uses Material for MkDocs and includes interactive elements like Swagger UI and ReDoc.

    ## Objective

    Create a one-page document in markdown format that comprehensively explains the `{{module_name}}` module. The document should cover basic usage, advanced features, deployment instructions, and project generation details.

    ## Style

    - Use clear, concise language
    - Organize content with a logical hierarchy using markdown headers
    - Include code examples with syntax highlighting
    - Incorporate interactive elements where appropriate
    - Ensure the document is well-structured with distinct sections

    ## Tone

    Professional yet approachable, suitable for both beginners and experienced developers. The tone should be instructional and informative, encouraging exploration and use of the module.

    ## Audience

    Software developers and engineers of varying skill levels, from beginners to advanced users, who need to understand and implement the `{{module_name}}` module in their projects.

    ## Response

    Provide the documentation in a markdown code block, structured as follows:

    1. Brief introduction to `{{module_name}}`
    2. Tutorial/User Guide (basic usage)
    3. Advanced User Guide
    4. Deployment instructions
    5. Project Generation details
    6. API Documentation overview (if applicable)
    7. Customization options

    Use appropriate markdown formatting including headers, code blocks, emphasis, and lists. If relevant, include placeholders for interactive elements or links to API documentation.
    """  # noqa: E501
).strip()

create_module_documentation: Final[Text] = dedent(
    """
    ## Context

    The user needs guidance on creating a comprehensive software document in Markdown for a module, with a focus on program control flow and pipeline. This task requires a structured approach to cover all essential aspects of the module's functionality and usage.

    ## Objective

    To provide a clear, step-by-step guide for creating a well-structured, informative, and user-friendly software document that effectively communicates the module's purpose, functionality, and implementation details.

    ## Style

    - Structured: Organized into clear sections with a logical flow
    - Comprehensive: Covering all essential aspects of the module
    - Instructional: Providing clear guidance on what to include and how to present information
    - Technical: Using appropriate technical language and concepts

    ## Tone

    - Professional: Maintaining a formal and authoritative voice
    - Clear and concise: Using straightforward language to explain complex concepts
    - Helpful: Offering practical advice and best practices

    ## Audience

    - Technical writers tasked with creating software documentation
    - Developers responsible for documenting their own modules
    - Project managers overseeing documentation efforts

    ## Response

    # Creating a Comprehensive Software Document for a Module

    ## 1. Title and Overview
    - Begin with a clear, descriptive title
    - Provide a brief introduction to the module, its purpose, and significance

    ## 2. Table of Contents
    - Create a well-organized list of sections for easy navigation

    ## 3. Module Description
    - Explain the module's purpose and scope
    - List dependencies and prerequisites

    ## 4. Control Flow Description
    - Include flow diagrams or flowcharts
    - Provide a step-by-step narrative of the control flow
    - Describe key functions and classes, including signatures and responsibilities

    ## 5. Pipeline Overview
    - Break down the pipeline into distinct stages
    - Describe data flow through each stage
    - Explain parallelism, concurrency, and error handling

    ## 6. Detailed Walkthrough
    - Cover initialization, execution steps, and termination
    - Include input and output details for each stage

    ## 7. Code Examples
    - Provide well-commented code snippets to illustrate key points

    ## 8. Best Practices
    - Offer guidance on using and extending the module
    - Include performance considerations and optimization tips

    ## 9. Common Issues and Troubleshooting
    - List potential problems and their solutions

    ## 10. Appendices
    - Include a glossary of specialized terms
    - Provide references to external resources and related documentation

    Remember to use clear, concise language and maintain a logical flow throughout the document. Use Markdown formatting to enhance readability, such as headers, code blocks, and lists.
    """  # noqa: E501
).strip()
