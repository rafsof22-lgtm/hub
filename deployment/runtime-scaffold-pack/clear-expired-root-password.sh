#!/usr/bin/env bash
set -eu

for required in DIGITALOCEAN_HOST DIGITALOCEAN_USER DIGITALOCEAN_PORT; do
  if [ -z "${!required:-}" ]; then
    echo "$required must be set in workflow env"
    exit 1
  fi
done

if [ ! -s .deploy_ssh_key ]; then
  echo ".deploy_ssh_key is missing; cannot test droplet SSH auth"
  exit 1
fi

target="${DIGITALOCEAN_USER}@${DIGITALOCEAN_HOST}"
ssh_options=(
  -i .deploy_ssh_key
  -o StrictHostKeyChecking=accept-new
  -o IdentitiesOnly=yes
  -o BatchMode=yes
  -o PreferredAuthentications=publickey
  -o ConnectTimeout=15
  -p "$DIGITALOCEAN_PORT"
)

if ssh "${ssh_options[@]}" "$target" 'true'; then
  echo "deploy_key_auth=already_usable"
  exit 0
fi

if ! command -v expect >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y expect
fi

cat > change_expired_root_password.exp <<'EXP'
set timeout 25
set current_password [lindex $argv 0]
set new_password [lindex $argv 1]
set target [lindex $argv 2]
set port [lindex $argv 3]
set changed 0

spawn ssh -tt -i .deploy_ssh_key -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes -o PreferredAuthentications=publickey -o ConnectTimeout=15 -p $port $target

expect {
  -re {(?i)(current|unix).*password:} {
    send -- "$current_password\r"
    exp_continue
  }
  -re {(?i)new.*password:} {
    send -- "$new_password\r"
    exp_continue
  }
  -re {(?i)retype.*password:} {
    send -- "$new_password\r"
    exp_continue
  }
  -re {(?i)(password.*updated|passwd:.*success)} {
    set changed 1
    exp_continue
  }
  -re {(^|\r|\n).*# $} {
    send -- "exit\r"
    exp_continue
  }
  eof {
    catch wait result
    set code [lindex $result 3]
    if {$changed == 1} {
      exit 0
    }
    exit $code
  }
  timeout {
    exit 124
  }
}
EXP

try_password_pair() {
  current_label="$1"
  current_password="$2"
  new_label="$3"
  new_password="$4"

  if [ -z "${current_password:-}" ] || [ -z "${new_password:-}" ]; then
    return 1
  fi

  echo "trying_root_password_change current_secret=$current_label new_secret=$new_label"
  set +e
  expect change_expired_root_password.exp "$current_password" "$new_password" "$target" "$DIGITALOCEAN_PORT"
  status=$?
  set -e

  if [ "$status" -ne 0 ]; then
    echo "root_password_change_failed current_secret=$current_label new_secret=$new_label"
    return 1
  fi

  if ssh "${ssh_options[@]}" "$target" 'true'; then
    echo "root_password_change_verified current_secret=$current_label new_secret=$new_label"
    return 0
  fi

  echo "root_password_changed_but_key_auth_still_blocked current_secret=$current_label new_secret=$new_label"
  return 1
}

declare -A candidate_values=(
  [DigO1]="${DIGO1:-}"
  [DigO2]="${DIGO2:-}"
  [DigO3]="${DIGO3:-}"
)

for current_label in DigO1 DigO2 DigO3; do
  for new_label in DigO1 DigO2 DigO3; do
    if [ "$current_label" = "$new_label" ]; then
      continue
    fi
    if try_password_pair "$current_label" "${candidate_values[$current_label]}" "$new_label" "${candidate_values[$new_label]}"; then
      exit 0
    fi
  done
done

for current_label in DigO1 DigO2 DigO3; do
  if try_password_pair "$current_label" "${candidate_values[$current_label]}" "$current_label" "${candidate_values[$current_label]}"; then
    exit 0
  fi
done

echo "expired_root_password_change=not_cleared"
exit 0
