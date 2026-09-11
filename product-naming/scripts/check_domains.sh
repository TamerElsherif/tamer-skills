#!/bin/sh
# check_domains.sh — is <name>.<tld> registered? Asks the registries' own RDAP service (no API key).
#
#   scripts/check_domains.sh [-t com,io,app] name1 name2 ...
#
# Output per name: one column per TLD with  free | taken | n/a(<code>)
#   free       = registry answered 404 (not registered right now; premium/reserved names are only known at a registrar)
#   taken      = registry answered 200
#   n/a(code)  = registry unreachable, rate-limited (429) or TLD unsupported — check it at a registrar
#
# Common TLDs go straight to their registry; anything else uses the IANA bootstrap (rdap.org), which
# does not serve every TLD and rate-limits bursts. Each TLD is probed once with a registered control
# domain (google.<tld>); if the control is not 200 the TLD is reported n/a instead of a false "free".
set -u
TLDS="com,io"
if [ "${1:-}" = "-t" ]; then TLDS="$2"; shift 2; fi
[ $# -eq 0 ] && { echo "usage: $0 [-t com,io,...] name..." >&2; exit 2; }

endpoint() {  # $1 = fqdn
  case "${1##*.}" in
    com|net)  echo "https://rdap.verisign.com/${1##*.}/v1/domain/$1" ;;
    io)       echo "https://rdap.identitydigital.services/rdap/domain/$1" ;;
    org)      echo "https://rdap.publicinterestregistry.org/rdap/domain/$1" ;;
    app|dev)  echo "https://pubapi.registry.google/rdap/domain/$1" ;;
    *)        echo "https://rdap.org/domain/$1" ;;
  esac
}
code() {
  out=$(curl -s -L -o /dev/null -w '%{http_code}' --max-time 20 "$(endpoint "$1")" 2>/dev/null)
  c=$(printf '%s' "$out" | head -c 3)
  [ -z "$c" ] && c=000
  echo "$c"
}

supported=""
for t in $(echo "$TLDS" | tr ',' ' '); do
  c=$(code "google.$t")
  if [ "$c" = "200" ]; then supported="$supported $t"
  else echo "note: .$t not verifiable (control domain returned $c) — reported as n/a" >&2; fi
done

printf "%-14s" name
for t in $(echo "$TLDS" | tr ',' ' '); do printf "%-10s" ".$t"; done
printf "\n"

for n in "$@"; do
  n=$(echo "$n" | tr 'A-Z' 'a-z')
  printf "%-14s" "$n"
  for t in $(echo "$TLDS" | tr ',' ' '); do
    case " $supported " in
      *" $t "*)
        c=$(code "$n.$t")
        case "$c" in 200) s=taken ;; 404) s=free ;; *) s="n/a($c)" ;; esac ;;
      *) s="n/a" ;;
    esac
    printf "%-10s" "$s"
    sleep 0.3
  done
  printf "\n"
done
