---
name: local_rag
description: Tools for interacting with the local "notes" knowledge base.
---

# Local RAG Skill

This skill allows the agent to utilize the `notes/` directory as a local knowledge base.

## Capabilities

1.  **Search**: Find relevant information in `notes/` using keywords or patterns.
2.  **Read**: Retrieve the content of specific notes.
3.  **Index**: Add new information to the knowledge base.

## Instructions

### 1. Searching for Information

When you need to find information about the project that might be stored locally:

-   **Step 1: Broad Search**
    Use `find_by_name` to look for relevant file names.
    ```generic
    tool: find_by_name
    args:
        SearchDirectory: "/Users/account1/dev/noetic/notes"
        Pattern: "*keyword*"
    ```

-   **Step 2: Content Search**
    If filename search is insufficient, use `grep_search` to find keywords inside files.
    ```generic
    tool: grep_search
    args:
        SearchPath: "/Users/account1/dev/noetic/notes"
        Query: "specific concept"
    ```

### 2. Reading Notes

-   Once a relevant file is identified, use `view_file` to read its content.
    ```generic
    tool: view_file
    args:
        AbsolutePath: "/Users/account1/dev/noetic/notes/path/to/file.md"
    ```

### 3. Adding to Knowledge Base (Indexing)

-   When you learn something new that should be persisted (e.g., architectural decision, key URL, design pattern), create a new markdown file in the appropriate subdirectory of `notes/`.
-   Use `write_to_file` to create the note.
-   **Frontmatter**: Always include YAML frontmatter with `tags` and `created` date.

    ```markdown
    ---
    tags: [topic, subtopic]
    created: YYYY-MM-DD
    ---
    # Title
    Content...
    ```
