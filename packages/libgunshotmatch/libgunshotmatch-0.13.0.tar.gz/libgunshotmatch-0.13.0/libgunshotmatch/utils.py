#!/usr/bin/env python3
#
#  utils.py
"""
Utility functions.
"""
#
#  Copyright © 2020-2023 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, Union

# 3rd party
import numpy
from attr import AttrsInstance
from chemistry_tools.spectrum_similarity import SpectrumSimilarity
from mathematical.utils import rounders
from pyms.DPA.Alignment import Alignment
from pyms.Peak.Class import Peak
from pyms.Spectrum import MassSpectrum
from scipy.stats import truncnorm  # type: ignore[import-untyped]

if TYPE_CHECKING:
	# this package
	from libgunshotmatch.project import Project

__all__ = ("round_rt", "get_truncated_normal", "ms_comparison", "get_rt_range", "create_alignment")


def round_rt(rt: Union[str, float, Decimal]) -> Decimal:
	"""
	Truncate precision of retention time to 10 decimal places.

	:param rt:
	"""

	# Limit to 10 decimal places as that's what Pandas writes JSON data as;
	# no need for greater precision.

	return rounders(rt, "0.0000000000")


def get_truncated_normal(
		mean: float,
		sd: float,
		low: float = 0,
		upp: float = 10,
		count: int = 10,
		random_state: Optional[int] = None,
		) -> Sequence[float]:
	"""
	Returns ``count`` values from a truncated normal distrubition.

	:param mean: The midpoint of the normal distribution.
	:param sd: The spread of the normal distribution (the standard deviation).
	:param low: The lower bound.
	:param upp: The upper bound.
	:param count:
	:param random_state: Optional seed for the random number generator.
	"""

	# From https://stackoverflow.com/a/74448424
	# By toco_tico https://stackoverflow.com/users/1060349/toto-tico
	# CC BY-SA 4.0

	dist = truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
	return dist.rvs(count, random_state=random_state)


def ms_comparison(top_ms: MassSpectrum, bottom_ms: MassSpectrum) -> Optional[float]:
	"""
	Performs a Mass Spectrum similarity calculation two mass spectra.

	:param top_ms:
	:param bottom_ms:

	If either of ``top_ms`` or ``bottom_ms`` is :py:obj:`None` then :py:obj:`None` is returned,
	otherwise a comparison score is returned.
	"""

	if top_ms is None or bottom_ms is None:
		return None

	top_spec = numpy.column_stack((top_ms.mass_list, top_ms.mass_spec))
	bottom_spec = numpy.column_stack((bottom_ms.mass_list, bottom_ms.mass_spec))

	sim = SpectrumSimilarity(
			top_spec,
			bottom_spec,
			b=1,
			xlim=(45, 500),  # TODO: configurable or taken from spectra
			)

	match, rmatch = sim.score()
	return match * 1000


_AI = TypeVar("_AI", bound=AttrsInstance)


def _fix_init_annotations(method: Type[_AI]) -> Type[_AI]:
	init_annotations = method.__init__.__annotations__
	cls_annotations = method.__annotations__

	for k, v in cls_annotations.items():
		if k in init_annotations:
			if init_annotations[k] is Any:
				init_annotations[k] = v
		else:
			init_annotations[k] = v

	return method


def _to_list(l: Iterable[str]) -> List[str]:
	"""
	Attrs type hint helper for converting to a list.

	Otherwise the errors are:

	libgunshotmatch/consolidate/__init__.py:701: error: Argument "name_filter" to "ConsolidatedPeakFilter" has incompatible type "List[str]"; expected "Iterable[_T]"  [arg-type]
	libgunshotmatch/project.py:202: error: List item 0 has incompatible type "str"; expected "_T"  [list-item]
	"""

	return list(l)


def get_rt_range(project: "Project") -> Tuple[float, float]:
	"""
	Returns the minimum and maximum retention times (in minutes) across the repeats.

	:param project:

	:rtype:

	.. versionadded:: 0.7.0
	"""

	# Get RT extremes from intensity matrix
	min_rts, max_rts = [], []
	for repeat in project.datafile_data.values():
		im = repeat.datafile.intensity_matrix
		assert im is not None
		times = im.time_list
		min_rts.append(times[0])
		max_rts.append(times[-1])

	min_rt = min(min_rts) / 60
	max_rt = max(max_rts) / 60

	return min_rt, max_rt


def create_alignment(
		peakpos: Sequence[Sequence[Optional[Peak]]],
		expr_code: List[str],
		similarity: float = 0,
		) -> Alignment:
	"""
	Create a new :class:`pyms.DPA.Alignment.Alignment` object.

	:param peakpos: Nested list of aligned peaks. Top level list contains lists of peaks for each experiment in ``expr_code``.
	:param expr_code: Experiment names. Order must match ``peakpos``.
	:param similarity:

	:rtype:

	.. versionadded:: 0.8.0
	"""

	alignment = Alignment(None)
	alignment.peakpos = [list(p) for p in peakpos]  # type: ignore[arg-type]
	alignment.peakalgt = numpy.transpose(alignment.peakpos).tolist()  # type: ignore[arg-type]
	alignment.expr_code = expr_code
	alignment.similarity = similarity

	return alignment
