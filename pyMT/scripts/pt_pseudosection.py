import pyMT.data_structures as WSDS
import matplotlib.pyplot as plt
import numpy as np
import e_colours.colourmaps as cm
import pyMT.utils as utils


def generate_ellipse(phi):
            jx = np.cos(np.arange(0, 2 * np.pi, np.pi / 30))
            jy = np.sin(np.arange(0, 2 * np.pi, np.pi / 30))
            phi_x = phi[0, 0] * jx + phi[0, 1] * jy
            phi_y = phi[1, 0] * jx + phi[1, 1] * jy
            return phi_x, phi_y


cmap = cm.jet_plus(64)
# listfile = r'C:\Users\eric\phd\Kilauea\ConvertedEDIs\2018-517\allsites.lst'
# listfile = r'C:\Users\eric\phd\Kilauea\ConvertedEDIs\all\allsites.lst'
listfile = r'C:\Users\eric\phd\Kilauea\ConvertedEDIs\all\515-520.lst'
# datafile = r'C:\Users\eric\Documents\MATLAB\MATLAB\Inversion\Test_Models\dimensionality\synthLayer.data'
data = WSDS.RawData(listfile=listfile)
normalize = 1
fill_param = 'phi_2'
periods = list(data.narrow_periods.keys())
scale = np.sqrt((len(data.site_names) - 1) ** 2 +
                (np.log10(np.max(periods)) -
                 np.log10(np.min(periods))) ** 2)
periods = []
loc = []
X = []
Y = []
fill_vals = []
ellipses = []
for ii, site_name in enumerate(data.site_names):
    site = data.sites[site_name]
    for jj, period in enumerate(site.periods):
        periods.append(np.log10(period))
        loc.append(ii)
        phi_x, phi_y = generate_ellipse(site.phase_tensors[jj].phi)
        phi_x, phi_y = (1000 * phi_x / site.phase_tensors[jj].phi_max,
                        1000 * phi_y / site.phase_tensors[jj].phi_max)
        radius = np.max(np.sqrt(phi_x ** 2 + phi_y ** 2))
        # if radius > 1000:
        phi_x, phi_y = [(scale / (radius * 100)) * x for x in (phi_x, phi_y)]
        # ellipses.append([np.log10(period) - phi_x, ii - phi_y])
        ellipses.append([ii - phi_x, np.log10(period) - phi_y])
        fill_vals.append(getattr(data.sites[site_name].phase_tensors[jj], fill_param))
xticks = np.arange(0, loc[-1], 24)
xtick_labels = [str(x) for x in np.arange(501, 531)]

fill_vals = np.array(fill_vals)
if fill_param in ['phi_max', 'phi_min', 'det_phi', ' phi_1', 'phi_2', 'phi_3']:
    lower, upper = (0, 90)
elif fill_param in ['Lambda']:
    lower, upper = (np.min(fill_vals), np.max(fill_vals))
elif fill_param == 'beta':
    lower, upper = (-10, 10)
elif fill_param in ['alpha', 'azimuth']:
    lower, upper = (-90, 90)
fill_vals = np.rad2deg(np.arctan(fill_vals))
fill_vals[fill_vals > upper] = upper
fill_vals[fill_vals < lower] = lower
norm_vals = utils.normalize_range(fill_vals,
                                  lower_range=lower,
                                  upper_range=upper,
                                  lower_norm=0,
                                  upper_norm=1)


def plot_it():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for ii, ellipse in enumerate(ellipses):
        ax.fill(ellipse[0], ellipse[1],
                color=cmap(norm_vals[ii]),
                zorder=0)
    fake_vals = np.linspace(lower, upper, len(fill_vals))
    fake_im = ax.scatter(loc,
                         periods,
                         c=fake_vals, cmap=cmap)
    fake_im.set_visible(False)
    cb = plt.colorbar(mappable=fake_im)
    cb.set_label(fill_param,
                 rotation=270,
                 labelpad=20,
                 fontsize=18)
    plt.xlabel('Hour')
    plt.ylabel(r'$\log_{10}$ Period (s)')
    plt.show()


plot_it()
# def plot_phase_tensor(data, normalize=True, fill_param='Beta'):
        # def generate_ellipse(phi):
        #     jx = np.cos(np.arange(0, 2 * np.pi, np.pi / 30))
        #     jy = np.sin(np.arange(0, 2 * np.pi, np.pi / 30))
        #     phi_x = phi[0, 0] * jx + phi[0, 1] * jy
        #     phi_y = phi[1, 0] * jx + phi[1, 1] * jy
        #     return phi_x, phi_y
        # ellipses = []
        # if fill_param != 'Lambda':
        #     fill_param = fill_param.lower()
        # # if fill_param == 'azimuth':
        # #     cmap = cm.hsv()
        # # else:
        # cmap = cm.jet()
        # X_all, Y_all = self.site_locations['all'][:, 0], self.site_locations['all'][:, 1]
        # scale = np.sqrt((np.max(X_all) - np.min(X_all)) ** 2 +
        #                 (np.max(Y_all) - np.min(Y_all)) ** 2)
        # for ii, site_name in enumerate(self.site_names):
        #     site = self.site_data[data_type].sites[site_name]
        #     phi_x, phi_y = generate_ellipse(site.phase_tensors[period_idx].phi)
        #     X, Y = X_all[ii], Y_all[ii]
        #     phi_x, phi_y = (1000 * phi_x / site.phase_tensors[period_idx].phi_max,
        #                     1000 * phi_y / site.phase_tensors[period_idx].phi_max)
        #     radius = np.max(np.sqrt(phi_x ** 2 + phi_y ** 2))
        #     # if radius > 1000:
        #     phi_x, phi_y = [(5 * scale / (radius * 100)) * x for x in (phi_x, phi_y)]
        #     ellipses.append([Y - phi_x, X - phi_y])
        # fill_vals = np.array([getattr(self.site_data[data_type].sites[site].phase_tensors[period_idx],
        #                               fill_param)
        #                       for site in self.site_names])
        # if fill_param in ['phi_max', 'phi_min', 'det_phi', ' phi_1', 'phi_2', 'phi_3']:
        #     lower, upper = (0, 90)
        # elif fill_param in ['Lambda']:
        #     lower, upper = (np.min(fill_vals), np.max(fill_vals))
        # elif fill_param == 'beta':
        #     lower, upper = (-10, 10)
        # elif fill_param in ['alpha', 'azimuth']:
        #     lower, upper = (-90, 90)
        # fill_vals = np.rad2deg(np.arctan(fill_vals))
        # fill_vals[fill_vals > upper] = upper
        # fill_vals[fill_vals < lower] = lower
        # norm_vals = utils.normalize_range(fill_vals,
        #                                   lower_range=lower,
        #                                   upper_range=upper,
        #                                   lower_norm=0,
        #                                   upper_norm=1)
        # for ii, ellipse in enumerate(ellipses):
        #     self.window['axes'][0].fill(ellipse[0], ellipse[1],
        #                                 color=cmap(norm_vals[ii]),
        #                                 zorder=0)
        # fake_vals = np.linspace(lower, upper, len(fill_vals))
        # fake_im = self.window['axes'][0].scatter(self.site_locations['all'][:, 1],
        #                                          self.site_locations['all'][:, 0],
        #                                          c=fake_vals, cmap=cmap)
        # fake_im.set_visible(False)
        # cb = self.window['colorbar'] = self.window['figure'].colorbar(mappable=fake_im)
        # cb.set_label(fill_param,
        #              rotation=270,
        #              labelpad=20,
        #              fontsize=18)
