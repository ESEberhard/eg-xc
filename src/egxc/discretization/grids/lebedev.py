# This code has been copied from pyscf
# https://github.com/pyscf/pyscf/blob/master/pyscf/dft/LebedevGrid.py
# and was originally modified from CxLebedevGrid.cpp (from Gerald Knizia).
# The following comments are copied from the header file CxLebedevGrid.h
#
#
# ccgk: This code generates Lebedev grids. It is based on C files from
# ccgk: Dmitri Laikov, which were converted to Fortran by Christoph van Wuellen.
# ccgk: I (Gerald Knizia) subsequently converted them back to C++.
# ccgk:
# ccgk: The original distribution contained the following readme file:
# ccgk:
#
#      Lebedev grids of orders n=6m+5 where m=0,1,...,21 in 16 digit precision
#      =======================================================================
#
#      The file Lebedev-Laikov.F implements a set of subroutines providing
#      Lebedev-Laikov grids of order n=2m+1, where m=1,2,...,15, and additionally
#      grids of order n=6m+5, where m=5,6,...,21. The parameters ensure
#      that angular integration of polynomials x**k * y**l * z**m, where k+l+m <= 131
#      can be performed with a relative accuracy of 2e-14 [1]. Note that the weights
#      are normalised to add up to 1.0.
#
#      For each order n a separate subroutine is provided named
#      LD. The parameters X, Y, Z are arrays for the
#      cartesian components of each point, and the parameter W is an array for the
#      weights. The subroutines increase the integer parameter N by number of grid
#      points generated. All these routines use the subroutine gen_oh which takes care
#      of the octahedral symmetry of the grids.
#
#      Christoph van Wuellen (Ruhr-Universitaet, Bochum, Germany) generated the
#      routines in Lebedev-Laikov.F by translating the original C-routines kindly
#      provided by Dmitri Laikov (Moscow State University, Moscow, Russia). We
#      are in debt to Dmitri Laikov for giving us permission to make these routines
#      publically available.
#
#      Huub van Dam
#      Daresbury Laboratory, Daresbury, United Kingdom
#      April, 2000
#
#      References
#      ==========
#
#      [1] V.I. Lebedev, and D.N. Laikov
#         "A quadrature formula for the sphere of the 131st
#         algebraic order of accuracy"
#         Doklady Mathematics, Vol. 59, No. 3, 1999, pp. 477-481.
#
# ccgk: and the following comments and references for the original of the subroutine SphGenOh:
#
#      chvd
#      chvd   This subroutine is part of a set of subroutines that generate
#      chvd   Lebedev grids [1-6] for integration on a sphere. The original
#      chvd   C-code [1] was kindly provided by Dr. Dmitri N. Laikov and
#      chvd   translated into fortran by Dr. Christoph van Wuellen.
#      chvd   This subroutine was translated from C to fortran77 by hand.
#      chvd
#      chvd   Users of this code are asked to include reference [1] in their
#      chvd   publications, and in the user- and programmers-manuals
#      chvd   describing their codes.
#      chvd
#      chvd   This code was distributed through CCL (http://www.ccl.net/).
#      chvd
#      chvd   [1] V.I. Lebedev, and D.N. Laikov
#      chvd       "A quadrature formula for the sphere of the 131st
#      chvd        algebraic order of accuracy"
#      chvd       Doklady Mathematics, Vol. 59, No. 3, 1999, pp. 477-481.
#      chvd
#      chvd   [2] V.I. Lebedev
#      chvd       "A quadrature formula for the sphere of 59th algebraic
#      chvd        order of accuracy"
#      chvd       Russian Acad. Sci. Dokl. Math., Vol. 50, 1995, pp. 283-286.
#      chvd
#      chvd   [3] V.I. Lebedev, and A.L. Skorokhodov
#      chvd       "Quadrature formulas of orders 41, 47, and 53 for the sphere"
#      chvd       Russian Acad. Sci. Dokl. Math., Vol. 45, 1992, pp. 587-592.
#      chvd
#      chvd   [4] V.I. Lebedev
#      chvd       "Spherical quadrature formulas exact to orders 25-29"
#      chvd       Siberian Mathematical Journal, Vol. 18, 1977, pp. 99-107.
#      chvd
#      chvd   [5] V.I. Lebedev
#      chvd       "Quadratures on a sphere"
#      chvd       Computational Mathematics and Mathematical Physics, Vol. 16,
#      chvd       1976, pp. 10-24.
#      chvd
#      chvd   [6] V.I. Lebedev
#      chvd       "Values of the nodes and weights of ninth to seventeenth
#      chvd        order Gauss-Markov quadrature formulae invariant under the
#      chvd        octahedron group with inversion"
#      chvd       Computational Mathematics and Mathematical Physics, Vol. 15,
#      chvd       1975, pp. 44-51.
#      chvd
#      cvw
#      cvw    Given a point on a sphere (specified by a and b), generate all
#      cvw    the equivalent points under Oh symmetry, making grid points with
#      cvw    weight v.
#      cvw    The variable num is increased by the number of different points
#      cvw    generated.
#      cvw
#      cvw    Depending on code, there are 6...48 different but equivalent
#      cvw    points.
#      cvw
#      cvw    code=1:   (0,0,1) etc                                (  6 points)
#      cvw    code=2:   (0,a,a) etc, a=1/sqrt(2)                   ( 12 points)
#      cvw    code=3:   (a,a,a) etc, a=1/sqrt(3)                   (  8 points)
#      cvw    code=4:   (a,a,b) etc, b=sqrt(1-2 a^2)               ( 24 points)
#      cvw    code=5:   (a,b,0) etc, b=sqrt(1-a^2), a input        ( 24 points)
#      cvw    code=6:   (a,b,c) etc, c=sqrt(1-a^2-b^2), a/b input  ( 48 points)
#      cvw

import numpy as np
from functools import lru_cache


# fmt: off
@lru_cache(maxsize=500)
def SphGenOh(code, a, b, v):
    if code == 0:
        a = 1.0
        g = np.array((
            #  pos/x          pos/y          pos/z         weight
            a,             0.,            0.,            v,
            -a,            0.,            0.,            v,
            0.,            a,             0.,            v,
            0.,            -a,            0.,            v,
            0.,            0.,            a,             v,
            0.,            0.,            -a,            v,
        )).reshape(6, 4)
    elif code == 1:
        a = np.sqrt(0.5)
        g = np.array((
            #  pos/x          pos/y          pos/z         weight
            0.,            a,             a,             v,
            0.,            -a,            a,             v,
            0.,            a,             -a,            v,
            0.,            -a,            -a,            v,
            a,             0.,            a,             v,
            -a,            0.,            a,             v,
            a,             0.,            -a,            v,
            -a,            0.,            -a,            v,
            a,             a,             0.,            v,
            -a,            a,             0.,            v,
            a,             -a,            0.,            v,
            -a,            -a,            0.,            v,
        )).reshape(12, 4)
    elif code == 2:
        a = np.sqrt(1./3.)
        g = np.array((
            #  pos/x          pos/y          pos/z         weight
            a,             a,             a,             v,
            -a,            a,             a,             v,
            a,             -a,            a,             v,
            -a,            -a,            a,             v,
            a,             a,             -a,            v,
            -a,            a,             -a,            v,
            a,             -a,            -a,            v,
            -a,            -a,            -a,            v,
        )).reshape(8, 4)
    elif code == 3:
        b = np.sqrt(1. - 2.*a*a)
        g = np.array((
            #  pos/x          pos/y          pos/z         weight
            a,             a,             b,             v,
            -a,            a,             b,             v,
            a,             -a,            b,             v,
            -a,            -a,            b,             v,
            a,             a,             -b,            v,
            -a,            a,             -b,            v,
            a,             -a,            -b,            v,
            -a,            -a,            -b,            v,
            a,             b,             a,             v,
            -a,            b,             a,             v,
            a,             -b,            a,             v,
            -a,            -b,            a,             v,
            a,             b,             -a,            v,
            -a,            b,             -a,            v,
            a,             -b,            -a,            v,
            -a,            -b,            -a,            v,
            b,             a,             a,             v,
            -b,            a,             a,             v,
            b,             -a,            a,             v,
            -b,            -a,            a,             v,
            b,             a,             -a,            v,
            -b,            a,             -a,            v,
            b,             -a,            -a,            v,
            -b,            -a,            -a,            v,
        )).reshape(24, 4)
    elif code == 4:
        b = np.sqrt(1. - a*a)
        g = np.array((
            #  pos/x          pos/y          pos/z         weight
            a,             b,             0.,            v,
            -a,            b,             0.,            v,
            a,             -b,            0.,            v,
            -a,            -b,            0.,            v,
            b,             a,             0.,            v,
            -b,            a,             0.,            v,
            b,             -a,            0.,            v,
            -b,            -a,            0.,            v,
            a,             0.,            b,             v,
            -a,            0.,            b,             v,
            a,             0.,            -b,            v,
            -a,            0.,            -b,            v,
            b,             0.,            a,             v,
            -b,            0.,            a,             v,
            b,             0.,            -a,            v,
            -b,            0.,            -a,            v,
            0.,            a,             b,             v,
            0.,            -a,            b,             v,
            0.,            a,             -b,            v,
            0.,            -a,            -b,            v,
            0.,            b,             a,             v,
            0.,            -b,            a,             v,
            0.,            b,             -a,            v,
            0.,            -b,            -a,            v,
        )).reshape(24, 4)
    elif code == 5:
        c = np.sqrt(1. - a*a - b*b)
        g = np.array((
            #  pos/x          pos/y          pos/z         weight
            a,             b,             c,             v,
            -a,            b,             c,             v,
            a,             -b,            c,             v,
            -a,            -b,            c,             v,
            a,             b,             -c,            v,
            -a,            b,             -c,            v,
            a,             -b,            -c,            v,
            -a,            -b,            -c,            v,
            a,             c,             b,             v,
            -a,            c,             b,             v,
            a,             -c,            b,             v,
            -a,            -c,            b,             v,
            a,             c,             -b,            v,
            -a,            c,             -b,            v,
            a,             -c,            -b,            v,
            -a,            -c,            -b,            v,
            b,             a,             c,             v,
            -b,            a,             c,             v,
            b,             -a,            c,             v,
            -b,            -a,            c,             v,
            b,             a,             -c,            v,
            -b,            a,             -c,            v,
            b,             -a,            -c,            v,
            -b,            -a,            -c,            v,
            b,             c,             a,             v,
            -b,            c,             a,             v,
            b,             -c,            a,             v,
            -b,            -c,            a,             v,
            b,             c,             -a,            v,
            -b,            c,             -a,            v,
            b,             -c,            -a,            v,
            -b,            -c,            -a,            v,
            c,             a,             b,             v,
            -c,            a,             b,             v,
            c,             -a,            b,             v,
            -c,            -a,            b,             v,
            c,             a,             -b,            v,
            -c,            a,             -b,            v,
            c,             -a,            -b,            v,
            -c,            -a,            -b,            v,
            c,             b,             a,             v,
            -c,            b,             a,             v,
            c,             -b,            a,             v,
            -c,            -b,            a,             v,
            c,             b,             -a,            v,
            -c,            b,             -a,            v,
            c,             -b,            -a,            v,
            -c,            -b,            -a,            v,
        )).reshape(48, 4)
    return g # type: ignore
# fmt: on


def MakeAngularGrid_6():
    grids = []
    a = 0
    b = 0
    v = 0.1666666666666667e0
    grids.append(SphGenOh(0, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_14():
    grids = []
    a = 0
    b = 0
    v = 0.6666666666666667e-1
    grids.append(SphGenOh(0, a, b, v))
    v = 0.7500000000000000e-1
    grids.append(SphGenOh(2, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_26():
    grids = []
    a = 0
    b = 0
    v = 0.4761904761904762e-1
    grids.append(SphGenOh(0, a, b, v))
    v = 0.3809523809523810e-1
    grids.append(SphGenOh(1, a, b, v))
    v = 0.3214285714285714e-1
    grids.append(SphGenOh(2, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_38():
    grids = []
    a = 0
    b = 0
    v = 0.9523809523809524e-2
    grids.append(SphGenOh(0, a, b, v))
    v = 0.3214285714285714e-1
    grids.append(SphGenOh(2, a, b, v))
    a = 0.4597008433809831e0
    v = 0.2857142857142857e-1
    grids.append(SphGenOh(4, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_50():
    grids = []
    a = 0
    b = 0
    v = 0.1269841269841270e-1
    grids.append(SphGenOh(0, a, b, v))
    v = 0.2257495590828924e-1
    grids.append(SphGenOh(1, a, b, v))
    v = 0.2109375000000000e-1
    grids.append(SphGenOh(2, a, b, v))
    a = 0.3015113445777636e0
    v = 0.2017333553791887e-1
    grids.append(SphGenOh(3, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_74():
    grids = []
    a = 0
    b = 0
    v = 0.5130671797338464e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.1660406956574204e-1
    grids.append(SphGenOh(1, a, b, v))
    v = -0.2958603896103896e-1
    grids.append(SphGenOh(2, a, b, v))
    a = 0.4803844614152614e0
    v = 0.2657620708215946e-1
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3207726489807764e0
    v = 0.1652217099371571e-1
    grids.append(SphGenOh(4, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_86():
    grids = []
    a = 0
    b = 0
    v = 0.1154401154401154e-1
    grids.append(SphGenOh(0, a, b, v))
    v = 0.1194390908585628e-1
    grids.append(SphGenOh(2, a, b, v))
    a = 0.3696028464541502e0
    v = 0.1111055571060340e-1
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6943540066026664e0
    v = 0.1187650129453714e-1
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3742430390903412e0
    v = 0.1181230374690448e-1
    grids.append(SphGenOh(4, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_110():
    grids = []
    a = 0
    b = 0
    v = 0.3828270494937162e-2
    grids.append(SphGenOh(0, a, b, v))
    v = 0.9793737512487512e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.1851156353447362e0
    v = 0.8211737283191111e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6904210483822922e0
    v = 0.9942814891178103e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3956894730559419e0
    v = 0.9595471336070963e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4783690288121502e0
    v = 0.9694996361663028e-2
    grids.append(SphGenOh(4, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_146():
    grids = []
    a = 0
    b = 0
    v = 0.5996313688621381e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.7372999718620756e-2
    grids.append(SphGenOh(1, a, b, v))
    v = 0.7210515360144488e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.6764410400114264e0
    v = 0.7116355493117555e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4174961227965453e0
    v = 0.6753829486314477e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1574676672039082e0
    v = 0.7574394159054034e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1403553811713183e0
    b = 0.4493328323269557e0
    v = 0.6991087353303262e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_170():
    grids = []
    a = 0
    b = 0
    v = 0.5544842902037365e-2
    grids.append(SphGenOh(0, a, b, v))
    v = 0.6071332770670752e-2
    grids.append(SphGenOh(1, a, b, v))
    v = 0.6383674773515093e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2551252621114134e0
    v = 0.5183387587747790e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6743601460362766e0
    v = 0.6317929009813725e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4318910696719410e0
    v = 0.6201670006589077e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2613931360335988e0
    v = 0.5477143385137348e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4990453161796037e0
    b = 0.1446630744325115e0
    v = 0.5968383987681156e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_194():
    grids = []
    a = 0
    b = 0
    v = 0.1782340447244611e-2
    grids.append(SphGenOh(0, a, b, v))
    v = 0.5716905949977102e-2
    grids.append(SphGenOh(1, a, b, v))
    v = 0.5573383178848738e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.6712973442695226e0
    v = 0.5608704082587997e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2892465627575439e0
    v = 0.5158237711805383e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4446933178717437e0
    v = 0.5518771467273614e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1299335447650067e0
    v = 0.4106777028169394e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3457702197611283e0
    v = 0.5051846064614808e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1590417105383530e0
    b = 0.8360360154824589e0
    v = 0.5530248916233094e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_230():
    grids = []
    a = 0
    b = 0
    v = -0.5522639919727325e-1
    grids.append(SphGenOh(0, a, b, v))
    v = 0.4450274607445226e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.4492044687397611e0
    v = 0.4496841067921404e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2520419490210201e0
    v = 0.5049153450478750e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6981906658447242e0
    v = 0.3976408018051883e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6587405243460960e0
    v = 0.4401400650381014e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4038544050097660e-1
    v = 0.1724544350544401e-1
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5823842309715585e0
    v = 0.4231083095357343e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3545877390518688e0
    v = 0.5198069864064399e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2272181808998187e0
    b = 0.4864661535886647e0
    v = 0.4695720972568883e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_266():
    grids = []
    a = 0
    b = 0
    v = -0.1313769127326952e-2
    grids.append(SphGenOh(0, a, b, v))
    v = -0.2522728704859336e-2
    grids.append(SphGenOh(1, a, b, v))
    v = 0.4186853881700583e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.7039373391585475e0
    v = 0.5315167977810885e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1012526248572414e0
    v = 0.4047142377086219e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4647448726420539e0
    v = 0.4112482394406990e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3277420654971629e0
    v = 0.3595584899758782e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6620338663699974e0
    v = 0.4256131351428158e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8506508083520399e0
    v = 0.4229582700647240e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3233484542692899e0
    b = 0.1153112011009701e0
    v = 0.4080914225780505e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2314790158712601e0
    b = 0.5244939240922365e0
    v = 0.4071467593830964e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_302():
    grids = []
    a = 0
    b = 0
    v = 0.8545911725128148e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.3599119285025571e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.3515640345570105e0
    v = 0.3449788424305883e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6566329410219612e0
    v = 0.3604822601419882e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4729054132581005e0
    v = 0.3576729661743367e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.9618308522614784e-1
    v = 0.2352101413689164e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2219645236294178e0
    v = 0.3108953122413675e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7011766416089545e0
    v = 0.3650045807677255e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2644152887060663e0
    v = 0.2982344963171804e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5718955891878961e0
    v = 0.3600820932216460e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2510034751770465e0
    b = 0.8000727494073952e0
    v = 0.3571540554273387e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1233548532583327e0
    b = 0.4127724083168531e0
    v = 0.3392312205006170e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_350():
    grids = []
    a = 0
    b = 0
    v = 0.3006796749453936e-2
    grids.append(SphGenOh(0, a, b, v))
    v = 0.3050627745650771e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.7068965463912316e0
    v = 0.1621104600288991e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4794682625712025e0
    v = 0.3005701484901752e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1927533154878019e0
    v = 0.2990992529653774e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6930357961327123e0
    v = 0.2982170644107595e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3608302115520091e0
    v = 0.2721564237310992e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6498486161496169e0
    v = 0.3033513795811141e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1932945013230339e0
    v = 0.3007949555218533e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3800494919899303e0
    v = 0.2881964603055307e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2899558825499574e0
    b = 0.7934537856582316e0
    v = 0.2958357626535696e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9684121455103957e-1
    b = 0.8280801506686862e0
    v = 0.3036020026407088e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1833434647041659e0
    b = 0.9074658265305127e0
    v = 0.2832187403926303e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_434():
    grids = []
    a = 0
    b = 0
    v = 0.5265897968224436e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.2548219972002607e-2
    grids.append(SphGenOh(1, a, b, v))
    v = 0.2512317418927307e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.6909346307509111e0
    v = 0.2530403801186355e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1774836054609158e0
    v = 0.2014279020918528e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4914342637784746e0
    v = 0.2501725168402936e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6456664707424256e0
    v = 0.2513267174597564e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2861289010307638e0
    v = 0.2302694782227416e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7568084367178018e-1
    v = 0.1462495621594614e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3927259763368002e0
    v = 0.2445373437312980e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8818132877794288e0
    v = 0.2417442375638981e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9776428111182649e0
    v = 0.1910951282179532e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2054823696403044e0
    b = 0.8689460322872412e0
    v = 0.2416930044324775e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5905157048925271e0
    b = 0.7999278543857286e0
    v = 0.2512236854563495e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5550152361076807e0
    b = 0.7717462626915901e0
    v = 0.2496644054553086e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9371809858553722e0
    b = 0.3344363145343455e0
    v = 0.2236607760437849e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_590():
    grids = []
    a = 0
    b = 0
    v = 0.3095121295306187e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.1852379698597489e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.7040954938227469e0
    v = 0.1871790639277744e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6807744066455243e0
    v = 0.1858812585438317e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6372546939258752e0
    v = 0.1852028828296213e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5044419707800358e0
    v = 0.1846715956151242e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4215761784010967e0
    v = 0.1818471778162769e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3317920736472123e0
    v = 0.1749564657281154e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2384736701421887e0
    v = 0.1617210647254411e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1459036449157763e0
    v = 0.1384737234851692e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6095034115507196e-1
    v = 0.9764331165051050e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6116843442009876e0
    v = 0.1857161196774078e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3964755348199858e0
    v = 0.1705153996395864e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1724782009907724e0
    v = 0.1300321685886048e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5610263808622060e0
    b = 0.3518280927733519e0
    v = 0.1842866472905286e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4742392842551980e0
    b = 0.2634716655937950e0
    v = 0.1802658934377451e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5984126497885380e0
    b = 0.1816640840360209e0
    v = 0.1849830560443660e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3791035407695563e0
    b = 0.1720795225656878e0
    v = 0.1713904507106709e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2778673190586244e0
    b = 0.8213021581932511e-1
    v = 0.1555213603396808e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5033564271075117e0
    b = 0.8999205842074875e-1
    v = 0.1802239128008525e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_770():
    grids = []
    a = 0
    b = 0
    v = 0.2192942088181184e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.1436433617319080e-2
    grids.append(SphGenOh(1, a, b, v))
    v = 0.1421940344335877e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.5087204410502360e-1
    v = 0.6798123511050502e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1228198790178831e0
    v = 0.9913184235294912e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2026890814408786e0
    v = 0.1180207833238949e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2847745156464294e0
    v = 0.1296599602080921e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3656719078978026e0
    v = 0.1365871427428316e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4428264886713469e0
    v = 0.1402988604775325e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5140619627249735e0
    v = 0.1418645563595609e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6306401219166803e0
    v = 0.1421376741851662e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6716883332022612e0
    v = 0.1423996475490962e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6979792685336881e0
    v = 0.1431554042178567e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1446865674195309e0
    v = 0.9254401499865368e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3390263475411216e0
    v = 0.1250239995053509e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5335804651263506e0
    v = 0.1394365843329230e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6944024393349413e-1
    b = 0.2355187894242326e0
    v = 0.1127089094671749e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2269004109529460e0
    b = 0.4102182474045730e0
    v = 0.1345753760910670e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8025574607775339e-1
    b = 0.6214302417481605e0
    v = 0.1424957283316783e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1467999527896572e0
    b = 0.3245284345717394e0
    v = 0.1261523341237750e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1571507769824727e0
    b = 0.5224482189696630e0
    v = 0.1392547106052696e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2365702993157246e0
    b = 0.6017546634089558e0
    v = 0.1418761677877656e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7714815866765732e-1
    b = 0.4346575516141163e0
    v = 0.1338366684479554e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3062936666210730e0
    b = 0.4908826589037616e0
    v = 0.1393700862676131e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3822477379524787e0
    b = 0.5648768149099500e0
    v = 0.1415914757466932e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_974():
    grids = []
    a = 0
    b = 0
    v = 0.1438294190527431e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.1125772288287004e-2
    grids.append(SphGenOh(2, a, b, v))
    a = 0.4292963545341347e-1
    v = 0.4948029341949241e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1051426854086404e0
    v = 0.7357990109125470e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1750024867623087e0
    v = 0.8889132771304384e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2477653379650257e0
    v = 0.9888347838921435e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3206567123955957e0
    v = 0.1053299681709471e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3916520749849983e0
    v = 0.1092778807014578e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4590825874187624e0
    v = 0.1114389394063227e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5214563888415861e0
    v = 0.1123724788051555e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6253170244654199e0
    v = 0.1125239325243814e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6637926744523170e0
    v = 0.1126153271815905e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6910410398498301e0
    v = 0.1130286931123841e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7052907007457760e0
    v = 0.1134986534363955e-2
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1236686762657990e0
    v = 0.6823367927109931e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2940777114468387e0
    v = 0.9454158160447096e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4697753849207649e0
    v = 0.1074429975385679e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6334563241139567e0
    v = 0.1129300086569132e-2
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5974048614181342e-1
    b = 0.2029128752777523e0
    v = 0.8436884500901954e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1375760408473636e0
    b = 0.4602621942484054e0
    v = 0.1075255720448885e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3391016526336286e0
    b = 0.5030673999662036e0
    v = 0.1108577236864462e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1271675191439820e0
    b = 0.2817606422442134e0
    v = 0.9566475323783357e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2693120740413512e0
    b = 0.4331561291720157e0
    v = 0.1080663250717391e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1419786452601918e0
    b = 0.6256167358580814e0
    v = 0.1126797131196295e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6709284600738255e-1
    b = 0.3798395216859157e0
    v = 0.1022568715358061e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7057738183256172e-1
    b = 0.5517505421423520e0
    v = 0.1108960267713108e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2783888477882155e0
    b = 0.6029619156159187e0
    v = 0.1122790653435766e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1979578938917407e0
    b = 0.3589606329589096e0
    v = 0.1032401847117460e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2087307061103274e0
    b = 0.5348666438135476e0
    v = 0.1107249382283854e-2
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4055122137872836e0
    b = 0.5674997546074373e0
    v = 0.1121780048519972e-2
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_1202():
    grids = []
    a = 0
    b = 0
    v = 0.1105189233267572e-3
    grids.append(SphGenOh(0, a, b, v))
    v = 0.9205232738090741e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.9133159786443561e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.3712636449657089e-1
    v = 0.3690421898017899e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.9140060412262223e-1
    v = 0.5603990928680660e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1531077852469906e0
    v = 0.6865297629282609e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2180928891660612e0
    v = 0.7720338551145630e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2839874532200175e0
    v = 0.8301545958894795e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3491177600963764e0
    v = 0.8686692550179628e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4121431461444309e0
    v = 0.8927076285846890e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4718993627149127e0
    v = 0.9060820238568219e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5273145452842337e0
    v = 0.9119777254940867e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6209475332444019e0
    v = 0.9128720138604181e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6569722711857291e0
    v = 0.9130714935691735e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6841788309070143e0
    v = 0.9152873784554116e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7012604330123631e0
    v = 0.9187436274321654e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1072382215478166e0
    v = 0.5176977312965694e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2582068959496968e0
    v = 0.7331143682101417e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4172752955306717e0
    v = 0.8463232836379928e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5700366911792503e0
    v = 0.9031122694253992e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9827986018263947e0
    b = 0.1771774022615325e0
    v = 0.6485778453163257e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9624249230326228e0
    b = 0.2475716463426288e0
    v = 0.7435030910982369e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9402007994128811e0
    b = 0.3354616289066489e0
    v = 0.7998527891839054e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9320822040143202e0
    b = 0.3173615246611977e0
    v = 0.8101731497468018e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9043674199393299e0
    b = 0.4090268427085357e0
    v = 0.8483389574594331e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8912407560074747e0
    b = 0.3854291150669224e0
    v = 0.8556299257311812e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8676435628462708e0
    b = 0.4932221184851285e0
    v = 0.8803208679738260e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8581979986041619e0
    b = 0.4785320675922435e0
    v = 0.8811048182425720e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8396753624049856e0
    b = 0.4507422593157064e0
    v = 0.8850282341265444e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8165288564022188e0
    b = 0.5632123020762100e0
    v = 0.9021342299040653e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8015469370783529e0
    b = 0.5434303569693900e0
    v = 0.9010091677105086e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7773563069070351e0
    b = 0.5123518486419871e0
    v = 0.9022692938426915e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7661621213900394e0
    b = 0.6394279634749102e0
    v = 0.9158016174693465e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7553584143533510e0
    b = 0.6269805509024392e0
    v = 0.9131578003189435e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7344305757559503e0
    b = 0.6031161693096310e0
    v = 0.9107813579482705e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.7043837184021765e0
    b = 0.5693702498468441e0
    v = 0.9105760258970126e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_1454():
    grids = []
    a = 0
    b = 0
    v = 0.7777160743261247e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.7557646413004701e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.3229290663413854e-1
    v = 0.2841633806090617e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8036733271462222e-1
    v = 0.4374419127053555e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1354289960531653e0
    v = 0.5417174740872172e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1938963861114426e0
    v = 0.6148000891358593e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2537343715011275e0
    v = 0.6664394485800705e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3135251434752570e0
    v = 0.7025039356923220e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3721558339375338e0
    v = 0.7268511789249627e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4286809575195696e0
    v = 0.7422637534208629e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4822510128282994e0
    v = 0.7509545035841214e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5320679333566263e0
    v = 0.7548535057718401e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6172998195394274e0
    v = 0.7554088969774001e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6510679849127481e0
    v = 0.7553147174442808e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6777315251687360e0
    v = 0.7564767653292297e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6963109410648741e0
    v = 0.7587991808518730e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7058935009831749e0
    v = 0.7608261832033027e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.9955546194091857e0
    v = 0.4021680447874916e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9734115901794209e0
    v = 0.5804871793945964e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9275693732388626e0
    v = 0.6792151955945159e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.8568022422795103e0
    v = 0.7336741211286294e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.7623495553719372e0
    v = 0.7581866300989608e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5707522908892223e0
    b = 0.4387028039889501e0
    v = 0.7538257859800743e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5196463388403083e0
    b = 0.3858908414762617e0
    v = 0.7483517247053123e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4646337531215351e0
    b = 0.3301937372343854e0
    v = 0.7371763661112059e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4063901697557691e0
    b = 0.2725423573563777e0
    v = 0.7183448895756934e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3456329466643087e0
    b = 0.2139510237495250e0
    v = 0.6895815529822191e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2831395121050332e0
    b = 0.1555922309786647e0
    v = 0.6480105801792886e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2197682022925330e0
    b = 0.9892878979686097e-1
    v = 0.5897558896594636e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1564696098650355e0
    b = 0.4598642910675510e-1
    v = 0.5095708849247346e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6027356673721295e0
    b = 0.3376625140173426e0
    v = 0.7536906428909755e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5496032320255096e0
    b = 0.2822301309727988e0
    v = 0.7472505965575118e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4921707755234567e0
    b = 0.2248632342592540e0
    v = 0.7343017132279698e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4309422998598483e0
    b = 0.1666224723456479e0
    v = 0.7130871582177445e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3664108182313672e0
    b = 0.1086964901822169e0
    v = 0.6817022032112776e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2990189057758436e0
    b = 0.5251989784120085e-1
    v = 0.6380941145604121e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6268724013144998e0
    b = 0.2297523657550023e0
    v = 0.7550381377920310e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5707324144834607e0
    b = 0.1723080607093800e0
    v = 0.7478646640144802e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5096360901960365e0
    b = 0.1140238465390513e0
    v = 0.7335918720601220e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4438729938312456e0
    b = 0.5611522095882537e-1
    v = 0.7110120527658118e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6419978471082389e0
    b = 0.1164174423140873e0
    v = 0.7571363978689501e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5817218061802611e0
    b = 0.5797589531445219e-1
    v = 0.7489908329079234e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_1730():
    grids = []
    a = 0
    b = 0
    v = 0.6309049437420976e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.6398287705571748e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.6357185073530720e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2860923126194662e-1
    v = 0.2221207162188168e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7142556767711522e-1
    v = 0.3475784022286848e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1209199540995559e0
    v = 0.4350742443589804e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1738673106594379e0
    v = 0.4978569136522127e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2284645438467734e0
    v = 0.5435036221998053e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2834807671701512e0
    v = 0.5765913388219542e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3379680145467339e0
    v = 0.6001200359226003e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3911355454819537e0
    v = 0.6162178172717512e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4422860353001403e0
    v = 0.6265218152438485e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4907781568726057e0
    v = 0.6323987160974212e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5360006153211468e0
    v = 0.6350767851540569e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6142105973596603e0
    v = 0.6354362775297107e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6459300387977504e0
    v = 0.6352302462706235e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6718056125089225e0
    v = 0.6358117881417972e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6910888533186254e0
    v = 0.6373101590310117e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7030467416823252e0
    v = 0.6390428961368665e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8354951166354646e-1
    v = 0.3186913449946576e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2050143009099486e0
    v = 0.4678028558591711e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3370208290706637e0
    v = 0.5538829697598626e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4689051484233963e0
    v = 0.6044475907190476e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5939400424557334e0
    v = 0.6313575103509012e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1394983311832261e0
    b = 0.4097581162050343e-1
    v = 0.4078626431855630e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1967999180485014e0
    b = 0.8851987391293348e-1
    v = 0.4759933057812725e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2546183732548967e0
    b = 0.1397680182969819e0
    v = 0.5268151186413440e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3121281074713875e0
    b = 0.1929452542226526e0
    v = 0.5643048560507316e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3685981078502492e0
    b = 0.2467898337061562e0
    v = 0.5914501076613073e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4233760321547856e0
    b = 0.3003104124785409e0
    v = 0.6104561257874195e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4758671236059246e0
    b = 0.3526684328175033e0
    v = 0.6230252860707806e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5255178579796463e0
    b = 0.4031134861145713e0
    v = 0.6305618761760796e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5718025633734589e0
    b = 0.4509426448342351e0
    v = 0.6343092767597889e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2686927772723415e0
    b = 0.4711322502423248e-1
    v = 0.5176268945737826e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3306006819904809e0
    b = 0.9784487303942695e-1
    v = 0.5564840313313692e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3904906850594983e0
    b = 0.1505395810025273e0
    v = 0.5856426671038980e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4479957951904390e0
    b = 0.2039728156296050e0
    v = 0.6066386925777091e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5027076848919780e0
    b = 0.2571529941121107e0
    v = 0.6208824962234458e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5542087392260217e0
    b = 0.3092191375815670e0
    v = 0.6296314297822907e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6020850887375187e0
    b = 0.3593807506130276e0
    v = 0.6340423756791859e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4019851409179594e0
    b = 0.5063389934378671e-1
    v = 0.5829627677107342e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4635614567449800e0
    b = 0.1032422269160612e0
    v = 0.6048693376081110e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5215860931591575e0
    b = 0.1566322094006254e0
    v = 0.6202362317732461e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5758202499099271e0
    b = 0.2098082827491099e0
    v = 0.6299005328403779e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6259893683876795e0
    b = 0.2618824114553391e0
    v = 0.6347722390609353e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5313795124811891e0
    b = 0.5263245019338556e-1
    v = 0.6203778981238834e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5893317955931995e0
    b = 0.1061059730982005e0
    v = 0.6308414671239979e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6426246321215801e0
    b = 0.1594171564034221e0
    v = 0.6362706466959498e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6511904367376113e0
    b = 0.5354789536565540e-1
    v = 0.6375414170333233e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_2030():
    grids = []
    a = 0
    b = 0
    v = 0.4656031899197431e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.5421549195295507e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2540835336814348e-1
    v = 0.1778522133346553e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6399322800504915e-1
    v = 0.2811325405682796e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1088269469804125e0
    v = 0.3548896312631459e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1570670798818287e0
    v = 0.4090310897173364e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2071163932282514e0
    v = 0.4493286134169965e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2578914044450844e0
    v = 0.4793728447962723e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3085687558169623e0
    v = 0.5015415319164265e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3584719706267024e0
    v = 0.5175127372677937e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4070135594428709e0
    v = 0.5285522262081019e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4536618626222638e0
    v = 0.5356832703713962e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4979195686463577e0
    v = 0.5397914736175170e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5393075111126999e0
    v = 0.5416899441599930e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6115617676843916e0
    v = 0.5419308476889938e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6414308435160159e0
    v = 0.5416936902030596e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6664099412721607e0
    v = 0.5419544338703164e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6859161771214913e0
    v = 0.5428983656630975e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6993625593503890e0
    v = 0.5442286500098193e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7062393387719380e0
    v = 0.5452250345057301e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7479028168349763e-1
    v = 0.2568002497728530e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1848951153969366e0
    v = 0.3827211700292145e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3059529066581305e0
    v = 0.4579491561917824e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4285556101021362e0
    v = 0.5042003969083574e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5468758653496526e0
    v = 0.5312708889976025e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6565821978343439e0
    v = 0.5438401790747117e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1253901572367117e0
    b = 0.3681917226439641e-1
    v = 0.3316041873197344e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1775721510383941e0
    b = 0.7982487607213301e-1
    v = 0.3899113567153771e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2305693358216114e0
    b = 0.1264640966592335e0
    v = 0.4343343327201309e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2836502845992063e0
    b = 0.1751585683418957e0
    v = 0.4679415262318919e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3361794746232590e0
    b = 0.2247995907632670e0
    v = 0.4930847981631031e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3875979172264824e0
    b = 0.2745299257422246e0
    v = 0.5115031867540091e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4374019316999074e0
    b = 0.3236373482441118e0
    v = 0.5245217148457367e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4851275843340022e0
    b = 0.3714967859436741e0
    v = 0.5332041499895321e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5303391803806868e0
    b = 0.4175353646321745e0
    v = 0.5384583126021542e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5726197380596287e0
    b = 0.4612084406355461e0
    v = 0.5411067210798852e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2431520732564863e0
    b = 0.4258040133043952e-1
    v = 0.4259797391468714e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3002096800895869e0
    b = 0.8869424306722721e-1
    v = 0.4604931368460021e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3558554457457432e0
    b = 0.1368811706510655e0
    v = 0.4871814878255202e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4097782537048887e0
    b = 0.1860739985015033e0
    v = 0.5072242910074885e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4616337666067458e0
    b = 0.2354235077395853e0
    v = 0.5217069845235350e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5110707008417874e0
    b = 0.2842074921347011e0
    v = 0.5315785966280310e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5577415286163795e0
    b = 0.3317784414984102e0
    v = 0.5376833708758905e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6013060431366950e0
    b = 0.3775299002040700e0
    v = 0.5408032092069521e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3661596767261781e0
    b = 0.4599367887164592e-1
    v = 0.4842744917904866e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4237633153506581e0
    b = 0.9404893773654421e-1
    v = 0.5048926076188130e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4786328454658452e0
    b = 0.1431377109091971e0
    v = 0.5202607980478373e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5305702076789774e0
    b = 0.1924186388843570e0
    v = 0.5309932388325743e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5793436224231788e0
    b = 0.2411590944775190e0
    v = 0.5377419770895208e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6247069017094747e0
    b = 0.2886871491583605e0
    v = 0.5411696331677717e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4874315552535204e0
    b = 0.4804978774953206e-1
    v = 0.5197996293282420e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5427337322059053e0
    b = 0.9716857199366665e-1
    v = 0.5311120836622945e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5943493747246700e0
    b = 0.1465205839795055e0
    v = 0.5384309319956951e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6421314033564943e0
    b = 0.1953579449803574e0
    v = 0.5421859504051886e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6020628374713980e0
    b = 0.4916375015738108e-1
    v = 0.5390948355046314e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6529222529856881e0
    b = 0.9861621540127005e-1
    v = 0.5433312705027845e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_2354():
    grids = []
    a = 0
    b = 0
    v = 0.3922616270665292e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.4703831750854424e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.4678202801282136e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2290024646530589e-1
    v = 0.1437832228979900e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5779086652271284e-1
    v = 0.2303572493577644e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.9863103576375984e-1
    v = 0.2933110752447454e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1428155792982185e0
    v = 0.3402905998359838e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1888978116601463e0
    v = 0.3759138466870372e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2359091682970210e0
    v = 0.4030638447899798e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2831228833706171e0
    v = 0.4236591432242211e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3299495857966693e0
    v = 0.4390522656946746e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3758840802660796e0
    v = 0.4502523466626247e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4204751831009480e0
    v = 0.4580577727783541e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4633068518751051e0
    v = 0.4631391616615899e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5039849474507313e0
    v = 0.4660928953698676e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5421265793440747e0
    v = 0.4674751807936953e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6092660230557310e0
    v = 0.4676414903932920e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6374654204984869e0
    v = 0.4674086492347870e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6615136472609892e0
    v = 0.4674928539483207e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6809487285958127e0
    v = 0.4680748979686447e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6952980021665196e0
    v = 0.4690449806389040e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7041245497695400e0
    v = 0.4699877075860818e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6744033088306065e-1
    v = 0.2099942281069176e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1678684485334166e0
    v = 0.3172269150712804e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2793559049539613e0
    v = 0.3832051358546523e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3935264218057639e0
    v = 0.4252193818146985e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5052629268232558e0
    v = 0.4513807963755000e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6107905315437531e0
    v = 0.4657797469114178e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1135081039843524e0
    b = 0.3331954884662588e-1
    v = 0.2733362800522836e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1612866626099378e0
    b = 0.7247167465436538e-1
    v = 0.3235485368463559e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2100786550168205e0
    b = 0.1151539110849745e0
    v = 0.3624908726013453e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2592282009459942e0
    b = 0.1599491097143677e0
    v = 0.3925540070712828e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3081740561320203e0
    b = 0.2058699956028027e0
    v = 0.4156129781116235e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3564289781578164e0
    b = 0.2521624953502911e0
    v = 0.4330644984623263e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4035587288240703e0
    b = 0.2982090785797674e0
    v = 0.4459677725921312e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4491671196373903e0
    b = 0.3434762087235733e0
    v = 0.4551593004456795e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4928854782917489e0
    b = 0.3874831357203437e0
    v = 0.4613341462749918e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5343646791958988e0
    b = 0.4297814821746926e0
    v = 0.4651019618269806e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5732683216530990e0
    b = 0.4699402260943537e0
    v = 0.4670249536100625e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2214131583218986e0
    b = 0.3873602040643895e-1
    v = 0.3549555576441708e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2741796504750071e0
    b = 0.8089496256902013e-1
    v = 0.3856108245249010e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3259797439149485e0
    b = 0.1251732177620872e0
    v = 0.4098622845756882e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3765441148826891e0
    b = 0.1706260286403185e0
    v = 0.4286328604268950e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4255773574530558e0
    b = 0.2165115147300408e0
    v = 0.4427802198993945e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4727795117058430e0
    b = 0.2622089812225259e0
    v = 0.4530473511488561e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5178546895819012e0
    b = 0.3071721431296201e0
    v = 0.4600805475703138e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5605141192097460e0
    b = 0.3508998998801138e0
    v = 0.4644599059958017e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6004763319352512e0
    b = 0.3929160876166931e0
    v = 0.4667274455712508e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3352842634946949e0
    b = 0.4202563457288019e-1
    v = 0.4069360518020356e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3891971629814670e0
    b = 0.8614309758870850e-1
    v = 0.4260442819919195e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4409875565542281e0
    b = 0.1314500879380001e0
    v = 0.4408678508029063e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4904893058592484e0
    b = 0.1772189657383859e0
    v = 0.4518748115548597e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5375056138769549e0
    b = 0.2228277110050294e0
    v = 0.4595564875375116e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5818255708669969e0
    b = 0.2677179935014386e0
    v = 0.4643988774315846e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6232334858144959e0
    b = 0.3113675035544165e0
    v = 0.4668827491646946e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4489485354492058e0
    b = 0.4409162378368174e-1
    v = 0.4400541823741973e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5015136875933150e0
    b = 0.8939009917748489e-1
    v = 0.4514512890193797e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5511300550512623e0
    b = 0.1351806029383365e0
    v = 0.4596198627347549e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5976720409858000e0
    b = 0.1808370355053196e0
    v = 0.4648659016801781e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6409956378989354e0
    b = 0.2257852192301602e0
    v = 0.4675502017157673e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5581222330827514e0
    b = 0.4532173421637160e-1
    v = 0.4598494476455523e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6074705984161695e0
    b = 0.9117488031840314e-1
    v = 0.4654916955152048e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6532272537379033e0
    b = 0.1369294213140155e0
    v = 0.4684709779505137e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6594761494500487e0
    b = 0.4589901487275583e-1
    v = 0.4691445539106986e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_2702():
    grids = []
    a = 0
    b = 0
    v = 0.2998675149888161e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.4077860529495355e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2065562538818703e-1
    v = 0.1185349192520667e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5250918173022379e-1
    v = 0.1913408643425751e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8993480082038376e-1
    v = 0.2452886577209897e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1306023924436019e0
    v = 0.2862408183288702e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1732060388531418e0
    v = 0.3178032258257357e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2168727084820249e0
    v = 0.3422945667633690e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2609528309173586e0
    v = 0.3612790520235922e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3049252927938952e0
    v = 0.3758638229818521e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3483484138084404e0
    v = 0.3868711798859953e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3908321549106406e0
    v = 0.3949429933189938e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4320210071894814e0
    v = 0.4006068107541156e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4715824795890053e0
    v = 0.4043192149672723e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5091984794078453e0
    v = 0.4064947495808078e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5445580145650803e0
    v = 0.4075245619813152e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6072575796841768e0
    v = 0.4076423540893566e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6339484505755803e0
    v = 0.4074280862251555e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6570718257486958e0
    v = 0.4074163756012244e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6762557330090709e0
    v = 0.4077647795071246e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6911161696923790e0
    v = 0.4084517552782530e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7012841911659961e0
    v = 0.4092468459224052e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7064559272410020e0
    v = 0.4097872687240906e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6123554989894765e-1
    v = 0.1738986811745028e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1533070348312393e0
    v = 0.2659616045280191e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2563902605244206e0
    v = 0.3240596008171533e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3629346991663361e0
    v = 0.3621195964432943e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4683949968987538e0
    v = 0.3868838330760539e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5694479240657952e0
    v = 0.4018911532693111e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6634465430993955e0
    v = 0.4089929432983252e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1033958573552305e0
    b = 0.3034544009063584e-1
    v = 0.2279907527706409e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1473521412414395e0
    b = 0.6618803044247135e-1
    v = 0.2715205490578897e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1924552158705967e0
    b = 0.1054431128987715e0
    v = 0.3057917896703976e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2381094362890328e0
    b = 0.1468263551238858e0
    v = 0.3326913052452555e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2838121707936760e0
    b = 0.1894486108187886e0
    v = 0.3537334711890037e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3291323133373415e0
    b = 0.2326374238761579e0
    v = 0.3700567500783129e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3736896978741460e0
    b = 0.2758485808485768e0
    v = 0.3825245372589122e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4171406040760013e0
    b = 0.3186179331996921e0
    v = 0.3918125171518296e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4591677985256915e0
    b = 0.3605329796303794e0
    v = 0.3984720419937579e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4994733831718418e0
    b = 0.4012147253586509e0
    v = 0.4029746003338211e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5377731830445096e0
    b = 0.4403050025570692e0
    v = 0.4057428632156627e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5737917830001331e0
    b = 0.4774565904277483e0
    v = 0.4071719274114857e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2027323586271389e0
    b = 0.3544122504976147e-1
    v = 0.2990236950664119e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2516942375187273e0
    b = 0.7418304388646328e-1
    v = 0.3262951734212878e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3000227995257181e0
    b = 0.1150502745727186e0
    v = 0.3482634608242413e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3474806691046342e0
    b = 0.1571963371209364e0
    v = 0.3656596681700892e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3938103180359209e0
    b = 0.1999631877247100e0
    v = 0.3791740467794218e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4387519590455703e0
    b = 0.2428073457846535e0
    v = 0.3894034450156905e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4820503960077787e0
    b = 0.2852575132906155e0
    v = 0.3968600245508371e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5234573778475101e0
    b = 0.3268884208674639e0
    v = 0.4019931351420050e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5627318647235282e0
    b = 0.3673033321675939e0
    v = 0.4052108801278599e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5996390607156954e0
    b = 0.4061211551830290e0
    v = 0.4068978613940934e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3084780753791947e0
    b = 0.3860125523100059e-1
    v = 0.3454275351319704e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3589988275920223e0
    b = 0.7928938987104867e-1
    v = 0.3629963537007920e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4078628415881973e0
    b = 0.1212614643030087e0
    v = 0.3770187233889873e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4549287258889735e0
    b = 0.1638770827382693e0
    v = 0.3878608613694378e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5000278512957279e0
    b = 0.2065965798260176e0
    v = 0.3959065270221274e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5429785044928199e0
    b = 0.2489436378852235e0
    v = 0.4015286975463570e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5835939850491711e0
    b = 0.2904811368946891e0
    v = 0.4050866785614717e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6216870353444856e0
    b = 0.3307941957666609e0
    v = 0.4069320185051913e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4151104662709091e0
    b = 0.4064829146052554e-1
    v = 0.3760120964062763e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4649804275009218e0
    b = 0.8258424547294755e-1
    v = 0.3870969564418064e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5124695757009662e0
    b = 0.1251841962027289e0
    v = 0.3955287790534055e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5574711100606224e0
    b = 0.1679107505976331e0
    v = 0.4015361911302668e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5998597333287227e0
    b = 0.2102805057358715e0
    v = 0.4053836986719548e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6395007148516600e0
    b = 0.2518418087774107e0
    v = 0.4073578673299117e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5188456224746252e0
    b = 0.4194321676077518e-1
    v = 0.3954628379231406e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5664190707942778e0
    b = 0.8457661551921499e-1
    v = 0.4017645508847530e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6110464353283153e0
    b = 0.1273652932519396e0
    v = 0.4059030348651293e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6526430302051563e0
    b = 0.1698173239076354e0
    v = 0.4080565809484880e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6167551880377548e0
    b = 0.4266398851548864e-1
    v = 0.4063018753664651e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6607195418355383e0
    b = 0.8551925814238349e-1
    v = 0.4087191292799671e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_3074():
    grids = []
    a = 0
    b = 0
    v = 0.2599095953754734e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.3603134089687541e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.3586067974412447e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.1886108518723392e-1
    v = 0.9831528474385880e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4800217244625303e-1
    v = 0.1605023107954450e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8244922058397242e-1
    v = 0.2072200131464099e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1200408362484023e0
    v = 0.2431297618814187e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1595773530809965e0
    v = 0.2711819064496707e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2002635973434064e0
    v = 0.2932762038321116e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2415127590139982e0
    v = 0.3107032514197368e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2828584158458477e0
    v = 0.3243808058921213e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3239091015338138e0
    v = 0.3349899091374030e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3643225097962194e0
    v = 0.3430580688505218e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4037897083691802e0
    v = 0.3490124109290343e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4420247515194127e0
    v = 0.3532148948561955e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4787572538464938e0
    v = 0.3559862669062833e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5137265251275234e0
    v = 0.3576224317551411e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5466764056654611e0
    v = 0.3584050533086076e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6054859420813535e0
    v = 0.3584903581373224e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6308106701764562e0
    v = 0.3582991879040586e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6530369230179584e0
    v = 0.3582371187963125e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6718609524611158e0
    v = 0.3584353631122350e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6869676499894013e0
    v = 0.3589120166517785e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6980467077240748e0
    v = 0.3595445704531601e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7048241721250522e0
    v = 0.3600943557111074e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5591105222058232e-1
    v = 0.1456447096742039e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1407384078513916e0
    v = 0.2252370188283782e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2364035438976309e0
    v = 0.2766135443474897e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3360602737818170e0
    v = 0.3110729491500851e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4356292630054665e0
    v = 0.3342506712303391e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5321569415256174e0
    v = 0.3491981834026860e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6232956305040554e0
    v = 0.3576003604348932e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9469870086838469e-1
    b = 0.2778748387309470e-1
    v = 0.1921921305788564e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1353170300568141e0
    b = 0.6076569878628364e-1
    v = 0.2301458216495632e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1771679481726077e0
    b = 0.9703072762711040e-1
    v = 0.2604248549522893e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2197066664231751e0
    b = 0.1354112458524762e0
    v = 0.2845275425870697e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2624783557374927e0
    b = 0.1750996479744100e0
    v = 0.3036870897974840e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3050969521214442e0
    b = 0.2154896907449802e0
    v = 0.3188414832298066e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3472252637196021e0
    b = 0.2560954625740152e0
    v = 0.3307046414722089e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3885610219026360e0
    b = 0.2965070050624096e0
    v = 0.3398330969031360e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4288273776062765e0
    b = 0.3363641488734497e0
    v = 0.3466757899705373e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4677662471302948e0
    b = 0.3753400029836788e0
    v = 0.3516095923230054e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5051333589553359e0
    b = 0.4131297522144286e0
    v = 0.3549645184048486e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5406942145810492e0
    b = 0.4494423776081795e0
    v = 0.3570415969441392e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5742204122576457e0
    b = 0.4839938958841502e0
    v = 0.3581251798496118e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1865407027225188e0
    b = 0.3259144851070796e-1
    v = 0.2543491329913348e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2321186453689432e0
    b = 0.6835679505297343e-1
    v = 0.2786711051330776e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2773159142523882e0
    b = 0.1062284864451989e0
    v = 0.2985552361083679e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3219200192237254e0
    b = 0.1454404409323047e0
    v = 0.3145867929154039e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3657032593944029e0
    b = 0.1854018282582510e0
    v = 0.3273290662067609e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4084376778363622e0
    b = 0.2256297412014750e0
    v = 0.3372705511943501e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4499004945751427e0
    b = 0.2657104425000896e0
    v = 0.3448274437851510e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4898758141326335e0
    b = 0.3052755487631557e0
    v = 0.3503592783048583e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5281547442266309e0
    b = 0.3439863920645423e0
    v = 0.3541854792663162e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5645346989813992e0
    b = 0.3815229456121914e0
    v = 0.3565995517909428e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5988181252159848e0
    b = 0.4175752420966734e0
    v = 0.3578802078302898e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2850425424471603e0
    b = 0.3562149509862536e-1
    v = 0.2958644592860982e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3324619433027876e0
    b = 0.7330318886871096e-1
    v = 0.3119548129116835e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3785848333076282e0
    b = 0.1123226296008472e0
    v = 0.3250745225005984e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4232891028562115e0
    b = 0.1521084193337708e0
    v = 0.3355153415935208e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4664287050829722e0
    b = 0.1921844459223610e0
    v = 0.3435847568549328e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5078458493735726e0
    b = 0.2321360989678303e0
    v = 0.3495786831622488e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5473779816204180e0
    b = 0.2715886486360520e0
    v = 0.3537767805534621e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5848617133811376e0
    b = 0.3101924707571355e0
    v = 0.3564459815421428e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6201348281584888e0
    b = 0.3476121052890973e0
    v = 0.3578464061225468e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3852191185387871e0
    b = 0.3763224880035108e-1
    v = 0.3239748762836212e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4325025061073423e0
    b = 0.7659581935637135e-1
    v = 0.3345491784174287e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4778486229734490e0
    b = 0.1163381306083900e0
    v = 0.3429126177301782e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5211663693009000e0
    b = 0.1563890598752899e0
    v = 0.3492420343097421e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5623469504853703e0
    b = 0.1963320810149200e0
    v = 0.3537399050235257e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6012718188659246e0
    b = 0.2357847407258738e0
    v = 0.3566209152659172e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6378179206390117e0
    b = 0.2743846121244060e0
    v = 0.3581084321919782e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4836936460214534e0
    b = 0.3895902610739024e-1
    v = 0.3426522117591512e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5293792562683797e0
    b = 0.7871246819312640e-1
    v = 0.3491848770121379e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5726281253100033e0
    b = 0.1187963808202981e0
    v = 0.3539318235231476e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6133658776169068e0
    b = 0.1587914708061787e0
    v = 0.3570231438458694e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6515085491865307e0
    b = 0.1983058575227646e0
    v = 0.3586207335051714e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5778692716064976e0
    b = 0.3977209689791542e-1
    v = 0.3541196205164025e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6207904288086192e0
    b = 0.7990157592981152e-1
    v = 0.3574296911573953e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6608688171046802e0
    b = 0.1199671308754309e0
    v = 0.3591993279818963e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6656263089489130e0
    b = 0.4015955957805969e-1
    v = 0.3595855034661997e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_3470():
    grids = []
    a = 0
    b = 0
    v = 0.2040382730826330e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.3178149703889544e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.1721420832906233e-1
    v = 0.8288115128076110e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4408875374981770e-1
    v = 0.1360883192522954e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7594680813878681e-1
    v = 0.1766854454542662e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1108335359204799e0
    v = 0.2083153161230153e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1476517054388567e0
    v = 0.2333279544657158e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1856731870860615e0
    v = 0.2532809539930247e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2243634099428821e0
    v = 0.2692472184211158e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2633006881662727e0
    v = 0.2819949946811885e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3021340904916283e0
    v = 0.2920953593973030e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3405594048030089e0
    v = 0.2999889782948352e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3783044434007372e0
    v = 0.3060292120496902e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4151194767407910e0
    v = 0.3105109167522192e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4507705766443257e0
    v = 0.3136902387550312e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4850346056573187e0
    v = 0.3157984652454632e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5176950817792470e0
    v = 0.3170516518425422e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5485384240820989e0
    v = 0.3176568425633755e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6039117238943308e0
    v = 0.3177198411207062e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6279956655573113e0
    v = 0.3175519492394733e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6493636169568952e0
    v = 0.3174654952634756e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6677644117704504e0
    v = 0.3175676415467654e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6829368572115624e0
    v = 0.3178923417835410e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6946195818184121e0
    v = 0.3183788287531909e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7025711542057026e0
    v = 0.3188755151918807e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7066004767140119e0
    v = 0.3191916889313849e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5132537689946062e-1
    v = 0.1231779611744508e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1297994661331225e0
    v = 0.1924661373839880e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2188852049401307e0
    v = 0.2380881867403424e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3123174824903457e0
    v = 0.2693100663037885e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4064037620738195e0
    v = 0.2908673382834366e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4984958396944782e0
    v = 0.3053914619381535e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5864975046021365e0
    v = 0.3143916684147777e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6686711634580175e0
    v = 0.3187042244055363e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.8715738780835950e-1
    b = 0.2557175233367578e-1
    v = 0.1635219535869790e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1248383123134007e0
    b = 0.5604823383376681e-1
    v = 0.1968109917696070e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1638062693383378e0
    b = 0.8968568601900765e-1
    v = 0.2236754342249974e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2035586203373176e0
    b = 0.1254086651976279e0
    v = 0.2453186687017181e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2436798975293774e0
    b = 0.1624780150162012e0
    v = 0.2627551791580541e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2838207507773806e0
    b = 0.2003422342683208e0
    v = 0.2767654860152220e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3236787502217692e0
    b = 0.2385628026255263e0
    v = 0.2879467027765895e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3629849554840691e0
    b = 0.2767731148783578e0
    v = 0.2967639918918702e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4014948081992087e0
    b = 0.3146542308245309e0
    v = 0.3035900684660351e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4389818379260225e0
    b = 0.3519196415895088e0
    v = 0.3087338237298308e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4752331143674377e0
    b = 0.3883050984023654e0
    v = 0.3124608838860167e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5100457318374018e0
    b = 0.4235613423908649e0
    v = 0.3150084294226743e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5432238388954868e0
    b = 0.4574484717196220e0
    v = 0.3165958398598402e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5745758685072442e0
    b = 0.4897311639255524e0
    v = 0.3174320440957372e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1723981437592809e0
    b = 0.3010630597881105e-1
    v = 0.2182188909812599e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2149553257844597e0
    b = 0.6326031554204694e-1
    v = 0.2399727933921445e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2573256081247422e0
    b = 0.9848566980258631e-1
    v = 0.2579796133514652e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2993163751238106e0
    b = 0.1350835952384266e0
    v = 0.2727114052623535e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3407238005148000e0
    b = 0.1725184055442181e0
    v = 0.2846327656281355e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3813454978483264e0
    b = 0.2103559279730725e0
    v = 0.2941491102051334e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4209848104423343e0
    b = 0.2482278774554860e0
    v = 0.3016049492136107e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4594519699996300e0
    b = 0.2858099509982883e0
    v = 0.3072949726175648e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4965640166185930e0
    b = 0.3228075659915428e0
    v = 0.3114768142886460e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5321441655571562e0
    b = 0.3589459907204151e0
    v = 0.3143823673666223e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5660208438582166e0
    b = 0.3939630088864310e0
    v = 0.3162269764661535e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5980264315964364e0
    b = 0.4276029922949089e0
    v = 0.3172164663759821e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2644215852350733e0
    b = 0.3300939429072552e-1
    v = 0.2554575398967435e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3090113743443063e0
    b = 0.6803887650078501e-1
    v = 0.2701704069135677e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3525871079197808e0
    b = 0.1044326136206709e0
    v = 0.2823693413468940e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3950418005354029e0
    b = 0.1416751597517679e0
    v = 0.2922898463214289e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4362475663430163e0
    b = 0.1793408610504821e0
    v = 0.3001829062162428e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4760661812145854e0
    b = 0.2170630750175722e0
    v = 0.3062890864542953e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5143551042512103e0
    b = 0.2545145157815807e0
    v = 0.3108328279264746e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5509709026935597e0
    b = 0.2913940101706601e0
    v = 0.3140243146201245e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5857711030329428e0
    b = 0.3274169910910705e0
    v = 0.3160638030977130e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6186149917404392e0
    b = 0.3623081329317265e0
    v = 0.3171462882206275e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3586894569557064e0
    b = 0.3497354386450040e-1
    v = 0.2812388416031796e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4035266610019441e0
    b = 0.7129736739757095e-1
    v = 0.2912137500288045e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4467775312332510e0
    b = 0.1084758620193165e0
    v = 0.2993241256502206e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4883638346608543e0
    b = 0.1460915689241772e0
    v = 0.3057101738983822e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5281908348434601e0
    b = 0.1837790832369980e0
    v = 0.3105319326251432e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5661542687149311e0
    b = 0.2212075390874021e0
    v = 0.3139565514428167e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6021450102031452e0
    b = 0.2580682841160985e0
    v = 0.3161543006806366e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6360520783610050e0
    b = 0.2940656362094121e0
    v = 0.3172985960613294e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4521611065087196e0
    b = 0.3631055365867002e-1
    v = 0.2989400336901431e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4959365651560963e0
    b = 0.7348318468484350e-1
    v = 0.3054555883947677e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5376815804038283e0
    b = 0.1111087643812648e0
    v = 0.3104764960807702e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5773314480243768e0
    b = 0.1488226085145408e0
    v = 0.3141015825977616e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6148113245575056e0
    b = 0.1862892274135151e0
    v = 0.3164520621159896e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6500407462842380e0
    b = 0.2231909701714456e0
    v = 0.3176652305912204e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5425151448707213e0
    b = 0.3718201306118944e-1
    v = 0.3105097161023939e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5841860556907931e0
    b = 0.7483616335067346e-1
    v = 0.3143014117890550e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6234632186851500e0
    b = 0.1125990834266120e0
    v = 0.3168172866287200e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6602934551848843e0
    b = 0.1501303813157619e0
    v = 0.3181401865570968e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6278573968375105e0
    b = 0.3767559930245720e-1
    v = 0.3170663659156037e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6665611711264577e0
    b = 0.7548443301360158e-1
    v = 0.3185447944625510e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_3890():
    grids = []
    a = 0
    b = 0
    v = 0.1807395252196920e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.2848008782238827e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.2836065837530581e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.1587876419858352e-1
    v = 0.7013149266673816e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4069193593751206e-1
    v = 0.1162798021956766e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7025888115257997e-1
    v = 0.1518728583972105e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1027495450028704e0
    v = 0.1798796108216934e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1371457730893426e0
    v = 0.2022593385972785e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1727758532671953e0
    v = 0.2203093105575464e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2091492038929037e0
    v = 0.2349294234299855e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2458813281751915e0
    v = 0.2467682058747003e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2826545859450066e0
    v = 0.2563092683572224e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3191957291799622e0
    v = 0.2639253896763318e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3552621469299578e0
    v = 0.2699137479265108e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3906329503406230e0
    v = 0.2745196420166739e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4251028614093031e0
    v = 0.2779529197397593e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4584777520111870e0
    v = 0.2803996086684265e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4905711358710193e0
    v = 0.2820302356715842e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5212011669847385e0
    v = 0.2830056747491068e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5501878488737995e0
    v = 0.2834808950776839e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6025037877479342e0
    v = 0.2835282339078929e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6254572689549016e0
    v = 0.2833819267065800e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6460107179528248e0
    v = 0.2832858336906784e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6639541138154251e0
    v = 0.2833268235451244e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6790688515667495e0
    v = 0.2835432677029253e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6911338580371512e0
    v = 0.2839091722743049e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6999385956126490e0
    v = 0.2843308178875841e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7053037748656896e0
    v = 0.2846703550533846e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4732224387180115e-1
    v = 0.1051193406971900e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1202100529326803e0
    v = 0.1657871838796974e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2034304820664855e0
    v = 0.2064648113714232e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2912285643573002e0
    v = 0.2347942745819741e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3802361792726768e0
    v = 0.2547775326597726e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4680598511056146e0
    v = 0.2686876684847025e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5528151052155599e0
    v = 0.2778665755515867e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6329386307803041e0
    v = 0.2830996616782929e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.8056516651369069e-1
    b = 0.2363454684003124e-1
    v = 0.1403063340168372e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1156476077139389e0
    b = 0.5191291632545936e-1
    v = 0.1696504125939477e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1520473382760421e0
    b = 0.8322715736994519e-1
    v = 0.1935787242745390e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1892986699745931e0
    b = 0.1165855667993712e0
    v = 0.2130614510521968e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2270194446777792e0
    b = 0.1513077167409504e0
    v = 0.2289381265931048e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2648908185093273e0
    b = 0.1868882025807859e0
    v = 0.2418630292816186e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3026389259574136e0
    b = 0.2229277629776224e0
    v = 0.2523400495631193e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3400220296151384e0
    b = 0.2590951840746235e0
    v = 0.2607623973449605e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3768217953335510e0
    b = 0.2951047291750847e0
    v = 0.2674441032689209e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4128372900921884e0
    b = 0.3307019714169930e0
    v = 0.2726432360343356e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4478807131815630e0
    b = 0.3656544101087634e0
    v = 0.2765787685924545e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4817742034089257e0
    b = 0.3997448951939695e0
    v = 0.2794428690642224e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5143472814653344e0
    b = 0.4327667110812024e0
    v = 0.2814099002062895e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5454346213905650e0
    b = 0.4645196123532293e0
    v = 0.2826429531578994e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5748739313170252e0
    b = 0.4948063555703345e0
    v = 0.2832983542550884e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1599598738286342e0
    b = 0.2792357590048985e-1
    v = 0.1886695565284976e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1998097412500951e0
    b = 0.5877141038139065e-1
    v = 0.2081867882748234e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2396228952566202e0
    b = 0.9164573914691377e-1
    v = 0.2245148680600796e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2792228341097746e0
    b = 0.1259049641962687e0
    v = 0.2380370491511872e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3184251107546741e0
    b = 0.1610594823400863e0
    v = 0.2491398041852455e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3570481164426244e0
    b = 0.1967151653460898e0
    v = 0.2581632405881230e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3949164710492144e0
    b = 0.2325404606175168e0
    v = 0.2653965506227417e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4318617293970503e0
    b = 0.2682461141151439e0
    v = 0.2710857216747087e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4677221009931678e0
    b = 0.3035720116011973e0
    v = 0.2754434093903659e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5023417939270955e0
    b = 0.3382781859197439e0
    v = 0.2786579932519380e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5355701836636128e0
    b = 0.3721383065625942e0
    v = 0.2809011080679474e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5672608451328771e0
    b = 0.4049346360466055e0
    v = 0.2823336184560987e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5972704202540162e0
    b = 0.4364538098633802e0
    v = 0.2831101175806309e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2461687022333596e0
    b = 0.3070423166833368e-1
    v = 0.2221679970354546e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2881774566286831e0
    b = 0.6338034669281885e-1
    v = 0.2356185734270703e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3293963604116978e0
    b = 0.9742862487067941e-1
    v = 0.2469228344805590e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3697303822241377e0
    b = 0.1323799532282290e0
    v = 0.2562726348642046e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4090663023135127e0
    b = 0.1678497018129336e0
    v = 0.2638756726753028e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4472819355411712e0
    b = 0.2035095105326114e0
    v = 0.2699311157390862e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4842513377231437e0
    b = 0.2390692566672091e0
    v = 0.2746233268403837e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5198477629962928e0
    b = 0.2742649818076149e0
    v = 0.2781225674454771e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5539453011883145e0
    b = 0.3088503806580094e0
    v = 0.2805881254045684e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5864196762401251e0
    b = 0.3425904245906614e0
    v = 0.2821719877004913e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6171484466668390e0
    b = 0.3752562294789468e0
    v = 0.2830222502333124e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3350337830565727e0
    b = 0.3261589934634747e-1
    v = 0.2457995956744870e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3775773224758284e0
    b = 0.6658438928081572e-1
    v = 0.2551474407503706e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4188155229848973e0
    b = 0.1014565797157954e0
    v = 0.2629065335195311e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4586805892009344e0
    b = 0.1368573320843822e0
    v = 0.2691900449925075e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4970895714224235e0
    b = 0.1724614851951608e0
    v = 0.2741275485754276e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5339505133960747e0
    b = 0.2079779381416412e0
    v = 0.2778530970122595e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5691665792531440e0
    b = 0.2431385788322288e0
    v = 0.2805010567646741e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6026387682680377e0
    b = 0.2776901883049853e0
    v = 0.2822055834031040e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6342676150163307e0
    b = 0.3113881356386632e0
    v = 0.2831016901243473e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4237951119537067e0
    b = 0.3394877848664351e-1
    v = 0.2624474901131803e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4656918683234929e0
    b = 0.6880219556291447e-1
    v = 0.2688034163039377e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5058857069185980e0
    b = 0.1041946859721635e0
    v = 0.2738932751287636e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5443204666713996e0
    b = 0.1398039738736393e0
    v = 0.2777944791242523e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5809298813759742e0
    b = 0.1753373381196155e0
    v = 0.2806011661660987e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6156416039447128e0
    b = 0.2105215793514010e0
    v = 0.2824181456597460e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6483801351066604e0
    b = 0.2450953312157051e0
    v = 0.2833585216577828e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5103616577251688e0
    b = 0.3485560643800719e-1
    v = 0.2738165236962878e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5506738792580681e0
    b = 0.7026308631512033e-1
    v = 0.2778365208203180e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5889573040995292e0
    b = 0.1059035061296403e0
    v = 0.2807852940418966e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6251641589516930e0
    b = 0.1414823925236026e0
    v = 0.2827245949674705e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6592414921570178e0
    b = 0.1767207908214530e0
    v = 0.2837342344829828e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5930314017533384e0
    b = 0.3542189339561672e-1
    v = 0.2809233907610981e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6309812253390175e0
    b = 0.7109574040369549e-1
    v = 0.2829930809742694e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6666296011353230e0
    b = 0.1067259792282730e0
    v = 0.2841097874111479e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6703715271049922e0
    b = 0.3569455268820809e-1
    v = 0.2843455206008783e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_4334():
    grids = []
    a = 0
    b = 0
    v = 0.1449063022537883e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.2546377329828424e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.1462896151831013e-1
    v = 0.6018432961087496e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3769840812493139e-1
    v = 0.1002286583263673e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6524701904096891e-1
    v = 0.1315222931028093e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.9560543416134648e-1
    v = 0.1564213746876724e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1278335898929198e0
    v = 0.1765118841507736e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1613096104466031e0
    v = 0.1928737099311080e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1955806225745371e0
    v = 0.2062658534263270e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2302935218498028e0
    v = 0.2172395445953787e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2651584344113027e0
    v = 0.2262076188876047e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2999276825183209e0
    v = 0.2334885699462397e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3343828669718798e0
    v = 0.2393355273179203e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3683265013750518e0
    v = 0.2439559200468863e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4015763206518108e0
    v = 0.2475251866060002e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4339612026399770e0
    v = 0.2501965558158773e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4653180651114582e0
    v = 0.2521081407925925e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4954893331080803e0
    v = 0.2533881002388081e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5243207068924930e0
    v = 0.2541582900848261e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5516590479041704e0
    v = 0.2545365737525860e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6012371927804176e0
    v = 0.2545726993066799e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6231574466449819e0
    v = 0.2544456197465555e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6429416514181271e0
    v = 0.2543481596881064e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6604124272943595e0
    v = 0.2543506451429194e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6753851470408250e0
    v = 0.2544905675493763e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6876717970626160e0
    v = 0.2547611407344429e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6970895061319234e0
    v = 0.2551060375448869e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7034746912553310e0
    v = 0.2554291933816039e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7067017217542295e0
    v = 0.2556255710686343e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4382223501131123e-1
    v = 0.9041339695118195e-4
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1117474077400006e0
    v = 0.1438426330079022e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1897153252911440e0
    v = 0.1802523089820518e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2724023009910331e0
    v = 0.2060052290565496e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3567163308709902e0
    v = 0.2245002248967466e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4404784483028087e0
    v = 0.2377059847731150e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5219833154161411e0
    v = 0.2468118955882525e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5998179868977553e0
    v = 0.2525410872966528e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6727803154548222e0
    v = 0.2553101409933397e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.7476563943166086e-1
    b = 0.2193168509461185e-1
    v = 0.1212879733668632e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1075341482001416e0
    b = 0.4826419281533887e-1
    v = 0.1472872881270931e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1416344885203259e0
    b = 0.7751191883575742e-1
    v = 0.1686846601010828e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1766325315388586e0
    b = 0.1087558139247680e0
    v = 0.1862698414660208e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2121744174481514e0
    b = 0.1413661374253096e0
    v = 0.2007430956991861e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2479669443408145e0
    b = 0.1748768214258880e0
    v = 0.2126568125394796e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2837600452294113e0
    b = 0.2089216406612073e0
    v = 0.2224394603372113e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3193344933193984e0
    b = 0.2431987685545972e0
    v = 0.2304264522673135e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3544935442438745e0
    b = 0.2774497054377770e0
    v = 0.2368854288424087e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3890571932288154e0
    b = 0.3114460356156915e0
    v = 0.2420352089461772e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4228581214259090e0
    b = 0.3449806851913012e0
    v = 0.2460597113081295e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4557387211304052e0
    b = 0.3778618641248256e0
    v = 0.2491181912257687e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4875487950541643e0
    b = 0.4099086391698978e0
    v = 0.2513528194205857e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5181436529962997e0
    b = 0.4409474925853973e0
    v = 0.2528943096693220e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5473824095600661e0
    b = 0.4708094517711291e0
    v = 0.2538660368488136e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5751263398976174e0
    b = 0.4993275140354637e0
    v = 0.2543868648299022e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1489515746840028e0
    b = 0.2599381993267017e-1
    v = 0.1642595537825183e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1863656444351767e0
    b = 0.5479286532462190e-1
    v = 0.1818246659849308e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2238602880356348e0
    b = 0.8556763251425254e-1
    v = 0.1966565649492420e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2612723375728160e0
    b = 0.1177257802267011e0
    v = 0.2090677905657991e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2984332990206190e0
    b = 0.1508168456192700e0
    v = 0.2193820409510504e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3351786584663333e0
    b = 0.1844801892177727e0
    v = 0.2278870827661928e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3713505522209120e0
    b = 0.2184145236087598e0
    v = 0.2348283192282090e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4067981098954663e0
    b = 0.2523590641486229e0
    v = 0.2404139755581477e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4413769993687534e0
    b = 0.2860812976901373e0
    v = 0.2448227407760734e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4749487182516394e0
    b = 0.3193686757808996e0
    v = 0.2482110455592573e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5073798105075426e0
    b = 0.3520226949547602e0
    v = 0.2507192397774103e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5385410448878654e0
    b = 0.3838544395667890e0
    v = 0.2524765968534880e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5683065353670530e0
    b = 0.4146810037640963e0
    v = 0.2536052388539425e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5965527620663510e0
    b = 0.4443224094681121e0
    v = 0.2542230588033068e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2299227700856157e0
    b = 0.2865757664057584e-1
    v = 0.1944817013047896e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2695752998553267e0
    b = 0.5923421684485993e-1
    v = 0.2067862362746635e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3086178716611389e0
    b = 0.9117817776057715e-1
    v = 0.2172440734649114e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3469649871659077e0
    b = 0.1240593814082605e0
    v = 0.2260125991723423e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3845153566319655e0
    b = 0.1575272058259175e0
    v = 0.2332655008689523e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4211600033403215e0
    b = 0.1912845163525413e0
    v = 0.2391699681532458e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4567867834329882e0
    b = 0.2250710177858171e0
    v = 0.2438801528273928e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4912829319232061e0
    b = 0.2586521303440910e0
    v = 0.2475370504260665e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5245364793303812e0
    b = 0.2918112242865407e0
    v = 0.2502707235640574e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5564369788915756e0
    b = 0.3243439239067890e0
    v = 0.2522031701054241e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5868757697775287e0
    b = 0.3560536787835351e0
    v = 0.2534511269978784e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6157458853519617e0
    b = 0.3867480821242581e0
    v = 0.2541284914955151e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3138461110672113e0
    b = 0.3051374637507278e-1
    v = 0.2161509250688394e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3542495872050569e0
    b = 0.6237111233730755e-1
    v = 0.2248778513437852e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3935751553120181e0
    b = 0.9516223952401907e-1
    v = 0.2322388803404617e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4317634668111147e0
    b = 0.1285467341508517e0
    v = 0.2383265471001355e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4687413842250821e0
    b = 0.1622318931656033e0
    v = 0.2432476675019525e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5044274237060283e0
    b = 0.1959581153836453e0
    v = 0.2471122223750674e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5387354077925727e0
    b = 0.2294888081183837e0
    v = 0.2500291752486870e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5715768898356105e0
    b = 0.2626031152713945e0
    v = 0.2521055942764682e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6028627200136111e0
    b = 0.2950904075286713e0
    v = 0.2534472785575503e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6325039812653463e0
    b = 0.3267458451113286e0
    v = 0.2541599713080121e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3981986708423407e0
    b = 0.3183291458749821e-1
    v = 0.2317380975862936e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4382791182133300e0
    b = 0.6459548193880908e-1
    v = 0.2378550733719775e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4769233057218166e0
    b = 0.9795757037087952e-1
    v = 0.2428884456739118e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5140823911194238e0
    b = 0.1316307235126655e0
    v = 0.2469002655757292e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5496977833862983e0
    b = 0.1653556486358704e0
    v = 0.2499657574265851e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5837047306512727e0
    b = 0.1988931724126510e0
    v = 0.2521676168486082e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6160349566926879e0
    b = 0.2320174581438950e0
    v = 0.2535935662645334e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6466185353209440e0
    b = 0.2645106562168662e0
    v = 0.2543356743363214e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4810835158795404e0
    b = 0.3275917807743992e-1
    v = 0.2427353285201535e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5199925041324341e0
    b = 0.6612546183967181e-1
    v = 0.2468258039744386e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5571717692207494e0
    b = 0.9981498331474143e-1
    v = 0.2500060956440310e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5925789250836378e0
    b = 0.1335687001410374e0
    v = 0.2523238365420979e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6261658523859670e0
    b = 0.1671444402896463e0
    v = 0.2538399260252846e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6578811126669331e0
    b = 0.2003106382156076e0
    v = 0.2546255927268069e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5609624612998100e0
    b = 0.3337500940231335e-1
    v = 0.2500583360048449e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5979959659984670e0
    b = 0.6708750335901803e-1
    v = 0.2524777638260203e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6330523711054002e0
    b = 0.1008792126424850e0
    v = 0.2540951193860656e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6660960998103972e0
    b = 0.1345050343171794e0
    v = 0.2549524085027472e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6365384364585819e0
    b = 0.3372799460737052e-1
    v = 0.2542569507009158e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6710994302899275e0
    b = 0.6755249309678028e-1
    v = 0.2552114127580376e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_4802():
    grids = []
    a = 0
    b = 0
    v = 0.9687521879420705e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.2307897895367918e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.2297310852498558e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2335728608887064e-1
    v = 0.7386265944001919e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4352987836550653e-1
    v = 0.8257977698542210e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6439200521088801e-1
    v = 0.9706044762057630e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.9003943631993181e-1
    v = 0.1302393847117003e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1196706615548473e0
    v = 0.1541957004600968e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1511715412838134e0
    v = 0.1704459770092199e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1835982828503801e0
    v = 0.1827374890942906e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2165081259155405e0
    v = 0.1926360817436107e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2496208720417563e0
    v = 0.2008010239494833e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2827200673567900e0
    v = 0.2075635983209175e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3156190823994346e0
    v = 0.2131306638690909e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3481476793749115e0
    v = 0.2176562329937335e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3801466086947226e0
    v = 0.2212682262991018e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4114652119634011e0
    v = 0.2240799515668565e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4419598786519751e0
    v = 0.2261959816187525e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4714925949329543e0
    v = 0.2277156368808855e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4999293972879466e0
    v = 0.2287351772128336e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5271387221431248e0
    v = 0.2293490814084085e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5529896780837761e0
    v = 0.2296505312376273e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6000856099481712e0
    v = 0.2296793832318756e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6210562192785175e0
    v = 0.2295785443842974e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6401165879934240e0
    v = 0.2295017931529102e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6571144029244334e0
    v = 0.2295059638184868e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6718910821718863e0
    v = 0.2296232343237362e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6842845591099010e0
    v = 0.2298530178740771e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6941353476269816e0
    v = 0.2301579790280501e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7012965242212991e0
    v = 0.2304690404996513e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7056471428242644e0
    v = 0.2307027995907102e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4595557643585895e-1
    v = 0.9312274696671092e-4
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1049316742435023e0
    v = 0.1199919385876926e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1773548879549274e0
    v = 0.1598039138877690e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2559071411236127e0
    v = 0.1822253763574900e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3358156837985898e0
    v = 0.1988579593655040e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4155835743763893e0
    v = 0.2112620102533307e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4937894296167472e0
    v = 0.2201594887699007e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5691569694793316e0
    v = 0.2261622590895036e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6405840854894251e0
    v = 0.2296458453435705e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.7345133894143348e-1
    b = 0.2177844081486067e-1
    v = 0.1006006990267000e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1009859834044931e0
    b = 0.4590362185775188e-1
    v = 0.1227676689635876e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1324289619748758e0
    b = 0.7255063095690877e-1
    v = 0.1467864280270117e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1654272109607127e0
    b = 0.1017825451960684e0
    v = 0.1644178912101232e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1990767186776461e0
    b = 0.1325652320980364e0
    v = 0.1777664890718961e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2330125945523278e0
    b = 0.1642765374496765e0
    v = 0.1884825664516690e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2670080611108287e0
    b = 0.1965360374337889e0
    v = 0.1973269246453848e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3008753376294316e0
    b = 0.2290726770542238e0
    v = 0.2046767775855328e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3344475596167860e0
    b = 0.2616645495370823e0
    v = 0.2107600125918040e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3675709724070786e0
    b = 0.2941150728843141e0
    v = 0.2157416362266829e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4001000887587812e0
    b = 0.3262440400919066e0
    v = 0.2197557816920721e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4318956350436028e0
    b = 0.3578835350611916e0
    v = 0.2229192611835437e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4628239056795531e0
    b = 0.3888751854043678e0
    v = 0.2253385110212775e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4927563229773636e0
    b = 0.4190678003222840e0
    v = 0.2271137107548774e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5215687136707969e0
    b = 0.4483151836883852e0
    v = 0.2283414092917525e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5491402346984905e0
    b = 0.4764740676087880e0
    v = 0.2291161673130077e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5753520160126075e0
    b = 0.5034021310998277e0
    v = 0.2295313908576598e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1388326356417754e0
    b = 0.2435436510372806e-1
    v = 0.1438204721359031e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1743686900537244e0
    b = 0.5118897057342652e-1
    v = 0.1607738025495257e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2099737037950268e0
    b = 0.8014695048539634e-1
    v = 0.1741483853528379e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2454492590908548e0
    b = 0.1105117874155699e0
    v = 0.1851918467519151e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2807219257864278e0
    b = 0.1417950531570966e0
    v = 0.1944628638070613e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3156842271975842e0
    b = 0.1736604945719597e0
    v = 0.2022495446275152e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3502090945177752e0
    b = 0.2058466324693981e0
    v = 0.2087462382438514e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3841684849519686e0
    b = 0.2381284261195919e0
    v = 0.2141074754818308e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4174372367906016e0
    b = 0.2703031270422569e0
    v = 0.2184640913748162e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4498926465011892e0
    b = 0.3021845683091309e0
    v = 0.2219309165220329e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4814146229807701e0
    b = 0.3335993355165720e0
    v = 0.2246123118340624e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5118863625734701e0
    b = 0.3643833735518232e0
    v = 0.2266062766915125e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5411947455119144e0
    b = 0.3943789541958179e0
    v = 0.2280072952230796e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5692301500357246e0
    b = 0.4234320144403542e0
    v = 0.2289082025202583e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5958857204139576e0
    b = 0.4513897947419260e0
    v = 0.2294012695120025e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2156270284785766e0
    b = 0.2681225755444491e-1
    v = 0.1722434488736947e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2532385054909710e0
    b = 0.5557495747805614e-1
    v = 0.1830237421455091e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2902564617771537e0
    b = 0.8569368062950249e-1
    v = 0.1923855349997633e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3266979823143256e0
    b = 0.1167367450324135e0
    v = 0.2004067861936271e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3625039627493614e0
    b = 0.1483861994003304e0
    v = 0.2071817297354263e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3975838937548699e0
    b = 0.1803821503011405e0
    v = 0.2128250834102103e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4318396099009774e0
    b = 0.2124962965666424e0
    v = 0.2174513719440102e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4651706555732742e0
    b = 0.2445221837805913e0
    v = 0.2211661839150214e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4974752649620969e0
    b = 0.2762701224322987e0
    v = 0.2240665257813102e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5286517579627517e0
    b = 0.3075627775211328e0
    v = 0.2262439516632620e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5586001195731895e0
    b = 0.3382311089826877e0
    v = 0.2277874557231869e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5872229902021319e0
    b = 0.3681108834741399e0
    v = 0.2287854314454994e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6144258616235123e0
    b = 0.3970397446872839e0
    v = 0.2293268499615575e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2951676508064861e0
    b = 0.2867499538750441e-1
    v = 0.1912628201529828e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3335085485472725e0
    b = 0.5867879341903510e-1
    v = 0.1992499672238701e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3709561760636381e0
    b = 0.8961099205022284e-1
    v = 0.2061275533454027e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4074722861667498e0
    b = 0.1211627927626297e0
    v = 0.2119318215968572e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4429923648839117e0
    b = 0.1530748903554898e0
    v = 0.2167416581882652e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4774428052721736e0
    b = 0.1851176436721877e0
    v = 0.2206430730516600e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5107446539535904e0
    b = 0.2170829107658179e0
    v = 0.2237186938699523e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5428151370542935e0
    b = 0.2487786689026271e0
    v = 0.2260480075032884e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5735699292556964e0
    b = 0.2800239952795016e0
    v = 0.2277098884558542e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6029253794562866e0
    b = 0.3106445702878119e0
    v = 0.2287845715109671e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6307998987073145e0
    b = 0.3404689500841194e0
    v = 0.2293547268236294e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3752652273692719e0
    b = 0.2997145098184479e-1
    v = 0.2056073839852528e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4135383879344028e0
    b = 0.6086725898678011e-1
    v = 0.2114235865831876e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4506113885153907e0
    b = 0.9238849548435643e-1
    v = 0.2163175629770551e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4864401554606072e0
    b = 0.1242786603851851e0
    v = 0.2203392158111650e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5209708076611709e0
    b = 0.1563086731483386e0
    v = 0.2235473176847839e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5541422135830122e0
    b = 0.1882696509388506e0
    v = 0.2260024141501235e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5858880915113817e0
    b = 0.2199672979126059e0
    v = 0.2277675929329182e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6161399390603444e0
    b = 0.2512165482924867e0
    v = 0.2289102112284834e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6448296482255090e0
    b = 0.2818368701871888e0
    v = 0.2295027954625118e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4544796274917948e0
    b = 0.3088970405060312e-1
    v = 0.2161281589879992e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4919389072146628e0
    b = 0.6240947677636835e-1
    v = 0.2201980477395102e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5279313026985183e0
    b = 0.9430706144280313e-1
    v = 0.2234952066593166e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5624169925571135e0
    b = 0.1263547818770374e0
    v = 0.2260540098520838e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5953484627093287e0
    b = 0.1583430788822594e0
    v = 0.2279157981899988e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6266730715339185e0
    b = 0.1900748462555988e0
    v = 0.2291296918565571e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6563363204278871e0
    b = 0.2213599519592567e0
    v = 0.2297533752536649e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5314574716585696e0
    b = 0.3152508811515374e-1
    v = 0.2234927356465995e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5674614932298185e0
    b = 0.6343865291465561e-1
    v = 0.2261288012985219e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6017706004970264e0
    b = 0.9551503504223951e-1
    v = 0.2280818160923688e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6343471270264178e0
    b = 0.1275440099801196e0
    v = 0.2293773295180159e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6651494599127802e0
    b = 0.1593252037671960e0
    v = 0.2300528767338634e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6050184986005704e0
    b = 0.3192538338496105e-1
    v = 0.2281893855065666e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6390163550880400e0
    b = 0.6402824353962306e-1
    v = 0.2295720444840727e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6711199107088448e0
    b = 0.9609805077002909e-1
    v = 0.2303227649026753e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6741354429572275e0
    b = 0.3211853196273233e-1
    v = 0.2304831913227114e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_5294():
    grids = []
    a = 0
    b = 0
    v = 0.9080510764308163e-4
    grids.append(SphGenOh(0, a, b, v))
    v = 0.2084824361987793e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.2303261686261450e-1
    v = 0.5011105657239616e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3757208620162394e-1
    v = 0.5942520409683854e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5821912033821852e-1
    v = 0.9564394826109721e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.8403127529194872e-1
    v = 0.1185530657126338e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1122927798060578e0
    v = 0.1364510114230331e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1420125319192987e0
    v = 0.1505828825605415e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1726396437341978e0
    v = 0.1619298749867023e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2038170058115696e0
    v = 0.1712450504267789e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2352849892876508e0
    v = 0.1789891098164999e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2668363354312461e0
    v = 0.1854474955629795e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2982941279900452e0
    v = 0.1908148636673661e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3295002922087076e0
    v = 0.1952377405281833e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3603094918363593e0
    v = 0.1988349254282232e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3905857895173920e0
    v = 0.2017079807160050e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4202005758160837e0
    v = 0.2039473082709094e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4490310061597227e0
    v = 0.2056360279288953e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4769586160311491e0
    v = 0.2068525823066865e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5038679887049750e0
    v = 0.2076724877534488e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5296454286519961e0
    v = 0.2081694278237885e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5541776207164850e0
    v = 0.2084157631219326e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5990467321921213e0
    v = 0.2084381531128593e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6191467096294587e0
    v = 0.2083476277129307e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6375251212901849e0
    v = 0.2082686194459732e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6540514381131168e0
    v = 0.2082475686112415e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6685899064391510e0
    v = 0.2083139860289915e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6810013009681648e0
    v = 0.2084745561831237e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6911469578730340e0
    v = 0.2087091313375890e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6988956915141736e0
    v = 0.2089718413297697e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7041335794868720e0
    v = 0.2092003303479793e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7067754398018567e0
    v = 0.2093336148263241e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3840368707853623e-1
    v = 0.7591708117365267e-4
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9835485954117399e-1
    v = 0.1083383968169186e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1665774947612998e0
    v = 0.1403019395292510e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2405702335362910e0
    v = 0.1615970179286436e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3165270770189046e0
    v = 0.1771144187504911e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3927386145645443e0
    v = 0.1887760022988168e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4678825918374656e0
    v = 0.1973474670768214e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5408022024266935e0
    v = 0.2033787661234659e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6104967445752438e0
    v = 0.2072343626517331e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6760910702685738e0
    v = 0.2091177834226918e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6655644120217392e-1
    b = 0.1936508874588424e-1
    v = 0.9316684484675566e-4
    grids.append(SphGenOh(5, a, b, v))
    a = 0.9446246161270182e-1
    b = 0.4252442002115869e-1
    v = 0.1116193688682976e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1242651925452509e0
    b = 0.6806529315354374e-1
    v = 0.1298623551559414e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1553438064846751e0
    b = 0.9560957491205369e-1
    v = 0.1450236832456426e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1871137110542670e0
    b = 0.1245931657452888e0
    v = 0.1572719958149914e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2192612628836257e0
    b = 0.1545385828778978e0
    v = 0.1673234785867195e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2515682807206955e0
    b = 0.1851004249723368e0
    v = 0.1756860118725188e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2838535866287290e0
    b = 0.2160182608272384e0
    v = 0.1826776290439367e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3159578817528521e0
    b = 0.2470799012277111e0
    v = 0.1885116347992865e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3477370882791392e0
    b = 0.2781014208986402e0
    v = 0.1933457860170574e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3790576960890540e0
    b = 0.3089172523515731e0
    v = 0.1973060671902064e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4097938317810200e0
    b = 0.3393750055472244e0
    v = 0.2004987099616311e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4398256572859637e0
    b = 0.3693322470987730e0
    v = 0.2030170909281499e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4690384114718480e0
    b = 0.3986541005609877e0
    v = 0.2049461460119080e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4973216048301053e0
    b = 0.4272112491408562e0
    v = 0.2063653565200186e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5245681526132446e0
    b = 0.4548781735309936e0
    v = 0.2073507927381027e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5506733911803888e0
    b = 0.4815315355023251e0
    v = 0.2079764593256122e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5755339829522475e0
    b = 0.5070486445801855e0
    v = 0.2083150534968778e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1305472386056362e0
    b = 0.2284970375722366e-1
    v = 0.1262715121590664e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1637327908216477e0
    b = 0.4812254338288384e-1
    v = 0.1414386128545972e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1972734634149637e0
    b = 0.7531734457511935e-1
    v = 0.1538740401313898e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2308694653110130e0
    b = 0.1039043639882017e0
    v = 0.1642434942331432e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2643899218338160e0
    b = 0.1334526587117626e0
    v = 0.1729790609237496e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2977171599622171e0
    b = 0.1636414868936382e0
    v = 0.1803505190260828e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3307293903032310e0
    b = 0.1942195406166568e0
    v = 0.1865475350079657e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3633069198219073e0
    b = 0.2249752879943753e0
    v = 0.1917182669679069e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3953346955922727e0
    b = 0.2557218821820032e0
    v = 0.1959851709034382e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4267018394184914e0
    b = 0.2862897925213193e0
    v = 0.1994529548117882e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4573009622571704e0
    b = 0.3165224536636518e0
    v = 0.2022138911146548e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4870279559856109e0
    b = 0.3462730221636496e0
    v = 0.2043518024208592e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5157819581450322e0
    b = 0.3754016870282835e0
    v = 0.2059450313018110e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5434651666465393e0
    b = 0.4037733784993613e0
    v = 0.2070685715318472e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5699823887764627e0
    b = 0.4312557784139123e0
    v = 0.2077955310694373e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5952403350947741e0
    b = 0.4577175367122110e0
    v = 0.2081980387824712e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2025152599210369e0
    b = 0.2520253617719557e-1
    v = 0.1521318610377956e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2381066653274425e0
    b = 0.5223254506119000e-1
    v = 0.1622772720185755e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2732823383651612e0
    b = 0.8060669688588620e-1
    v = 0.1710498139420709e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3080137692611118e0
    b = 0.1099335754081255e0
    v = 0.1785911149448736e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3422405614587601e0
    b = 0.1399120955959857e0
    v = 0.1850125313687736e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3758808773890420e0
    b = 0.1702977801651705e0
    v = 0.1904229703933298e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4088458383438932e0
    b = 0.2008799256601680e0
    v = 0.1949259956121987e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4410450550841152e0
    b = 0.2314703052180836e0
    v = 0.1986161545363960e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4723879420561312e0
    b = 0.2618972111375892e0
    v = 0.2015790585641370e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5027843561874343e0
    b = 0.2920013195600270e0
    v = 0.2038934198707418e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5321453674452458e0
    b = 0.3216322555190551e0
    v = 0.2056334060538251e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5603839113834030e0
    b = 0.3506456615934198e0
    v = 0.2068705959462289e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5874150706875146e0
    b = 0.3789007181306267e0
    v = 0.2076753906106002e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6131559381660038e0
    b = 0.4062580170572782e0
    v = 0.2081179391734803e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2778497016394506e0
    b = 0.2696271276876226e-1
    v = 0.1700345216228943e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3143733562261912e0
    b = 0.5523469316960465e-1
    v = 0.1774906779990410e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3501485810261827e0
    b = 0.8445193201626464e-1
    v = 0.1839659377002642e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3851430322303653e0
    b = 0.1143263119336083e0
    v = 0.1894987462975169e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4193013979470415e0
    b = 0.1446177898344475e0
    v = 0.1941548809452595e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4525585960458567e0
    b = 0.1751165438438091e0
    v = 0.1980078427252384e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4848447779622947e0
    b = 0.2056338306745660e0
    v = 0.2011296284744488e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5160871208276894e0
    b = 0.2359965487229226e0
    v = 0.2035888456966776e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5462112185696926e0
    b = 0.2660430223139146e0
    v = 0.2054516325352142e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5751425068101757e0
    b = 0.2956193664498032e0
    v = 0.2067831033092635e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6028073872853596e0
    b = 0.3245763905312779e0
    v = 0.2076485320284876e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6291338275278409e0
    b = 0.3527670026206972e0
    v = 0.2081141439525255e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3541797528439391e0
    b = 0.2823853479435550e-1
    v = 0.1834383015469222e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3908234972074657e0
    b = 0.5741296374713106e-1
    v = 0.1889540591777677e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4264408450107590e0
    b = 0.8724646633650199e-1
    v = 0.1936677023597375e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4609949666553286e0
    b = 0.1175034422915616e0
    v = 0.1976176495066504e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4944389496536006e0
    b = 0.1479755652628428e0
    v = 0.2008536004560983e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5267194884346086e0
    b = 0.1784740659484352e0
    v = 0.2034280351712291e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5577787810220990e0
    b = 0.2088245700431244e0
    v = 0.2053944466027758e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5875563763536670e0
    b = 0.2388628136570763e0
    v = 0.2068077642882360e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6159910016391269e0
    b = 0.2684308928769185e0
    v = 0.2077250949661599e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6430219602956268e0
    b = 0.2973740761960252e0
    v = 0.2082062440705320e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4300647036213646e0
    b = 0.2916399920493977e-1
    v = 0.1934374486546626e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4661486308935531e0
    b = 0.5898803024755659e-1
    v = 0.1974107010484300e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5009658555287261e0
    b = 0.8924162698525409e-1
    v = 0.2007129290388658e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5344824270447704e0
    b = 0.1197185199637321e0
    v = 0.2033736947471293e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5666575997416371e0
    b = 0.1502300756161382e0
    v = 0.2054287125902493e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5974457471404752e0
    b = 0.1806004191913564e0
    v = 0.2069184936818894e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6267984444116886e0
    b = 0.2106621764786252e0
    v = 0.2078883689808782e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6546664713575417e0
    b = 0.2402526932671914e0
    v = 0.2083886366116359e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5042711004437253e0
    b = 0.2982529203607657e-1
    v = 0.2006593275470817e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5392127456774380e0
    b = 0.6008728062339922e-1
    v = 0.2033728426135397e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5726819437668618e0
    b = 0.9058227674571398e-1
    v = 0.2055008781377608e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6046469254207278e0
    b = 0.1211219235803400e0
    v = 0.2070651783518502e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6350716157434952e0
    b = 0.1515286404791580e0
    v = 0.2080953335094320e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6639177679185454e0
    b = 0.1816314681255552e0
    v = 0.2086284998988521e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5757276040972253e0
    b = 0.3026991752575440e-1
    v = 0.2055549387644668e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6090265823139755e0
    b = 0.6078402297870770e-1
    v = 0.2071871850267654e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6406735344387661e0
    b = 0.9135459984176636e-1
    v = 0.2082856600431965e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6706397927793709e0
    b = 0.1218024155966590e0
    v = 0.2088705858819358e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6435019674426665e0
    b = 0.3052608357660639e-1
    v = 0.2083995867536322e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6747218676375681e0
    b = 0.6112185773983089e-1
    v = 0.2090509712889637e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


def MakeAngularGrid_5810():
    grids = []
    a = 0
    b = 0
    v = 0.9735347946175486e-5
    grids.append(SphGenOh(0, a, b, v))
    v = 0.1907581241803167e-3
    grids.append(SphGenOh(1, a, b, v))
    v = 0.1901059546737578e-3
    grids.append(SphGenOh(2, a, b, v))
    a = 0.1182361662400277e-1
    v = 0.3926424538919212e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3062145009138958e-1
    v = 0.6667905467294382e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5329794036834243e-1
    v = 0.8868891315019135e-4
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7848165532862220e-1
    v = 0.1066306000958872e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1054038157636201e0
    v = 0.1214506743336128e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1335577797766211e0
    v = 0.1338054681640871e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1625769955502252e0
    v = 0.1441677023628504e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.1921787193412792e0
    v = 0.1528880200826557e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2221340534690548e0
    v = 0.1602330623773609e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2522504912791132e0
    v = 0.1664102653445244e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.2823610860679697e0
    v = 0.1715845854011323e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3123173966267560e0
    v = 0.1758901000133069e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3419847036953789e0
    v = 0.1794382485256736e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3712386456999758e0
    v = 0.1823238106757407e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3999627649876828e0
    v = 0.1846293252959976e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4280466458648093e0
    v = 0.1864284079323098e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4553844360185711e0
    v = 0.1877882694626914e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.4818736094437834e0
    v = 0.1887716321852025e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5074138709260629e0
    v = 0.1894381638175673e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5319061304570707e0
    v = 0.1898454899533629e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5552514978677286e0
    v = 0.1900497929577815e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.5981009025246183e0
    v = 0.1900671501924092e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6173990192228116e0
    v = 0.1899837555533510e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6351365239411131e0
    v = 0.1899014113156229e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6512010228227200e0
    v = 0.1898581257705106e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6654758363948120e0
    v = 0.1898804756095753e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6778410414853370e0
    v = 0.1899793610426402e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6881760887484110e0
    v = 0.1901464554844117e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.6963645267094598e0
    v = 0.1903533246259542e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7023010617153579e0
    v = 0.1905556158463228e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.7059004636628753e0
    v = 0.1907037155663528e-3
    grids.append(SphGenOh(3, a, b, v))
    a = 0.3552470312472575e-1
    v = 0.5992997844249967e-4
    grids.append(SphGenOh(4, a, b, v))
    a = 0.9151176620841283e-1
    v = 0.9749059382456978e-4
    grids.append(SphGenOh(4, a, b, v))
    a = 0.1566197930068980e0
    v = 0.1241680804599158e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2265467599271907e0
    v = 0.1437626154299360e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.2988242318581361e0
    v = 0.1584200054793902e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.3717482419703886e0
    v = 0.1694436550982744e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.4440094491758889e0
    v = 0.1776617014018108e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5145337096756642e0
    v = 0.1836132434440077e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.5824053672860230e0
    v = 0.1876494727075983e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6468283961043370e0
    v = 0.1899906535336482e-3
    grids.append(SphGenOh(4, a, b, v))
    a = 0.6095964259104373e-1
    b = 0.1787828275342931e-1
    v = 0.8143252820767350e-4
    grids.append(SphGenOh(5, a, b, v))
    a = 0.8811962270959388e-1
    b = 0.3953888740792096e-1
    v = 0.9998859890887728e-4
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1165936722428831e0
    b = 0.6378121797722990e-1
    v = 0.1156199403068359e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1460232857031785e0
    b = 0.8985890813745037e-1
    v = 0.1287632092635513e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1761197110181755e0
    b = 0.1172606510576162e0
    v = 0.1398378643365139e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2066471190463718e0
    b = 0.1456102876970995e0
    v = 0.1491876468417391e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2374076026328152e0
    b = 0.1746153823011775e0
    v = 0.1570855679175456e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2682305474337051e0
    b = 0.2040383070295584e0
    v = 0.1637483948103775e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2989653312142369e0
    b = 0.2336788634003698e0
    v = 0.1693500566632843e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3294762752772209e0
    b = 0.2633632752654219e0
    v = 0.1740322769393633e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3596390887276086e0
    b = 0.2929369098051601e0
    v = 0.1779126637278296e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3893383046398812e0
    b = 0.3222592785275512e0
    v = 0.1810908108835412e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4184653789358347e0
    b = 0.3512004791195743e0
    v = 0.1836529132600190e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4469172319076166e0
    b = 0.3796385677684537e0
    v = 0.1856752841777379e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4745950813276976e0
    b = 0.4074575378263879e0
    v = 0.1872270566606832e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5014034601410262e0
    b = 0.4345456906027828e0
    v = 0.1883722645591307e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5272493404551239e0
    b = 0.4607942515205134e0
    v = 0.1891714324525297e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5520413051846366e0
    b = 0.4860961284181720e0
    v = 0.1896827480450146e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5756887237503077e0
    b = 0.5103447395342790e0
    v = 0.1899628417059528e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1225039430588352e0
    b = 0.2136455922655793e-1
    v = 0.1123301829001669e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1539113217321372e0
    b = 0.4520926166137188e-1
    v = 0.1253698826711277e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1856213098637712e0
    b = 0.7086468177864818e-1
    v = 0.1366266117678531e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2174998728035131e0
    b = 0.9785239488772918e-1
    v = 0.1462736856106918e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2494128336938330e0
    b = 0.1258106396267210e0
    v = 0.1545076466685412e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2812321562143480e0
    b = 0.1544529125047001e0
    v = 0.1615096280814007e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3128372276456111e0
    b = 0.1835433512202753e0
    v = 0.1674366639741759e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3441145160177973e0
    b = 0.2128813258619585e0
    v = 0.1724225002437900e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3749567714853510e0
    b = 0.2422913734880829e0
    v = 0.1765810822987288e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4052621732015610e0
    b = 0.2716163748391453e0
    v = 0.1800104126010751e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4349335453522385e0
    b = 0.3007127671240280e0
    v = 0.1827960437331284e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4638776641524965e0
    b = 0.3294470677216479e0
    v = 0.1850140300716308e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4920046410462687e0
    b = 0.3576932543699155e0
    v = 0.1867333507394938e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5192273554861704e0
    b = 0.3853307059757764e0
    v = 0.1880178688638289e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5454609081136522e0
    b = 0.4122425044452694e0
    v = 0.1889278925654758e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5706220661424140e0
    b = 0.4383139587781027e0
    v = 0.1895213832507346e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5946286755181518e0
    b = 0.4634312536300553e0
    v = 0.1898548277397420e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.1905370790924295e0
    b = 0.2371311537781979e-1
    v = 0.1349105935937341e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2242518717748009e0
    b = 0.4917878059254806e-1
    v = 0.1444060068369326e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2577190808025936e0
    b = 0.7595498960495142e-1
    v = 0.1526797390930008e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2908724534927187e0
    b = 0.1036991083191100e0
    v = 0.1598208771406474e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3236354020056219e0
    b = 0.1321348584450234e0
    v = 0.1659354368615331e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3559267359304543e0
    b = 0.1610316571314789e0
    v = 0.1711279910946440e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3876637123676956e0
    b = 0.1901912080395707e0
    v = 0.1754952725601440e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4187636705218842e0
    b = 0.2194384950137950e0
    v = 0.1791247850802529e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4491449019883107e0
    b = 0.2486155334763858e0
    v = 0.1820954300877716e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4787270932425445e0
    b = 0.2775768931812335e0
    v = 0.1844788524548449e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5074315153055574e0
    b = 0.3061863786591120e0
    v = 0.1863409481706220e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5351810507738336e0
    b = 0.3343144718152556e0
    v = 0.1877433008795068e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5619001025975381e0
    b = 0.3618362729028427e0
    v = 0.1887444543705232e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5875144035268046e0
    b = 0.3886297583620408e0
    v = 0.1894009829375006e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6119507308734495e0
    b = 0.4145742277792031e0
    v = 0.1897683345035198e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2619733870119463e0
    b = 0.2540047186389353e-1
    v = 0.1517327037467653e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.2968149743237949e0
    b = 0.5208107018543989e-1
    v = 0.1587740557483543e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3310451504860488e0
    b = 0.7971828470885599e-1
    v = 0.1649093382274097e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3646215567376676e0
    b = 0.1080465999177927e0
    v = 0.1701915216193265e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3974916785279360e0
    b = 0.1368413849366629e0
    v = 0.1746847753144065e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4295967403772029e0
    b = 0.1659073184763559e0
    v = 0.1784555512007570e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4608742854473447e0
    b = 0.1950703730454614e0
    v = 0.1815687562112174e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4912598858949903e0
    b = 0.2241721144376724e0
    v = 0.1840864370663302e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5206882758945558e0
    b = 0.2530655255406489e0
    v = 0.1860676785390006e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5490940914019819e0
    b = 0.2816118409731066e0
    v = 0.1875690583743703e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5764123302025542e0
    b = 0.3096780504593238e0
    v = 0.1886453236347225e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6025786004213506e0
    b = 0.3371348366394987e0
    v = 0.1893501123329645e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6275291964794956e0
    b = 0.3638547827694396e0
    v = 0.1897366184519868e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3348189479861771e0
    b = 0.2664841935537443e-1
    v = 0.1643908815152736e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.3699515545855295e0
    b = 0.5424000066843495e-1
    v = 0.1696300350907768e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4042003071474669e0
    b = 0.8251992715430854e-1
    v = 0.1741553103844483e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4375320100182624e0
    b = 0.1112695182483710e0
    v = 0.1780015282386092e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4699054490335947e0
    b = 0.1402964116467816e0
    v = 0.1812116787077125e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5012739879431952e0
    b = 0.1694275117584291e0
    v = 0.1838323158085421e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5315874883754966e0
    b = 0.1985038235312689e0
    v = 0.1859113119837737e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5607937109622117e0
    b = 0.2273765660020893e0
    v = 0.1874969220221698e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5888393223495521e0
    b = 0.2559041492849764e0
    v = 0.1886375612681076e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6156705979160163e0
    b = 0.2839497251976899e0
    v = 0.1893819575809276e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6412338809078123e0
    b = 0.3113791060500690e0
    v = 0.1897794748256767e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4076051259257167e0
    b = 0.2757792290858463e-1
    v = 0.1738963926584846e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4423788125791520e0
    b = 0.5584136834984293e-1
    v = 0.1777442359873466e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4760480917328258e0
    b = 0.8457772087727143e-1
    v = 0.1810010815068719e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5085838725946297e0
    b = 0.1135975846359248e0
    v = 0.1836920318248129e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5399513637391218e0
    b = 0.1427286904765053e0
    v = 0.1858489473214328e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5701118433636380e0
    b = 0.1718112740057635e0
    v = 0.1875079342496592e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5990240530606021e0
    b = 0.2006944855985351e0
    v = 0.1887080239102310e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6266452685139695e0
    b = 0.2292335090598907e0
    v = 0.1894905752176822e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6529320971415942e0
    b = 0.2572871512353714e0
    v = 0.1898991061200695e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.4791583834610126e0
    b = 0.2826094197735932e-1
    v = 0.1809065016458791e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5130373952796940e0
    b = 0.5699871359683649e-1
    v = 0.1836297121596799e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5456252429628476e0
    b = 0.8602712528554394e-1
    v = 0.1858426916241869e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5768956329682385e0
    b = 0.1151748137221281e0
    v = 0.1875654101134641e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6068186944699046e0
    b = 0.1442811654136362e0
    v = 0.1888240751833503e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6353622248024907e0
    b = 0.1731930321657680e0
    v = 0.1896497383866979e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6624927035731797e0
    b = 0.2017619958756061e0
    v = 0.1900775530219121e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5484933508028488e0
    b = 0.2874219755907391e-1
    v = 0.1858525041478814e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.5810207682142106e0
    b = 0.5778312123713695e-1
    v = 0.1876248690077947e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6120955197181352e0
    b = 0.8695262371439526e-1
    v = 0.1889404439064607e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6416944284294319e0
    b = 0.1160893767057166e0
    v = 0.1898168539265290e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6697926391731260e0
    b = 0.1450378826743251e0
    v = 0.1902779940661772e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6147594390585488e0
    b = 0.2904957622341456e-1
    v = 0.1890125641731815e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6455390026356783e0
    b = 0.5823809152617197e-1
    v = 0.1899434637795751e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6747258588365477e0
    b = 0.8740384899884715e-1
    v = 0.1904520856831751e-3
    grids.append(SphGenOh(5, a, b, v))
    a = 0.6772135750395347e0
    b = 0.2919946135808105e-1
    v = 0.1905534498734563e-3
    grids.append(SphGenOh(5, a, b, v))
    return np.vstack(grids)


# ~= (L+1)**2/3
LEBEDEV_ORDER = {
    0: 1,
    3: 6,
    5: 14,
    7: 26,
    9: 38,
    11: 50,
    13: 74,
    15: 86,
    17: 110,
    19: 146,
    21: 170,
    23: 194,
    25: 230,
    27: 266,
    29: 302,
    31: 350,
    35: 434,
    41: 590,
    47: 770,
    53: 974,
    59: 1202,
    65: 1454,
    71: 1730,
    77: 2030,
    83: 2354,
    89: 2702,
    95: 3074,
    101: 3470,
    107: 3890,
    113: 4334,
    119: 4802,
    125: 5294,
    131: 5810,
}
LEBEDEV_NGRID = np.array(list(LEBEDEV_ORDER.values()))


@lru_cache(maxsize=50)
def MakeAngularGrid(points):
    """Angular grids for specified Lebedev points"""
    if points in (0, 1):
        return np.array((0.0, 0.0, 0.0, 1.0))

    if points not in LEBEDEV_NGRID:
        raise ValueError('Unsupported angular grids %d' % points)

    fn = globals()['MakeAngularGrid_' + str(points)]
    grids = fn()
    return grids
