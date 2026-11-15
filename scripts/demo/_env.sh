# Dung chung cho moi kich ban demo: ve thu muc goc repo, chon Python co du thu vien
# (Anaconda: torch, pyspark, kafka, streamlit; Homebrew python thieu torch).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
if [ -x /opt/anaconda3/bin/python3 ]; then PY=/opt/anaconda3/bin/python3; else PY=python3; fi
if [ -x /opt/anaconda3/bin/streamlit ]; then STREAMLIT=/opt/anaconda3/bin/streamlit; else STREAMLIT=streamlit; fi
banner() { printf '\n\033[1;34m== %s ==\033[0m\n' "$1"; }
