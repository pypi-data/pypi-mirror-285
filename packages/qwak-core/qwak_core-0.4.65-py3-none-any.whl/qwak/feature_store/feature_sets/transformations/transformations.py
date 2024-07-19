import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from inspect import signature
from typing import Any, Callable, Dict, List, Optional, Tuple
from warnings import warn

from _qwak_proto.qwak.feature_store.features.aggregation_pb2 import (
    AggregationField as ProtoAggregationField,
    TimeWindow as ProtoTimeWindow,
)
from _qwak_proto.qwak.feature_store.features.feature_set_types_pb2 import (
    KoalasTransformation as ProtoKoalasTransformation,
    PySparkTransformation as ProtoPySparkTransformation,
    SqlTransformation as ProtoSqlTransformation,
    TransformArguments as ProtoTransformArguments,
    Transformation as ProtoTransformation,
    UdfTransformation as ProtoUdfTransformation,
)
from qwak.exceptions import QwakException
from qwak.feature_store._common.value import (
    UPDATE_QWAK_SDK_WITH_FEATURE_STORE_EXTRA_MSG,
)
from qwak.feature_store.feature_sets.transformations.aggregations.aggregations import (
    BaseAggregate,
    QwakAggregation,
)
from qwak.feature_store.feature_sets.transformations.aggregations.windows import Window
from qwak.tools.logger import logger as qwak_logger

logger = qwak_logger.get_qwak_logger()


@dataclass
class BaseTransformation(ABC):
    """
    Base class for Qwak transformations.

    Windows and aggregates are supported only for streaming aggregation featuresets.
    """

    windows: List[Window] = field(init=False, default_factory=list)
    aggregations: Tuple[BaseAggregate] = field(init=False, default_factory=tuple)
    _artifact_path: Optional[str] = field(init=False, default=None)

    def aggregate(self, *aggregations: QwakAggregation):
        self.aggregations += aggregations
        return self

    def by_windows(self, *time_windows: str):
        self.windows += Window._from_string(*set(time_windows))
        return self

    def get_names(self) -> List[str]:
        return [a.get_name() for a in self.aggregations]

    def get_features_names(self) -> List[str]:
        if self.windows and self.aggregations:
            return [
                f"{name}_{tu.get_feature_suffix()}"
                for tu in self.windows
                for name in self.get_names()
            ]
        else:
            raise QwakException(
                "Feature names are retrieved for streaming aggregation featuresets only"
            )

    def _get_aggregations_proto(self) -> List[ProtoAggregationField]:
        """
        Converts a user-defined streaming aggregation transformation to a list of proto aggregation fields
        Time windows are applied to all defined aggregations (cartesian product)
        """

        time_windows: List[ProtoTimeWindow] = [
            ProtoTimeWindow(length=window.length, time_unit=window.time_unit_proto)
            for window in self.windows
        ]

        proto_aggregations: List[ProtoAggregationField] = []

        for aggregation in self.aggregations:
            aggregation_params = {
                aggregation._key: aggregation.to_proto(),
                "time_windows": time_windows,
            }
            if aggregation.has_alias():
                aggregation_params["field_name_prefix"] = aggregation._alias_name

            proto_aggregations.append(ProtoAggregationField(**aggregation_params))

        return proto_aggregations

    @classmethod
    def _from_proto(cls, proto: ProtoTransformation):
        function_mapping = {
            "sql_transformation": SparkSqlTransformation,
            "koalas_transformation": KoalasTransformation,
            "pyspark_transformation": PySparkTransformation,
            "udf_transformation": UdfTransformation,
        }

        function_type: str = proto.WhichOneof("type")

        if function_type in function_mapping:
            function_class = function_mapping.get(function_type)
            return function_class._from_proto(proto)

        raise QwakException(f"Got unsupported transformation type: {function_type}")

    @abstractmethod
    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        pass

    def get_functions(self) -> Optional[List[Callable]]:
        return None

    def _validate_udfs(self):
        udfs: Optional[List[Callable]] = self.get_functions()

        if udfs and len(udfs) > 0:
            python_major = sys.version_info[0]
            python_minor = sys.version_info[1]
            if f"{python_major}.{python_minor}" != "3.8":
                raise QwakException(
                    f"Feature store UDFs are only supported for python 3.8, instead got: "
                    f"{python_major}.{python_minor}"
                )


@dataclass
class KoalasTransformation(BaseTransformation):
    """
    Koalas transformation, providing the user with the ability to define a Koalas based UDF for the transformation
    of the FeatureSet. This option will be deprecated in future versions.
    @param function: The Koalas function defined for the transformation
    @type: Callable
    @deprecated
    """

    function: Optional[Callable] = None
    qwargs: Optional[Dict[str, str]] = None

    def __post_init__(self):
        warn(
            "Koalas transformation is about to be deprecated. "
            "Please use PySparkTransformation, SparkSqlTransformation or UDFTransformation instead",
            DeprecationWarning,
            stacklevel=2,
        )

        self.qwargs = self.qwargs if self.qwargs else {}
        self.qwargs = {str(k): str(v) for k, v in self.qwargs.items()}
        self._artifact_path = None

        if not self.function:
            raise QwakException(
                "Please provide a valid function for the koalas transformation"
            )

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            koalas_transformation=ProtoKoalasTransformation(
                function_name=self.function.__name__,
                qwargs=ProtoTransformArguments(qwargs=self.qwargs),
            ),
            artifact_path=self._artifact_path,
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        koalas_transformation = proto.koalas_transformation
        qwargs = {}
        if koalas_transformation.WhichOneof("args_option") == "qwargs":
            qwargs = koalas_transformation.qwargs.qwargs

        def f():
            print(
                f"Loading Koalas UDFs is not supported. Can not load {koalas_transformation.function_name}"
            )

        f.__name__ = koalas_transformation.function_name

        return cls(function=f, qwargs=qwargs)

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]


@dataclass
class PySparkTransformation(BaseTransformation):
    """
    PySpark transformation, providing the user with the ability to define a PySpark based UDF for the transformation
    of the FeatureSet.
    @param function: The PySpark function defined for the transformation
    @type: Callable
    @deprecated
    """

    function: Optional[Callable] = None
    qwargs: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.qwargs = self.qwargs if self.qwargs else {}
        self.qwargs = {str(k): str(v) for k, v in self.qwargs.items()}
        self._artifact_path = None
        self._validate_function()

    def _validate_function(self):
        try:
            import pyspark.sql as ps
        except Exception:
            raise QwakException(
                "Missing 'pyspark' dependency required for PySpark transformation. "
                f"{UPDATE_QWAK_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
            )

        if not self.function:
            raise QwakException(
                "Please provide a valid function for the PySpark transformation"
            )

        function_signature = signature(self.function)
        function_parameters = function_signature.parameters

        if (
            len(function_parameters) == 0
            or list(function_parameters.values())[0].annotation
            != Dict[str, ps.DataFrame]
        ):
            raise QwakException(
                "The first argument of a PySpark transformation function must have `Dict[str, pyspark.sql.DataFrame]` type annotation"
            )
        elif len(function_parameters) == 2:
            second_argument = list(function_parameters.values())[1]
            if (
                second_argument.name != "qwargs"
                or second_argument.annotation != Dict[str, Any]
            ):
                raise QwakException(
                    "The second argument of a PySpark transformation function must be named `qwargs` and have "
                    "`Dict[str, Any]` type annotation."
                )
        if function_signature.return_annotation != ps.DataFrame:
            raise QwakException(
                "PySpark transformation function must have `pyspark.sql.DataFrame` return type annotation."
            )

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            pyspark_transformation=ProtoPySparkTransformation(
                function_name=self.function.__name__,
                qwargs=ProtoTransformArguments(qwargs=self.qwargs),
            ),
            artifact_path=self._artifact_path,
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        try:
            import pyspark.sql as ps
        except Exception:
            raise QwakException(
                "Missing 'pyspark' dependency required for PySpark transformation. "
                f"{UPDATE_QWAK_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
            )

        pyspark_transformation = proto.pyspark_transformation
        qwargs = {}
        if pyspark_transformation.WhichOneof("args_option") == "qwargs":
            qwargs = pyspark_transformation.qwargs.qwargs

        def f(dfs: Dict[str, ps.DataFrame]) -> ps.DataFrame:
            print(
                f"Loading Pyspark UDFs is not supported. Can not load {pyspark_transformation.function_name}"
            )

        f.__name__ = pyspark_transformation.function_name

        return cls(function=f, qwargs=qwargs)

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]


@dataclass
class SparkSqlTransformation(BaseTransformation):
    """
    A Spark SQL transformation
    :param sql: A valid Spark SQL transformation
    :param functions: PySpark Pandas UDFs
    Example transformation:
    ... code-block:: python
        SparkSqlTransformation("SELECT user_id, age FROM data_source")
    Example transformation with additional UDFs:
    ... code-block:: python
        @qwak_pandas_udf(output_schema=Schema([
            Column(type=Type.long)]))
        def plus_one(column_a: pd.Series) -> pd.Series:
            return column_a + 1


        @qwak_pandas_udf(output_schema=Schema([
            Column(type=Type.long)]))
        def mul_by_two(column_a: pd.Series) -> pd.Series:
            return column_a * 2

        SparkSqlTransformation("SELECT user_id, age FROM data_source", functions=[plus_one, mul_by_two])
    """

    sql: str = str()
    functions: Optional[List[Callable]] = None

    def __post_init__(self):
        if not self.sql:
            raise QwakException(
                "SQL statement can not be empty when using a SparkSqlTransformation"
            )

    @classmethod
    def _from_proto(cls, proto: "ProtoSqlTransformation"):
        return cls(sql=proto.sql_transformation.sql)

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        return ProtoTransformation(
            sql_transformation=ProtoSqlTransformation(
                sql=self.sql,
                function_names=(
                    [function.__name__ for function in self.functions]
                    if self.functions
                    else None
                ),
            ),
            artifact_path=artifact_path,
        )

    def get_functions(self) -> Optional[List[Callable]]:
        return self.functions


@dataclass
class UdfTransformation(BaseTransformation):
    """
    A UDF Transformation
    :param function: A valid user defined pandas function decorated with the @qwak_pandas_udf decorator
    Example transformation:
    ... code-block:: python

    @qwak_pandas_udf(output_schema=Schema([Column(type=Type.long)]))
    def my_pandas_udf() -> pd.Series:
        data = np.random.randn(3)
        series = pd.Series(data)
        return series

    UdfTransformation(function=my_pandas_udf)
    """

    function: Callable = ()

    def __post_init__(self):
        if not self.function:
            raise QwakException("Please provide a function to the UdfTransformation")

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            artifact_path=artifact_path,
            udf_transformation=ProtoUdfTransformation(
                function_name=self.function.__name__
            ),
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        return cls(
            function=lambda x: print("Loading UDFs is not yet supported"),
        )

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]
