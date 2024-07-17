from pydantic import BaseModel, RootModel

class ImagePreds(BaseModel):
  """Predictions of a single image
  - `preds[i], logprobs[i]`: one of the top paths word + logprobability
   - If you're using `tf.ctc.beam_decode`, then `preds[i]` will be the i-th most probable word
  """
  preds: list[str]
  logprobs: list[float]

class TFSOk(BaseModel):
  predictions: list[ImagePreds]

class TFSError(BaseModel):
  error: str
  
TFSResponse = RootModel[TFSOk | TFSError]