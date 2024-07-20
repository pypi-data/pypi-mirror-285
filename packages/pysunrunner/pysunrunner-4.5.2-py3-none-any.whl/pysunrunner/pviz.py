import numpy as np
import matplotlib.pyplot as plt

def plot_equatorial_cut(data, r_coords, t_coords, p_coords, ax, cmap = None, title = None, r_scale = False, log_scale = False, 
    zmin = None, zmax = None):
    """
    Function to plot the equatorial cut.

    Parameters:
    D: PLUTO 3D array of data values.
    r_coords: array representing the r grid
    t_coords: array representing the theta grid
    p_coords: array representing the phi grid
    cmap: colormap name
    title: plot title
    r_scale (logical): if True scaled data is plotted (x R^2)
    log_scale (logical): if True log10 of data is plotted
    zmin (scalar): Minumum value for color scaling
    zmax (scalar): Maximum value for color scaling
 
    **Outputs**:
    ax: subplot with equitorial cut of data
    """

    if cmap is None:
        cmap = 'rainbow'
    if zmin is None:
        zmin = np.min(data)
    if zmax is None:
        zmax = np,max(data)
    if title is None:
        title = ''

    # Convert from co-latitude to latitude
    t_coords = np.pi/2 - t_coords
    # calculate R^2
    if (r_scale):
        r2_coords = np.multiply(r_coords, r_coords)

    # Create a meshgrid for spherical coordinates
    phi_grid, r_grid = np.meshgrid(p_coords, r_coords)


    # Find the index where theta is closest to 0 (equatorial plane)

    theta_equatorial_index = np.argmin(np.abs(t_coords - 0))

    tmp = data[:,theta_equatorial_index,:]

    # Transpose
    tmp = tmp.T

    if r_scale:
        tmp = np.multiply(tmp, r2_coords)

    if log_scale:
        tmp = np.log10(tmp)    

    Z = tmp.T
    c = ax.pcolormesh(phi_grid, r_grid, Z, shading='auto', cmap=cmap, vmin = zmin, vmax = zmax)
    ax.set_title(title)
    ax.grid(False, axis ='y')  # Remove R grid
    ax.grid(False, axis ='x')  # Remove angle grid
    ax.set_ylim(0, np.max(r_coords))
    ax.set_yticks([]) # remove the R labels  (remove line if we want to keep it)    
    colorbar = plt.colorbar(c, ax=ax, orientation='horizontal', shrink = 0.5, aspect = 20)

    return ax


def plot_phi_cut(data, r_coords, t_coords, p_coords, ax, phi_cut = np.pi, cmap = None, title = None, r_scale = False, log_scale = False, 
    zmin = None, zmax = None):
    """
    Function to plot phi cut.

    Parameters:
    D: PLUTO 3D array of data values.
    r_coords: array representing the r grid
    t_coords: array representing the theta grid
    p_coords: array representing the phi grid
    phi_cut: angle in radians for phi_cut, default is meridonial
    cmap: colormap name
    title: plot title
    r_scale (logical): if True scaled data is plotted (x R^2)
    log_scale (logical): if True log10 of data is plotted
    zmin (scalar): Minumum value for color scaling
    zmax (scalar): Maximum value for color scaling
 
    **Outputs**:
    ax: subplot with equitorial cut of data
    """

    if cmap is None:
        cmap = 'rainbow'
    if zmin is None:
        zmin = np.min(data)
    if zmax is None:
        zmax = np,max(data)
    if title is None:
        title = ''

    # Convert from co-latitude to latitude
    t_coords = np.pi/2 - t_coords

    # calculate R^2
    if (r_scale):
        r2_coords = np.multiply(r_coords, r_coords)

    # Create a meshgrid for theta and R
    t_grid, r_grid = np.meshgrid(t_coords, r_coords)

    # Find the index where phi is to phi_cut

    phi_index = np.argmin(np.abs(p_coords - phi_cut))

    tmp = data[:,:,phi_index]

    # Transpose
    tmp = tmp.T

    if r_scale:
        tmp = np.multiply(tmp, r2_coords)

    if log_scale:
        tmp = np.log10(tmp)    

    Z = tmp.T
    c = ax.pcolormesh(t_grid, r_grid, Z, shading='auto', cmap=cmap, vmin = zmin, vmax = zmax)
    ax.set_title(title)
    ax.grid(False)
    ax.set_thetalim(-np.pi / 2, np.pi / 2)
    ax.set_xticks([-np.pi/2, -np.pi/4,0,np.pi/4,np.pi/2])
    colorbar = plt.colorbar(c, ax=ax, orientation='horizontal', shrink = 0.5, aspect = 20, pad = 0.05)

    return ax

def plot_slice(data, r_coords, t_coords, p_coords, ax, r_cut = None, theta_cut = np.pi/2.0, phi_cut = np.pi, cmap = None, title = None, 
    xlabel = 'R (AU)', ylabel = 'V (km s$^{s-1}$)', r_scale = False, log_scale = False, ymin = None, ymax = None):
    """
    Function to plot 1-D slices

    Parameters:
    data: PLUTO 3D array of data values.
    r_coords: array representing the r grid
    t_coords: array representing the theta grid
    p_coords: array representing the phi grid
    r_cut: distance in AU for an r-cut, if None data plotted as a function of r
    theta_cut: angle in radians for a theta-cut, default is equatorial, if None cuts are plotted as a function of theta
    phi_cut: angle in radians for phi-cut, default is meridonial, if None cuts are plotted as a function of phi
    cmap: colormap name
    title: plot title
    xlabel: x-axis label
    ylabel: y-axis label
    r_scale (logical): if True scaled data is plotted (x R^2)
    log_scale (logical): if True log10 of data is plotted
    ymin (scalar): Minumum y-axis value for plot
    ymax (scalar): Maximum vy-axis value for plot
 
    **Outputs**:
    ax: A plot with one or more slices
    """

    if cmap is None:
        cmap = 'rainbow'

    if title is None:
        title = ''
    
    # Convert from co-latitude to latitude
    t_coords = np.pi/2 - t_coords
    theta_cut = np.pi/2 - theta_cut


    # for all of these need to also define slice_dim - it can be either 0 or 1 
    
    if r_cut is None:
        theta_cut = np.array(theta_cut)
        phi_cut = np.array(phi_cut)
        theta_cut = np.atleast_1d(theta_cut)
        phi_cut = np.atleast_1d(phi_cut)
        slice_dim = 1
        if len(theta_cut) == 1:
            theta_index = np.argmin(np.abs(t_coords - theta_cut))
            data_2d = data[:,theta_index,:]
            slice_index = np.array([np.argmin(np.abs(p_coords - phi)) for phi in phi_cut])
            slice_val = p_coords[slice_index]
        else:
            phi_index = np.argmin(np.abs(p_coords - phi_cut))
            data_2d = data[:,:,phi_index]
            slice_index = np.array([np.argmin(np.abs(t_coords - theta)) for theta in theta_cut])
            slice_val = t_coords[slice_index]

        label = np.round(np.rad2deg(slice_val)).astype(int)
        x = r_coords

    if theta_cut is None:
        r_cut = np.array(r_cut)
        phi_cut = np.array(phi_cut)
        r_cut = np.atleast_1d(r_cut)
        phi_cut = np.atleast_1d(phi_cut)   
        if len(r_cut) == 1:
            r_index = np.argmin(np.abs(r_coords - r_cut))
            data_2d = data[r_index,:,:]
            slice_index = np.array([np.argmin(np.abs(p_coords - phi)) for phi in phi_cut])
            slice_dim = 1
            slice_val = p_coords[slice_index]
            label = np.round(np.rad2deg(slice_val)).astype(int)
        else:
            phi_index = np.argmin(np.abs(p_coords - phi_cut))
            data_2d = data[:,:,phi_index]
            slice_index = np.array([np.argmin(np.abs(r_coords - r)) for r in r_cut])
            slice_dim = 0
            slice_val = r_coords[slice_index]
            label = np.round(slice_val).astype(int)

        x = t_coords

    if phi_cut is None:
        r_cut = np.array(r_cut)
        theta_cut = np.array(theta_cut)
        r_cut = np.atleast_1d(r_cut)
        theta_cut = np.atleast_1d(theta_cut)
        slice_dim = 0    
        if len(r_cut) == 1:
            r_index = np.argmin(np.abs(r_coords - r_cut))
            data_2d = data[r_index,:,:]
            slice_index = np.array([np.argmin(np.abs(t_coords - theta)) for theta in theta_cut])
            slice_val = t_coords[slice_index]
            label = np.round(np.rad2deg(slice_val)).astype(int)
        else:
            theta_index = np.argmin(np.abs(t_coords - theta_cut))
            data_2d = data[:,theta_index,:]
            slice_index = np.array([np.argmin(np.abs(r_coords - r)) for r in r_cut])
            slice_val = r_coords[slice_index]
            label = np.round(slice_val).astype(int)

        x = p_coords


    if ymin is None:
        ymin = np.min(data_2d)
    if ymax is None:
        ymax = np.ax(data_2d)

    n_slice = len(slice_index)
    indices = np.linspace(0, 1, n_slice)
    # cmap = plt.colormaps[cmap)
    cmap = plt.cm.get_cmap(cmap)
    colors = cmap(indices)

 
    # calculate R^2
    if r_scale:
        r2_coords = np.multiply(r_coords, r_coords)

    if log_scale:
        data_2d = np.log10(data_2d)

    jcount = 0
    if slice_dim == 1:
        for islice in slice_index:
            y = data_2d[:,islice]
            ax.plot(x, y, color = colors[jcount], label = label[jcount])
            jcount = jcount + 1

    jcount = 0
    if slice_dim == 0:
        for islice in slice_index:
            y = data_2d[islice,:]
            if r_scale:
                y = np.multiply(y, r2_coords)
            ax.plot(x, y, color = colors[jcount], label = label[jcount])
            jcount = jcount + 1

# Set ymin and ymax
    plt.ylim(ymin, ymax)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()

    return ax
