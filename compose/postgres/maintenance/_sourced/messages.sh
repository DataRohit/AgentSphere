#!/usr/bin/env bash

# Function to print a newline
message_newline() {
    echo
}

# Function to print a debug message
message_debug() {
    echo -e "DEBUG: ${@}"
}

# Function to print a welcome message in bold
message_welcome() {
    echo -e "\e[1m${@}\e[0m"
}

# Function to print a warning message in yellow
message_warning() {
    echo -e "\e[33mWARNING\e[0m: ${@}"
}

# Function to print an error message in red
message_error() {
    echo -e "\e[31mERROR\e[0m: ${@}"
}

# Function to print an info message in white
message_info() {
    echo -e "\e[37mINFO\e[0m: ${@}"
}

# Function to print a suggestion message in yellow
message_suggestion() {
    echo -e "\e[33mSUGGESTION\e[0m: ${@}"
}

# Function to print a success message in green
message_success() {
    echo -e "\e[32mSUCCESS\e[0m: ${@}"
}
