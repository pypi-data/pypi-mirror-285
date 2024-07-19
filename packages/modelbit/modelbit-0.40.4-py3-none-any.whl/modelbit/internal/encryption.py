from io import BytesIO, BufferedReader, BufferedWriter, StringIO
from typing import Any, Union, Optional, cast, List, TextIO
import base64, sys, os
from tqdm import tqdm

from .describe import calcHash, calcHashFromFile, fileSize
from modelbit.utils import inNotebook, inDeployment, storeFileOnSuccess

ZSTD_MAGIC_NUMBER = b"\x28\xB5\x2F\xFD"
GZIP_MAGIC_NUMBER = b"\x1f\x8b"
readBlockSize = 16 * 1024 * 1024  # 16MB
showStatusThresholdBytes = 100_000_000


def _isLikelyZstd(data: bytes) -> bool:
  return data[0:4] == ZSTD_MAGIC_NUMBER


def _isLikelyGzip(data: bytes) -> bool:
  return data[0:2] == GZIP_MAGIC_NUMBER


# Cipher is stateful, so we need to make new ones for each read operation
def _makeCipher(key64: str, iv64: str) -> Any:
  from Cryptodome.Cipher import AES
  return AES.new(base64.b64decode(key64), AES.MODE_CBC, iv=base64.b64decode(iv64))  # type: ignore


def _assertHashMatch(expected: str, actual: str):
  if expected != actual:
    raise ValueError(f"Hash mismatch. Expected={expected} Found={actual}")


def getStatusOutputStream(visible: bool) -> TextIO:
  outputStream: TextIO = sys.stdout
  if not inNotebook():  # printing to stdout breaks git's add file flow
    outputStream = sys.stderr
  if os.getenv('MB_TXT_MODE') or not visible or inDeployment():
    outputStream = StringIO()
  return outputStream


def _decryptZstd(cipher: Any, data: BufferedReader, outWriter: Union[BytesIO, BufferedWriter], inputSize: int,
                 desc: str) -> None:
  import zstandard
  from Cryptodome.Cipher import AES
  from Cryptodome.Util.Padding import unpad

  dCtx = zstandard.ZstdDecompressor()
  dCom = dCtx.stream_writer(outWriter, write_size=50_000_000)

  with tqdm(total=inputSize,
            unit='B',
            unit_scale=True,
            miniters=1,
            desc=f"Decrypting '{desc}'",
            file=getStatusOutputStream(visible=inputSize > showStatusThresholdBytes)) as t:
    rData = data.read(readBlockSize)
    while rData:
      t.update(len(rData))
      chunk = cipher.decrypt(rData)
      if len(chunk) != readBlockSize or len(data.peek(1)) == 0:  # last block
        chunk = unpad(chunk, AES.block_size)
      dCom.write(chunk)
      rData = data.read(readBlockSize)


def decryptAndValidateToBytes(encFilePath: str, key64: str, iv64: str, expectedHash: Optional[str],
                              desc: str) -> memoryview:
  byteStream = BytesIO()
  _decryptAndValidate(encFilePath=encFilePath, key64=key64, iv64=iv64, outWriter=byteStream, desc=desc)
  buff = byteStream.getbuffer()

  if expectedHash:
    _assertHashMatch(expectedHash, calcHash(buff))

  return buff


def decryptAndValidateToFile(encFilePath: str, key64: str, iv64: str, toFile: str,
                             expectedHash: Optional[str], desc: str) -> None:
  with storeFileOnSuccess(finalPath=toFile) as tmpPath:
    with open(tmpPath, "wb") as f:
      _decryptAndValidate(encFilePath=encFilePath, key64=key64, iv64=iv64, outWriter=f, desc=desc)

  if expectedHash:
    _assertHashMatch(expectedHash, calcHashFromFile(toFile))


def _decryptAndValidate(encFilePath: str, key64: str, iv64: str, outWriter: Union[BytesIO, BufferedWriter],
                        desc: str) -> None:
  from Cryptodome.Cipher import AES
  from Cryptodome.Util.Padding import unpad

  with open(encFilePath, "rb") as f:
    head = _makeCipher(key64=key64, iv64=iv64).decrypt(f.read(AES.block_size))

  with open(encFilePath, "rb") as data:
    if _isLikelyZstd(head):
      _decryptZstd(cipher=_makeCipher(key64=key64, iv64=iv64),
                   data=data,
                   outWriter=outWriter,
                   inputSize=fileSize(encFilePath),
                   desc=desc)
    elif _isLikelyGzip(head):
      import zlib
      zData = unpad(_makeCipher(key64=key64, iv64=iv64).decrypt(data.read()), AES.block_size)
      uncompressedData = zlib.decompress(zData, zlib.MAX_WBITS | 32)
      outWriter.write(uncompressedData)
    else:
      raise Exception("Unknown compression format")


def encryptDataFromBytes(inData: bytes, outFile: str, key64: str, iv64: str, desc: str) -> None:
  with open(outFile, "wb") as outWriter:
    return _encryptData(inReader=BytesIO(inData),
                        outWriter=outWriter,
                        key64=key64,
                        iv64=iv64,
                        inputSize=len(inData),
                        desc=desc)


def encryptDataFromFile(inFile: str, outFile: str, key64: str, iv64: str, desc: str) -> None:
  with open(inFile, "rb") as inReader:
    with open(outFile, "wb") as outWriter:
      return _encryptData(inReader=inReader,
                          outWriter=outWriter,
                          key64=key64,
                          iv64=iv64,
                          inputSize=fileSize(inFile),
                          desc=desc)


def _encryptData(inReader: Union[BytesIO, BufferedReader], outWriter: Union[BytesIO, BufferedWriter],
                 key64: str, iv64: str, inputSize: int, desc: str) -> None:
  import zstandard
  from Cryptodome.Cipher import AES
  from Cryptodome.Util.Padding import pad
  cipher = AES.new(mode=AES.MODE_CBC, key=base64.b64decode(key64), iv=base64.b64decode(iv64))  # type: ignore

  cCtx = zstandard.ZstdCompressor()
  chunker = cCtx.chunker(chunk_size=readBlockSize, size=inputSize)
  with tqdm(total=inputSize,
            unit='B',
            unit_scale=True,
            miniters=1,
            desc=f"Encrypting '{desc}'",
            file=getStatusOutputStream(visible=inputSize > showStatusThresholdBytes)) as t:
    inChunk = inReader.read(readBlockSize)
    while inChunk:
      for outChunk in cast(List[bytes], chunker.compress(inChunk)):  # type: ignore
        outWriter.write(cipher.encrypt(outChunk))
      t.update(len(inChunk))
      inChunk = inReader.read(readBlockSize)
    finalChunks = cast(List[bytes], list(chunker.finish()))  # type: ignore
    finalChunk = b"".join(finalChunks)
    outWriter.write(cipher.encrypt(pad(finalChunk, AES.block_size)))
    t.update(len(finalChunk))
