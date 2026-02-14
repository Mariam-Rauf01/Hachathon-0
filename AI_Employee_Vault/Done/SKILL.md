# AI Employee Skills

## Overview
This document defines the available skills for the Personal AI Employee system. These skills allow Claude to interact with the vault file system.

## Skills

### read_vault_file
- **Description**: Reads the content of a specified file in the vault
- **Parameters**:
  - `file_path` (string): Path to the file relative to the vault root (e.g., "Dashboard.md", "Needs_Action/task.md")
- **Returns**: String containing the file content
- **Example**: `read_vault_file(file_path="Dashboard.md")`

### write_vault_file
- **Description**: Writes content to a specified file in the vault
- **Parameters**:
  - `file_path` (string): Path to the file relative to the vault root
  - `content` (string): Content to write to the file
- **Returns**: Confirmation of successful write
- **Example**: `write_vault_file(file_path="Dashboard.md", content="# Updated Dashboard\nContent here...")`

### list_vault_files
- **Description**: Lists all files in a specified vault directory
- **Parameters**:
  - `directory` (string): Directory to list files from (e.g., "Needs_Action", "Inbox", "")
- **Returns**: Array of file names in the directory
- **Example**: `list_vault_files(directory="Needs_Action")`

### move_vault_file
- **Description**: Moves a file from one location to another within the vault
- **Parameters**:
  - `source_path` (string): Source file path relative to vault root
  - `destination_path` (string): Destination file path relative to vault root
- **Returns**: Confirmation of successful move
- **Example**: `move_vault_file(source_path="Needs_Action/task.md", destination_path="Done/task.md")`

### append_to_dashboard
- **Description**: Appends information to the Dashboard.md file
- **Parameters**:
  - `section` (string): Section of the dashboard to update (e.g., "Pending Tasks", "Notes", "Recent Actions")
  - `content` (string): Content to add to the specified section
- **Returns**: Confirmation of successful update
- **Example**: `append_to_dashboard(section="Notes", content="- New note added on $(date)")`

## Usage Guidelines
- Always reference files relative to the vault root directory
- Use forward slashes (/) for file paths even on Windows systems
- When updating Dashboard.md, preserve the existing structure and only modify relevant sections
- Follow the Company_Handbook.md guidelines when processing tasks