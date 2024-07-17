# Moveread OCR

## CLIs

### Data Exporting

```bash
ocr records boxes 'data/ocr-dataset/**/*' -vo path/to/tfrecords
ocr records samples 'data/ocr-dataset/**/*' -vo path/to/tfrecords
```

### Inference

```bash
ocr predict -v --weights model.weights.h5 --data path/to/tfrecords > top-preds.ndjson
```

### Finetuning

```bash
ocr finetune -vw model.weights.h5 --train path/to/tfrecords --val path/to/tfrecords \
  --epochs 20 --batch-size 32 --lr 0.001
```

### Evaluation

```bash
ocr evaluate -vw model.weights.h5 -d path/to/tfrecords
```

### Serving Export

```bash
ocr export -vw model.weights.h5 -o path/to/SavedModel
```