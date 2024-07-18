import numpy as np
from scipy.spatial import cKDTree


class SpatialAnalysis:
    @staticmethod
    def idw_interpolate(x, y, coordinates, values, power=2):
        """
        Function for IDW interpolation
        @param x: x values of raster pixels
        @param y: y values of raster pixels
        @param coordinates: coordinates of known points
        @param values: values of known points
        @param power: power parameter for IDW
        @return: interpolated values at (x, y) positions
        """
        # Ensure inputs are numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)
        coordinates = np.asarray(coordinates)
        values = np.asarray(values)

        # Create KDTree for efficient distance computation
        tree = cKDTree(coordinates)

        # Determine the number of nearest neighbors to query
        k = min(4, len(values))  # Ensure k does not exceed the number of known values

        # Find distances and indices of nearest neighbors
        distances, indices = tree.query(np.column_stack((x, y)), k=k)  # k=3 nearest neighbors

        # Check the shapes of the arrays
        print(f"Distances shape: {distances.shape}")
        print(f"Indices shape: {indices.shape}")
        print(f"Values shape: {values.shape}")

        # Compute weights based on distances
        with np.errstate(divide='ignore', invalid='ignore'):
            weights = 1 / distances ** power
            weights[distances == 0] = np.inf  # Handle zero distances

        weights /= np.sum(weights, axis=1)[:, None]

        # Check the shapes again
        print(f"Weights shape: {weights.shape}")
        print(f"Indexed Values shape: {values[indices].shape}")

        # Compute interpolated values
        interpolated_values = np.sum(weights * values[indices], axis=1)

        return interpolated_values

