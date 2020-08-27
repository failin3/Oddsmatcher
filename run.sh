pkill chromium
until nohup python3 src/main.py -p --schedule $1 > log.txt 2>&1; do
    echo "Server 'Oddsmatcher' crashed with exit code $?.  Respawning.." >&2
    sleep 1
    pkill -P $$
    sleep 1
done
