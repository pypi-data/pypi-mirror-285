# asr-eval-utils
- jiwer-based asr-metrics
  - error-rates-of-interest by patching jiwer and Levenshtein.editops
- markdown-tables
  - for all kind of metrics not only ASR-specific
- transcript diffs
  - ansi conversion to html

## markdown table examples
#### WER table 
service \ corpus | common-voice | testset-ard
--- | --- | ---
nemo-conformer | 0.0897 | 0.1580
wav2vec2 | 0.1227 | 0.1299

#### overall_processing speed table
service \ corpus | common-voice | testset-ard
--- | --- | ---
nemo-conformer | 9.4456 | 7.6277
wav2vec2 | 3.6375 | 2.9431

## diff example
![img.png](images/diff_example.png)

## patched jiwer for "error-rates-of-interest"
- ref="foo,bar.",
- hyp="f,oobar...",
- of_interest={",", "."},
- expected={"cer": 2.0, "delr": 0.5, "hitr": 0.5, "insr": 1.5, "subr": 0.0},
- explanation: `len-of-interst is 2 (one comma one fullstop); 3 insertions make 3/2=1.5 insr`
