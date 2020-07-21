until python3 main.py -p; do
    echo "Server 'Oddsmatcher' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
