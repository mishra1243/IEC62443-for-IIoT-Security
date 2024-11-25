#!/bin/bash

# Location of the allowed commands file
ALLOWED_COMMANDS_FILE="/home/superadmin/allowed_commands.txt"

# Check if the command is allowed
is_allowed() {
    local command=$(echo "$1" | awk '{print $1}')  # Extract the base command
    if [[ ! -f "$ALLOWED_COMMANDS_FILE" || ! -s "$ALLOWED_COMMANDS_FILE" ]]; then
        # If the file doesn't exist or is empty, allow all commands
        return 0
    fi
    grep -Fxq "$command" "$ALLOWED_COMMANDS_FILE"
}

# Execute the command if allowed
execute_command() {
    local command="$1"
    shift  # Remove the command from the argument list
    local args="$@"
    
    if is_allowed "$command"; then
        $command $args
    else
        echo "Command not allowed: $command"
        return 1
    fi
}

# Main loop for interactive session
while true; do
    echo -n "admin$ "
    read -r input_command args
    
    # If the input is empty, continue to next loop iteration
    [[ -z "$input_command" ]] && continue
    
    # If the user types 'exit', break the loop and close the shell
    if [[ "$input_command" == "exit" ]]; then
        break
    fi

    # Try to execute the command
    execute_command "$input_command" $args
done