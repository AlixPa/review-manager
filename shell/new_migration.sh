#!/bin/bash

search_dir=database/migrations
max_nb=0

for entry in "$search_dir"/*; do
    filename=$(basename "$entry")
    if [[ "$filename" =~ ^([0-9]{5}).* ]]; then
        mig_nb="${BASH_REMATCH[1]}"
        if (( mig_nb > max_nb )); then
            max_nb=$mig_nb
        fi
    fi
done

next_nb=$(( max_nb + 1 ))
next_nb_padded=$(printf "%05d" "$next_nb")

echo "Creating migration file number $next_nb_padded for migration $1"
echo "-- depends:" > "$search_dir/${next_nb_padded}_$1.sql"