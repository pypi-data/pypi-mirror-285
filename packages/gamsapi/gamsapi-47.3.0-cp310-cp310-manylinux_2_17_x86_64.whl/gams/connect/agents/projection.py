#
# GAMS - General Algebraic Modeling System Python API
#
# Copyright (c) 2017-2024 GAMS Development Corp. <support@gams.com>
# Copyright (c) 2017-2024 GAMS Software GmbH <support@gams.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from gams import transfer as gt
import pandas as pd
import copy
import re
from gams.connect.agents.connectagent import ConnectAgent


class Projection(ConnectAgent):

    def __init__(self, system_directory, cdb, inst):
        super().__init__(system_directory, cdb, inst)

        self._parse_options()

        if self._trace > 3:
            pd.set_option("display.max_rows", None, "display.max_columns", None)

    def _parse_options(self):
        self._aggregation_method = self._inst.get("aggregationMethod", "first")
        self._as_parameter = self._inst.get("asParameter")
        if self._as_parameter is not None:
            self._cdb.print_log(
                "Warning: The option <asParameter> is deprecated and will be removed in a future release. To get the same behavior as with asParameter: True, use symName.all(i1,i2,...,iN) in <name>."
            )
        self._as_set = self._inst.get("asSet", False)
        self._name = self._inst.get("name")
        self._new_name = self._inst.get("newName")
        self._text = self._inst.get("text", None)
        self._trace = self._inst.get("trace", 0)

        if self._trace > 1:
            self._cdb.print_log(
                "Input (root):"
                f"\n  aggregationMethod: >{self._inst.get('aggregationMethod', '')}<"
                f"\n  asSet: >{self._inst.get('asSet', '')}<"
                f"\n  name: >{self._inst.get('name')}<"
                f"\n  newName: >{self._inst.get('newName')}<"
                f"\n  text: >{self._inst.get('text', '')}<"
                f"\n  trace: >{self._inst.get('trace', '')}<"
                "\n"
            )

        if self._trace > 1:
            self._cdb.print_log(
                "Processed Input (root):"
                f"\n  aggregationMethod: >{self._aggregation_method}<"
                f"\n  asSet: >{self._as_set}<"
                f"\n  name: >{self._name}<"
                f"\n  newName: >{self._new_name}<"
                f"\n  text: >{self._text}<"
                f"\n  trace: >{self._trace}<"
                "\n"
            )

    def _generate_text(self, df, ssym, sdom, suffix_list, suffix_to_index):
        """Generates set element text."""

        if (
            (isinstance(ssym, gt.Set) and not self._text in [None, ""])
            or (
                isinstance(ssym, (gt.Variable, gt.Equation))
                and suffix_list
                and not suffix_to_index
                and not self._text in [None, ""]
            )
            or (isinstance(ssym, gt.Parameter) and not self._text in [None, ""])
        ):
            df.columns = [*df.columns[:-1], "element_text"]
            df["element_text"] = df["element_text"].astype(str)
            sdom.append("element_text")
            execcmd = 'df["element_text"] = ("' + self._text + '")'
            for i, r in enumerate(sdom):
                execcmd = execcmd.replace(
                    "{" + r + "}",
                    '" + df[df.columns[' + str(i) + ']].astype(str) + "',
                )
            exec(execcmd)
            if self._trace > 2:
                self._cdb.print_log(f"DataFrame after text adjustment:\n{df}")

        return df

    def _combine_scalars(self):
        """Aggregates a list of scalars of the same type into a 1-dimensional symbol (of the same type) that holds the symbol names as labels."""

        symrecords_list = []
        sym_types = []
        for sym_name in self._name:
            if sym_name not in self._cdb._container:
                self.connect_error(
                    f"Symbol '{sym_name}' not found in Connect database."
                )
            sym = self._cdb._container[sym_name]
            if sym.dimension != 0:
                self.connect_error(
                    f"Symbol '{sym_name}' needs to be a scalar when specified in <name> using a list."
                )
            sym_types.append(type(sym))
            df = self.sym_records_no_none(sym).copy(deep=True)
            symrecords_list.append(df)
        if not all(t == sym_types[0] for t in sym_types):
            self.connect_error(
                f"All symbols need to be of the same type when specified in <name> using a list."
            )

        df = pd.concat(symrecords_list, ignore_index=True)
        df.insert(0, "uni_0", self._name)
        sym0 = self._cdb._container[self._name[0]]

        if isinstance(sym0, gt.Parameter):
            gt.Parameter(
                self._cdb._container,
                self._new_name,
                ["*"],
                records=df,
            )
        elif isinstance(sym0, gt.Equation):
            gt.Equation(
                self._cdb._container,
                self._new_name,
                sym0.type,
                ["*"],
                records=df,
            )
        elif isinstance(sym0, gt.Variable):
            gt.Variable(
                self._cdb._container,
                self._new_name,
                sym0.type,
                ["*"],
                records=df,
            )

    def _split_index(self, match, symname):
        """Splits provided index space into a list of indices. Return an empty list if no index space is provided."""

        if match.group("index"):
            index = match.group("index").split(",")
            for i in index:
                if index.count(i) > 1:
                    self.connect_error(
                        f"Multiple use of index >{i}< in index list of symbol >{symname}<."
                    )
            return index
        else:
            return []

    def _process_symbol_name(self):
        """Processes strings provided by the name/newName option. Splits name/newName into the symbol name, suffix and index list."""

        regex = r"(?P<name>[a-zA-Z0-9_]+)(\.?(?P<suffix>([a-zA-Z]*)|(\[[a-zA-Z,\s]*\])))?(\((?P<index>[a-zA-Z0-9_,]+)\))?"
        ms = re.fullmatch(regex, self._name)
        if not ms:
            self.connect_error(f"Invalid <name>: >{self._name}<.")
        mt = re.fullmatch(regex, self._new_name)
        if not mt:
            self.connect_error(f"Invalid <newName>: >{self._new_name}<.")

        # NAME
        ssym_name = ms.group("name")
        if ssym_name not in self._cdb._container:
            self.connect_error(f"Symbol '{ssym_name}' not found in Connect database.")
        ssym = self._cdb._container[ssym_name]
        tsym_name = mt.group("name")

        # INDEX
        sindex_list = self._split_index(ms, ssym_name)
        tindex_list = self._split_index(mt, tsym_name)
        if len(sindex_list) != ssym.dimension:
            self.connect_error(
                f"Number of provided indices for symbol >{ssym_name}< <> dimension of the symbol ({len(sindex_list)}<>{ssym.dimension})."
            )
        if set(tindex_list) - set(sindex_list):
            self.connect_error(
                f"Unknown index >{(set(tindex_list) - set(sindex_list))}< in <newName>: >{self._new_name}<."
            )
        index_map = [sindex_list.index(d) for d in tindex_list]
        tsym_domain = [ssym.domain[d] for d in index_map]

        # SUFFIX
        suffix_dict = {
            "l": "level",
            "m": "marginal",
            "lo": "lower",
            "up": "upper",
            "scale": "scale",
            "all": "all",
        }
        attribute_list = [a for a in suffix_dict.values() if a != "all"]

        if mt.group("suffix"):
            self.connect_error(f"No suffix allowed on <newName>: >{self._new_name}<.")
        suffix = ms.group("suffix")
        if suffix == "":
            suffix_list = []

        suffix_to_index = False
        if suffix:
            if not isinstance(ssym, (gt.Variable, gt.Equation)):
                self.connect_error(
                    f"Suffix given but symbol >{ssym_name}< is not a variable or an equation."
                )

            if re.search(r"[\[\]]", suffix):
                suffix_to_index = True
                tsym_domain.append("attribute")
                suffix = re.sub(r"[\[\]]", "", suffix)
                if suffix == "":
                    self.connect_error(f"Suffix list is empty.")
                else:
                    suffix_list = list(
                        dict.fromkeys(s.strip() for s in suffix.split(","))
                    )
            else:
                suffix_list = [suffix]

            for s in suffix_list:
                if s not in suffix_dict.keys():
                    self.connect_error(
                        f"Unknown suffix >{s}< (use {", ".join([s for s in suffix_dict.keys()])})."
                    )
            # resolve v.all and v.[all]
            if "all" in suffix_list:
                suffix_list = attribute_list
                if not suffix_to_index:  # might have been added before already
                    suffix_to_index = True
                    tsym_domain.append("attribute")
            else:
                suffix_list = list(map(suffix_dict.get, suffix_list))
        elif self._as_parameter:  # deprecated
            suffix_to_index = True
            tsym_domain.append("attribute")
            suffix_list = attribute_list

        if self._trace > 1:
            self._cdb.print_log(
                "Processed <name>:"
                f"\n  name: >{ssym_name}<"
                f"\n  index: >{sindex_list}<"
                f"\n  suffix: >{suffix_list}<"
                f"\n  suffix to index: >{suffix_to_index}<"
                "\n"
            )
            self._cdb.print_log(
                "Processed <newName>:"
                f"\n  name: >{tsym_name}<"
                f"\n  index: >{tindex_list}<"
                "\n"
            )

        return (
            ssym,
            ssym_name,
            sindex_list,
            suffix_list,
            suffix_to_index,
            tsym_name,
            tindex_list,
            index_map,
            tsym_domain,
        )

    def _create_target_symbol(
        self, ssym, ssym_name, tsym_name, tsym_domain, suffix_list
    ):
        """Create target symbol in Connect container."""

        if self._as_set or isinstance(ssym, gt.Set):
            tsym = gt.Set(self._cdb._container, tsym_name, tsym_domain)
        elif suffix_list or isinstance(ssym, gt.Parameter):
            tsym = gt.Parameter(self._cdb._container, tsym_name, tsym_domain)
        elif isinstance(ssym, gt.Equation):
            tsym = gt.Equation(self._cdb._container, tsym_name, ssym.type, tsym_domain)
        elif isinstance(ssym, gt.Variable):
            tsym = gt.Variable(self._cdb._container, tsym_name, ssym.type, tsym_domain)
        else:
            self.connect_error(
                f"Projection can't handle symbol type >{type(ssym)}< of symbol >{ssym_name}<."
            )
        if self._trace > 1:
            self._cdb.print_log(
                f"Created >{tsym_name}< as {len(tsym_domain)}-dim {type(tsym)}."
            )

        return tsym

    def _apply_aggregation_method(self, df, ssym_name, index_map):
        """Applies selected aggregation method."""

        if len(index_map) > 0:
            df = df.groupby(
                [self._cdb._container[ssym_name].domain_labels[d] for d in index_map]
            )
        func = getattr(df, self._aggregation_method)
        if not callable(func):
            self.connect_error(
                f"<aggregationMethod>: >{self._aggregation_method}< not callable."
            )
        df = func()
        if self._trace > 2:
            self._cdb.print_log(f"DataFrame after aggregation:\n{df}")
        return df

    def _drop_text(self, df, ssym, suffix_list, suffix_to_index):
        """Drops set element text."""

        if isinstance(ssym, gt.Set) and self._text == "":
            df.drop(columns=df.columns[-1], inplace=True)
        elif isinstance(ssym, (gt.Variable, gt.Equation)) and suffix_to_index:
            df.drop(columns=df.columns[-1], inplace=True)
        elif (
            isinstance(ssym, (gt.Variable, gt.Equation))
            and suffix_list
            and self._text in [None, ""]
        ):
            df.drop(columns=df.columns[-1], inplace=True)
        elif isinstance(ssym, (gt.Variable, gt.Equation)) and not suffix_list:
            df.drop(
                columns=["level", "marginal", "lower", "upper", "scale"],
                inplace=True,
            )
        elif isinstance(ssym, gt.Parameter) and self._text in [None, ""]:
            df.drop(columns=df.columns[-1], inplace=True)

        return df

    def _apply_categories(self, ssym, tsym, suffix_to_index, suffix_list, index_map):
        """Applies categories from the source symbol to the domains of the target symbol."""

        if tsym.dimension > 0:
            for i in range(tsym.dimension):
                if suffix_to_index and i == tsym.dimension - 1:
                    cats = suffix_list
                else:
                    cats = ssym.records[
                        ssym.records.columns[index_map[i]]
                    ].cat.categories

                tsym.records.isetitem(
                    i,
                    tsym.records.iloc[:, i].astype(
                        pd.CategoricalDtype(
                            categories=cats,
                            ordered=True,
                        )
                    ),
                )

    def execute(self):

        # list of scalars into a 1-dim parameter/var/equ
        if isinstance(self._name, list):
            self._combine_scalars()

            if self._trace > 0:
                self.describe_container(self._cdb._container, "Connect Container")
            if self._trace > 2:
                self._cdb.print_log(
                    f"Connect Container symbol={self._new_name}:\n {self._cdb._container[self._new_name].records}\n"
                )

            return

        (
            ssym,
            ssym_name,
            sindex_list,
            suffix_list,
            suffix_to_index,
            tsym_name,
            tindex_list,
            index_map,
            tsym_domain,
        ) = self._process_symbol_name()

        tsym = self._create_target_symbol(
            ssym, ssym_name, tsym_name, tsym_domain, suffix_list
        )

        assert len(index_map) == tsym.dimension or (
            len(index_map) + 1 == tsym.dimension and suffix_to_index
        ), "Number of domains for <newName> <> dimension of <newName>"
        assert len(tsym_domain) == tsym.dimension or (
            len(tsym_domain) + 1 == tsym.dimension and suffix_to_index
        ), "Number of domains for <newName> <> dimension of <newName>"
        assert (
            not suffix_list or isinstance(tsym, gt.Parameter) or self._as_set
        ), "Type of <newName> needs to be parameter or asSet needs to be True"
        assert (
            suffix_list or suffix_to_index or self._as_set or type(ssym) == type(tsym)
        ), "No suffix, asSet: False but type of <name> <> type of <newName>"

        df = copy.deepcopy(self._cdb._container[ssym_name].records)
        # For symbols with None records or empty dataframe, an empty df is assigned then returned
        if df is None or df.empty:
            self.transform_sym_none_to_empty(tsym)
            return

        if suffix_list:
            suffixes_to_drop = set(
                ["level", "marginal", "lower", "upper", "scale"]
            ) - set(suffix_list)
            df.drop(columns=list(suffixes_to_drop), inplace=True)
            if self._trace > 2:
                self._cdb.print_log(f"DataFrame after dropping suffixes:\n{df}")

        if isinstance(tsym, gt.Set):
            df = self._generate_text(
                df, ssym, sindex_list, suffix_list, suffix_to_index
            )

        if ssym.dimension == len(tindex_list) and not ssym.hasDuplicateRecords():
            # index space of same length and no duplicate records -> no aggregation
            permutation = True
            if (
                suffix_to_index
                and tsym_domain[:-1] == ssym.domain
                or not suffix_to_index
                and tsym_domain == ssym.domain
            ):
                permutation = False

            if permutation:
                # index space of same length but not identical -> permutation
                if self._trace > 1:
                    self._cdb.print_log(f"Permutation only!")
                cols_permuted = df.columns.tolist()
                for i, d in enumerate(index_map):
                    cols_permuted[i] = df.columns.tolist()[d]
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame before permutation:\n{df}")
                if self._trace > 1:
                    self._cdb.print_log(f"Column permutation:\n{cols_permuted}")
                df = df.reindex(columns=cols_permuted)
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after permutation:\n{df}")

            if suffix_to_index:
                # stack suffix index
                if ssym.dimension == 0:
                    # source and target symbols have 0 dimensions (scalar)
                    df = df.stack().droplevel(0)
                    df = list(dict(df).items())
                else:
                    df.set_index(list(df.columns[: ssym.dimension]), inplace=True)
                    df = df.stack().reset_index()
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after stacking suffix index:\n{df}")

        else:
            # TODO: Raise error if sets, variable or equations (without suffix) are not used with first/last aggregation
            drop_cols = self._cdb._container[ssym_name].domain_labels[: ssym.dimension]
            df[drop_cols] = df[drop_cols].astype(str)

            if (
                tsym.dimension == 0 or (tsym.dimension == 1 and suffix_to_index)
            ) and self._aggregation_method in [
                "first",
                "last",
            ]:
                # target symbol has 0 dimensions (scalar) and aggregation first/last -> fast aggregation

                df.drop(columns=drop_cols, inplace=True)
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after dropping columns:\n{df}")
                if self._aggregation_method == "first":
                    df = df.iloc[0]
                else:
                    df = df.iloc[-1]
                if isinstance(tsym, (gt.Variable, gt.Equation)):
                    df = dict(df)
                elif suffix_to_index:
                    df = list(dict(df).items())
                if self._trace > 2:
                    self._cdb.print_log(
                        f"DataFrame after first/last aggregation:\n{df}"
                    )
            else:
                df.set_index(
                    pd.MultiIndex.from_frame(
                        df[self._cdb._container[ssym_name].domain_labels]
                    ),
                    inplace=True,
                )
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after .set_index():\n{df}")

                df.drop(columns=drop_cols, inplace=True)
                if self._trace > 2:
                    self._cdb.print_log(f"DataFrame after dropping columns:\n{df}")

                df = self._apply_aggregation_method(df, ssym_name, index_map)

                if type(df) == pd.DataFrame:
                    # TODO: Replace type(df) == pd.DataFrame
                    if suffix_to_index:
                        df = df.stack()
                        if self._trace > 2:
                            self._cdb.print_log(
                                f"DataFrame after stacking suffix index:\n{df}"
                            )

                    df = df.reset_index(drop=False)
                    if self._trace > 2:
                        self._cdb.print_log(f"DataFrame after .reset_index():\n{df}")

        if type(df) == pd.DataFrame and isinstance(tsym, gt.Set):
            # TODO: Replace type(df) == pd.DataFrame
            df = self._drop_text(df, ssym, suffix_list, suffix_to_index)

        if self._trace > 2:
            self._cdb.print_log(f"DataFrame before .setRecords():\n{df}")
        tsym.setRecords(df)

        self._apply_categories(ssym, tsym, suffix_to_index, suffix_list, index_map)

        if self._trace > 0:
            self.describe_container(self._cdb._container, "Connect Container")
        if self._trace > 2:
            self._cdb.print_log(
                f"Connect Container symbol={tsym_name}:\n {tsym.records}\n"
            )
