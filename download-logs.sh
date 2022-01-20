#!/usr/bin/env bash
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
file_name="heroku-logs.$current_time"
cd logs || exit
heroku ps:copy complete.log --output="$file_name.log"
