#!/bin/bash

WATCHED_DIR="/home/z004ymtp/Secret"
LOG_FILE="/home/z004ymtp/Logs/file_logs.txt"
TEMP_FILE=$(mktemp)

inotifywait -m -e modify,create,delete,move "$WATCHED_DIR" --format '%T %w %f %e' --timefmt '%Y-%m-%d %H:%M:%S' |
while read -r timestamp directory file event; do
    log_entry="$timestamp - $directory$file - $event"
    echo "$log_entry" > "$TEMP_FILE"
    
    # Append existing log file to the temp file
    cat "$LOG_FILE" >> "$TEMP_FILE"
    
    # Move temp file to log file
    mv "$TEMP_FILE" "$LOG_FILE"
done
