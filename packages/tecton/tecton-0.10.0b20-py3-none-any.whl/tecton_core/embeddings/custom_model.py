from __future__ import annotations

import importlib
from collections import abc
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import MutableMapping
from typing import Optional

import numpy
import pyarrow
import torch

from tecton_core import data_types
from tecton_core import schema
from tecton_core.errors import TectonInternalError


_LOAD_FN_NAME = "load_context"
_PRE_PROCESSOR_FN_NAME = "preprocessor"
_POST_PROCESSOR_FN_NAME = "postprocessor"
_RESERVED_MODEL_CONTEXT_KEY = "model"
_TECTON_MODEL_SPEC_NAME = "_tecton_custom_model"

_CONTEXT_PARAM = Mapping[str, Any]
_PRE_PROCESSOR_FN = Optional[Callable[[Mapping[str, numpy.ndarray], _CONTEXT_PARAM], Mapping[str, torch.Tensor]]]
_POST_PROCESSOR_FN = Optional[Callable[[torch.Tensor, _CONTEXT_PARAM], torch.Tensor]]

# TODO(jiadong): Implement this as a function to handle complex data type.
_TECTON_TYPE_TO_ARROW_TYPE: Mapping[data_types.DataType, pyarrow.DataType] = {
    data_types.Int32Type(): pyarrow.int32(),
    data_types.Int64Type(): pyarrow.int64(),
    data_types.Float32Type(): pyarrow.float32(),
    data_types.Float64Type(): pyarrow.float64(),
    data_types.StringType(): pyarrow.string(),
}


def _default_pytorch_preprocessor(input: Mapping[str, numpy.ndarray]) -> Mapping[str, torch.Tensor]:
    return {name: torch.tensor(array) for name, array in input.items()}


# TODO(jiadong): CustomModelContainer is pytorch based currently. It can be refactored to a structure that has a `BaseModelContainer` and framework specific model container becomes subclasses of it. The base class can have `load` function implmeneted which is framework agonistic and each subclass implements the `predict` function.
class CustomModelContainer:
    _data_dir: Path

    # Late init params
    _context: MutableMapping[str, Any]

    _preprocessor: _PRE_PROCESSOR_FN = None
    _postprocessor: _POST_PROCESSOR_FN = None

    def __init__(self, data_dir: str) -> None:
        self._data_dir = Path(data_dir)
        self._context = {}

    def load(self):
        model_module = self._load_model_module()

        _load_fn = getattr(model_module, _LOAD_FN_NAME, None)
        if not _load_fn:
            msg = f"`{_LOAD_FN_NAME}` function is missing in the model repo"
            raise AttributeError(msg)

        _load_fn(self._data_dir, self._context)

        model = self._context.get(_RESERVED_MODEL_CONTEXT_KEY, None)
        if not model:
            msg = "No 'model' found in the context. `load` function should initialize the model and put it in the context with 'model' key."
            raise ValueError(msg)

        self._preprocessor = getattr(model_module, _PRE_PROCESSOR_FN_NAME, None)
        self._postprocessor = getattr(model_module, _POST_PROCESSOR_FN_NAME, None)

    def _load_model_module(self):
        # TODO(jiadong): Read main python file name from ModelArtifactInfo instead of using hardcoded `model.py`
        spec = importlib.util.spec_from_file_location(_TECTON_MODEL_SPEC_NAME, self._data_dir / "model.py")
        model_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model_module)
        return model_module

    def predict(self, input: pyarrow.RecordBatch) -> torch.Tensor:
        numpy_dict = {name: column.to_numpy() for name, column in zip(input.schema.names, input.columns)}
        if self._preprocessor:
            input = self._preprocessor(numpy_dict, self._context)
        else:
            input = _default_pytorch_preprocessor(numpy_dict)

        if not isinstance(input, abc.Mapping):
            msg = f"`preprocessor` needs to return a 'Mapping[str, torch.Tensor]', but received '{type(input)}'"
            raise TypeError(msg)

        for k, v in input.items():
            if not isinstance(v, torch.Tensor):
                msg = f"`preprocessor` needs to return a 'Mapping[str, torch.Tensor]' but detected '{k}' returned by preprocessor is an instance of type {type(v)}."
                raise TypeError(msg)

        model = self._context[_RESERVED_MODEL_CONTEXT_KEY]
        with torch.no_grad():
            output = model(**input)

        if self._postprocessor:
            output = self._postprocessor(output, self._context)

            if not isinstance(output, torch.Tensor):
                msg = (
                    f"`postprocessor` needs to return a 'torch.Tensor' but detected an instance of type {type(output)}"
                )
                raise TypeError(msg)

        return output


# TODO(EMBED-117): Bisect input data if the inference OOM.
def custom_model_inference(
    batch: pyarrow.RecordBatch,
    *,
    model: CustomModelContainer,
    input_columns: List[schema.Column],
    output_column: schema.Column,
    cuda_device: str,
    model_input_schema: List[schema.Column],
) -> pyarrow.RecordBatch:
    with torch.device(cuda_device):
        input_batch = batch.select([col.name for col in input_columns])
        model_input_names = [col.name for col in model_input_schema]

        # Rename input columns to model input schema column names.
        # TODO(jiadong): we can use pyarrow built-in `rename_columns` when we upgrade pyarrow to 16.0+.
        input_columns = [input_batch.column(i) for i in range(input_batch.num_columns)]
        input_batch = pyarrow.RecordBatch.from_arrays(input_columns, model_input_names)

        output = model.predict(input_batch)
        output = output.cpu().numpy()

        # TODO(jiadong): Following check only works scalar types. If the output type is array, it currently fails here. Will iterate this check and a test case to cover array ouput.
        num_of_rows = batch.num_rows
        if output.shape == (num_of_rows,) or output.shape == (num_of_rows, 1):
            output = output.reshape(-1)
        elif output.shape != (1, num_of_rows):
            msg = f"Expect the shape of output tensor to be either (1, {num_of_rows}) or ({num_of_rows}, 1), but got {output.shape}"
            raise TectonInternalError(msg)

        output = pyarrow.array(list(output), type=_TECTON_TYPE_TO_ARROW_TYPE[output_column.dtype])

        batch_with_results = pyarrow.RecordBatch.from_arrays(
            [*batch.columns, output],
            schema=batch.schema.append(pyarrow.field(output_column.name, output.type)),
        )
    return batch_with_results


# TODO(jiadong): Implement custom model batch function.
def default_custom_batch_fn(
    batch: pyarrow.RecordBatch,
) -> Iterator[pyarrow.RecordBatch]:
    yield batch


@dataclass
class CustomModelInferenceFuncConfig:
    _model_dir: str
    _extra_kwargs: Mapping[str, Any]
    _cuda_device: str

    # Note: _final_kwargs is a late init object.
    _final_kwargs: Optional[Mapping[str, Any]] = None

    @classmethod
    def create(
        cls,
        model_dir: str,
        cuda_device: str,
        input_columns: List[schema.Column],
        output_column: schema.Column,
        model_input_schema: List[schema.Column],
    ) -> CustomModelInferenceFuncConfig:
        return cls(
            _model_dir=model_dir,
            _cuda_device=cuda_device,
            _extra_kwargs=MappingProxyType(
                {
                    "cuda_device": cuda_device,
                    "input_columns": input_columns,
                    "output_column": output_column,
                    "model_input_schema": model_input_schema,
                }
            ),
        )

    def load(self):
        model_container = CustomModelContainer(data_dir=self._model_dir)
        with torch.device(self._cuda_device):
            model_container.load()

        self._final_kwargs = MappingProxyType(dict(model=model_container, **self._extra_kwargs))
        return self

    def kwargs(self) -> Mapping[str, Any]:
        if self._final_kwargs is None:
            msg = "`load` must be called prior to calling `kwargs`."
            raise ValueError(msg)
        return self._final_kwargs


@dataclass
class CustomModelBatchFuncConfig:
    # TODO(jiadong): Add necessary params to batch function config such as user-provided batch size.

    # Note: _final_kwargs is a late init object.
    _final_kwargs: Optional[Mapping[str, Any]] = None

    @classmethod
    def create(cls) -> CustomModelBatchFuncConfig:
        return cls()

    def load(self):
        self._final_kwargs = MappingProxyType({})
        return self

    def kwargs(self) -> Mapping[str, Any]:
        if self._final_kwargs is None:
            msg = "`load` must be called prior to calling `kwargs`."
            raise ValueError(msg)
        return self._final_kwargs
