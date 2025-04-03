#!/usr/bin/env bash

# Function to prompt for user confirmation
yes_no() {
    # Description of the function
    declare desc="Prompt for confirmation. \$\"\{1\}\": confirmation message."

    # Get the confirmation message
    local arg1="${1}"

    # Initialize response variable
    local response=

    # Prompt user for input
    read -r -p "${arg1} (y/[n])? " response

    # Check if response is yes
    if [[ "${response}" =~ ^[Yy]$ ]]; then
        # Exit with success if yes
        exit 0
    else
        # Exit with failure if no
        exit 1
    fi
}
