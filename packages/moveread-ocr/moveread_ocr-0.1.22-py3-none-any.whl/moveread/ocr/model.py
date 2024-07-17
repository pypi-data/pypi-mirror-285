import keras
kl = keras.layers
from .data import VOCABULARY

def ChessCRNN(
  num_classes: int = len(VOCABULARY) + 1, *,
  batch_size: int | None = 64,
  conv_kernel_initializer: str = 'lecun_uniform',
  lstm_dropout: float = 0.25
) -> keras.Model:
  """The original Moveread model: A CNN + RNN designed to work with CTC
  - `num_classes`: should be the vocabulary size + 1 (for the CTC blank token)
  """
  return keras.Sequential([
    kl.Input(shape=(256, 64, 1), batch_size=batch_size, name='image'),
    kl.Conv2D(64, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv1', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same', name='maxpool1'),
    kl.Conv2D(128, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv2', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same', name='maxpool2'),
    kl.Conv2D(256, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv3', kernel_initializer=conv_kernel_initializer),
    kl.Conv2D(256, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv4', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(1, 2), padding='same', name='maxpool3'),
    kl.Conv2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv5', kernel_initializer=conv_kernel_initializer),
    kl.BatchNormalization(),
    kl.Conv2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv6', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 1), strides=(2, 1), padding='valid'),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(3, 2), padding='valid'),
    kl.Reshape((11, -1)),
    kl.Bidirectional(kl.LSTM(256, return_sequences=True, dropout=lstm_dropout), name='BiLSTM1'),
    kl.Bidirectional(kl.LSTM(256, return_sequences=True, dropout=lstm_dropout), name='BiLSTM2'),
    kl.Dense(num_classes, activation=None, name='dense')
  ], name='ChessCRNN')

def BaseCRNN(
  num_classes: int = len(VOCABULARY) + 1, *,
  batch_size: int | None = 64,
  conv_kernel_initializer: str = 'lecun_uniform',
  lstm_dropout: float = 0.25
) -> keras.Model:
  """The original Moveread model: A CNN + RNN designed to work with CTC
  - `num_classes`: should be the vocabulary size + 1 (for the CTC blank token)
  """
  return keras.Sequential([
    kl.Input(shape=(256, 64, 1), batch_size=batch_size, name='image'),
    kl.Conv2D(64, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv1', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same', name='maxpool1'),
    kl.Conv2D(128, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv2', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same', name='maxpool2'),
    kl.Conv2D(256, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv3', kernel_initializer=conv_kernel_initializer),
    kl.Conv2D(256, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv4', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 2), strides=(1, 2), padding='same', name='maxpool3'),
    kl.Conv2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv5', kernel_initializer=conv_kernel_initializer),
    kl.BatchNormalization(),
    kl.Conv2D(512, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', use_bias=False, name='conv6', kernel_initializer=conv_kernel_initializer),
    kl.MaxPooling2D(pool_size=(2, 1), strides=(2, 1), padding='valid'),
    kl.Reshape((32, -1)),
    kl.Bidirectional(kl.LSTM(256, return_sequences=True, dropout=lstm_dropout), name='BiLSTM1'),
    kl.Bidirectional(kl.LSTM(256, return_sequences=True, dropout=lstm_dropout), name='BiLSTM2'),
    kl.Dense(num_classes, activation=None, name='dense')
  ], name='BaseCRNN')


def AdaptedChessCRNN(
  base: keras.Model, num_classes: int = len(VOCABULARY) + 1,
  *, lstm_dropout: float = 0.25
) -> keras.Model:
  """Adapts the head of pre-trained `BaseCRNN` to a `ChessCRNN`"""
  base_model = keras.Model(
    inputs=base.layers[0].input,
    outputs=base.get_layer(name='conv6').output,
    name="pretrained"
  )
  model = keras.Sequential([
    base_model,
    kl.MaxPool2D(pool_size=(2, 1), strides=(2, 1), padding="valid"),
    kl.MaxPool2D(pool_size=(2, 2), strides=(3, 2), padding="valid"),
    kl.Reshape((11, -1)),
    kl.Bidirectional(kl.LSTM(512, return_sequences=True, dropout=lstm_dropout), name="BiLSTM1"),
    kl.Bidirectional(kl.LSTM(512, return_sequences=True, dropout=lstm_dropout), name="BiLSTM2"),
    kl.Dense(num_classes, activation=None, name="dense")
  ], name="finetuned2")
  model.build((None, 256, 64, 1))
  return model


def load_model(weights: str, *, lstm_dropout: float = 0.25):
  """Returns `(model, char2num, num2char)`"""
  char2num = keras.layers.StringLookup(vocabulary=list(VOCABULARY), num_oov_indices=1)
  num2char = keras.layers.StringLookup(vocabulary=char2num.get_vocabulary(), invert=True)
  size = len(char2num.get_vocabulary())
  base = BaseCRNN(size)
  model = AdaptedChessCRNN(base, size, lstm_dropout=lstm_dropout)
  model.load_weights(weights)
  return model, char2num, num2char