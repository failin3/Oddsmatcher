until nohup python3 src/main.py -p > log.txt 2>&1; do
    echo "Server 'Oddsmatcher' crashed with exit code $?.  Respawning.." >&2
    sleep 1
    pkill -o chromium
    sleep 1
done