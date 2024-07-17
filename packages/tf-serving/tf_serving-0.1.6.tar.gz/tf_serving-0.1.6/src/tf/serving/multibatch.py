from typing_extensions import Sequence, Unpack
from haskellian import iter as I, Iter, either as E
from .request import ImagePreds, predict, Params, PredictErr

def transpose(sample: ImagePreds) -> list[tuple[str, float]]:
  return list(zip(sample.preds, sample.logprobs))

@E.do[PredictErr]()
async def multipredict(b64_multibatch: Sequence[Sequence[str]], **params: Unpack[Params]) -> Sequence[Sequence[Sequence[tuple[str, float]]]]:
  """Predicts multiple player batches at once
  - Each `b64_multibatch[ply][player]` is a base64-encoded JPG/PNG/WEBP image
  - Returns an array of shape `BATCH x PLAYERS x TOP_PREDS` of `(pred, logprob)`
  """
  if len(b64_multibatch) == 0:
    return []
  num_players = len(b64_multibatch[0])
  flatbatch = list(I.flatten(b64_multibatch))
  flatpreds = (await predict(flatbatch, **params)).unsafe()
  return Iter(flatpreds) \
    .map(transpose) \
    .batch(num_players).sync()
