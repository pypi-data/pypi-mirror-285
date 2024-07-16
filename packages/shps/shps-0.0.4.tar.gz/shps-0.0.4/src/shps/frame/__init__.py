
    def strain(self, x, y, z):
        """Calculate the strain at a point expressed in local coordinate.

        Parameters
        ----------
        x: float
            the 1st local coordinate.
        y: float
            the 2nd local coordinate.
        z: float
            the 3rd local coordinate.

        Returns
        -------
        strain: numpy.ndarray
            the strain vector with six components.

        """
        u, t11, t21, t31, t12, t22, t32 = self.local_displacement().reshape(7)
        L = self.initial_length

        # Shape functions and their derivatives
        # def f1(x): return 1 - 3 * (x/L)**2 + 2 * (x/L)**3
        # def f2(x): return x * (1 - x/L)**2
        # def f3(x): return 1 - f1(x)
        # def f4(x): return (x**2) * (x/L - 1) / L
        def f5(x):
            return 1 - x / L

        def f6(x):
            return x / L

        # def df1(x): return -6*x/L**2 + 6*x**2/L**3
        def df2(x):
            return (1 - x / L)**2 - 2 * x * (1 - x / L) / L

        # def df3(x): return 6*x/L**2 - 6*x**2/L**3
        def df4(x):
            return 2 * x * (-1 + x / L) / L + x**2 / L**2

        def df5(x):
            return -1 / L

        def df6(x):
            return 1 / L

        # def ddf1(x): return -6/L**2 + 12*x/L**3
        def ddf2(x):
            return -4 * (1 - x / L) / L + 2 * x / L**2

        # def ddf3(x): return 6/L**2 - 12*x/L**3
        def ddf4(x):
            return 2 * (-1 + x / L) / L + 4 * x / L**2

        # def ddf5(x): return 0
        # def ddf6(x): return 0

        if self.beamtype == "Bernoulli":
            # u1 = f6(x) * u
            # u2 = f2(x) * t31 + f4(x) * t32
            # u3 = -f2(x) * t21 - f4(x) * t22

            du1 = df6(x) * u
            du2 = df2(x) * t31 + df4(x) * t32
            du3 = -df2(x) * t21 - df4(x) * t22

            # ddu1 = ddf6(x)
            ddu2 = ddf2(x) * t31 + ddf4(x) * t32
            ddu3 = -ddf2(x) * t21 - ddf4(x) * t22

            # t1 = f5(x) * t11 + f6(x) * t12
            t2 = -du3
            t3 = du2

            dt1 = df5(x) * t11 + df6(x) * t12
            dt2 = -ddu3
            dt3 = ddu2

        elif self.beamtype == "Timoshenko":
            du1 = u / L
            du2 = 0.0
            du3 = 0.0

            ddu2 = 0.0
            ddu3 = 0.0

            t1 = f5(x) * t11 + f6(x) * t12
            t2 = f5(x) * t21 + f6(x) * t22
            t3 = f5(x) * t31 + f6(x) * t32

            dt1 = (t12 - t11) / L
            dt2 = (t22 - t21) / L
            dt3 = (t32 - t31) / L

        eps_11 = (
            du1
            + (du2**2 + du3**2) / 2
            - y * dt3
            + z * dt2
            + (y**2 + z**2) * dt1**2 / 2
        )
        eps_22 = (
            -self.first_lame_constant
            * eps_11
            / (2 * (self.first_lame_constant + self.second_lame_constant))
        )
        eps_33 = eps_22
        gamma_12 = du2 - t3 - z * dt1
        gamma_13 = du3 + t2 + y * dt1

        return np.array([[eps_11, eps_22, eps_33, gamma_12, 0.0, gamma_13]]).T

