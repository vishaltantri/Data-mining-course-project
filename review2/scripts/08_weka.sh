#!/usr/bin/env bash
# Review 2 — Phase G: WEKA evaluations (J48, NaiveBayes, InfoGainAttributeEval)
#
# Run from the repository root:   bash review2/scripts/08_weka.sh
# Reads : review1/weka/diabetes_dw_export.arff (70,692 instances x 22 attributes,
#         exported from the data warehouse by review1/scripts/07_export_for_weka.py)
# Writes: review2/weka/j48_cv_output.txt          (J48, 10-fold CV)
#         review2/weka/naive_bayes_cv_output.txt  (NaiveBayes, 10-fold CV)
#         review2/weka/infogain_ranking.txt       (InfoGainAttributeEval + Ranker)
#         review2/weka/j48_cv_predictions.csv     (per-instance CV probabilities)
#         review2/weka/naive_bayes_cv_predictions.csv
#
# The prediction CSVs are WEKA's own cross-validated predictions; they are used
# by 09_weka_roc.R to plot the same threshold/ROC curves the Explorer's
# "Visualize threshold curve" shows.

set -euo pipefail

WEKA_JAR="${WEKA_JAR:-/home/vct/Desktop/DataMiningLab/weka-3-8-7-bellsoft-x64-linux (1)/weka-3-8-7/weka.jar}"
ARFF="review1/weka/diabetes_dw_export.arff"
OUT="review2/weka"
mkdir -p "$OUT"

if [ ! -f "$WEKA_JAR" ]; then
  echo "weka.jar not found at: $WEKA_JAR" >&2
  echo "Set WEKA_JAR=/path/to/weka.jar and re-run." >&2
  exit 1
fi

echo "== Phase G: WEKA 3.8.7, dataset: $ARFF (70,692 instances, 22 attributes)"

JAVA_OPTS="--add-opens java.base/java.lang=ALL-UNNAMED"

# One run for the full evaluation report, one for per-instance predictions
# (adding -classifications makes WEKA print only the predictions).
eval_run() { # $1 = classifier, $2 = output txt
  java $JAVA_OPTS -cp "$WEKA_JAR" "$1" -t "$ARFF" -x 10 -s 1 > "$2" 2>&1
}
pred_run() { # $1 = classifier, $2 = output csv
  java $JAVA_OPTS -cp "$WEKA_JAR" "$1" -t "$ARFF" -x 10 -s 1 \
    -classifications "weka.classifiers.evaluation.output.prediction.CSV -distribution" \
    2>/dev/null | awk '/^inst#,/{flag=1} flag' > "$2"
}

echo "== J48 (C4.5), 10-fold cross-validation..."
eval_run weka.classifiers.trees.J48 "$OUT/j48_cv_output.txt"
echo "   -> $OUT/j48_cv_output.txt"
pred_run weka.classifiers.trees.J48 "$OUT/j48_cv_predictions.csv"
echo "   -> $OUT/j48_cv_predictions.csv ($(wc -l < "$OUT/j48_cv_predictions.csv") lines)"

echo "== NaiveBayes, 10-fold cross-validation..."
eval_run weka.classifiers.bayes.NaiveBayes "$OUT/naive_bayes_cv_output.txt"
echo "   -> $OUT/naive_bayes_cv_output.txt"
pred_run weka.classifiers.bayes.NaiveBayes "$OUT/naive_bayes_cv_predictions.csv"
echo "   -> $OUT/naive_bayes_cv_predictions.csv ($(wc -l < "$OUT/naive_bayes_cv_predictions.csv") lines)"

echo "== InfoGainAttributeEval + Ranker (attribute selection)..."
java $JAVA_OPTS -cp "$WEKA_JAR" weka.attributeSelection.AttributeSelection \
  -i "$ARFF" \
  -E "weka.attributeSelection.InfoGainAttributeEval " \
  -S "weka.attributeSelection.Ranker -T -1.7976931348623157E308 -N -1" \
  > "$OUT/infogain_ranking.txt" 2>&1
echo "   -> $OUT/infogain_ranking.txt"

echo "== Phase G complete."
