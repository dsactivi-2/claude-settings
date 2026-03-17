export WORKFLOW_HOME="$HOME/.claude/workflow"
export WORKFLOW_AGENT="$WORKFLOW_HOME/sync-agent.py"

workflow-safe-run() {
  if [ -f "$WORKFLOW_AGENT" ]; then
    python3 "$WORKFLOW_AGENT" "$@" >/dev/null 2>&1 || true
  fi
}

workflow-chpwd-hook() {
  workflow-safe-run snapshot --reason chpwd
}

workflow-precmd-hook() {
  workflow-safe-run snapshot --reason precmd
}

autoload -Uz add-zsh-hook
add-zsh-hook chpwd workflow-chpwd-hook
add-zsh-hook precmd workflow-precmd-hook

alias wf-init='python3 "$WORKFLOW_AGENT" init'
alias wf-start='python3 "$WORKFLOW_AGENT" session-start'
alias wf-stop='python3 "$WORKFLOW_AGENT" session-stop'
alias wf-snap='python3 "$WORKFLOW_AGENT" snapshot'
alias wf-daily='python3 "$WORKFLOW_AGENT" daily'
alias wf-status='python3 "$WORKFLOW_AGENT" status'
