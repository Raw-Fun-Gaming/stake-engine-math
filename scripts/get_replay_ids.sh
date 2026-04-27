#!/bin/bash
# Extract low/average/max payout event IDs from publish_files lookup tables.
# Outputs a markdown table ready to paste into replay_event_ids.md.
#
# Usage:
#   ./scripts/get_replay_ids.sh <game>
#   ./scripts/get_replay_ids.sh farm_pop
#
# Reads: games/<game>/build/publish_files/look_up_table_<mode>.csv
# Lookup table columns: id, seed, payout_value
#   - payout_value / 100 = multiplier  (e.g. 1000000 = 10000x)
#   - IDs are 1-based in the file; output subtracts 1 for 0-based RGS IDs

set -e

GAME=${1:?"Usage: $0 <game_name>"}
DIR="games/${GAME}/build/publish_files"

if [ ! -d "$DIR" ]; then
  echo "Error: $DIR not found. Run the build first." >&2
  exit 1
fi

# Detect available modes from existing files
MODES=()
for f in "$DIR"/look_up_table_*.csv; do
  mode=$(basename "$f" | sed 's/look_up_table_//' | sed 's/\.csv//')
  MODES+=("$mode")
done

echo "# ${GAME} — Replay Mode Event IDs"
echo ""
echo "IDs are 0-based. Multipliers are payout × bet."
echo "_Last updated: $(date +%Y-%m-%d)_"
echo ""
echo "| Mode | Tier | ID | Multiplier |"
echo "|------|------|----|------------|"

for mode in "${MODES[@]}"; do
  f="$DIR/look_up_table_${mode}.csv"

  # Low: smallest non-zero payout
  low=$(awk -F, '$3>0' "$f" | sort -t, -k3,3n | head -1)
  low_id=$(echo "$low" | cut -d, -f1)
  low_val=$(echo "$low" | cut -d, -f3)
  low_mult=$(awk "BEGIN{printf \"%.2fx\", $low_val/100}")

  # Max: largest payout
  max=$(sort -t, -k3,3n "$f" | tail -1)
  max_id=$(echo "$max" | cut -d, -f1)
  max_val=$(echo "$max" | cut -d, -f3)
  max_mult=$(awk "BEGIN{printf \"%.2fx\", $max_val/100}")

  # Average: row closest to mean of winning spins
  mean=$(awk -F, '$3>0{c++;t+=$3} END{printf "%.0f", t/c}' "$f")
  avg=$(awk -F, -v m="$mean" 'BEGIN{best=-1} $3>0{d=$3-m; if(d<0)d=-d; if(best<0||d<best){best=d; row=$0}} END{print row}' "$f")
  avg_id=$(echo "$avg" | cut -d, -f1)
  avg_val=$(echo "$avg" | cut -d, -f3)
  avg_mult=$(awk "BEGIN{printf \"%.2fx\", $avg_val/100}")

  # Subtract 1 for 0-based IDs
  echo "| ${mode} | Low | $((low_id - 1)) | ${low_mult} |"
  echo "| ${mode} | Average | $((avg_id - 1)) | ${avg_mult} |"
  echo "| ${mode} | Max | $((max_id - 1)) | ${max_mult} |"
done
