import ctypes
import os
import sys

import numpy
import platform

from collections import namedtuple

#### dependency check
if sys.platform == "win32":
    import ctypes
    try:
        for library in ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"]:
            ctypes.windll.LoadLibrary(library)
    except:
        print("  WARNING Please install MSVC 2015-2019 runtime from https://docs.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist")


#### loading DLL / DYLIB / SO  ####
if sys.platform == "win32":
    dll_platform = "windows/x64"
    dll_name = "ailia_tokenizer.dll"
    load_fn = ctypes.WinDLL
elif sys.platform == "darwin":
    dll_platform = "mac"
    dll_name = "libailia_tokenizer.dylib"
    load_fn = ctypes.CDLL
else:
    is_arm = "arm" in platform.machine() or platform.machine() == "aarch64"
    if is_arm:
        if platform.architecture()[0] == "32bit":
            dll_platform = "linux/armeabi-v7a"
        else:
            dll_platform = "linux/arm64-v8a"
    else:
        dll_platform = "linux/x64"
    dll_name = "libailia_tokenizer.so"
    load_fn = ctypes.CDLL

dll_found = False
candidate = ["", str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep), str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep) + dll_platform + str(os.sep)]
for dir in candidate:
    try:
        dll = load_fn(dir + dll_name)
        dll_found = True
    except:
        pass
if not dll_found:
    msg = "DLL load failed : \'" + dll_name + "\' is not found"
    raise ImportError(msg)

# ==============================================================================

from ctypes import *

AILIA_TOKENIZER_STATUS_SUCCESS = ( 0 )

AILIA_TOKENIZER_TYPE_WHISPER = ( 0 )
AILIA_TOKENIZER_TYPE_CLIP = ( 1 )
AILIA_TOKENIZER_TYPE_XLM_ROBERTA = ( 2 )
AILIA_TOKENIZER_TYPE_MARIAN = ( 3 )
AILIA_TOKENIZER_TYPE_BERT_JAPANESE_WORDPIECE = ( 4 )
AILIA_TOKENIZER_TYPE_BERT_JAPANESE_CHARACTER = ( 5 )
AILIA_TOKENIZER_TYPE_T5 = ( 6 )
AILIA_TOKENIZER_TYPE_ROBERTA = ( 7 )
AILIA_TOKENIZER_TYPE_BERT_UNCASED = ( 8 )
AILIA_TOKENIZER_TYPE_BERT_CASED = ( 9 )

AILIATokenizer = c_void_p

AILIA_TOKENIZER_FLAG_NONE = 0
AILIA_TOKENIZER_FLAG_UTF8_SAFE = 1

class ailia_tokenizer:
    def __init__(self):
        self.lib = dll
        self.lib.ailiaTokenizerCreate.restype = c_int
        self.lib.ailiaTokenizerCreate.argtypes = (POINTER(c_void_p), c_int32, c_int32)
        
        self.lib.ailiaTokenizerDestroy.restype = None
        self.lib.ailiaTokenizerDestroy.argtypes = (c_void_p, )

        self.lib.ailiaTokenizerOpenModelFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenModelFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenModelFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenModelFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenDictionaryFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenDictionaryFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenDictionaryFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenDictionaryFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenVocabFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenVocabFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenVocabFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenVocabFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenMergeFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenMergeFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenMergeFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenMergeFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerEncode.restype = ctypes.c_int
        self.lib.ailiaTokenizerEncode.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # utf8
        )
        dll.ailiaTokenizerGetTokenCount.restype = ctypes.c_int
        dll.ailiaTokenizerGetTokenCount.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.POINTER(ctypes.c_uint),   # count
        )
        dll.ailiaTokenizerGetTokens.restype = ctypes.c_int
        dll.ailiaTokenizerGetTokens.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # count
        )
        self.lib.ailiaTokenizerDecode.restype = ctypes.c_int
        self.lib.ailiaTokenizerDecode.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # token_count
        )
        dll.ailiaTokenizerGetTextLength.restype = ctypes.c_int
        dll.ailiaTokenizerGetTextLength.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.POINTER(ctypes.c_uint),   # count
        )
        dll.ailiaTokenizerGetText.restype = ctypes.c_int
        dll.ailiaTokenizerGetText.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.byte, flags='CONTIGUOUS'
            ),                               # text
            ctypes.c_uint                    # len
        )

    def __check(self, status):
        if status != AILIA_TOKENIZER_STATUS_SUCCESS:
            raise AiliaTokenizerError(f"ailia tokenizer error", status)

    def Create(self, arg0, arg1, arg2):
        self.__check(self.lib.ailiaTokenizerCreate(cast(pointer(arg0), POINTER(c_void_p)), arg1, arg2))

    def Destroy(self, arg0):
        self.lib.ailiaTokenizerDestroy(cast(arg0, c_void_p))

    def OpenModelFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenModelFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenModelFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenDictionaryFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenDictionaryFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenDictionaryFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenVocabFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenVocabFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenVocabFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenMergeFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenMergeFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenMergeFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def Encode(self, arg0, arg1):
        self.__check(self.lib.ailiaTokenizerEncode(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))
    
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTokenCount(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int32, order='C')

        self.__check(self.lib.ailiaTokenizerGetTokens(cast(arg0, c_void_p), buf, count))

        return buf

    def Decode(self, arg0, arg1, arg2):
        buf = numpy.zeros((len(arg1)), dtype=numpy.int32, order='C')
        for i in range(len(arg1)):
            buf[i] = arg1[i]

        self.__check(self.lib.ailiaTokenizerDecode(cast(arg0, c_void_p), buf, arg2))
    
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTextLength(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int8, order='C')

        self.__check(self.lib.ailiaTokenizerGetText(cast(arg0, c_void_p), buf, count))

        return bytes(buf[0:len(buf) - 1]).decode("utf-8")
    
# ==============================================================================
# BaseTokenizer
# ==============================================================================

class AiliaTokenizerError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(f"{message} code:{code}")
        self.code = code

class AiliaTokenizerResult:
    def __init__(self, input_ids, attention_mask):
        self.input_ids = input_ids
        self.attention_mask = attention_mask

    def __getitem__(self, key):
        if key in self.__dict__:
            return getattr(self, key)
        raise KeyError(f"No such key: {key}")

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()
    
    def __repr__(self):
        return str(self.__dict__)

class AiliaTokenizerResultWithTokenTypeIds:
    def __init__(self, input_ids, attention_mask, token_type_ids):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.token_type_ids = token_type_ids

    def __getitem__(self, key):
        if key in self.__dict__:
            return getattr(self, key)
        raise KeyError(f"No such key: {key}")

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def __repr__(self):
        return str(self.__dict__)

class BaseTokenizer:
    _pad_token_id = -1
    _initialized = False
    _token_type_ids = False

    def __init__(self):
        self.instance = AILIATokenizer()
        self.dll = ailia_tokenizer()

    def __del__(self):
        if self.instance:
            self.dll.Destroy(self.instance)
    
    def _padding(self, input_ids, attention_masks, token_type_ids, max_len, return_tensors):
        if self._pad_token_id == -1:
            raise AiliaTokenizerError("unknown padding token id.", -1)

        if return_tensors == 'np':
            padding_ids = numpy.zeros((len(input_ids), max_len), dtype=numpy.int64)
            padding_attention_masks = numpy.zeros((len(input_ids), max_len), dtype=numpy.int64)
            padding_token_type_ids = numpy.zeros((len(input_ids), max_len), dtype=numpy.int64)

            for batch in range(len(input_ids)):
                padding_ids[batch, 0:input_ids[batch].shape[0]] = input_ids[batch]
                padding_ids[batch, input_ids[batch].shape[0]:max_len] = self._pad_token_id
                padding_attention_masks[batch, 0:attention_masks[batch].shape[0]] = attention_masks[batch]
                padding_token_type_ids[batch, 0:token_type_ids[batch].shape[0]] = token_type_ids[batch]
        else:
            padding_ids = [[self._pad_token_id] * max_len for _ in range(len(input_ids))]
            padding_attention_masks = [[0] * max_len for _ in range(len(input_ids))]
            padding_token_type_ids = [[0] * max_len for _ in range(len(input_ids))]

            for batch in range(len(input_ids)):
                padding_ids[batch][:len(input_ids[batch])] = input_ids[batch]
                padding_attention_masks[batch][:len(attention_masks[batch])] = attention_masks[batch]
                padding_token_type_ids[batch][:len(token_type_ids[batch])] = token_type_ids[batch]

        return padding_ids, padding_attention_masks, padding_token_type_ids

    def encode(self, text, padding=True, truncation=True, return_tensors=None, max_length = None):
        if not self._initialized:
            raise AiliaTokenizerError("from_pretrained not called.", -1)
        if return_tensors != 'np' and return_tensors != None:
            raise AiliaTokenizerError("return tensors pt not supported. please use np.", -1)

        reduce_axis = False
        if type(text) == str:
            text = [text]
            if return_tensors != 'np':
                reduce_axis = True

        input_ids = []
        attention_masks = []
        token_type_ids = []
        max_len = 0

        for t in text:
            input_id = self.dll.Encode(self.instance, t).astype(numpy.int64)
            if truncation and max_length is not None and input_id.shape[0] > max_length:
                input_id[max_length - 1] = input_id[-1]
                input_id = input_id[0:max_length]
            attention_mask = input_id.copy()
            attention_mask[:] = 1
            token_type_id = input_id.copy()
            token_type_id[:] = 0
            input_ids.append(input_id)
            attention_masks.append(attention_mask)
            token_type_ids.append(token_type_id)
            max_len = max(max_len, input_id.shape[0])

        if padding:
            input_ids, attention_masks, token_type_ids = self._padding(input_ids, attention_masks, token_type_ids, max_len, return_tensors)
        else:
            if return_tensors == 'np':
                input_ids = numpy.array(input_ids, dtype=object)
                attention_masks = numpy.array(attention_masks, dtype=object)
                token_type_ids = numpy.array(token_type_ids, dtype=object)
            else:
                input_ids = [input_ids]
                attention_masks = [attention_masks]
                token_type_ids = [token_type_ids]

        if reduce_axis:
            input_ids = input_ids[0]
            attention_masks = attention_masks[0]
            token_type_ids = token_type_ids[0]

        if self._token_type_ids:
            return AiliaTokenizerResultWithTokenTypeIds(input_ids=input_ids, attention_mask=attention_masks, token_type_ids=token_type_ids)
        else:
            return AiliaTokenizerResult(input_ids=input_ids, attention_mask=attention_masks)

    def decode(self, input_ids, skip_special_tokens = False):
        if not self._initialized:
            raise AiliaTokenizerError("from_pretrained not called.", -1)
        if skip_special_tokens != True:
            raise AiliaTokenizerError("skip_special_tokens must be true.", -1)
        text = self.dll.Decode(self.instance, input_ids, len(input_ids))
        return text

    def __call__(self, text, padding=True, truncation=True, return_tensors=None, max_length = None):
        return self.encode(text, padding, truncation, return_tensors, max_length)

    def convert_tokens_to_ids(self, tokens):
        is_str = False
        if type(tokens) == str:
            tokens = [tokens]
            is_str = True

        ids = []
        for token in tokens:
            id = self.encode(token)["input_ids"]
            ids.append(id[1])
        
        if is_str:
            return ids[0]

        return ids

# ==============================================================================
# Whisper
# ==============================================================================

class WhisperTokenizer(BaseTokenizer):
    def from_pretrained():
        target = WhisperTokenizer()
        mode = AILIA_TOKENIZER_TYPE_WHISPER
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target._initialized = True
        target._pad_token_id = 50257 # PADではなくEOSでPADする
        return target

# ==============================================================================
# Clip
# ==============================================================================

class CLIPTokenizer(BaseTokenizer):
    def from_pretrained():
        target = CLIPTokenizer()
        mode = AILIA_TOKENIZER_TYPE_CLIP
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target._initialized = True
        target._pad_token_id = 49407 # PADではなくEOSでPADする
        return target

# ==============================================================================
# XLMRoberta
# ==============================================================================

class XLMRobertaTokenizer(BaseTokenizer):
    def from_pretrained(model_path):
        target = XLMRobertaTokenizer()
        mode = AILIA_TOKENIZER_TYPE_XLM_ROBERTA
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, model_path)
        target._initialized = True
        target._pad_token_id = 1 # fairseqにpadのIDがない
        return target

# ==============================================================================
# Marian
# ==============================================================================

class MarianTokenizer(BaseTokenizer):
    def from_pretrained(model_path):
        target = MarianTokenizer()
        mode = AILIA_TOKENIZER_TYPE_MARIAN
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, model_path)
        target._initialized = True
        target._pad_token_id = 32000
        return target

# ==============================================================================
# BertJapaneseTokenizer
# ==============================================================================

class BertJapaneseWordPieceTokenizer(BaseTokenizer):
    def from_pretrained(dict_path, vocab_path):
        target = BertJapaneseWordPieceTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT_JAPANESE_WORDPIECE
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenDictionaryFile(target.instance, dict_path)
        target.dll.OpenVocabFile(target.instance, vocab_path)
        target._initialized = True
        target._pad_token_id = target.dll.Encode(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        return target

class BertJapaneseCharacterTokenizer(BaseTokenizer):
    def from_pretrained(dict_path, vocab_path):
        target = BertJapaneseCharacterTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT_JAPANESE_CHARACTER
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenDictionaryFile(target.instance, dict_path)
        target.dll.OpenVocabFile(target.instance, vocab_path)
        target._initialized = True
        target._pad_token_id = target.dll.Encode(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        return target

# ==============================================================================
# T5
# ==============================================================================

class T5Tokenizer(BaseTokenizer):
    def from_pretrained(model_path):
        target = T5Tokenizer()
        mode = AILIA_TOKENIZER_TYPE_T5
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, model_path)
        target._initialized = True
        target._pad_token_id = 0
        return target

# ==============================================================================
# Roberta
# ==============================================================================

class RobertaTokenizer(BaseTokenizer):
    def from_pretrained(vocab_path, marges_path):
        target = RobertaTokenizer()
        mode = AILIA_TOKENIZER_TYPE_ROBERTA
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, vocab_path)
        target.dll.OpenMergeFile(target.instance, marges_path)
        target._initialized = True
        target._pad_token_id = target.dll.Encode(target.instance, "[PAD]").astype(numpy.int64)[1]
        return target

# ==============================================================================
# BERT
# ==============================================================================

class BertUncasedTokenizer(BaseTokenizer):
    def from_pretrained(vocab_path):
        target = BertUncasedTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT_UNCASED
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, vocab_path)
        target._initialized = True
        target._pad_token_id = target.dll.Encode(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        return target

class BertCasedTokenizer(BaseTokenizer):
    def from_pretrained(vocab_path):
        target = BertCasedTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT_CASED
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, vocab_path)
        target._initialized = True
        target._pad_token_id = target.dll.Encode(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        return target
