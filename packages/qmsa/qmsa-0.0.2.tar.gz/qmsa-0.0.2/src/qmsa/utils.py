import numpy as np
def mesh_cartesian(num_points, factor=1,spacing=False):
    if type(num_points)==list:
        if len(num_points)==3:
            x = np.linspace(0, 1, num_points[0], endpoint=False)
            y = np.linspace(0, 1, num_points[1], endpoint=False)
            z = np.linspace(0, 1, num_points[2], endpoint=False)
        elif len(num_points)==1:
            x = np.linspace(0, 1, num_points[0], endpoint=False)
            y = np.linspace(0, 1, num_points[0], endpoint=False)
            z = np.linspace(0, 1, num_points[0], endpoint=False)

    elif type(num_points)==int:
        x = np.linspace(0, 1, num_points, endpoint=False)
        y = np.linspace(0, 1, num_points, endpoint=False)
        z = np.linspace(0, 1, num_points, endpoint=False)
    if spacing!=False:
        spacing = round(1/(len(x)*len(y)*len(z)),10)
        three_dim = np.array([[i, j,k,spacing] for i in x for j in y for k in z])
    else:
        three_dim = np.array([[i, j,k] for i in x for j in y for k in z])
    return (three_dim*factor)