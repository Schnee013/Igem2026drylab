#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
alignment_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)
raw_dir="$alignment_dir/topology/raw"

printf '%s\n' 'receptor_id	analysis_set	sequence_id	sequence_length	prediction_class	predictor	tm_id	start	end	length	n_terminal_side	c_terminal_side	signal_start	signal_end	source_gff3'

find "$raw_dir" -mindepth 3 -maxdepth 3 -type f -name TMRs.gff3 | LC_ALL=C sort |
while IFS= read -r gff; do
    receptor_dir=${gff%/DeepTMHMM/TMRs.gff3}
    receptor_id=${receptor_dir##*/}
    topology_file=${gff%/TMRs.gff3}/predicted_topologies.3line
    metadata_file=${gff%/TMRs.gff3}/metadata.json
    prediction_class=$(awk 'NR == 1 {sub(/^.* \| /, ""); print; exit}' "$topology_file")
    sequence_length=$(awk '/^# .* Length:/ {print $NF; exit}' "$gff")
    predictor=$(awk -F '"' '/"app_uri"/ {print $4; exit}' "$metadata_file")
    source_gff3=${gff#"$alignment_dir/"}

    case "$receptor_id" in
        Celegans_N2_DAF37_Q18321|Celegans_N2_DAF38_Q9U320)
            analysis_set=supplementary_reference
            ;;
        *)
            analysis_set=formal_alignment_input
            ;;
    esac

    awk -F '\t' \
        -v receptor_id="$receptor_id" \
        -v analysis_set="$analysis_set" \
        -v sequence_length="$sequence_length" \
        -v prediction_class="$prediction_class" \
        -v predictor="$predictor" \
        -v source_gff3="$source_gff3" '
        BEGIN { OFS = "\t" }
        !/^#/ && NF >= 4 {
            count++
            sequence_id = $1
            feature[count] = $2
            start[count] = $3
            end[count] = $4
            if ($2 == "signal") {
                signal_start = $3
                signal_end = $4
            }
        }
        END {
            if (signal_start == "") {
                signal_start = "."
                signal_end = "."
            }
            tm = 0
            for (i = 1; i <= count; i++) {
                if (feature[i] != "TMhelix")
                    continue
                tm++
                print receptor_id, analysis_set, sequence_id, sequence_length,
                      prediction_class, predictor, "TM" tm, start[i], end[i],
                      end[i] - start[i] + 1, feature[i - 1], feature[i + 1],
                      signal_start, signal_end, source_gff3
            }
            if (tm != 7) {
                print "Expected 7 TM helices for " receptor_id ", found " tm > "/dev/stderr"
                exit 1
            }
        }
    ' "$gff"
done
