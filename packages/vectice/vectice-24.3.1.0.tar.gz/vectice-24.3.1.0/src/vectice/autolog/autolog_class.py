from __future__ import annotations

import ast
import logging
import os
import re
import tempfile
from base64 import b64decode
from collections import OrderedDict
from functools import reduce
from importlib.util import find_spec
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar

import PIL.Image as Image
from typing_extensions import TypedDict

from vectice.api.http_error_handlers import VecticeException
from vectice.autolog.autolog_asset_factory import AssetFactory
from vectice.autolog.model_library import ModelLibrary
from vectice.models.dataset import Dataset
from vectice.models.model import Model
from vectice.models.table import Table
from vectice.utils.code_parser import FilePathVisitor, VariableVisitor, parse_comments, preprocess_code

if TYPE_CHECKING:
    from tempfile import TemporaryDirectory

    from catboost.core import CatBoost
    from keras import Model as KerasModel  # type: ignore[reportMissingImports]
    from keras.layers import InputLayer  # type: ignore[reportMissingImports]
    from lightgbm.basic import Booster
    from pandas import DataFrame
    from pyspark.sql import DataFrame as SparkDF
    from sklearn.base import BaseEstimator
    from sklearn.pipeline import Pipeline
    from statsmodels.base.wrapper import ResultsWrapper
    from torch.nn import Module as TorchModel

    # Vectice Object types
    from vectice.autolog.asset_services import TVecticeObjects
    from vectice.models import Phase
    from vectice.models.resource.metadata.db_metadata import TableType

    ModelTypes = TypeVar("ModelTypes", BaseEstimator, Booster, CatBoost, KerasModel, TorchModel, Pipeline)
    TModel = TypedDict(
        "TModel",
        {
            "variable": str,
            "model": ModelTypes,
            "library": ModelLibrary,
            "metrics": dict,
        },
    )
    DataframeTypes = TypeVar("DataframeTypes", SparkDF, DataFrame)
    TDataset = TypedDict(
        "TDataset",
        {"variable": str, "dataframe": DataframeTypes, "type": TableType},
    )


try:
    from IPython.core.getipython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "To use autolog, please install extra dependencies from vectice package using '%pip install vectice[autolog]'"
    ) from None

is_plotly = False
is_matplotlib = False
if find_spec("plotly") is not None:
    is_plotly = True

if find_spec("matplotlib") is not None:
    is_matplotlib = True

_logger = logging.getLogger(__name__)

NOTEBOOK_CELLS = {}
GRAPHS = []
running = False


def _get_cell_id_and_plot_name(ipython: Any) -> tuple[str, str]:
    # Collab
    # cell_id = IP.get_parent()["metadata"]["colab"]["cell_id"]

    # Databricks
    # cell_id = IP.get_parent()["metadata"]["commandId"]
    cell_metadata = ipython.get_parent()["metadata"]  # type: ignore
    if cell_metadata.get("colab") and "cell_id" in cell_metadata.get("colab"):  # type: ignore
        cell_id = cell_metadata["colab"]["cell_id"]
        plot_name = f"vect_plot_{cell_id}"
    elif cell_metadata.get("commandId"):  # type: ignore
        cell_id = cell_metadata["commandId"]
        plot_name = f"vect_plot_{cell_id[-6:]}"
    else:
        cell_id = cell_metadata["cellId"]
        plot_name = (
            f"vect_plot_{cell_id.split('-')[-1]}"
            if "vscode-notebook-cell" not in cell_id
            else f"vect_plot_{cell_id.split('ipynb#')[-1]}"
        )
    return cell_id, plot_name


def start_listen():
    ipython = get_ipython()  # type: ignore

    def _notebook_cell_content_update():
        global NOTEBOOK_CELLS

        cell_id, _ = _get_cell_id_and_plot_name(ipython)
        cell_content = ipython.get_parent()["content"]["code"]  # type: ignore
        NOTEBOOK_CELLS[cell_id] = cell_content

    def _check_graph_libraries(cell_content: str) -> bool:
        # check for imports and recommended aliases
        if "matplotlib" in cell_content or "plt" in cell_content:
            return True
        if "seaborn" in cell_content or "sns" in cell_content:
            return True
        if "plotly" in cell_content or "px" in cell_content:
            _logger.warning("Plotly is not supported currently.")
            return False
        return False

    def _get_graphs(remove: bool) -> list[str]:

        # check for a valid matplotlib extension, this covers seaborn aswell
        def is_valid_matplotlib_extension(filename: str) -> bool:
            valid_extensions = {".png", ".pdf", ".ps", ".eps", ".svg", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
            _, extension = os.path.splitext(filename)
            return extension.lower() in valid_extensions

        cell_content = ipython.get_parent()["content"]["code"]  # type: ignore
        # get commented lines and not lines with comments
        lines = cell_content.split("\n")
        matched_lines = "\n".join(
            [line for line in lines if (remove and re.search(r"^#.*", line)) or not re.search(r"^#.*", line)]
        )
        cell = preprocess_code(matched_lines)
        tree = ast.parse(cell)
        visitor = FilePathVisitor(is_graph_path=True)
        visitor.visit(tree)

        graph_paths = []
        for graph in visitor.file_paths:
            if is_valid_matplotlib_extension(graph) and "http" not in graph:
                graph_paths.append(graph)
        return graph_paths

    def _remove_commented_graphs():
        # removes a saved graph if commented out
        graphs = _get_graphs(True)

        for graph in graphs:
            if graph in GRAPHS:
                GRAPHS.remove(graph)

    def _get_saved_graphs() -> list[str]:
        graphs = _get_graphs(False)

        for graph in graphs:
            if graph not in GRAPHS:
                GRAPHS.append(graph)
        return graphs

    def _capture_graph():
        # globals allows the function to get the variable, or it outside it's scope
        global GRAPHS
        # running variable prevents recursion
        global running

        cell_content = ipython.get_parent()["content"]["code"]  # type: ignore
        # we generate plot names that are then used in the cell magic
        _, plot_name = _get_cell_id_and_plot_name(ipython)
        # check if graphs have been commented out before getting saved graphs
        _remove_commented_graphs()
        # get the saved graphs
        saved_graphs = _get_saved_graphs()
        # check if running already and that there aren't saved graphs as saved graphs are the priority
        if not running and not saved_graphs and _check_graph_libraries(cell_content):
            running = True
            # Remove autolog from cell so we don't create an extra iteration
            clean_cell = re.sub(r"autolog.*?$", "", cell_content)
            ipython.run_cell_magic("capture", plot_name, clean_cell)  # type: ignore
            # Check if plot name is already in our list as we don't want duplicates
            if plot_name not in GRAPHS:
                GRAPHS.append(plot_name)
        # remove event graph if save graph true, prevents double capturing
        if saved_graphs and plot_name in GRAPHS:
            GRAPHS.remove(plot_name)
        running = False

    def _load_ipython_extension():
        """Load the extension in IPython."""
        ipython.events.register("pre_execute", _capture_graph)  # type: ignore
        ipython.events.register("post_execute", _notebook_cell_content_update)  # type: ignore

    if ipython and not any([ev for ev in ipython.events.callbacks["post_execute"] if "_notebook_cell_content_update" in str(ev)]):  # type: ignore
        _load_ipython_extension()


####### Autolog logic
class Autolog:
    def __init__(
        self,
        phase: Phase | None,
        ipy: InteractiveShell,
        is_notebook: bool,
        create: bool = True,
        note: str | None = None,
        capture_schema_only: bool = True,
        capture_comments: bool = True,
    ):
        from vectice.services.phase_service import PhaseService

        if phase is None:
            raise ValueError("Login")

        if create is True:
            iteration = phase.create_iteration()
        else:
            iteration = PhaseService(
                phase._client  # pyright: ignore[reportPrivateUsage]
            ).get_active_iteration_or_create(phase)

        self._iteration = iteration
        self._iteration_service = iteration._service  # pyright: ignore[reportPrivateUsage]
        self._capture_schema_only = capture_schema_only
        self._ip = ipy
        self._local_vars = self._ip.user_global_ns
        self._capture_comments = capture_comments
        self._is_notebook = is_notebook
        self._cell_content = self._get_notebook_cell_content() if is_notebook is True else self._get_cell_content()
        self._vectice_data = self._get_variable_matches(self._local_vars)
        self._failed_assets = []

        # Get back objects to log
        self._assets = self._get_assets()
        graphs = self._get_graphs(is_notebook)

        if note:
            self._iteration_service.log_comment(note)
            _logger.info(f"Note logged in iteration {self._iteration.name!r}.")

        # Log objects

        self._log_assets(self._assets)

        if graphs:
            for graph in graphs:
                try:
                    self._iteration_service.log_image_or_file(graph)
                    graph = graph if isinstance(graph, str) else graph.filename
                    _logger.info(f"Graph {graph!r} logged in iteration {self._iteration.name!r}.")
                except Exception as e:
                    self._failed_assets.append({"reason": e, "asset": graph, "type": "Graph"})

        if len(self._failed_assets):
            _logger.warning("The following assets failed to log:")
        for failed_asset in self._failed_assets:
            _logger.warning(f"{failed_asset['type']} {failed_asset['asset']!r}, reason: {failed_asset['reason']}")

    def _get_variable_matches(self, local_vars: dict[str, Any]) -> list[dict[Any, Any]]:
        vectice_data = []
        all_cell_vars = set()
        all_vectice_calls = set()
        for cell_not_processed in self._cell_content:
            cell = preprocess_code(cell_not_processed)
            variable_comments = parse_comments(cell_not_processed) if self._capture_comments else []
            vectice_match = {}
            all_vars: OrderedDict[str, Any] = OrderedDict()

            vectice_match["cell"] = cell
            vectice_match["comments"] = variable_comments

            # Parse the cell content using the VariableVisitor
            try:
                tree = ast.parse(cell)
            except SyntaxError as err:
                raise SyntaxError(
                    "Autolog is unable to parse the code. Make sure all non-Python syntax, such as bash commands, are properly indented and preceded by '%' or '!'. If the error persist, please contact your sales representative."
                ) from err

            visitor = VariableVisitor()
            visitor.visit(tree)
            # Keep set of all vectice call vars
            all_vectice_calls = all_vectice_calls.union(visitor.vectice_call_vars)
            # Update all_vars with variable names and values in the order they appear
            for var in visitor.variables:
                if var in local_vars and var not in all_vars:
                    all_vars[var] = local_vars[var]
                # check if the var exists in a previous cell for autolog.notebook before the vectice object uses the var
                if self._is_notebook:
                    all_vectice_calls = {vect_var for vect_var in all_vectice_calls if vect_var not in all_cell_vars}
                # Keep track of all vars
                all_cell_vars.add(var)

            vectice_match["variables"] = all_vars
            vectice_data.append(vectice_match)
        clean_vectice_data = []
        for data in vectice_data:
            for var in all_vectice_calls:
                # the order of cells misses vars
                if var in data["variables"]:
                    del data["variables"][var]
            # check that there are vars for the cell and then append or if there are comments
            if len(data["variables"]) >= 1 or len(data["comments"]) >= 1:
                clean_vectice_data.append(data)
        return clean_vectice_data

    def _get_notebook_cell_content(self) -> list[Any]:
        cell_id, _ = _get_cell_id_and_plot_name(self._ip)
        cell_content = self._ip.get_parent()["content"]["code"]  # type: ignore
        NOTEBOOK_CELLS[cell_id] = cell_content
        return list(NOTEBOOK_CELLS.values())

    def _get_cell_content(self) -> list[Any]:
        """Used by autolog cell to get the content of the cell. This is used to parse for variables."""
        cell_content = self._ip.get_parent()["content"]["code"]  # pyright: ignore[reportAttributeAccessIssue]
        if cell_content is None:
            raise ValueError("Failed to get cell content.")
        return [cell_content]

    def _get_asset_comments(self, comments: dict, key: str) -> tuple[str | None, str | None]:
        try:
            comment_before = comments["comment_matches_before"][key]["comment"]
        except KeyError:
            comment_before = None
        try:
            comment_after = comments["comment_matches_after"][key]["comment"]
        except KeyError:
            comment_after = None
        return comment_before, comment_after

    def _get_assets(self) -> list[TModel | TDataset | TVecticeObjects]:
        assets = []
        for data in self._vectice_data:
            for key in data["variables"].keys():
                # skip cell inputs/outputs
                if key.startswith("_"):
                    continue
                asset = data["variables"][key]
                try:
                    asset_information = AssetFactory.get_asset_service(key, asset, data).get_asset()
                    if asset_information is not None:
                        assets.append(asset_information)
                except VecticeException:
                    pass
        return self._deduplicate_assets(assets)

    def _deduplicate_assets(self, assets: list[dict[str, Any]]) -> list[TModel | TDataset | TVecticeObjects]:
        unique_dict = {}
        result = []

        for item in assets:
            variable = item["variable"]

            if variable not in unique_dict.keys():
                # If variable is not seen before, add it to the dictionary
                unique_dict[variable] = item
                result.append(item)
            else:
                existing_item = unique_dict[variable]
                if "vectice_object" in item:
                    existing_item["vectice_object"] = item["vectice_object"]
                elif "dataframe" in item:
                    existing_item["type"] = item["type"]
                else:
                    existing_item["library"] = item["library"]

                    # Merge dictionaries for the "metrics" attribute
                    existing_item_metrics = existing_item["metrics"]
                    item_metrics = item["metrics"]

                    for key, value in item_metrics.items():
                        existing_item_metrics[key] = value

        return result

    def _get_lightgbm_info(self, model: Booster) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            params = {
                key: value
                for key, value in model._get_loaded_param().items()  # pyright: ignore[reportPrivateUsage]
                if value is not None
            }
            return "lightgbm", params
        except AttributeError:
            return None, None

    def _get_model_library(self, model: ModelTypes):
        if "xgboost" in str(model.__class__):
            return "xgboost"
        if "lightgbm" in str(model.__class__):
            return "lightgbm"
        if str(model.__class__.__module__) == "sklearn.model_selection._search":
            return "sklearn-searchcv"
        return "sklearn"

    def _get_pipeline_steps(self, pipeline: Pipeline) -> dict:
        sklearn_pipeline = {}
        try:
            for step in pipeline.steps:
                step_name, step_obj = step
                if hasattr(step_obj, "named_transformers_"):
                    for k, v in step_obj.named_transformers_.items():
                        sklearn_pipeline[f"pipeline_{step_name}_{k}_steps"] = list(v.named_steps.keys())
            return sklearn_pipeline
        except Exception:
            return sklearn_pipeline

    def _get_pipeline_info(self, pipeline: Pipeline) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        # if pipeline with classifier
        try:
            from sklearn.base import is_classifier, is_regressor

            model = pipeline.steps[-1][-1]
            model_name = pipeline.steps[-1][0]
            if is_regressor(model) or is_classifier(model):
                model_params = {
                    f"{model_name}_{key}": value
                    for key, value in model.get_params().items()
                    if value is not None and bool(str(value))
                }
                model_params.update(self._get_pipeline_steps(pipeline))
                return "sklearn-pipeline", model_params
        except Exception:
            pass

        try:
            pipeline_params = {
                str(key): value
                for key, value in pipeline.get_params().items()
                if value is not None and bool(str(value))
            }
            return "sklearn-pipeline", pipeline_params
        except Exception:
            return None, None

    def _get_sklearn_or_xgboost_or_lgbm_info(
        self, model: BaseEstimator
    ) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        def _flatten_dict(params: dict, parent_key: str = "") -> dict:
            def _reduce_items(acc: list, item: tuple) -> list:
                key, value = item
                new_key = f"{parent_key}_{key}" if parent_key else key
                return (
                    [*acc, *_flatten_dict(value, new_key).items()]
                    if isinstance(value, dict)
                    else [*acc, (new_key, value)]
                )

            return dict(reduce(_reduce_items, params.items(), []))

        try:
            library = self._get_model_library(model)
            base_parameters = (
                model.best_estimator_  # pyright: ignore[reportAttributeAccessIssue]
                if library == "sklearn-searchcv"
                else model
            )
            params = _flatten_dict(
                {
                    str(key): value
                    for key, value in base_parameters.get_params().items()
                    if value is not None and bool(str(value))
                }
            )
            return library, params
        except AttributeError:
            return None, None

    def _format_keras_params(self, model: KerasModel) -> dict[str, Any]:
        params: dict[str, Any] = {}

        def _get_output_shape(layer: InputLayer) -> tuple:
            try:
                # Keras 2.15.1 & below
                return layer.output_shape
            except AttributeError:
                return layer.output.shape  # pyright: ignore[reportAttributeAccessIssue]

        for i, layer in enumerate(model.layers):
            output_shape = _get_output_shape(layer)
            params[f"Layer-{i}"] = {
                "name": layer.name,
                "param": layer.count_params(),
                "output shape": output_shape,
            }
        params["Total # of weights"] = model.count_params()

        return params

    def _get_keras_info(self, model: KerasModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            return "keras", self._format_keras_params(model)
        except Exception:
            return None, None

    def _get_all_cells_comments(self) -> list[dict]:
        # Get all comments from all cells
        all_comments_and_variables = []
        for data in self._vectice_data:
            if data["comments"]:
                for comments in data["comments"]:
                    all_comments_and_variables.append(comments)
        return all_comments_and_variables

    def _get_comments_before(
        self, all_comments_and_variables: list[dict], asset: TModel | TDataset | TVecticeObjects, comments_logged: list
    ):
        comments_to_log = []
        for data in all_comments_and_variables:
            # If we find the variable we log all the comments found
            if data["variable"] == asset["variable"]:
                return comments_to_log
            # We only want comments remaining
            if data["comment"] not in comments_logged:
                comments_to_log.append(data["comment"])
        # return nothing if we don't see the asset
        return []

    def _log_comments_before_asset(
        self, all_comments_and_variables: list[dict], asset: TModel | TDataset | TVecticeObjects, comments_logged: list
    ) -> list:
        # Get comments to log before each asset
        comments_before = self._get_comments_before(all_comments_and_variables, asset, comments_logged)
        # Log comments before each asset
        if comments_before:
            for comment in comments_before:
                if comment:
                    self._iteration_service.log_comment(comment)
            # Keep track of what's logged
            return comments_logged + comments_before
        return comments_logged

    def _log_remaining_comments(self, all_unique_comments: set, comments_logged: list) -> None:
        # Ensure last asset comments are filtered out
        all_comments_logged = set(comments_logged)
        still_comments_to_log = list(all_unique_comments - all_comments_logged)
        # Log remaining comments after last asset
        if still_comments_to_log:
            for comment in still_comments_to_log:
                if comment:
                    self._iteration_service.log_comment(comment)
        # Logging for comments captured
        all_comments_logged.discard(None)
        filtered_comments = list(filter(lambda comment: comment is not None, still_comments_to_log))
        if filtered_comments or all_comments_logged:
            _logger.info(f"Comments logged in iteration {self._iteration.name!r}.")

    def _format_pytorch_params(self, model: TorchModel) -> dict[str, Any]:
        params: dict[str, Any] = {}

        model_layers = list(model.children())
        # Get the parameters of each layer
        total_params = sum(param.numel() for param in model.parameters())
        for i, layer in enumerate(model_layers):
            layer_params = sum(param.numel() for param in layer.parameters())
            output_shape = layer.out_features if hasattr(layer, "out_features") else None
            params[f"Layer-{i}"] = {
                "name": layer._get_name(),  # pyright: ignore[reportPrivateUsage]
                "param": layer_params,
                "output shape": output_shape,
            }
            params["Total # of weights"] = total_params

        return params

    def _get_pytorch_info(self, model: TorchModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            return "torch", self._format_pytorch_params(model)
        except Exception:
            return None, None

    def _log_assets(
        self,
        assets: list[TModel | TDataset | TVecticeObjects],
    ):
        from vectice.services import iteration_service

        # all comments and variables
        all_comments_and_variables = self._get_all_cells_comments()
        # Unique comment set
        all_unique_comments = set([data["comment"] for data in all_comments_and_variables])
        # Keep track of what is logged
        comments_logged = []
        for asset in assets:
            try:
                comments_logged = self._log_comments_before_asset(all_comments_and_variables, asset, comments_logged)
                if "vectice_object" in asset:
                    self._log_vectice_asset(asset)
                elif "model" in asset:
                    self._log_model(asset)
                elif "dataframe" in asset:
                    self._log_dataset(asset)
            except Exception as e:
                self._failed_assets.append(
                    {"reason": e, "asset": asset["variable"], "type": "Model" if "model" in asset else "Dataset"}
                )
        # Log the remaining comments
        self._log_remaining_comments(all_unique_comments, comments_logged)
        # After logging, don't re-use code file
        iteration_service.lineage_file_id = None

    def _get_catboost_info(self, model: CatBoost) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            params = {str(key): value for key, value in model.get_all_params().items() if value is not None}
            return "catboost", params
        except AttributeError:
            return None, None

    def _get_statsmodel_info(self, model: ResultsWrapper) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        try:
            # model params
            model_params = {"model_type": model.model.__class__.__name__, "formula": model.model.formula}
            # statsmodels fitted/Resultswrapper
            params = {str(key): value for key, value in model.params.items() if value is not None}
            model_params.update(params)
            return "statsmodel", model_params
        except AttributeError:
            return None, None

    def _get_model_params(self, asset: TModel) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        library = asset["library"]
        model = asset["model"]

        if library is ModelLibrary.SKLEARN:
            return self._get_sklearn_or_xgboost_or_lgbm_info(model)  # pyright: ignore[reportArgumentType]
        if library is ModelLibrary.SKLEARN_PIPELINE:
            return self._get_pipeline_info(model)  # pyright: ignore[reportArgumentType]
        if library is ModelLibrary.LIGHTGBM:
            return self._get_lightgbm_info(model)  # pyright: ignore[reportArgumentType]
        if library is ModelLibrary.CATBOOST:
            return self._get_catboost_info(model)  # pyright: ignore[reportArgumentType]
        if library is ModelLibrary.KERAS:
            return self._get_keras_info(model)  # pyright: ignore[reportArgumentType]
        if library is ModelLibrary.STATSMODEL:
            return self._get_statsmodel_info(model)  # pyright: ignore[reportArgumentType]
        if library is ModelLibrary.PYTORCH:
            return self._get_pytorch_info(model)  # pyright: ignore[reportArgumentType]
        return None, None

    def _check_for_single_model(self):
        model_list = [asset for asset in self._assets if "model" in asset]
        if len(model_list) > 1:
            return False
        return True

    def _get_single_model_metrics(self) -> dict:
        from vectice.autolog.asset_services.metric_service import MetricService

        # get a single models metrics for notebook function
        metrics = {}
        if not self._check_for_single_model():
            return {}
        for data in self._vectice_data:
            cell_metrics = MetricService(data["cell"])._get_model_metrics(data)  # type: ignore[reportPrivateUsage]
            if cell_metrics:
                metrics.update(cell_metrics)
        return metrics

    def _log_model(self, model: TModel):
        temp_dir: TemporaryDirectory | None = None
        temp_file_path: str | None = None
        if model["library"] is ModelLibrary.KERAS:
            graph = None

            try:
                from keras.utils import plot_model  # type: ignore[reportMissingImports]

                temp_dir = tempfile.TemporaryDirectory()
                file_name = f"{model['variable']!s}_plot.png"
                temp_file_path = rf"{temp_dir.name}\{file_name}"
                graph = plot_model(model["model"], to_file=temp_file_path, show_shapes=True, show_layer_names=False)

                if graph is None:
                    temp_file_path = None
                    _logger.info(
                        "Unable to generate the model plot. Please check the 'plot_model' function from the Keras library is working correctly. Make sure that the graphviz and pydot packages are installed and configured properly."
                    )

            except Exception as e:
                _logger.info(
                    f"Unable to generate the model plot. Ensure that the Keras library is correctly installed and up-to-date. Error details: {e}"
                )

        model_object = model["model"]

        library, params = self._get_model_params(model)
        if model["library"] is ModelLibrary.STATSMODEL:
            algorithm = str(model_object.model.__class__).split(".")[-1]  # type: ignore[reportAttributeAccessIssue]
            model_summary = model_object.summary().as_text()  # type: ignore[reportAttributeAccessIssue]
        elif model["library"] is ModelLibrary.SKLEARN_PIPELINE:
            model_summary = None
            try:
                algorithm = str(model_object.steps[-1][-1].__class__).split(".")[-1]  # type: ignore[reportAttributeAccessIssue]
            except Exception:
                algorithm = str(model_object.__class__).split(".")[-1]
        else:
            algorithm = str(model_object.__class__).split(".")[-1]
            model_summary = None

        algorithm = algorithm.replace("'>", "")
        model_name = f"{self._iteration.phase.id}-{model['variable']}"
        # safety check, if no metrics and single model, get metrics
        model_metrics = model["metrics"] if model["metrics"] else self._get_single_model_metrics()
        temp_files = []
        if library == "sklearn-pipeline":
            temp_dir, temp_json_file_path, temp_html_file_path = self._get_sklearn_pipeline(model_object, model_name)
            if temp_json_file_path:
                temp_files.append(temp_json_file_path)
            if temp_html_file_path:
                temp_files.append(temp_html_file_path)

        if library == "sklearn-searchcv":
            tables = self._get_sklearn_search_results_and_space_tables(model_object, model_name)
            temp_files.extend(tables)

        self._iteration_service.log_model(
            Model(
                library=library,
                technique=algorithm,
                metrics=model_metrics,
                properties=params,
                name=model_name,
                predictor=model_object,
                attachments=temp_file_path or temp_files,
            )
        )
        _logger.info(f"Model {model_name!r} logged in iteration {self._iteration.name!r}.")

        if model_summary:
            # log statsmodel summary
            self._iteration_service.log_comment(model_summary)

        if temp_dir is not None:
            temp_dir.cleanup()

    def _get_sklearn_pipeline(
        self, pipeline: ModelTypes, model_name: str
    ) -> tuple[TemporaryDirectory[str], str, str] | tuple[None, None, None]:
        temp_dir = None
        try:
            from sklearn.utils import estimator_html_repr

            from vectice.utils.sklearn_pipe_utils import pipeline_to_json

            temp_dir = tempfile.TemporaryDirectory()
            json_file_name = f"{model_name!s}_pipeline.json"
            html_file_name = f"{model_name!s}_pipeline.html"
            temp_json_file_path = rf"{temp_dir.name}\{json_file_name}"
            temp_html_file_path = rf"{temp_dir.name}\{html_file_name}"

            pipeline_json = pipeline_to_json(pipeline)
            pipeline_html = estimator_html_repr(pipeline)
            if pipeline_json:
                with open(temp_json_file_path, "w") as json_file:
                    json_file.write(pipeline_json)

            if pipeline_html:
                with open(temp_html_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(pipeline_html)

            return temp_dir, temp_json_file_path, temp_html_file_path
        except Exception:
            return None, None, None

    def _get_sklearn_search_results_and_space_tables(self, model: ModelTypes, model_name: str) -> list:
        tables = []
        try:
            import pandas as pd

            results_df = pd.DataFrame(model.cv_results_)  # pyright: ignore[reportAttributeAccessIssue]
        except Exception:
            return tables
        try:
            tables.append(self._get_sklearn_search_space(model, model_name, results_df))
        except Exception:
            pass
        try:
            tables.append(self._get_sklearn_search_results(model, model_name, results_df))
        except Exception:
            pass
        return tables

    def _get_sklearn_search_results(self, model: ModelTypes, model_name: str, results_df: DataFrame) -> Table:
        sorted_df = results_df.sort_values(by="rank_test_score")
        top_scores_df = sorted_df.head(5)
        return Table(top_scores_df, name=f"{model_name}_search_results")

    def _get_sklearn_search_space(self, model: ModelTypes, model_name: str, results_df: DataFrame) -> Table:
        import pandas as pd

        param_columns = [col for col in results_df.columns if "param" in col and "params" not in col]
        data_dict = {}
        for param in param_columns:
            try:
                data_dict[f"{param} (min,max)"] = [[results_df[param].min(), results_df[param].max()]]
            except Exception:
                data_dict[f"{param} (uniques)"] = [results_df[param].unique()]

        params_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data_dict.items()]))
        # Transpose the DataFrame
        df_transposed = params_df.transpose()
        # Reset the index to move row headers into a column
        df_transposed_reset = df_transposed.reset_index()
        # Rename the index column for clarity
        df_transposed_reset = df_transposed_reset.rename(columns={"index": "Parameters", 0: "Values"})
        return Table(df_transposed_reset, name=f"{model_name}_search_space")

    def _log_vectice_asset(self, asset: TVecticeObjects) -> None:
        asset_to_log = asset["vectice_object"]
        asset_name = asset["variable"]
        if isinstance(asset_to_log, Dataset):
            dataset_name = asset_to_log.name if asset_to_log.name else asset_name
            self._iteration_service.log_dataset(asset_to_log)
            _logger.info(f"Dataset {dataset_name!r} logged in iteration {self._iteration.name!r}.")
        elif isinstance(asset_to_log, Table):
            table_name = asset_to_log.name if asset_to_log.name else asset_name
            self._iteration_service.log_table(asset_to_log)
            _logger.info(f"Table {table_name!r} logged in iteration {self._iteration.index!r}.")
        elif isinstance(asset_to_log, Model):
            model_name = asset_to_log.name if asset_to_log.name else asset_name
            self._iteration_service.log_model(asset_to_log)
            _logger.info(f"Model {model_name!r} logged in iteration {self._iteration.index!r}.")
        else:
            self._iteration._log_validation_model(asset_to_log)  # pyright: ignore[reportPrivateUsage]

    def _log_dataset(self, dataset: TDataset) -> None:
        from vectice import Dataset, DatasetType, FileResource, NoResource

        resource = self._get_dataset_resource(dataset)
        dataset_name = f"{self._iteration.phase.id}-{dataset['variable']}"
        no_resource_dataset = Dataset(
            type=DatasetType.UNKNOWN,
            resource=NoResource(
                dataframes=dataset["dataframe"],
                origin="DATAFRAME",
                type=dataset["type"],
                capture_schema_only=self._capture_schema_only,
            ),
            name=dataset_name,
        )
        if resource:
            # TODO Dataset type ?
            vec_dataset = Dataset(
                type=DatasetType.UNKNOWN,
                resource=FileResource(
                    paths=resource,
                    dataframes=dataset["dataframe"],
                    capture_schema_only=self._capture_schema_only,
                ),
                name=dataset_name,
            )
        else:
            vec_dataset = no_resource_dataset
        try:
            self._iteration_service.log_dataset(vec_dataset)
        except FileNotFoundError:
            self._iteration_service.log_dataset(no_resource_dataset)
        _logger.info(f"Dataset {dataset_name!r} logged in iteration {self._iteration.name!r}.")

    def _get_dataset_resource(self, dataset: TDataset) -> str | None:
        import re

        if not self._cell_content:
            return None
        try:
            # Avoid getting stray dataset with autolog.notebook()

            match = []
            for cell in self._cell_content:
                cell = preprocess_code(cell)
                tree = ast.parse(cell)
                visitor = FilePathVisitor(is_dataset_path=True)
                visitor.visit(tree)
                for resource_info in visitor.dataset_file_paths:
                    path_var, file_path = resource_info["variable"], resource_info["path"]
                    dataset_variable = re.escape(dataset["variable"])
                    if path_var:
                        pattern = rf"{dataset_variable}\s*=\s*pd\.read_csv\(\s*{path_var}\s*\).*\n"
                    else:
                        regex_path = re.escape(file_path)
                        pattern = rf"{dataset_variable}\s*=\s*pd\.read_csv\(.*?{regex_path}.*?\).*\n"
                    match_dataset_path = re.search(pattern, cell)
                    if match_dataset_path:
                        match.append(file_path)

            if len(match) < 1:
                return None
            # TODO update regex
            # check if read csv has comma dominated arguments
            return match[0]
        except TypeError:
            return None

    def _get_image_data(self, graph: str) -> str | None:
        try:
            captured = self._local_vars[graph]
        except KeyError:
            return None
        try:
            return captured.outputs[0].data["image/png"]
        except IndexError:
            return None

    def _get_graphs(self, is_notebook: bool) -> list[Any]:
        global GRAPHS

        _, plot_name = _get_cell_id_and_plot_name(self._ip)

        graphs = []
        # Create png data and don't convert saved graphs
        graphs_data = [
            (graph, self._get_image_data(graph))
            for graph in GRAPHS
            if not os.path.isfile(graph) and self._get_image_data(graph)
        ]
        # Create the Images from the png_data from the cell magic
        for graph_name, png_bytes in graphs_data:
            if isinstance(png_bytes, str):
                png_bytes = b64decode(png_bytes)
                bytes_io = BytesIO(png_bytes)
                image = Image.open(bytes_io)
                image.filename = f"{graph_name}.png"  # type: ignore
                # Check if it is cell event graph and make sure graph belongs to cell with the plot_name /  if notebook get all graph png data. Else statement causes duplicates
                if (not is_notebook and plot_name == graph_name) or is_notebook:
                    graphs.append(image)

        for graph in GRAPHS:
            is_str_graph = isinstance(graph, str)
            is_saved_graph_in_cell = "savefig" in str(self._cell_content) or "write_image" in str(self._cell_content)
            is_cell_condition = not is_notebook and graph in str(self._cell_content) and is_saved_graph_in_cell
            is_notebook_condition = is_notebook and os.path.isfile(graph)
            # check for cell saved graphs, check if graph is in cell as multiple cells can be run / check for notebook saved graphs, filepath check makes sure it's a saved graph and not a plot_name
            if is_str_graph and (is_cell_condition or is_notebook_condition):
                graphs.append(graph)
        return graphs
