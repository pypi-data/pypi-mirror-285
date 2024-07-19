#!/usr/bin/env python3
#
#  consolidate.py
"""
Functions for combining peak identifications across aligned peaks into a single set of results.
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
from collections import Counter, defaultdict
from fnmatch import fnmatch
from itertools import permutations
from multiprocessing import Pool
from typing import Any, Dict, Iterator, List, Mapping, MutableSequence, Optional, Tuple, Type, Union, cast

# 3rd party
import attr
import numpy
import pandas  # type: ignore[import-untyped]
import pyms_nist_search
from pyms.DPA.Alignment import Alignment
from pyms.Spectrum import MassSpectrum
from pyms_nist_search import ReferenceData, SearchResult
from typing_extensions import Self

# this package
from libgunshotmatch.consolidate._fields import (
		_attrs_convert_cas,
		_attrs_convert_ms_comparison,
		_attrs_convert_reference_data
		)
from libgunshotmatch.consolidate._spectra import PermsListType, _map_func
from libgunshotmatch.method import ConsolidateMethod
from libgunshotmatch.method._fields import Integer
from libgunshotmatch.peak import QualifiedPeak
from libgunshotmatch.utils import _fix_init_annotations, _to_list

__all__ = (
		"ConsolidatedPeak",
		"ConsolidatedSearchResult",
		"match_counter",
		"pairwise_ms_comparisons",
		"ConsolidatedPeakFilter",
		"InvertedFilter",
		"combine_spectra",
		)


@attr.define(frozen=True)
class ConsolidatedSearchResult:
	"""
	Represents a candidate compound for a peak.

	This is determined from a set of :class:`SearchResults <pyms_nist_search.search_result.SearchResult>` for a set of aligned peaks.
	"""

	# TODO:  Not currently copying hit_prob from SearchResult

	#: The name of the candidate compound.
	name: str

	#: The CAS number of the compound.
	cas: str = attr.field(converter=_attrs_convert_cas)

	mf_list: List[int] = attr.field(default=attr.Factory(list))
	"""
	List of Match Factors comparing the mass spectrum of the peak with the reference spectrum in each aligned peak.

	Will contain NaN where the compound was not in the hit list for a peak.
	"""

	rmf_list: List[int] = attr.field(default=attr.Factory(list))
	"""
	List of Reverse Match Factors comparing the reference spectrum with the spectrum for each aligned peak.

	Will contain NaN where the compound was not in the hit list for a peak.
	"""

	hit_numbers: List[int] = attr.field(default=attr.Factory(list))
	"""
	List of "hit" numbers from NIST MS Search.

	Lower is better. Will contain NaN where the compound was not in the hit list for a peak.
	"""

	#: The reference mass spectrum for the compound from the NIST library.
	reference_data: Optional[ReferenceData] = attr.field(converter=_attrs_convert_reference_data, default=None)

	@property
	def match_factor(self) -> float:
		"""
		The average match factor.

		Missing values (where the compound was not in the hit list for a peak) are excluded from the calculation.
		"""

		return numpy.nanmean(self.mf_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def match_factor_stdev(self) -> float:
		"""
		The standard deviation of the match factors.

		Missing values (where the compound was not in the hit list for a peak) are excluded from the calculation.
		"""

		return numpy.nanstd(self.mf_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def reverse_match_factor(self) -> float:
		"""
		The average reverse match factor.

		Missing values (where the compound was not in the hit list for a peak) are excluded from the calculation.
		"""

		return numpy.nanmean(self.rmf_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def reverse_match_factor_stdev(self) -> float:
		"""
		The standard deviation of the reverse match factors.

		Missing values (where the compound was not in the hit list for a peak) are excluded from the calculation.
		"""

		return numpy.nanstd(self.rmf_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def average_hit_number(self) -> float:
		"""
		The average hit number.

		Missing values (where the compound was not in the hit list for a peak) are excluded from the calculation.
		"""

		return numpy.nanmean(self.hit_numbers)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def hit_number_stdev(self) -> float:
		"""
		The standard deviation of the hit numbers.

		Missing values (where the compound was not in the hit list for a peak) are excluded from the calculation.
		"""

		return numpy.nanstd(self.hit_numbers)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	def __len__(self) -> int:
		"""
		The number of aligned peaks the compound appeared in the hit list for.
		"""

		return numpy.count_nonzero(~numpy.isnan(self.hit_numbers))

	def __repr__(self) -> str:
		return f"<Consolidated Search Result: {self.name} \tmf={self.match_factor}\tn={len(self)}>"

	def __str__(self) -> str:
		return self.__repr__()

	def to_dict(self) -> Dict[str, Any]:
		"""
		Returns a dictionary representation of this :class:`~.ConsolidatedSearchResult`.

		All keys are native, JSON-serializable, Python objects.
		"""

		if self.reference_data is None:
			reference_data_as_dict = None
		else:
			reference_data_as_dict = self.reference_data.to_dict()

		return {
				"name": self.name,
				"cas": self.cas,
				"mf_list": self.mf_list,
				"rmf_list": self.rmf_list,
				"hit_numbers": self.hit_numbers,
				"reference_data": reference_data_as_dict,
				}

	@classmethod
	def from_dict(cls: Type["ConsolidatedSearchResult"], d: Mapping[str, Any]) -> "ConsolidatedSearchResult":
		"""
		Construct a :class:`~.ConsolidatedSearchResult` from a dictionary.

		:param d:
		"""

		hit_numbers = [float("nan") if hn == -65535 else hn for hn in d["hit_numbers"]]
		mf_list = [float("nan") if mf == -65535 else mf for mf in d["mf_list"]]
		rmf_list = [float("nan") if mf == -65535 else mf for mf in d["rmf_list"]]

		return cls(
				name=d["name"],
				cas=d["cas"],
				mf_list=mf_list,
				rmf_list=rmf_list,
				hit_numbers=hit_numbers,
				reference_data=d["reference_data"],
				)


def _attrs_convert_hits(hits: Optional[List[ConsolidatedSearchResult]]) -> List[ConsolidatedSearchResult]:
	if hits is None:
		hits = []

	hits = list(hits)
	for hit in hits:
		if not isinstance(hit, ConsolidatedSearchResult):
			raise TypeError("'hits' must be a list of ConsolidatedSearchResult objects")

	return hits


@attr.define(init=False)
class ConsolidatedPeak:
	"""
	A Peak that has been produced by consolidating the properties and search results of several qualified peaks.

	:param rt_list: List of retention times of the aligned peaks.
	:param area_list: List of peak areas for the aligned peaks.
	:param ms_list: List of mass spectra for the aligned peaks.
	:param minutes: Retention time units flag.
		If :py:obj:`True`, retention time is in minutes;
		if :py:obj:`False` retention time is in seconds
	:param hits: Optional list of possible identities for this peak.
	:param ms_comparison: Mapping or Pandas :class:`~pandas.Series` giving pairwise mass spectral comparison scores.
	:param meta: Optional dictionary for storing e.g. peak number or whether the peak should be hidden.

	.. latex:clearpage::
	.. autosummary-widths:: 3/10
	"""

	#: List of retention times of the aligned peaks.
	rt_list: List[float] = attr.field(converter=list)

	#: List of peak areas for the aligned peaks.
	area_list: List[float] = attr.field(converter=list)

	#: List of mass spectra for the aligned peaks.
	ms_list: MutableSequence[Optional[MassSpectrum]] = attr.field(converter=list)

	#: Optional list of possible identities for this peak.
	hits: List[ConsolidatedSearchResult] = attr.field(converter=_attrs_convert_hits)

	#: Pairwise mass spectral comparison scores.
	ms_comparison: pandas.Series = attr.field(converter=_attrs_convert_ms_comparison)

	#: Optional dictionary for storing e.g. peak number or whether the peak should be hidden.
	meta: Dict[str, Any]

	def __init__(
			self,
			rt_list: List[float],
			area_list: List[float],
			ms_list: MutableSequence[Optional[MassSpectrum]],
			*,
			minutes: bool = False,
			hits: Optional[List[ConsolidatedSearchResult]] = None,
			ms_comparison: Union[Mapping[str, float], pandas.Series, None] = None,
			meta: Optional[Dict[str, Any]] = None
			):

		# TODO: Type check rt_list and ms_list
		# 		if not isinstance(rt, (int, float)):
		# 			raise TypeError("'rt' must be a number")
		#
		# 			if ms and not isinstance(ms, MassSpectrum) and not isinstance(ms, (int, float)):
		# 				raise TypeError("'ms' must be a number or a MassSpectrum object")
		#

		if minutes:
			rt_list = [rt * 60.0 for rt in rt_list]

		self.rt_list = rt_list
		self.area_list = area_list
		self.ms_list = ms_list
		self.meta = meta or {}
		self.ms_comparison = ms_comparison

		if hits is None:
			self.hits = []
		else:
			self.hits = hits

	@property
	def rt(self) -> float:
		"""
		The average retention time across the aligned peaks.
		"""

		return numpy.nanmean(self.rt_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def rt_stdev(self) -> float:
		"""
		The standard deviation of the retention time across the aligned peaks.
		"""

		return numpy.nanstd(self.rt_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def area(self) -> float:
		"""
		The average peak area across the aligned peaks.
		"""

		return numpy.nanmean(self.area_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def area_stdev(self) -> float:
		"""
		The standard deviation of the peak area across the aligned peaks.
		"""

		return numpy.nanstd(self.area_list)  # type: ignore[return-value]  # mypy thinks type is "floating[Any]"

	@property
	def average_ms_comparison(self) -> float:
		"""
		The average of the pairwise mass spectral comparison scores.
		"""

		# return self._average_ms_comparison

		if self.ms_comparison.empty:
			return 0
		else:
			return numpy.nanmean(self.ms_comparison)

	@property
	def ms_comparison_stdev(self) -> float:
		"""
		The standard deviation of the pairwise mass spectral comparison scores.
		"""

		# return self._ms_comparison_stdev

		if self.ms_comparison.empty:
			return 0
		else:
			return numpy.nanstd(self.ms_comparison)

	# def _calculate_spectra(self):
	# 	"""
	# 	Calculate Combined and Averaged spectra
	# 	"""

	# 	mass_lists = []
	# 	intensity_lists = []

	# 	for spec in self._ms_list:

	# 		if spec:
	# 			# print(spec.mass_list)
	# 			mass_lists.append(spec.mass_list)
	# 			intensity_lists.append(spec.intensity_list)
	# 		else:
	# 			# print()
	# 			pass

	# 	if all_equal(mass_lists):
	# 		mass_list = mass_lists[0]
	# 		# print(intensity_lists)
	# 		combined_intensity_list = list(sum(map(numpy.array, intensity_lists)))
	# 		self._combined_mass_spectrum = MassSpectrum(
	# 				mass_list=mass_list, intensity_list=combined_intensity_list
	# 				)

	# 		# averaged_intensity_list = [intensity / len(mass_lists) for intensity in combined_intensity_list]

	# 		averaged_intensity_list = []
	# 		avg_intensity_array = numpy.array(intensity_lists)
	# 		for column in avg_intensity_array.T:
	# 			if sum(column) == 0 or numpy.count_nonzero(column) == 0:
	# 				averaged_intensity_list.append(0)
	# 			else:
	# 				averaged_intensity_list.append(sum(column) / numpy.count_nonzero(column))

	# 		self._averaged_mass_spectrum = MassSpectrum(
	# 				mass_list=mass_list, intensity_list=averaged_intensity_list
	# 				)

	# 	else:
	# 		warnings.warn("Mass Ranges Differ. Unable to process")
	# 		self._combined_mass_spectrum = None
	# 		self._averaged_mass_spectrum = None

	# @property
	# def combined_mass_spectrum(self):
	# 	return self._combined_mass_spectrum

	# @property
	# def averaged_mass_spectrum(self):
	# 	return self._averaged_mass_spectrum

	def __repr__(self) -> str:
		return f"<Consolidated Peak: {self.rt}>"

	def __str__(self) -> str:
		return self.__repr__()

	# def __eq__(self, other):
	# 	"""
	# 	Return whether this ConsolidatedPeak object is equal to another object

	# 	:param other: The other object to test equality with
	# 	:type other: object

	# 	:rtype: bool
	# 	"""

	# 	if isinstance(other, self.__class__):
	# 		if self.rt_list == other.rt_list and self.area_list == other.area_list:
	# 			return self._ms_list == other._ms_list
	# 		#: TODO: compare hits, meta and ms_comparison
	# 		return False
	# 	else:
	# 		return NotImplemented

	def to_dict(self) -> Dict[str, Any]:
		"""
		Returns a dictionary representation of this :class:`~.ConsolidatedPeak`.

		All keys are native, JSON-serializable, Python objects.
		"""

		return {
				"rt_list": self.rt_list,
				"area_list": self.area_list,
				"meta": self.meta,
				"hits": [hit.to_dict() for hit in self.hits],
				"ms_list": [dict(ms) if ms else None for ms in self.ms_list],
				"ms_comparison": self.ms_comparison.to_dict(),
				}

	def __iter__(self) -> Iterator[Tuple[str, Any]]:
		yield from self.to_dict().items()

	def __len__(self) -> int:
		"""
		How many instances of the peak make up this :class:`~.ConsolidatedPeak`.
		"""

		return numpy.count_nonzero(~numpy.isnan(self.rt_list))

	@classmethod
	def from_dict(cls: Type["ConsolidatedPeak"], d: Mapping[str, Any]) -> "ConsolidatedPeak":
		"""
		Construct a :class:`~.ConsolidatedPeak` from a dictionary.

		:param d:
		"""

		hits = []
		for hit in d["hits"]:
			hits.append(ConsolidatedSearchResult.from_dict(hit))

		ms_list: MutableSequence[Optional[MassSpectrum]] = []
		for msd in d["ms_list"]:
			if msd is None:
				ms_list.append(None)
			else:
				ms_list.append(MassSpectrum.from_dict(msd))

		rt_list = [float("nan") if hn == -65535 else hn for hn in d["rt_list"]]
		area_list = [float("nan") if hn == -65535 else hn for hn in d["area_list"]]

		return cls(
				rt_list=rt_list,
				area_list=area_list,
				ms_list=ms_list,
				meta=d["meta"],
				ms_comparison=d["ms_comparison"],
				hits=hits,
				)


def pairwise_ms_comparisons(alignment: Alignment, parallel: bool = True) -> pandas.DataFrame:
	"""
	Between Samples Spectra Comparison.

	:param alignment:
	:param parallel: Set to :py:obj:`False` to disable parallelisation.

	:returns: :class:`pandas.DataFrame` where the columns are pairwise spectrum similarity scores and the rows are the peaks.
	"""

	perms: PermsListType = []

	ms_alignment: pandas.DataFrame = alignment.get_ms_alignment(require_all_expr=False)

	# Alternatively ms_alignment.columns
	for i in permutations(alignment.expr_code, 2):
		if i[::-1] not in perms:
			perms.append(i)  # type: ignore[arg-type]

	rows_list: List[Tuple[int, pandas.Series, PermsListType]] = []

	for peak_number, spectra in ms_alignment.iterrows():
		# Spectra is a Series where each element (column) corresponds to a MassSpectrum in a repeat.
		rows_list.append((peak_number, spectra, perms))

	if parallel:
		with Pool(len(ms_alignment.columns)) as p:
			ms_comparison = p.starmap(_map_func, rows_list)
	else:
		ms_comparison = [_map_func(*row) for row in rows_list]

	# TODO: linear mode

	# Convert list of (peak_number, comparisons) pairs to data frame
	column_labels = ["{} & {}".format(*perm) for perm in perms]
	comparison_dict = dict(ms_comparison)

	comparison_df = pandas.DataFrame.from_dict(data=comparison_dict, columns=column_labels, orient="index")

	return comparison_df


def match_counter(
		engine: pyms_nist_search.Engine,
		peak_numbers: List[int],
		qualified_peaks: List[List[QualifiedPeak]],
		ms_comp_data: pandas.DataFrame,
		) -> List[ConsolidatedPeak]:
	"""
	Find the most likely compound for each peak.

	:param engine:
	:param peak_numbers: List of peak numbers to process.
	:param qualified_peaks: List of lists of qualified aligned peaks for each repeat.
	:param ms_comp_data: Dataframe giving pairwise mass spectrum comparisons for each set of aligned peaks.
	"""

	# Convert peak_numbers to a set and sort smallest to largest
	peak_numbers = sorted(set(peak_numbers))

	peak: Optional[QualifiedPeak]
	hit: SearchResult

	aligned_peaks = []
	consolidated_peaks = []

	for idx, peak_no in enumerate(peak_numbers):
		# idx relates to the position in the QualifiedPeak lists for each repeat.
		# peak_no correlates to the ``peak_number`` attribute of the QualifiedPeak objects
		row: List[Optional[QualifiedPeak]] = []
		# for experiment in project.alignment.expr_code:
		for experiment in qualified_peaks:
			assert experiment is not None
			for peak in experiment:
				if peak.peak_number == peak_no:
					row.append(peak)
					break
			else:
				row.append(None)

		aligned_peaks.append(row)

		rt_data = []
		area_data = []
		ms_data: MutableSequence[Optional[MassSpectrum]] = []
		hits = []
		names = []

		for peak in row:
			if peak:
				rt_data.append(peak.rt)
				assert peak.area is not None
				area_data.append(peak.area)
				ms_data.append(peak.mass_spectrum)

				for hit in peak.hits:
					hits.append(hit)
					names.append(hit.name)

			else:
				rt_data.append(numpy.nan)
				area_data.append(numpy.nan)
				ms_data.append(None)

		names.sort()
		names_count = Counter(names)
		# print(names_count)
		# exit()

		hits_data = []

		# for compound, count in names_count.items():
		for compound in names_count:
			# TODO: is the counter actually necessary
			# as the output from the for loop is sorted afterwards anyway?

			# numpy,nan is officially a float, but it doesn't matter for our purposes
			# and the other elements in the lists most definately want to be integers
			NaN = cast(int, numpy.nan)

			mf_data: List[int] = []
			rmf_data: List[int] = []
			hit_num_data: List[int] = []

			for peak in row:
				if peak is None:
					mf_data.append(NaN)
					rmf_data.append(NaN)
					hit_num_data.append(NaN)

				else:
					# print(peak.bounds)
					# input(">")
					for hit_idx, hit in enumerate(peak.hits):
						if hit.name == compound:
							mf_data.append(hit.match_factor)
							rmf_data.append(hit.reverse_match_factor)
							hit_num_data.append(hit_idx + 1)
							CAS = hit.cas
							spec_loc = hit.spec_loc

							break
					else:
						mf_data.append(NaN)
						rmf_data.append(NaN)
						hit_num_data.append(NaN)

			# print(f"Obtaining reference data for {compound} (CAS {CAS})")
			ref_data = engine.get_reference_data(spec_loc)
			# print(ref_data)
			hits_data.append(
					ConsolidatedSearchResult(
							name=compound,
							cas=CAS,
							mf_list=mf_data,
							rmf_list=rmf_data,
							hit_numbers=hit_num_data,
							reference_data=ref_data,
							)
					)

		# Sort consolidated hit list
		hits_data = sorted(hits_data, key=lambda k: (len(k), k.match_factor, -k.average_hit_number), reverse=True)
		# consolidated_peak = ConsolidatedPeak(rt_data, area_data, ms_data, peak_number=n, hits=hits_data, ms_comparison=ms_comp_data.loc[n])
		consolidated_peak = ConsolidatedPeak(
				rt_data,
				area_data,
				ms_data,
				hits=hits_data,
				ms_comparison=ms_comp_data.loc[peak_no],
				meta={"peak_number": idx}  # The position of the peaks in the QualifiedPeak lists
				)

		# consolidated_peak.hits = hits_data  # [:n_hits]

		# consolidated_peak.ms_comparison = ms_comp_data.loc[n]

		consolidated_peaks.append(consolidated_peak)

	return consolidated_peaks


@_fix_init_annotations
@attr.define
class ConsolidatedPeakFilter:
	"""
	Class to filter a list of consolidated peaks to exclude peaks by hit name, match factor etc.

	.. versionadded:: 0.2.0
	"""

	name_filter: List[str] = attr.field(converter=_to_list, default=attr.Factory(list))
	"""
	List of glob-style matches for compound names.

	Consolidated peaks matching any of these will be excluded.
	"""

	min_match_factor: int = Integer.field(default=600)
	"""
	Minimum average match factor.

	Consolidated peaks with an average match factor below this will be excluded.
	"""

	min_appearances: int = Integer.field(default=-1)
	"""
	Number of times the hit must appear across the individual aligned peaks.

	Consolidated peaks where the most common hit appears fewer times than this will be excluded.

	If set to ``-1`` the number of instances of the peak in the project are used.
	"""

	#: If :py:obj:`True` details of excluded peaks will be printed.
	verbose: bool = False

	@classmethod
	def from_method(cls: Type[Self], method: ConsolidateMethod) -> Self:
		"""
		Construct a :class:`~.ConsolidatedPeakFilter` from a :class:`~.ConsolidateMethod`.

		:param method:

		:rtype:

		.. latex:clearpage::
		"""

		return cls(
				name_filter=method.name_filter,
				min_match_factor=method.min_match_factor,
				min_appearances=method.min_appearances,
				)

	def print_skip_reason(self, peak: ConsolidatedPeak, reason: str) -> None:
		"""
		Print the reason for skipping a peak, if :py:attr:`.ConsolidatedPeakFilter.verbose` is :py:obj:`True`.

		:param peak: The peak being skipped.
		:param reason: The reason for skipping the peak.
		"""

		if self.verbose:
			print(f"Skipping peak at {peak.rt / 60:0.3f} mins:", reason)

	def should_filter_peak(self, peak: ConsolidatedPeak) -> bool:
		"""
		Returns :py:obj:`True` if the peak should be excluded based on the current filter options.

		:param peak:
		"""

		hit = peak.hits[0]

		if self.min_appearances == -1:
			# Set to how many times the peak appears
			min_appearances = len(peak)
		else:
			min_appearances = self.min_appearances

		if len(hit) < min_appearances:
			self.print_skip_reason(peak, f"top hit {hit.name!r} only appears {len(hit)} times")
			return True

		hit_name = hit.name.lower()
		for nf in self.name_filter:
			if fnmatch(hit_name, nf):
				self.print_skip_reason(peak, f"name {hit.name!r} matches {nf!r}")
				return True

		# mean_match_factor = mean(hit.mf_list)
		mean_match_factor = hit.match_factor
		if mean_match_factor < self.min_match_factor:
			self.print_skip_reason(peak, f"MF {mean_match_factor} <600")
			return True

		return False

	def filter(self, consolidated_peaks: List[ConsolidatedPeak]) -> List[ConsolidatedPeak]:  # noqa: A003  # pylint: disable=redefined-builtin
		"""
		Filter a list of consolidated peaks.

		:param consolidated_peaks:
		"""

		return [cp for cp in consolidated_peaks if not self.should_filter_peak(cp)]


@_fix_init_annotations
@attr.define
class InvertedFilter(ConsolidatedPeakFilter):
	"""
	Inverted version of :class:`~.ConsolidatedPeakFilter`.

	Returns peaks which would be excluded by a :class:`~.ConsolidatedPeakFilter`.

	.. versionadded:: 0.10.0
	"""

	def print_skip_reason(self, peak: ConsolidatedPeak, reason: str) -> None:  # noqa: D102
		if self.verbose:
			print(f"Would reject peak at {peak.rt / 60:0.3f} mins:", reason)

	def filter(self, consolidated_peaks: List[ConsolidatedPeak]) -> List[ConsolidatedPeak]:  # noqa: A003  # pylint: disable=redefined-builtin
		"""
		Filter a list of consolidated peaks.

		:param consolidated_peaks:
		"""

		filtered_consolidated_peaks = []

		for cp in consolidated_peaks:
			if self.should_filter_peak(cp):
				filtered_consolidated_peaks.append(cp)

		return filtered_consolidated_peaks


def combine_spectra(peak: ConsolidatedPeak) -> Tuple[List[int], List[float]]:
	"""
	Sum the intensities across all mass spectra in the given peak.

	:param peak:

	:returns: List of masses and list of corresponding intensities.

	.. versionadded:: v0.11.0
	"""

	combined_ms_data: Dict[int, float] = defaultdict(float)

	for ms in peak.ms_list:
		if ms is not None:
			for mass, intensity in zip(ms.mass_list, ms.intensity_list):
				combined_ms_data[mass] += intensity

	mass_list, intensity_list = [], []
	for mass, intensity in combined_ms_data.items():
		mass_list.append(mass)
		intensity_list.append(intensity)

	# mass_list, intensity_list = zip(*combined_ms_data.items())

	return mass_list, intensity_list
