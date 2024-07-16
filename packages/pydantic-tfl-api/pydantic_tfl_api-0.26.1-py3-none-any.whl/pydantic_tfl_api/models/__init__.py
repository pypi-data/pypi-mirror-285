# portions of this code are from https://github.com/dhilmathy/TfL-python-api
# this code from 
# MIT License

# Copyright (c) 2018 Mathivanan Palanisamy
# Copyright (c) 2024 Rob Aleck

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from .additional_properties import AdditionalProperties  # no dependencies
from .line_mode_group import LineModeGroup  # no dependencies
from .line_group import LineGroup  # no dependencies
from .stop_point import (
    StopPoint,
)  # dependent on Line (commented out), LineGroup, LineModeGroup, AdditionalProperties
from .stop_points_response import StopPointsResponse  # dependent on StopPoint

from .route_section_naptan_entry_sequence import (
    RouteSectionNaptanEntrySequence,
)  # dependent on StopPoint
from .affected_route import (
    AffectedRoute,
)  # dependent on RouteSectionNaptanEntrySequence
from .disruption import Disruption  # dependent on AffectedRoute and StopPoint

from .service_type import ServiceType  # no dependencies
from .route_section import RouteSection  # no dependencies

from .passenger_flow import PassengerFlow  # no dependencies
from .train_loading import TrainLoading  # no dependencies
from .crowding import Crowding  # dependent on PassengerFlow and TrainLoading

from .validity_period import ValidityPeriod  # no dependencies
from .line_status import LineStatus  # dependent on ValidityPeriod

from .line import (
    Line,
)  # dependent on Disruption, LineStatus, RouteSection, ServiceType, Crowding

from .prediction_timing import PredictionTiming  # no dependencies
from .prediction import Prediction  # dependent on PredictionTiming

from .api_error import ApiError  # no dependencies
from .mode import Mode  # no dependencies

from .matched_stop import MatchedStop  # no dependencies
from .ordered_route import OrderedRoute  # no dependencies
from .route_sequence import RouteSequence  # dependent on MatchedStop and OrderedRoute

__all__ = [
    "AdditionalProperties",
    "AffectedRoute",
    "ApiError",
    "Crowding",
    "Disruption",
    "Line",
    "LineGroup",
    "LineModeGroup",
    "LineStatus",
    "Mode",
    "MatchedStop",
    "OrderedRoute",
    "PassengerFlow",
    "Prediction",
    "PredictionTiming",
    "RouteSection",
    "RouteSectionNaptanEntrySequence",
    "RouteSequence",
    "ServiceType",
    "StopPoint",
    "StopPointsResponse",
    "TrainLoading",
    "ValidityPeriod",
]
