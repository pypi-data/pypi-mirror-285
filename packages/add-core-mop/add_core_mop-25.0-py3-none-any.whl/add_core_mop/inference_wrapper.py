import importlib
import json
import sys
import os
import pkgutil
from typing import Any, Dict, List, Optional
from pathlib import Path
import numpy as np
from add_core_mop.base_model_wrapper import BaseModelWrapper, MopInferenceInput
from add_core_mop.constant import CM_MODEL_WRAPPER_NAME, SINGLETON_NAME
from pyraisdk.dynbatch import BaseModel, DynamicBatchModel
import importlib.util

modules = {}

valid_score_paths = set()
first_score_path = ""

for path in sys.path:
    if not os.path.isdir(path):
        continue
    for root, dirs, files in os.walk(path):
        if os.path.basename(root) == 'score':
            valid_score_paths.add(root)

if len(valid_score_paths) == 1:
    first_score_path = next(iter(valid_score_paths))
    print(f"Found the unique 'score' directory: {first_score_path}")
elif len(valid_score_paths) == 0:
    print("No 'score' directory found.")
else:
    raise Exception("More than one 'score' directory found. Please check the paths.")

for subdir in next(os.walk(first_score_path))[1]:
    subdir_path = os.path.join(first_score_path, subdir)
    inference_file_path = os.path.join(subdir_path, CM_MODEL_WRAPPER_NAME + '.py')

    if os.path.isfile(inference_file_path):
        try:
            module_name = f'{CM_MODEL_WRAPPER_NAME}'

            spec = importlib.util.spec_from_file_location(module_name, inference_file_path)
            if spec is None:
                raise ImportError(f"Cannot load spec for module {module_name}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            spec.loader.exec_module(module)
            modules[subdir] = module
            print(f"Successfully imported {CM_MODEL_WRAPPER_NAME} module from {inference_file_path}")
        except Exception as e:
            print(f"Failed to import module {CM_MODEL_WRAPPER_NAME} from {inference_file_path}: {e}")

for key, module in modules.items():
    print(f"{key}: {module}")

inference_modules = modules
ModelWrapper = None
ModelWrappers = {}

if inference_modules:
    for folder, module in inference_modules.items():
        print(f"Folder: {folder}, Module: {module}")
else:
    print("No modules found with the name:", CM_MODEL_WRAPPER_NAME)

if len(inference_modules) == 1:
    inference_module = next(iter(inference_modules.values()))
    wrappers = []
    for i in inference_module.__dict__.keys():
        if hasattr(inference_module.__dict__.get(i), '__bases__'):
            if BaseModelWrapper in inference_module.__dict__.get(i).__bases__[0].__bases__:
                wrappers.append(getattr(inference_module, i))
            if BaseModelWrapper in inference_module.__dict__.get(i).__bases__:
                wrappers.append(getattr(inference_module, i))

    ModelWrappers[SINGLETON_NAME] = [i for i in wrappers if i.__module__ == CM_MODEL_WRAPPER_NAME][0]
    ModelWrapper = ModelWrappers[SINGLETON_NAME]
else:
    for folder, module in inference_modules.items():
        wrappers = []
        for i in module.__dict__.keys():
            if hasattr(module.__dict__.get(i), '__bases__'):
                if BaseModelWrapper in module.__dict__.get(i).__bases__[0].__bases__:
                    wrappers.append(getattr(module, i))
                if BaseModelWrapper in module.__dict__.get(i).__bases__:
                    wrappers.append(getattr(module, i))

        EachModelWrapper = [i for i in wrappers if i.__module__ == CM_MODEL_WRAPPER_NAME][0]
        ModelWrappers[folder] = EachModelWrapper


class MOPInferenceWrapper:
    def __init__(self, base_model_wrapper_inner: BaseModelWrapper) -> None:
        self.model_wrapper = base_model_wrapper_inner

    def init(self, model_root: str) -> None:
        self.model_wrapper.init(model_root)

    def run(self, item: Dict, triggered_by_mop) -> Dict:
        if not triggered_by_mop:
            model_output = self.model_wrapper.inference(item)
            return [model_output]
        else:
            mop_input = MopInferenceInput().from_dict(item)
            model_input = self.model_wrapper.convert_mop_input_to_model_input(mop_input)
            model_output = self.model_wrapper.inference(model_input)
            mop_output = self.model_wrapper.convert_model_output_to_mop_output(model_output)

            return mop_output.output

    def run_batch(self, items: List[dict], triggered_by_mop: bool, batch_size: Optional[int] = None) -> List[dict]:
        if not triggered_by_mop:
            model_outputs = self.model_wrapper.inference_batch(items)
            return model_outputs
        else:
            model_inputs = [
                self.model_wrapper.convert_mop_input_to_model_input(MopInferenceInput().from_dict(item)) for item
                in
                items]

            model_outputs = self.model_wrapper.inference_batch(model_inputs)

            mop_outputs = [self.model_wrapper.convert_model_output_to_mop_output(model_output).output for
                           model_output in model_outputs]
            return mop_outputs


batch_model: Optional[DynamicBatchModel] = None
base_model_wrapper: Optional[BaseModelWrapper] = None
inference_wrapper: Optional[MOPInferenceWrapper] = None
inference_wrappers: Dict[str, MOPInferenceWrapper] = {}
batch_size: Optional[int] = None
triggered_by_mop: bool = False

if len(inference_modules) == 1:
    base_model_wrapper: BaseModelWrapper = ModelWrappers[SINGLETON_NAME]()
    inference_wrapper: MOPInferenceWrapper = MOPInferenceWrapper(base_model_wrapper)


class WrapModel(BaseModel):
    def predict(self, items: List[Any]) -> List[Any]:
        return inference_wrapper.run_batch(items, triggered_by_mop=triggered_by_mop, batch_size=batch_size)


class NumpyJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return json.JSONEncoder.default(self, obj)


"""
This is init function.

Parameters:
    model_root - root where the model file exists

Returns:
    None
"""


def check_model_directory(directory):
    directories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    if 'models' in directories:
        return True
    else:
        return False


def mop_init(model_root, dynamic_batch_args: None):
    global batch_model
    global batch_size
    p = Path(model_root)

    if check_model_directory(p):
        models_dir = p / 'models'
        index = 0
        for child in models_dir.iterdir():
            if child.name == 'score':
                continue

            model_name = child.stem
            wrapper = MOPInferenceWrapper(ModelWrappers[model_name]())
            model_each_root = os.path.join(str(child), 'model')
            wrapper.init(model_each_root)
            inference_wrappers[model_name] = wrapper
            index = index + 1
    else:
        print(f"else case： {model_root}")
        inference_wrapper.init(model_root)

    # assign environment variable
    if dynamic_batch_args is not None:
        os.environ["PYRAISDK_MAX_BATCH_SIZE"] = str(dynamic_batch_args.get('max_batch_size'))
        os.environ["PYRAISDK_IDLE_BATCH_SIZE"] = str(dynamic_batch_args.get('idle_batch_size'))
        os.environ["PYRAISDK_MAX_BATCH_INTERVAL"] = str(dynamic_batch_args.get('max_batch_interval'))

        batch_model = DynamicBatchModel(WrapModel())
        batch_size = dynamic_batch_args.get('max_batch_size')


"""
This is run function.

Parameters:
    raw_data - row input data to do inference
    triggered_by_mop - whether the function is triggered by mop
    **kwargs - dynamic parameter

Returns:
    inference result
    {"holder_type":"8fb40941-9eb7-4bb2-8242-b266c25f1251", "data": {"data": ["hello, Sample Post Data!"]}}
"""


def mop_run(raw_data: any, is_mop_triggered: bool = False, **kwargs) -> any:
    global triggered_by_mop
    global inference_wrapper
    triggered_by_mop = is_mop_triggered
    if isinstance(raw_data, dict) and 'holder_type' in raw_data:
        holder_type = raw_data['holder_type']
        inference_wrapper = inference_wrappers[holder_type]
        raw_data = raw_data['data']
        print("mop_run raw_data contains 'holder_type' key")
    else:
        print("mop_run raw_data is not a dictionary or does not contain 'holder_type' key")

    if batch_model is not None:
        print("mop_run batch_model case")
        raw_data = raw_data if isinstance(raw_data, list) else [raw_data]
        inference_result = batch_model.predict(raw_data, timeout=60)
        return inference_result
    if isinstance(raw_data, dict):
        print("mop_run dict case")
        inference_result = inference_wrapper.run(raw_data, triggered_by_mop)
        return inference_result
    if isinstance(raw_data, list):
        print("mop_run list case")
        inference_result = inference_wrapper.run_batch(raw_data, triggered_by_mop=triggered_by_mop)
        return inference_result
    raise Exception("Invalid input data format")


def build_response(inference_result: any) -> any:
    if isinstance(inference_result, dict):
        output_str = json.dumps(inference_result, cls=NumpyJsonEncoder)
        return json.loads(output_str)
    if isinstance(inference_result, list):
        res = [item.__dict__ if hasattr(inference_result, '__dict__') else item for item in inference_result]
        output_str = json.dumps(res, cls=NumpyJsonEncoder)
        return json.loads(output_str)
    if hasattr(inference_result, '__dict__'):
        output_str = json.dumps(inference_result.__dict__, cls=NumpyJsonEncoder)
        return json.loads(output_str)
    return inference_result


def get_model_wrapper():
    return inference_wrapper


if __name__ == "__main__":
    model_root = "D:\code\carnegie-mop\sample\model"
    # mop_init(model_root, None)
    #
    # text_dict = {"text": "354"}
    # res = mop_run(text_dict, True)
    # print(res)
    # text_dict = [{"text": "354"}]
    # res = mop_run(text_dict, True)
    # print(res)

    dynamic_batch = {
        'enable': True,
        'max_batch_size': 12,
        'idle_batch_size': 3,
        'max_batch_interval': 0.2
    }

    mop_init(model_root, dynamic_batch)

    text_dict = {"text": "354"}
    res = mop_run(text_dict, True)
    print(res)
