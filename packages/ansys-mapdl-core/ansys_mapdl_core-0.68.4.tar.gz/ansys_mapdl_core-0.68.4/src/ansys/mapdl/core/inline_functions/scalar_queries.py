# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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

from .core import _QueryExecution


class _ScalarQueries(_QueryExecution):
    _mapdl = None

    def temp(self, n: int) -> float:
        """Returns temperature at node ``n``.

        Temperature at node ``n``.

        Parameters
        ----------
        n : int
            Node number

        Returns
        -------
        float
            Temperature

        Examples
        --------
        We create a block of solid material, and constrain the
        temperature DOF of all its nodes to a uniform value, and then solve.

        Then we can use ``queries.temp`` to get the temperature
        at the first node of the solved model.

        >>> from ansys.mapdl.core import launch_mapdl
        >>> mapdl = launch_mapdl()
        >>> mapdl.clear()
        >>> mapdl.prep7()
        >>> mapdl.mp("kxx", 1, 45)
        >>> mapdl.et(1, 'SOLID70')
        >>> mapdl.block(0, 1, 0, 1, 0, 1)
        >>> mapdl.esize(0.5)
        >>> mapdl.vmesh(1)
        >>> mapdl.d("all", "temp", 5)
        >>> mapdl.slashsolu()
        >>> mapdl.solve()
        >>> mapdl.queries.temp(1)
        5.0
        """
        return self._run_query(f"TEMP({n})", integer=False)

    def pres(self, n: int) -> float:
        """Returns pressure at node ``n``.

        Pressure at node ``n``.

        Parameters
        ----------
        n : int
            Node number

        Returns
        -------
        float
            Pressure

        Examples
        --------
        We create a block of solid material, and constrain the
        pressure DOF of all its nodes to a uniform value, and then solve.

        Then we can use ``queries.pres`` to get the pressure
        at the first node of the solved model.

        >>> mapdl.clear()
        >>> mapdl.prep7()
        >>> mapdl.mp("ex", 1, 1)
        >>> mapdl.et(1, 'CPT215')
        >>> mapdl.keyopt(1, 12, 1)
        >>> mapdl.block(0, 1, 0, 1, 0, 1)
        >>> mapdl.esize(0.5)
        >>> mapdl.vmesh(1)
        >>> mapdl.d("all", "pres", 5)
        >>> mapdl.d("all", "ux", 0, lab2="uy", lab3="uz")
        >>> mapdl.run("/SOLU")
        >>> mapdl.solve()
        >>> mapdl.queries.pres(1)
        5.0
        """
        return self._run_query(f"PRES({n})", integer=False)

    def volt(self, n: int) -> float:
        """Returns electric potential at node ``n``.

        Electric potential at node ``n``.

        Parameters
        ----------
        n : int
            Node number

        Returns
        -------
        float
            Electric potential

        Examples
        --------
        We create a block of solid material, and constrain the
        volt DOF of all its nodes to a uniform value, and then solve.

        Then we can use ``queries.volt`` to get the Electric Potential
        at the first node of the solved model.

        >>> mapdl.clear()
        >>> mapdl.prep7()
        >>> mapdl.mp("perx", 1, 1)
        >>> mapdl.et(1, 'SOLID122')
        >>> mapdl.block(0, 1, 0, 1, 0, 1)
        >>> mapdl.esize(0.5)
        >>> mapdl.vmesh(1)
        >>> mapdl.d("all", "volt", 5)
        >>> mapdl.run("/SOLU")
        >>> mapdl.solve()
        >>> mapdl.queries.volt(1)
        5.0
        """
        return self._run_query(f"VOLT({n})", integer=False)

    def mag(self, n: int) -> float:
        """Returns magnetic scalar potential at node ``n``.

        Magnetic scalar potential at node ``n``.

        Parameters
        ----------
        n : int
            Node number

        Returns
        -------
        float
            Magnetic scalar potential

        Examples
        --------
        We create a block of solid material, and constrain the
        mag DOF of all its nodes to a uniform value, and then solve.

        Then we can use ``queries.mag`` to get the Magnetic Scalar
        Potential at the first node of the solved model.

        >>> mapdl.clear()
        >>> mapdl.prep7()
        >>> mapdl.mp("murx", 1, 1)
        >>> mapdl.et(1, 'SOLID96')
        >>> mapdl.block(0, 1, 0, 1, 0, 1)
        >>> mapdl.esize(0.5)
        >>> mapdl.vmesh(1)
        >>> mapdl.d("all", "mag", 5)
        >>> mapdl.run("/SOLU")
        >>> mapdl.solve()
        >>> mapdl.queries.mag(1)
        5.0
        """
        return self._run_query(f"MAG({n})", integer=False)
