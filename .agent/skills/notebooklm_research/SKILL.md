---
name: notebooklm_research
description: Tools for deep research using Google NotebookLM.
---

# NotebookLM Research Skill

This skill integrates Google's NotebookLM for deep research, synthesis, and long-term knowledge retrieval.

## Capabilities

1.  **Query**: Ask questions to your NotebookLM notebooks.
2.  **Source Management**: Add new sources from your local files or URLs.
3.  **Synthesis**: Generate reports, deep dives, or audio overviews.

## Instructions

### 1. Querying NotebookLM

-   Use `mcp_notebooklm_notebook_list` to find the relevant notebook (usually "Noetic Project" or similar).
-   Use `mcp_notebooklm_notebook_query` to ask questions.

    ```generic
    tool: mcp_notebooklm_notebook_query
    args:
        notebook_id: "UUID"
        query: "What are the key themes in the uploaded documents regarding [Topic]?"
    ```

### 2. Adding Sources

-   **Local Files**: To add a local markdown file as a source, you must first ensure it is readable, then use `mcp_notebooklm_notebook_add_text` (copying the text) or `mcp_notebooklm_notebook_add_drive` if it's synced to Drive.
    -   *Preferred Method*: Read the local file with `view_file`, then upload the text content directly using `mcp_notebooklm_notebook_add_text`.
    ```generic
    tool: mcp_notebooklm_notebook_add_text
    args:
        notebook_id: "UUID"
        title: "Filename"
        text: "File Content..."
    ```

-   **URLs**: Use `mcp_notebooklm_notebook_add_url` for web resources.

### 3. Generating Insights

-   If you need a high-level summary, use `mcp_notebooklm_notebook_describe`.
-   For audio summaries (e.g., for the user to listen to), use `mcp_notebooklm_audio_overview_create`.
