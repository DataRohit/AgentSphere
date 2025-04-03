#!/usr/bin/env bash

# Function to display a countdown timer
countdown() {
    # Description of the function
    declare desc="A simple countdown. Source: https://superuser.com/a/611582"

    # Get the number of seconds to count down
    local seconds="${1}"

    # Calculate the end time
    local d=$(($(date +%s) + "${seconds}"))

    # Display countdown until end time is reached
    while [ "$d" -ge `date +%s` ]; do
        # Show remaining time in HH:MM:SS format
        echo -ne "$(date -u --date @$(($d - `date +%s`)) +%H:%M:%S)\r"
        # Sleep for a short interval
        sleep 0.1
    done
}
