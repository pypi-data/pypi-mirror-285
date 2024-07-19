"""
Aggregations that can be used to define Features.
Functions for Derived Features 
- add
- subtract 
- multiply
- safe_divide
- binarize
- bucketize
    
`Spark's Bucketizer Feature Transformer <https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.feature.Bucketizer.html>`_
"""
import warnings
from typing import Union, List, Dict, Any

# TODO: [RJS 2024-06-20] - Modify the docstring for aggregation functions used for derived feature.


class WindowAggregation:
    """
    WindowAggregation will be used for calculating aggregation on given feature for fixed window.

    Parameters
    ----------
    self: str
        self object of the class is the first argument
    function: str
        Aggregation function to be performed on given feature
    ""

    Returns
    -------
    None

    Notes
    -----

    Examples
    --------
    >>>     transform=WindowAggregation(
    ...         function="SUM"
    ...         )
    """

    def __init__(
        self,
        function: str,
    ):
        self.function = function
        self.transform_args = {
            "function": self.function,
            "function_type": "WindowAggregation",
        }


class SlidingWindowAggregation:
    """
    SlidingWindowAggregation will be used for calculating aggregation on given feature based on given rows or given range.
    It will be a varibale window.
    It will also provide functionality like order_by (will be a list) and partition_by.

    Parameters
    ----------
    self: str
        self object of the class is the first argument
    function: str
        Aggregation function to be performed on given feature
    partition_by: str
        to partition the large dataset (DataFrame) into smaller files based on one or multiple columns while writing to disk
    order_by: list[str]
       list of coulmn on which function will be performed
    rangeBetween:
        Creates a WindowSpec with the frame boundaries defined, from start (inclusive) to end (inclusive).
    rowsBetween:
       Creates a WindowSpec with the frame boundaries defined, from start (inclusive) to end (inclusive).

    Returns
    -------
    None

    Notes
    -----

    Examples
    --------
    >>>     feature_logic=FeatureLogic(
    ...         aggregation_fn=SlidingWindowAggregation(
    ...         function="SUM",
    ...         partition_by="category",
    ...         order_by=["id"],
    ...         rangeBetween={"frame_start":"v1","frameEnd":"v2"},
    ...         rowsBetween={"frameStart":"v1","frameEnd":"v2"}
    ...     )
    """

    def __init__(
        self,
        function: str,
        partition_by: str,
        rangeBetween: Dict = None,
        rowsBetween: Dict = None,
        window_period: str = None,
        window_duration: str = None,
        order_by: List[str] = [],
    ):
        warnings.warn(
            "This is currently a partially-implemented feature. If a data source has different folders/keys (e.g. one key for each day or one key for each hour etc.) this may lead to unexpected and inaccurate results. This is because additional data may need to be read to complete the window that has been specified for some rows. A follow-up release will allow the specification of an optional cushion argument, so that each feature job can read additional keys/folders of data to accommodate the window frame provided for all rows."
        )

        self.function = function
        self.partition_by = partition_by
        self.order_by = order_by
        self.rangeBetween = rangeBetween
        self.rowsBetween = rowsBetween
        self.window_period = window_period
        self.window_duration = window_duration
        if self.rangeBetween is not None:
            frame_start_range = self.frame_start_range_val = self.rangeBetween.get(
                "frame_start"
            )
            frame_end_range = self.frame_end_range_val = self.rangeBetween.get(
                "frame_end"
            )
            self.frame_start_range_exists = frame_start_range is not None
            self.frame_end_range_exists = frame_end_range is not None
            if self._validate_range():
                self._validate_frame_range_valid_window()

        if rowsBetween is not None:
            self.frame_start_rows = self.frame_start_rows_val = rowsBetween.get(
                "frame_start"
            )
            self.frame_end_rows = self.frame_end_rows_val = rowsBetween.get("frame_end")
            self.frame_start_rows_exists = self.frame_start_rows is not None
            self.frame_end_rows_exists = self.frame_end_rows is not None
            if self._validate_rows():
                self._validate_frame_rows_valid_window()

        if window_period != None and window_duration != None:
            self.streaming_slidingwindow_args()

    def _validate_order_by(self, order_by: List[str]) -> bool:
        """
        Validate that the specified order column is not empty.

        Args:
            order_by (List[str]): The name of the column to use for ordering.

        Raises:
            ValueError: If the order_by is empty.

        Returns:
            bool

        """
        if len(order_by) == 0:
            raise ValueError("order_by should not be empty")
        return True

    def _validate_range(self) -> bool:
        """
        Validate that the  start range value  and end range value should not be None.
        Raises:
            ValueError: If frame_start_range and frame_end_range is None .
        Returns:
            bool
        """
        if not self.frame_start_range_exists:
            raise ValueError(
                "Please enter the value of frame_start_range. It should not be null"
            )
        elif not self.frame_end_range_exists:
            raise ValueError(
                "Please enter the value of frame_end_range. It should not be null"
            )
        return (
            self.frame_start_range_exists
            and self.frame_end_range_exists
            and self._validate_order_by(self.order_by)
        )

    def _validate_frame_range_valid_window(self) -> Dict:
        """
        Validate that the  start range value  should be less than equal to  end range value .
        Raises:
            ValueError: If frame_start_range is greater frame_end_range is None .
        Returns:
            dict
        """
        if (
            self.frame_start_range_exists
            and self.frame_end_range_exists
            and (self.frame_start_range_val <= self.frame_end_range_val)
        ):
            self.transform_args = {
                "function": self.function,
                "partition_by": self.partition_by,
                "order_by": self.order_by,
                "rangeBetween": self.rangeBetween,
                "function_type": "SlidingWindowAggregation",
            }
        else:
            raise ValueError(
                "The start value of the range should be smaller than or equal to the end value of the range."
            )

    def streaming_slidingwindow_args(self) -> Dict:
        self.transform_args = {
            "function": self.function,
            "partition_by": self.partition_by,
            "order_by": self.order_by,
            "window_period": self.window_period,
            "window_duration": self.window_duration,
            "function_type": "SlidingWindowAggregation",
        }

    def _validate_rows(self) -> bool:
        """
        Validate that the  start rows value  and end rows value should not be None.
        Raises:
            ValueError: If frame_start_rows and frame_end_rows is None .
        Returns:
            bool
        """
        if not self.frame_start_rows_exists:
            raise ValueError(
                " Please enter the value of frame_start_rows. It should not be null"
            )
        elif not self.frame_end_rows_exists:
            raise ValueError(
                "Please enter the value of frame_end_rows. It should not be null"
            )
        return (
            self.frame_start_rows_exists
            and self.frame_end_rows_exists
            and self._validate_order_by(self.order_by)
        )

    def _validate_frame_rows_valid_window(self) -> Dict:
        """
        Validate that the  start rows value  should be less than equal to  end rows value .
        Raises:
            ValueError: If  value of frame_start_rows is greater than  frame_end_rows.
        Returns:
            dict
        """
        if (
            self.frame_start_rows_exists
            and self.frame_end_rows_exists
            and (self.frame_start_rows_val <= self.frame_end_rows_val)
        ):
            self.transform_args = {
                "function": self.function,
                "partition_by": self.partition_by,
                "order_by": self.order_by,
                "rowsBetween": self.rowsBetween,
                "function_type": "SlidingWindowAggregation",
            }
        else:
            raise ValueError(
                "The start value of the rows should be smaller than or equal to the end value of the rows."
            )


def add(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by adding multiple raw/derived features

    Parameters
    ----------
    *args: accepting variable number of feature names

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "add",
            "feature_list": ['feature_1', 'feature_2', ...]
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "add",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj


def subtract(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by subtracting feature1 from feature2

    Parameters
    ----------
    feature1: string
        name of the feature to be subtracted
    feature2: string
        name of the feature from which we'll subtract

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "subtract",
            "feature_list": ['feature_1', 'feature_2']
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """

    if len(feature_list) != 2:
        raise ValueError(
            "feature_list must contain exactly two elements: ['feature1', 'feature2']"
        )

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "subtract",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj


def multiply(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by multiplying multiple raw/derived features

    Parameters
    ----------
    *args: accepting variable number of feature names

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "multiply",
            "feature_list": ['feature_1', 'feature_2', ...]
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """
    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "multiply",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj


def safe_divide(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by safe dividing feature1 from feature2

    Parameters
    ----------
    feature1: string
        name of the feature to be divided
    feature2: string
        name of the feature from which we'll divide

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "safe_divide",
            "feature_list": ['feature_1', 'feature_2']
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """
    if len(feature_list) != 2:
        raise ValueError(
            "feature_list must contain exactly two elements: ['feature1', 'feature2']"
        )

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "safe_divide",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj


def binarize(
    feature: str,
    threshold: Union[int, float],
    groupby_keys: List,
    if_true: Union[int, float, bool, str] = 1,
    if_false: Union[int, float, bool, str] = 0,
) -> Dict[str, Any]:
    """
    Performs binarization by thresholding numerical features to binary features using Spark's Binarizer Feature Transformer

    Parameters
    ----------
    feature: str
        feature name to binarize
    threshold: Union[int, float]
        threshold value can either be an int or float. Feature will be binarized based on the threshold value
    if_true: Union[int, float, bool, str]
        For feature values greater than threshold, if_true value will be set to the binarize feature. Default set to 1
    if_false: Union[int, float, bool, str]
        For feature values less than threshold, if_false value will be set to the binarize feature. Default set to 0

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "binarize",
            "feature_list": [feature],
            feature_transform_args : {
                "labels": [if_true, if_false],
                "threshold": threshold,
            }
        }

    Notes
    -----

    Examples
    --------
    >>> create_derived_feature = CreateDerivedFeature(
    ...     feature_name="player_count_test",
    ...     feature_description="Total players",
    ...     feature_data_type="FLOAT",
    ...     owners=["all-ds@company.com", "temp"],
    ...     schedule="*/7 * * * *",
    ...     entity=["player_count"],
    ...     online=False,
    ...     offline=True,
    ...     transform=src.modules.aggregations.binarize(
    ...         feature = "raw_feature_test",
    ...         threshold = 500,
    ...         if_true = "less",
    ...         if_false = "more"
    ...     ),
    ... )
    """

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "binarize",
        "feature_list": [feature],
        "feature_transform_args": {
            "labels": [if_true, if_false],
            "threshold": threshold,
        },
        "groupby_keys": groupby_keys,
    }
    return obj


def bucketize(
    feature: str, groupby_keys: List, splits: List[Union[int, float]], labels: List[str]
) -> Dict[str, Any]:
    """
    Transforms a column of continuous features to a column of feature buckets, where the buckets are specified by users using [Spark's Bucketizer Feature Transformer](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.feature.Bucketizer.html)

    Parameters
    ----------
    feature: str
        name of the feature to be bucketized
    splits: List[Union[int, float]]
        list of splits based on which a continuous feature will be bucketized
    labels: List[str]
        list of labels that will be assigend as per the splits

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "bucketize",
            "feature_list": [feature],
            "feature_transform_args" : {
                "labels": labels,
                "splits": splits,
            }
        }

    Example
    -------
    >>> create_derived_feature = CreateDerivedFeature(
    ...     feature_name="player_count_test",
    ...     feature_description="Total players",
    ...     feature_data_type="FLOAT",
    ...     owners=["all-ds@company.com", "temp"],
    ...     schedule="*/7 * * * *",
    ...     entity=["player_count"],
    ...     online=False,
    ...     offline=True,
    ...     transform=src.modules.aggregations.bucketize(
    ...         feature = "raw_feature_test",
    ...         splits = [-float("inf"), 500, 750, float("inf")],
    ...         labels = ["less_than_500", "greater_than_500","greater_than_750"],
    ...     ),
    ... )
    ... _
    ... create_derived_feature.register_feature()
    ... create_derived_feature.deploy_feature()
    ..."""
    # converting to string for out of range values
    splits_str = [str(split) for split in splits]

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "bucketize",
        "feature_list": [feature],
        "feature_transform_args": {
            "labels": labels,
            "splits": splits_str,
        },
        "groupby_keys": groupby_keys,
    }
    return obj


def MIN(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by finding the minimum of multiple raw/derived features

    Parameters
    ----------
    *args: accepting variable number of feature names

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "min",
            "feature_list": ['feature_1', 'feature_2', ...]
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "min",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj


def MAX(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by finding the maximum of multiple raw/derived features

    Parameters
    ----------
    *args: accepting variable number of feature names

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "max",
            "feature_list": ['feature_1', 'feature_2', ...]
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "max",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj


def AVG(feature_list: List[str], groupby_keys: List[str]) -> Dict[str, Any]:
    """
    Aggregation function to create a derived feature by calculating the average of multiple raw/derived features

    Parameters
    ----------
    *args: accepting variable number of feature names

    Returns
    -------
    returns a json object as below:


    >>> {
            "transform": "avg",
            "feature_list": ['feature_1', 'feature_2', ...]
        }

    Notes
    -----
    Only feature names will be accepted as arguments

    Examples
    --------

    """

    if not groupby_keys:
        raise ValueError("groupby_keys must contain at least one key")

    obj = {
        "transform": "avg",
        "feature_list": feature_list,
        "groupby_keys": groupby_keys,
    }
    return obj
