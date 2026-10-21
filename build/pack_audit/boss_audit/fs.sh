# usage: fs.sh base query
curl -sS -A "Mozilla/5.0" -G "$1/api.php" --data-urlencode action=query --data-urlencode list=search --data-urlencode srnamespace=6 --data-urlencode "srsearch=$2" --data-urlencode srlimit=15 --data-urlencode format=json | python3 -I -c 'import json,sys;[print(" ",x["title"]) for x in json.load(sys.stdin)["query"]["search"]]'
