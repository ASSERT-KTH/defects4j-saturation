# Sourced by all harness scripts.
# repository root, derived from this script's location
export D4J_CLAUDE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export D4J_HOME="${D4J_HOME:-$D4J_CLAUDE_ROOT/d4j}"
# Defects4J 3.x requires Java 11.
export JAVA_HOME="${D4J_JAVA_HOME:-/usr/lib/jvm/java-11-openjdk-amd64}"
export PATH="$JAVA_HOME/bin:$D4J_HOME/framework/bin:$PATH"
# Ant/JVM headroom; keep modest so N workers fit in RAM.
export ANT_OPTS="${ANT_OPTS:--Xmx2g -Djava.awt.headless=true}"
export TZ=UTC
