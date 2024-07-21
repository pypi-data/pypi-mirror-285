from scipy.interpolate import griddata
from itertools import product
import numpy as np
import os
import shutil
from boss.pp.mesh import Mesh


class PFMain:
    def __init__(
        self,
        n_tasks=2,
        mesh_size=10,
        bounds=np.array([[0, 1.0], [0, 1.0]]),
        models=None,
    ):
        """
        Calculates the Pareto front and optimal solutions for multi-objective optimization.

        - Overview:
            - This class finds the Pareto front and corresponding solutions for problems with any number of input dimensions and objectives.


        Parameters
        ----------
        n_tasks : int
            The number of objectives to optimize.

        mesh_size : int
            The size of the discretized data for each model.

        bounds : ndarray
            The bounds for each model.

        models : boss result function
            The BOSS GP models.

        Returns
        -------
        None
            This function does not return anything directly, but performs calculations
            to determine the Pareto front and the Pareto optimal solutions.
        """

        self.n_tasks = n_tasks
        self.mesh_size = mesh_size
        self.bounds = bounds
        self.n_dim = np.shape(self.bounds)[0]
        self.models = models
        self.n_mesh = (self.mesh_size,) * self.n_dim
        self.mesher = Mesh(self.bounds, grid_pts=self.mesh_size)
        self.X_mg = self.mesher.grid

    def get_data_on_grid(self, path, bounds, x_pts):
        """
        Retrieve data on a grid.

        Description
        -----------
        This subroutine is a needed function when meshes don't match from different tasks.

        Parameters
        ----------
        path : str
            Path to the models.

        bounds : ndarray
            The bounds for each model.

        x_pts : ndarray
            All input data points.

        Returns
        -------
        ndarray
            Numpy array with models evaluated on a uniform mesh grid
        """

        data = np.loadtxt(path)
        x_inp = tuple([data[:, i] for i in range(self.n_dim)])
        y_inp = data[:, self.n_dim]
        x_pts_int = tuple([x_pts[i] for i in range(self.n_dim)])
        gd = griddata(x_inp, y_inp, x_pts_int, method="nearest")
        return gd

    def x_mesh(self, bounds, n_mesh):
        """
         Description:
         ----------
         Generates a linear space between the edges of the bounds for each input dimension.

         Parameters:
         ----------

         bounds : ndarray
             The bounds for each model.

         n_mesh : ndarray
             An array of shape mesh_size * model dimension

        Returns
        -------
        ndarray
             Numpy array with shape (n_dimension, mesh size)
        """
        x = [
            np.linspace(self.bounds[i, 0], self.bounds[i, 1], n_mesh[i])
            for i in range(self.n_dim)
        ]
        return x

    def position_coordinates(self, coordinate_grid, n_dim, values):
        """
        Arrange input data in n-dimensional space to correspond to model predictions for each objective.

        Description
        -----------
        Arranges the input data in n-dimensional space to correspond to the model prediction
        for that input for each objective.

        Parameters
        ----------
        coordinate_grid : ndarray
            Input data on the defined grid.

        n_dim : int
            Input dimensionality of each model.

        values : ndarray
            Corresponding prediction for each objective.

        Returns
        -------
        ndarray

            Numpy array with shape (model dimension, )
        """
        positions_tmp = coordinate_grid
        for i in range(self.n_dim):
            positions_tmp = positions_tmp.take(indices=values[i], axis=1)
        return positions_tmp

    def evaluate_mesh(self, f, X_mg):
        """
        Evaluate mesh (model prediction) depending on the dimensions of meshgrid.

        Description
        -----------
        Evaluation for a mesh (model prediction) depending on the dimensions of the meshgrid

        Parameters
        ----------
        f : function
            A function that returns an numpy array of the evaluated matrix on the uniform meshgrid.

        X_mg : ndarray
            See mesher class for more information

        Returns
        -------
        ndarray

            Numpy array with shape (mesh size, mesh size ......, n_dimensions times )
        """
        x_ind = []

        for i in range(self.n_dim):
            if self.n_dim > 1:
                x_ind.append(np.take(self.X_mg[i], 0, axis=i))
            else:
                x_ind.append(self.X_mg[i])
        nx_ind = []
        for i in range(self.n_dim):
            nx_ind.append(len(x_ind[i]))
        F = []
        bounds_list = [[] for i in range(self.n_dim)]
        for i in range(self.n_dim):
            bounds_list[i] = nx_ind[i]
        bounds_list = np.reshape(bounds_list, (self.n_dim, 1))
        for value in product(*(range(*bl) for bl in bounds_list)):
            values = [value[xx] for xx in range(self.n_dim)]
            coordinate_grid = np.array([self.X_mg[i] for i in range(self.n_dim)])
            positions = self.position_coordinates(coordinate_grid, self.n_dim, values)
            F.append(f(positions))
        F = np.array(F).reshape(tuple(nx_ind))
        return F

    def squeeze_mesh(self, n_size, data_pts):
        """
        Flatten an N-dimensional tensor.

        Description
        -----------
        Flattens a N-dimensional tensor.

        Parameters
        ----------
        n_size : int
            Input dimensionality of each model.

        data_pts : ndarray
            Input data on the defined grid.

        Returns
        -------
        ndarray

            Numpy array with shape (mesh size^n_dimensions, n_dimensions )
        """

        Y_squeezed_tmp = [data_pts[i].flatten()[:, None] for i in range(n_size)]
        Y_squeezed = np.hstack(tuple(Y_squeezed_tmp))
        return Y_squeezed

    def is_pareto(self, Y):
        """
        Check if a point in an N-dimensional tensor is Pareto or not.

        Description
        -----------
        Check if a point in an N-dimensional tensor is Pareto or not, hence boolean.

        Parameters
        ----------
        Y : ndarray
            Corresponding prediction for each objective.

        Returns
        -------
        ndarray
            Boolean array that corresponds to the index of the meshgrid which is a Pareto front/optimal solution.
        """
        pareto_mask = np.ones(Y.shape[0], dtype=bool)
        for i, y in enumerate(Y):
            if np.any(np.all(y < Y, axis=1)):
                pareto_mask[i] = False
        return pareto_mask

    def calc_pareto(self, functions, bounds, n_mesh):
        """
        Calculate the Pareto optimal solutions for any input dimensions and any number of objectives.

        Description
        -----------
        This function calculates the Pareto optimal solutions for any input dimensions and any number of objectives.

        Parameters
        ----------
        functions : ndarray
            Models of the various objectives.

        bounds : ndarray
            The bounds for each model.

        n_mesh : ndarray
            Output of the function n_mesh_generator.

        Returns
        -------
        pareto_solutions : ndarray
            Pareto optimal solutions (shape: number of dimensions, number of solutions).

        pareto_front : ndarray
            Pareto front (number of objectives, number of solutions).

        feasible_points : ndarray
            Feasible points (meshsize^number of dimensions, number of objectives).
        """
        func = [functions[i] for i in range(self.n_tasks)]
        all_Ys = [self.evaluate_mesh(func[i], self.X_mg) for i in range(self.n_tasks)]
        Xdata_pts = [self.X_mg[i] for i in range(self.n_dim)]
        X = self.squeeze_mesh(self.n_dim, Xdata_pts)
        Ydata_pts = [all_Ys[i] for i in range(self.n_tasks)]
        Y_feasible = self.squeeze_mesh(self.n_tasks, Ydata_pts)
        pareto_mask = self.is_pareto(Y_feasible)
        Y_pareto = Y_feasible[pareto_mask]
        X_pareto = X[pareto_mask]
        return X_pareto, Y_pareto, Y_feasible

    def all_functions(self, path):
        """
        Create functions in the format needed for Pareto code for different mesh sizes.

        Description
        -----------
        Creates functions in the format needed for Pareto analysis at different mesh sizes.
        The paths to the outputs from BOSS are the only needed inputs.

        Parameters
        ----------
        path : str
            Paths to the output to n-dimensional BOSS models.

        Returns
        -------
        ndarray
            A function that returns an numpy array of the evaluated matrix on the uniform meshgrid.
        """

        def func(X):
            return self.get_data_on_grid(path, self.bounds, X)

        return func

    def boss_functions(self):
        """
        Calculate the prediction of the model on an n-dimensional grid.

        Description
        -----------
        Calculates the prediction of the model on an n-dimensional input model grid.

        Returns
        -------
        function
            A function that returns an ndarray of the BOSS predictions model.
        """

        def f(x):
            return self.models.predict(np.atleast_2d(x))[0]

        return f

    def write_output(self, file_name, Y, n_size):
        """
        Create outputs in n columns for plotting.

        Description
        -----------
        Creates outputs in n columns for plotting.
        1st input is the user-given name and the second input is the output from the analyze module.

        Parameters
        ----------
        file_name : str
            Output file name.

        Y : ndarray
            Pareto and feasible points.

        n_size : int
            Input dimensionality of the models.

        Returns
        -------
        None
        """
        with open(file_name, "w") as p_file:
            for i in range(len(Y)):
                for count in range(n_size):
                    if count == n_size - 1:
                        p_file.write("%s\n" % Y[i][count])
                    else:
                        p_file.write("%s " % Y[i][count])

    def generate_grid_models(self):
        """
        Generate an N-dimensional discretized Gaussian Process model if 'models' folder isn't created.

        Description
        -----------
        Generates an N-dimensional discretized Gaussian Process model if the 'models' folder isn't created.

        Returns
        -------
        None
        """
        if self.models is not None:
            # boss_gp_model = self.models
            # X_mg = self.build_mesh(self.bounds, self.n_mesh)
            X_mg_ind = [self.X_mg[i].ravel() for i in range(self.n_dim)]
            if self.n_tasks > 1:
                Y = [
                    self.models.model.predict(np.column_stack((X_mg_ind)), index=i)[0]
                    for i in range(self.n_tasks)
                ]
            else:
                Y = [
                    self.models.model.predict(np.column_stack((X_mg_ind)))[0]
                    for i in range(self.n_tasks)
                ]
            xp_ind = [
                self.x_mesh(self.bounds, self.n_mesh)[i] for i in range(self.n_dim)
            ]
            boundaries_list = [self.n_mesh[j] for j in range(self.n_dim)]
            boundaries_list = np.reshape(boundaries_list, (self.n_dim, 1))
            # Check if the folder exists
            if os.path.exists("models"):
                # Delete the existing folder
                print("warning: overwriting folder 'models'")
                shutil.rmtree("models")
            os.mkdir("models")
            for nt in range(self.n_tasks):
                with open("models/grid_model_obj_%s.dat" % nt, "w") as file_tmp:
                    count_tmp = 0
                    for values in product(*(range(*b) for b in boundaries_list)):
                        for ind in range(self.n_dim):
                            file_tmp.write(
                                "%s " % (xp_ind[ind][values[self.n_dim - 1 - ind]])
                            )
                        file_tmp.write("%s\n" % (Y[nt][count_tmp][0]))
                        count_tmp += 1

    def get_pareto(self):
        """
        Start the Pareto calculations and return the Pareto fronts, optimal solutions,
        and feasible points from the function calc_pareto.

        Description
        -----------
        Starts the Pareto calculations and returns the Pareto fronts, optimal solutions,
        and feasible points from the function calc_pareto.

        Returns
        -------
        pareto_solutions : ndarray
            Pareto optimal solutions (shape: number of dimensions, number of solutions).

        pareto_front : ndarray
            Pareto front (number of objectives, number of solutions).

        feasible_points : ndarray
            Feasible points (meshsize^number of dimensions, number of objectives).
        """
        # self.input_path_generator()
        paths = []
        for i in range(self.n_tasks):
            paths.append("models/grid_model_obj_%s.dat" % i)

        self.generate_grid_models()
        functions = [self.all_functions(paths[i]) for i in range(self.n_tasks)]
        X_pareto, Y_pareto, Y_feasible = self.calc_pareto(
            functions, self.bounds, self.n_mesh
        )
        return X_pareto, Y_pareto, Y_feasible

    def run(self):
        """
        Runs the paretofront postprocessing routine

        Returns
        -------
        None

        """
        X_pareto, Y_pareto, Y_feasible = self.get_pareto()

        # Check if the folder exists
        if os.path.exists("postprocessing/pareto"):
            # Delete the existing folder
            print("warning: overwriting folder 'postprocessing/pareto'")
            shutil.rmtree("postprocessing/pareto")
        if os.path.exists("postprocessing/"):
            os.mkdir("postprocessing/pareto")
        else:
            # print("postprocessing file does not exist, making one")
            os.mkdir("postprocessing")
            os.mkdir("postprocessing/pareto")
        os.mkdir("postprocessing/pareto/pf_data_models")
        os.mkdir("postprocessing/pareto/pf_graph_models")
        self.write_output(
            "postprocessing/pareto/pf_data_models/y_pareto_output.dat",
            Y_pareto,
            self.n_tasks,
        )
        self.write_output(
            "postprocessing/pareto/pf_data_models/x_pareto_output.dat",
            X_pareto,
            self.n_dim,
        )
        self.write_output(
            "postprocessing/pareto/pf_data_models/y_feasible_output.dat",
            Y_feasible,
            self.n_tasks,
        )

    # Visualization of the pareto front below ############
    def plot_pf(self, *args, elev=None, azim=None):
        """
        Description:
        ----------

        Plots the pareto front

        Returns
        -------
        None

        """
        if self.n_tasks == 2:
            import matplotlib.pyplot as plt

            fig = plt.figure()
            Y_pareto = np.atleast_2d(
                np.loadtxt("postprocessing/pareto/pf_data_models/y_pareto_output.dat")
            )
            Y_feasible = np.atleast_2d(
                np.loadtxt("postprocessing/pareto/pf_data_models/y_feasible_output.dat")
            )

            plt.scatter(
                Y_feasible[:, 0], Y_feasible[:, 1], c="gray", label="Feasible points"
            )  # Pareto X1, X2
            plt.scatter(
                Y_pareto[:, 0],
                Y_pareto[:, 1],
                c=Y_pareto[:, 1],
                cmap="rainbow",
                label="Pareto Front",
            )

            plt.title("2D Pareto Front")
            if len(args) == 0 or len(args) == 1:
                print("Not enough labels, using default names, task1 and task2")
                label1 = "task1"
                label2 = "task2"
            elif len(args) > 2:
                print("Number of labels greater than the number of tasks")
                label1 = "task1"
                label2 = "task2"
            else:
                label1 = "%s" % (args[0])
                label2 = "%s" % (args[1])
            plt.xlabel("%s" % (label1), fontsize=16)
            plt.ylabel("%s" % (label2), fontsize=16)
            plt.grid()
            plt.xticks(fontsize=16)
            plt.yticks(fontsize=16)
            plt.legend()
            plt.tight_layout()
            plt.savefig("postprocessing/pareto/pf_graph_models/pareto_front_y.png")
            # plt.show()

        if self.n_tasks == 3:
            import matplotlib.pyplot as plt

            data_feas = np.atleast_2d(
                np.loadtxt("postprocessing/pareto/pf_data_models/y_feasible_output.dat")
            )
            data_pf = np.atleast_2d(
                np.loadtxt("postprocessing/pareto/pf_data_models/y_pareto_output.dat")
            )
            x = data_feas[:, 0]
            y = data_feas[:, 1]
            z = data_feas[:, 2]
            x_pf = data_pf[:, 0]
            y_pf = data_pf[:, 1]
            z_pf = data_pf[:, 2]
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection="3d")
            # Customize the scatter plot with colors, sizes, and transparency
            ax.scatter(x, y, z, s=50, color="grey", alpha=0.7)
            ax.scatter(
                x_pf,
                y_pf,
                z_pf,
                s=50,
                c=z_pf,
                cmap="viridis",
                alpha=0.9,
                label="Pareto front",
                zorder="10",
            )

            # Customize the axis labels and title
            if len(args) in [0, 1, 2]:
                print("Not enough labels, using default names, task1 and task2")
                label1 = "task1"
                label2 = "task2"
                label3 = "task3"
            elif len(args) > 3:
                print("Number of labels greater than the number of tasks")
                label1 = "task1"
                label2 = "task2"
                label3 = "task3"
            else:
                label1 = "%s" % (args[0])
                label2 = "%s" % (args[1])
                label3 = "%s" % (args[2])

            ax.set_xlabel("%s" % label1, fontsize=16, labelpad=10)
            ax.set_ylabel("%s" % label2, fontsize=16, labelpad=10)
            ax.set_zlabel("%s" % label3, fontsize=16, labelpad=10)
            ax.set_title("Pareto front in 3D", fontsize=16)

            # Change tick label font size
            ax.tick_params(axis="x", labelsize=16)
            ax.tick_params(axis="y", labelsize=16)
            ax.tick_params(axis="z", labelsize=16)

            # Show the plot
            # Customize view angle
            ax.view_init(elev=elev, azim=azim)  # Set the elevation and azimuth angles
            # plt.show()
            plt.savefig("postprocessing/pareto/pf_graph_models/3d_pareto_front.png")

    def plot_pos(self, *args, **kwargs):
        """
        Description:
        ----------

        [Plots the pareto optimal soultions]
        """
        if self.n_dim == 1:
            model_names = []
            for names in kwargs.items():
                model_names.append(names[1])

            import matplotlib.pyplot as plt

            for i in range(self.n_tasks):
                plt.clf()
                data = np.loadtxt("models/grid_model_obj_%s.dat" % i)
                X_p = np.atleast_2d(
                    np.loadtxt(
                        "postprocessing/pareto/pf_data_models/x_pareto_output.dat"
                    )
                )

                if len(args) == 0:
                    print("Not enough label, using default name 'X'")
                    x_label = "X"
                elif len(args) > 1:
                    print("Too many labels")
                    x_label = "X"
                else:
                    x_label = "%s" % args[0]

                if model_names == []:
                    model_label = "Model %s" % i
                else:
                    model_label = "%s" % model_names[i]

                plt.plot(data[:, 0], data[:, 1], lw=4, label=model_label)

                # print(X_p, np.shape((X_p))[1] )
                plt.scatter(X_p, 0 * X_p + np.min(data[:, 1]))

                plt.xticks(fontsize=16)
                plt.yticks(fontsize=16)
                plt.xlabel("%s" % x_label, fontsize=16)
                plt.ylabel("%s" % model_label, fontsize=16)
                plt.legend(fontsize=16)
                plt.tight_layout()
                plt.savefig(
                    "postprocessing/pareto/pf_graph_models/pareto_optimal_solution_task_%s.png"
                    % i
                )

        if self.n_dim == 2:
            model_names = []
            for names in kwargs.items():
                model_names.append(names[1])

            import matplotlib.pyplot as plt

            fig = plt.figure()
            X_pareto = np.atleast_2d(
                np.loadtxt("postprocessing/pareto/pf_data_models/x_pareto_output.dat")
            )
            for i in range(self.n_tasks):
                plt.clf()
                data = np.loadtxt("models/grid_model_obj_%s.dat" % i)
                mesh_ = int(np.sqrt(len(data)))
                xp1 = np.linspace(self.bounds[0][0], self.bounds[0][1], mesh_)
                xp2 = np.linspace(self.bounds[1][0], self.bounds[1][1], mesh_)
                y = data[:, 2]
                plt.scatter(
                    X_pareto[:, 0],
                    X_pareto[:, 1],
                    c=X_pareto[:, 1],
                    cmap="rainbow",
                    zorder=5,
                    label="pareto optimal solutions",
                )
                cset = plt.contourf(
                    xp1, xp2, y.reshape(len(xp1), len(xp2)), levels=mesh_, cmap="Greys"
                )
                plt.contour(
                    xp1,
                    xp2,
                    y.reshape(len(xp1), len(xp2)),
                    20,
                    colors="teal",
                    linestyles="dotted",
                    levels=mesh_,
                )
                # Add a color bar
                colorbar = plt.colorbar(cset, pad=0.15)
                # Change the size of colorbar tick labels
                colorbar.ax.tick_params(labelsize=16)  # Adjust the tick label siz
                if model_names == []:
                    colorbar.set_label("Model %s" % i, fontsize=16)
                else:
                    colorbar.set_label("%s" % model_names[i], fontsize=16)

                if len(args) == 0 or len(args) == 1:
                    print("Not enough labels, using default names, X1 and X2")
                    label1 = "X1"
                    label2 = "X2"
                elif len(args) > 2:
                    print("Number of labels greater than the number of tasks")
                    label1 = "X1"
                    label2 = "X2"
                else:
                    label1 = "%s" % (args[0])
                    label2 = "%s" % (args[1])
                plt.xlabel("%s" % (label1), fontsize=16)
                plt.ylabel("%s" % (label2), fontsize=16)
                plt.xticks(fontsize=16)
                plt.xticks(
                    np.linspace(self.bounds[0][0], self.bounds[0][1], 5)
                )  # Adjust the range based on your data
                plt.yticks(fontsize=16)
                plt.yticks(np.linspace(self.bounds[1][0], self.bounds[1][1], 5))
                plt.legend()
                plt.tight_layout()
                plt.savefig(
                    "postprocessing/pareto/pf_graph_models/pareto_optimal_solutions_task_%s.png"
                    % (i)
                )

        if self.n_dim == 3:
            import matplotlib.pyplot as plt

            data_inp = np.atleast_2d(
                np.loadtxt("postprocessing/pareto/pf_data_models/x_pareto_output.dat")
            )
            x = data_inp[:, 0]
            y = data_inp[:, 1]
            z = data_inp[:, 2]
            # Create a 3D scatter plot
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection="3d")
            # Customize the scatter plot with colors, sizes, and transparency
            scatter = ax.scatter(
                x, y, z, s=50, c=z, cmap="viridis", alpha=0.7, label="Model"
            )
            # Customize the axis labels and title
            if len(args) == 0 or len(args) == 1 or len(args) == 2:
                print("Not enough labels, using default names, X_i; i  = 1,2,3")
                label1 = "X1"
                label2 = "X2"
                label3 = "X3"
            elif len(args) > 3:
                print("Number of labels greater than the number of tasks")
                label1 = "X1"
                label2 = "X2"
                label3 = "X3"
            else:
                label1 = "%s" % (args[0])
                label2 = "%s" % (args[1])
                label3 = "%s" % (args[2])
            ax.set_xlabel("%s" % label1, fontsize=16, labelpad=10)
            ax.set_ylabel("%s" % label2, fontsize=16, labelpad=10)
            ax.set_zlabel("%s" % label3, fontsize=16, labelpad=10)
            ax.set_title("3D Pareto optimal solutions", fontsize=16)

            # Change tick label font size
            ax.tick_params(axis="x", labelsize=16)  # pad = 10
            ax.tick_params(axis="y", labelsize=16)
            ax.tick_params(axis="z", labelsize=16)

            plt.savefig(
                "postprocessing/pareto/pf_graph_models/3d_pareto_optimal_solutions.png"
            )

            model_names = []
            for names in kwargs.items():
                model_names.append(names[1])

            for i in range(self.n_tasks):
                data_inp = np.loadtxt("models/grid_model_obj_%s.dat" % i)
                x = data_inp[:, 0]
                y = data_inp[:, 1]
                z = data_inp[:, 2]
                out = data_inp[:, 3]
                # Create a 3D scatter plot
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection="3d")

                # Customize the scatter plot with colors, sizes, and transparency
                scatter = ax.scatter(
                    x, y, z, s=50, c=out, cmap="viridis", alpha=0.7, label="Model"
                )

                # Add a color bar
                colorbar = plt.colorbar(scatter, pad=0.15)
                if model_names == []:
                    colorbar.set_label("Model %s" % i, fontsize=16)
                else:
                    colorbar.set_label("%s" % model_names[i], fontsize=16)

                # Customize the axis labels and title
                if len(args) == 0 or len(args) == 1 or len(args) == 2:
                    print("Not enough labels, using default names, X_i; i  = 1,2,3")
                    label1 = "X1"
                    label2 = "X2"
                    label3 = "X3"
                elif len(args) > 3:
                    print("Number of labels greater than the number of tasks")
                    label1 = "X1"
                    label2 = "X2"
                    label3 = "X3"
                else:
                    label1 = "%s" % (args[0])
                    label2 = "%s" % (args[1])
                    label3 = "%s" % (args[2])
                ax.set_xlabel("%s" % label1, fontsize=16, labelpad=10)
                ax.set_ylabel("%s" % label2, fontsize=16, labelpad=10)
                ax.set_zlabel("%s" % label3, fontsize=16, labelpad=10)
                ax.set_title("3D Surrogate model", fontsize=16)

                # Change tick label font size
                ax.tick_params(axis="x", labelsize=16)  # pad = 10
                ax.tick_params(axis="y", labelsize=16)
                ax.tick_params(axis="z", labelsize=16)
                # Change limits on color bar
                scatter.set_clim(np.min(out), np.max(out))

                # Change the size of colorbar tick labels
                colorbar.ax.tick_params(labelsize=16)  # Adjust the tick label siz

                # Show the plot
                # ax.view_init(elev=elev, azim=azim)
                # plt.show()
                plt.savefig(
                    "postprocessing/pareto/pf_graph_models/3d_surrogate_model_%s.png"
                    % i
                )
