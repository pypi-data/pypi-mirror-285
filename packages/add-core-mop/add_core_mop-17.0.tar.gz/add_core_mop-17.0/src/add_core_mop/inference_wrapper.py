import importlib
import json
import sys
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import numpy as np
from src.add_core_mop.base_model_wrapper import BaseModelWrapper, MopInferenceInput
from src.add_core_mop.constant import CM_MODEL_WRAPPER_NAME
from pyraisdk.dynbatch import BaseModel, DynamicBatchModel

for path in sys.path:
    print(path)

current_dir = os.path.dirname(os.path.abspath(__file__))

models_dir = None
while current_dir != os.path.dirname(current_dir):
    potential_models_dir = os.path.join(current_dir, 'models')
    if os.path.exists(potential_models_dir):
        models_dir = potential_models_dir
        break
    current_dir = os.path.dirname(current_dir)

inference_module = None
inference_modules = []
ModelWrappers = {}

if models_dir:
    for dir_name in os.listdir(models_dir):
        dir_path = os.path.join(models_dir, dir_name)
        if os.path.isdir(dir_path):
            src_path = os.path.join(dir_path, 'src')
            if os.path.exists(src_path):
                for file_name in os.listdir(src_path):
                    if file_name.startswith('inference') and file_name.endswith('.py'):
                        prefix = "inference-"
                        module_name = file_name[:-3]  # 去掉 .py 后缀
                        module_version = module_name[len(prefix):]
                        module_path = f"{src_path.replace(os.path.sep, '.')}.{module_name}"
                        each_inference_module = importlib.import_module(module_path)
                        print(f"Imported module: {module_path} as {module_name}")

                        each_wrappers = []
                        for i in inference_module.__dict__.keys():
                            if hasattr(inference_module.__dict__.get(i), '__bases__'):
                                if BaseModelWrapper in inference_module.__dict__.get(i).__bases__[0].__bases__:
                                    each_wrappers.append(getattr(inference_module, i))
                                if BaseModelWrapper in inference_module.__dict__.get(i).__bases__:
                                    each_wrappers.append(getattr(inference_module, i))

                        EachModelWrapper = [i for i in each_wrappers if i.__module__.startswith(CM_MODEL_WRAPPER_NAME)][0]
                        ModelWrappers[module_version] = EachModelWrapper
else:
    inference_module = importlib.import_module(CM_MODEL_WRAPPER_NAME)


wrappers = []
for i in inference_module.__dict__.keys():
    if hasattr(inference_module.__dict__.get(i), '__bases__'):
        if BaseModelWrapper in inference_module.__dict__.get(i).__bases__[0].__bases__:
            wrappers.append(getattr(inference_module, i))
        if BaseModelWrapper in inference_module.__dict__.get(i).__bases__:
            wrappers.append(getattr(inference_module, i))

ModelWrapper = [i for i in wrappers if i.__module__ == CM_MODEL_WRAPPER_NAME][0]


class MOPInferenceWrapper:
    def __init__(self, base_model_wrapper: BaseModelWrapper) -> None:
        self.model_wrapper = base_model_wrapper

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
base_model_wrapper: BaseModelWrapper = ModelWrapper()
inference_wrappers: Dict[str, MOPInferenceWrapper] = {}
inference_wrapper: MOPInferenceWrapper = MOPInferenceWrapper(base_model_wrapper)
batch_size: Optional[int] = None
triggered_by_mop: bool = False


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
    global base_model_wrapper
    p = Path(model_root)

    if check_model_directory(p):
        models_dir = p / 'models'
        index = 0
        for child in models_dir.iterdir():

            model_name = child.stem
            wrapper = MOPInferenceWrapper(ModelWrappers[model_name])
            model_each_root = os.path.join(str(child), 'model')

            print(f"test number: {index}, model_each_root: {model_each_root}")
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
