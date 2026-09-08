#!/bin/bash
# Run "$@" with the local dependency caches masked.
#
# ~/.m2, ~/.gradle and friends hold RELEASED jars of the very projects these
# bugs come from. A version published after the fix contains the fixed
# bytecode, so unzipping and decompiling one is ground-truth access -- with no
# repository, patch file or network involved, which is why the original
# five-channel contamination audit did not catch it. One session (Time-14, the
# no-fault-localization campaign) did exactly this and had to be excluded.
#
# Masking uses an empty tmpfs over each cache inside a bubblewrap sandbox:
#   * the real caches on disk are untouched
#   * HOME and the uid are unchanged, so the CLI keeps its credentials and does
#     not refuse `bypassPermissions` (it rejects that flag as root, which rules
#     out `unshare -r`, whose single-uid mapping forces uid 0)
#   * the hiding survives `find /`, unlike moving a path or changing HOME
#
# SANDBOX_MASK overrides the list. Exit 127 means no sandbox is available, so a
# caller can decide whether to proceed unprotected rather than silently do so.
set -uo pipefail

command -v bwrap >/dev/null || { echo "sandbox_caches: bwrap not installed" >&2; exit 127; }

MASK="$HOME/.m2 $HOME/.gradle $HOME/.ivy2 $HOME/.cache/coursier $HOME/.sbt"
# other home trees on this host can hold a second, larger cache
for d in /home_before_move/*/.m2 /home_before_move/*/.gradle; do
  [ -d "$d" ] && MASK="$MASK $d"
done
: "${SANDBOX_MASK:=$MASK}"

ARGS=(--dev-bind / /)
for d in $SANDBOX_MASK; do
  [ -d "$d" ] && ARGS+=(--tmpfs "$d")
done
exec bwrap "${ARGS[@]}" -- "$@"
