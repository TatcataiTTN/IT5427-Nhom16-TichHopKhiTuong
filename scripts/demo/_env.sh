# Dung chung cho moi kich ban demo: ve thu muc goc repo, chon Python co du thu vien
# (Anaconda: torch, pyspark, kafka, streamlit; Homebrew python thieu torch).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
if [ -x /opt/anaconda3/bin/python3 ]; then PY=/opt/anaconda3/bin/python3; else PY=python3; fi
if [ -x /opt/anaconda3/bin/streamlit ]; then STREAMLIT=/opt/anaconda3/bin/streamlit; else STREAMLIT=streamlit; fi
# PySpark 4.x can Java 17+; may co the de Java 11 lam mac dinh (loi UnsupportedClassVersionError)
for v in 17 21; do
  J="/opt/homebrew/opt/openjdk@$v/libexec/openjdk.jdk/Contents/Home"
  if [ -x "$J/bin/java" ]; then export JAVA_HOME="$J"; export PATH="$J/bin:$PATH"; break; fi
done
export SPARK_LOCAL_IP="${SPARK_LOCAL_IP:-127.0.0.1}"
banner() { printf '\n\033[1;34m== %s ==\033[0m\n' "$1"; }
