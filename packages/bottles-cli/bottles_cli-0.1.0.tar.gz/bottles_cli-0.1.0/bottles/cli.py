import click
import subprocess
import re
import json
import time
from pathlib import Path
import anthropic

def find_git_root(path):
    """Find the root directory of the Git project."""
    path = Path(path).resolve()
    for parent in [path, *path.parents]:
        if (parent / '.git').is_dir():
            return parent
    return None

def get_non_ignored_files(root):
    """Get a list of files not ignored by Git."""
    try:
        result = subprocess.run(['git', 'ls-files', '-c', '--others', '--exclude-standard'],
                                cwd=root, capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        click.secho("Error: Failed to get non-ignored files from Git.", fg='red', err=True)
        return []

def scan_file_for_b(file_path):
    """Scan a file for lines starting with '@b'."""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip().startswith('@b ')]
    except (IOError, UnicodeDecodeError):
        click.secho(f"Warning: Could not read file {file_path}", fg='yellow', err=True)
        return []

def read_file_contents(file_path):
    """Read the contents of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except IOError:
        click.secho(f"Warning: Could not read file {file_path}", fg='yellow', err=True)
        return ""

def create_system_prompt(files_with_contents):
    """Create the system prompt with file contents."""
    base_prompt = """
You are an expert FAANG Senior Software Engineer, You are an expert at selecting and choosing the best tools, and doing your utmost to avoid unnecessary duplication and complexity.

You will be given files with its name and contents. Your task is to follow the instructions in the lines starting with '@b' and update the files.

When asked to update a file, you will provide the entire file contents. Do not abbreviate or summarize the file. Make sure to remove the lines starting with '@b'.

Put the file in a <file> tag at the end of the response.
"""
    for file_name, content in files_with_contents:
        base_prompt += f"\n\nFile: {file_name}\nContents:\n{content}\n"
    return base_prompt

def call_anthropic(client, system_prompt, messages):
    """Call the Anthropic API."""
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        temperature=0,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text  # Extract the text content from the response

def extract_file_content(response, max_retries=3):
    """Extract file content from the LLM response with retry logic."""
    for attempt in range(max_retries):
        match = re.search(r'<file>(.*?)</file>', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            click.secho(f"Attempt {attempt + 1}: Failed to extract file content. Retrying...", fg='yellow')
            time.sleep(1)  # Wait for 1 second before retrying
    click.secho("Failed to extract file content after multiple attempts.", fg='red', err=True)
    return None

def write_file_content(file_path, content):
    """Write content to a file."""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        click.secho(f"Successfully updated file: {file_path}", fg='green')
    except IOError:
        click.secho(f"Error: Could not write to file {file_path}", fg='red', err=True)

def git_create_branch(git_root, branch_name):
    """Create a new Git branch."""
    try:
        subprocess.run(['git', 'checkout', '-b', branch_name], cwd=git_root, check=True)
        click.secho(f"Created and switched to new branch: {branch_name}", fg='green')
    except subprocess.CalledProcessError as e:
        click.secho(f"Error creating Git branch: {e}", fg='red', err=True)

def git_commit(git_root, message):
    """Create a Git commit with the given message."""
    try:
        subprocess.run(['git', 'add', '.'], cwd=git_root, check=True)
        subprocess.run(['git', 'commit', '-m', message], cwd=git_root, check=True)
        click.secho(f"Created Git commit: {message}", fg='green')
    except subprocess.CalledProcessError as e:
        click.secho(f"Error creating Git commit: {e}", fg='red', err=True)

def generate_branch_name(client, b_instructions):
    """Generate a branch name based on @b instructions using LLM."""
    system_prompt = "You are an expert at creating concise and descriptive Git branch names."
    user_message = f"Based on the following @b instructions, generate a short, descriptive branch name (max 5 words, use hyphens for spaces):\n\n{b_instructions}, put the proposed branch name in <branch_name> tags"
    messages = [{"role": "user", "content": user_message}]
    response = call_anthropic(client, system_prompt, messages).strip().lower()
    # parse the response to extract the branch name
    branch_name = re.search(r'<branch_name>(.*?)</branch_name>', response, re.DOTALL)
    if branch_name:
        return "bottles/" + branch_name.group(1)
    else:
        click.secho("Failed to extract branch name from response.", fg='red', err=True)
        raise ValueError("Failed to extract branch name from response.")

def read_state(git_root):
    """Read the .bottles-state.json file."""
    state_file = git_root / '.bottles-state.json'
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return {}

def write_state(git_root, state):
    """Write the .bottles-state.json file."""
    state_file = git_root / '.bottles-state.json'
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def get_current_commit_hash(git_root):
    """Get the current commit hash."""
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=git_root, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def get_current_branch(git_root):
    """Get the name of the current Git branch."""
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                            cwd=git_root, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def get_commit_diffs(git_root, start_commit):
    """Get the git diff of every commit since the given commit hash."""
    result = subprocess.run(['git', 'log', '--reverse', '--patch', f'{start_commit}..HEAD'],
                            cwd=git_root, capture_output=True, text=True, check=True)
    return result.stdout


def apply_changes(git_root, current_branch, previous_branch):
    """Squash and rebase the current bottles branch back into the previous branch."""
    try:
        # Squash all commits on the current branch
        subprocess.run(['git', 'reset', '--soft', previous_branch], cwd=git_root, check=True)
        subprocess.run(['git', 'commit', '-m', f"Apply changes from {current_branch}"], cwd=git_root, check=True)
        
        # Switch to the previous branch
        subprocess.run(['git', 'checkout', previous_branch], cwd=git_root, check=True)
        
        # Rebase the changes
        subprocess.run(['git', 'rebase', current_branch], cwd=git_root, check=True)
        
        # Delete the bottles branch
        subprocess.run(['git', 'branch', '-D', current_branch], cwd=git_root, check=True)
        
        click.secho(f"Successfully applied changes from {current_branch} to {previous_branch}", fg='green')
    except subprocess.CalledProcessError as e:
        click.secho(f"Error applying changes: {e}", fg='red', err=True)

def review_changes(git_root, current_branch, previous_branch):
    """Show the diff between the bottles branch and the previous branch."""
    try:
        result = subprocess.run(['git', 'diff', f'{previous_branch}..{current_branch}'],
                                cwd=git_root, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        click.secho(f"Error reviewing changes: {e}", fg='red', err=True)
        return None

@click.group()
def cli():
    pass

@cli.command()
def process():
    """Process files in the Git project with '@b' instructions."""
    click.secho("Starting the process...", fg='cyan', bold=True)
    
    cwd = Path.cwd()
    git_root = find_git_root(cwd)

    if not git_root:
        click.secho("Error: Not in a Git repository.", fg='red', err=True)
        return

    click.secho(f"Found Git root: {git_root}", fg='green')

    # Read the current state
    state = read_state(git_root)

    # Get the current branch name
    current_branch = get_current_branch(git_root)

    # Check if we're on a branch that's recorded in our state
    if current_branch in state:
        click.secho(f"Already on a Bottles branch: {current_branch}", fg='green')
        start_commit = state[current_branch]['start_commit']
        previous_branch = state[current_branch]['previous_branch']
    else:
        start_commit = None
        previous_branch = current_branch

    non_ignored_files = get_non_ignored_files(git_root)
    click.secho(f"Found {len(non_ignored_files)} non-ignored files", fg='cyan')

    files_with_b = []
    files_with_contents = []
    all_b_instructions = []

    click.secho("Scanning files for '@b' directives...", fg='cyan')
    for file in non_ignored_files:
        file_path = git_root / file
        b_instructions = scan_file_for_b(file_path)
        if b_instructions:
            files_with_b.append(file)
            files_with_contents.append((file, read_file_contents(file_path)))
            all_b_instructions.extend(b_instructions)
            click.secho(f"Found '@b' directives in: {file}", fg='green')

    if not files_with_b:
        click.secho("No files found with '@b' instructions.", fg='yellow')
        return

    click.secho(f"Found {len(files_with_b)} files with '@b' instructions", fg='cyan')

    client = anthropic.Anthropic()

    if not start_commit:
        # Generate branch name
        branch_name = generate_branch_name(client, "\n".join(all_b_instructions))
        
        # Get the current commit hash before creating the new branch
        current_commit_hash = get_current_commit_hash(git_root)

        # Create the new branch
        git_create_branch(git_root, branch_name)

        # Update the state with the new branch and commit hash
        state[branch_name] = {
            'start_commit': current_commit_hash,
            'previous_branch': previous_branch
        }
        write_state(git_root, state)
        start_commit = current_commit_hash
        current_branch = branch_name

    # Create initial commit
    git_commit(git_root, "Initial commit before processing @b instructions")

    # Get the git diff of every commit since the start_commit
    commit_diffs = get_commit_diffs(git_root, start_commit)

    click.secho("Creating system prompt...", fg='cyan')
    system_prompt = create_system_prompt(files_with_contents)

    messages = []

    # Add the commit diffs as context
    if commit_diffs:
        messages.append({"role": "user", "content": f"Here are the git diffs of changes made since the last run:\n\n{commit_diffs}"})
        messages.append({"role": "assistant", "content": "I understand. I'll pay attention to the context of these changes when planning and making further modifications."})

    click.secho("Creating initial plan...", fg='cyan')
    initial_plan_prompt = """
Please create a detailed plan for addressing the @b instructions in the files.

Provide a step-by-step plan that outlines the changes to be made for each file, including:
1. What parts of the file need to be modified
2. What new code or content needs to be added
3. Any potential challenges or considerations

Take into account the git diffs provided earlier when creating this plan.
"""
    messages.append({"role": "user", "content": initial_plan_prompt})
    initial_plan = call_anthropic(client, system_prompt, messages)
    messages.append({"role": "assistant", "content": initial_plan})
    click.secho("Initial Plan:", fg='green', bold=True)
    click.echo(initial_plan)

    click.secho("Processing files...", fg='cyan')
    for file in files_with_b:
        click.secho(f"Updating file: {file}", fg='cyan')
        user_message = f"Please provide the updated contents for the file '{file}' based on the @b instructions and the context of changes in the git diffs."
        messages.append({"role": "user", "content": user_message})
        updated_content_response = call_anthropic(client, system_prompt, messages)
        messages.append({"role": "assistant", "content": updated_content_response})
        
        extracted_content = extract_file_content(updated_content_response)
        if extracted_content:
            file_path = git_root / file
            write_file_content(file_path, extracted_content)
        else:
            click.secho(f"Failed to update file: {file}", fg='red')

    # Create final commit
    git_commit(git_root, "Updated files based on @b instructions")

    click.secho("Process completed successfully!", fg='green', bold=True)

@cli.command()
def apply():
    """Apply changes from the current bottles branch to the previous branch."""
    git_root = find_git_root(Path.cwd())
    if not git_root:
        click.secho("Error: Not in a Git repository.", fg='red', err=True)
        return

    git_commit(git_root, "final commit before applying changes")

    state = read_state(git_root)
    current_branch = get_current_branch(git_root)

    if current_branch not in state:
        click.secho("Error: Not on a Bottles branch.", fg='red', err=True)
        return

    previous_branch = state[current_branch]['previous_branch']
    apply_changes(git_root, current_branch, previous_branch)

    # Remove the current branch from the state
    del state[current_branch]
    write_state(git_root, state)

@cli.command()
def review():
    """Review changes between the current bottles branch and the previous branch."""
    git_root = find_git_root(Path.cwd())
    if not git_root:
        click.secho("Error: Not in a Git repository.", fg='red', err=True)
        return

    state = read_state(git_root)
    current_branch = get_current_branch(git_root)

    if current_branch not in state:
        click.secho("Error: Not on a Bottles branch.", fg='red', err=True)
        return

    previous_branch = state[current_branch]['previous_branch']
    diff = review_changes(git_root, current_branch, previous_branch)

    if diff:
        click.echo("Changes between the current Bottles branch and the previous branch:")
        click.echo(diff)
    else:
        click.secho("No changes found or error occurred while reviewing changes.", fg='yellow')

if __name__ == '__main__':
    cli()
