# TensorFlow Serving Client

> Client for OCR predictions against TensorFlow Serving

```bash
pip install tf-serving
```

## Model

The served model must return the following schema:

```typescript
{
  preds: StringTensor[BATCH x TOP_PATHS],
  logprobs: FloatTensor[BATCH x TOP_PATHS]
}
```

## Usage

```python
from tf.serving import predict, encode64

with open('path/to/image.jpg', 'rb') as f:
  img = encode64(f.read())

await predict([img], host='http://localhost', port=8501, endpoint='/v1/models/ocr:predict')
# Right(value=[ImagePreds(preds=['Place', 'Piace', ...], logprobs=[-0.187645972, -2.03857613, ...])], tag='right')
```