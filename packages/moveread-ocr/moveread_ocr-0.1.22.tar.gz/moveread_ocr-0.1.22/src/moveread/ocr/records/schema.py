from typing import Literal
import tf.records as tfr
import moveread.ocr as mo

BOX_SCHEMA = tfr.schema(image=tfr.Tensor((256, 64, 1), 'float'))
SCHEMA = tfr.schema(label='string', **BOX_SCHEMA)
