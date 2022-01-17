rm -rf rudder-alerta-enrichment-plugin
git clone -b $1 git@github.com:rudderlabs/rudder-alerta-enrichment-plugin.git
docker build --no-cache --build-arg=COMMIT_ID_VALUE="$(git log --format="%H" -n 1)" -t rudderlabs/alerta:$1 .
rm -rf rudder-alerta-enrichment-plugin
