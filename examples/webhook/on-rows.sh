#!/bin/sh
# Called with the new rows on stdin, one JSON object per line.
# Example: keep a CSV of name and phone. jq treats every value as data.
jq -r '[."Name", ."Phone"] | @csv' >> leads.csv
