
import matplotlib
import matplotlib.pyplot as plt
from dlm.origami.general import XY_SCALE, default_colours, default_colour_names
from dlm.common.myfuncs import circ_dist
from dlm.common.colormaps import get_colors, get_norm
import numpy as np

class Mixed:
    '''
    A class to represent a mixed pool of staples. The domains of the second staple pool
    partly overlap with the first pool.
    '''

    def __init__(self, pool1, pool2, rotation=0):
        """
        Initializes a Mixed object.

        Args:
            pool1 (Pool): The first staple pool.
            pool2 (Pool): The second staple pool.
            rotation (int, optional): The rotation value. Defaults to 0.
        """
        self._pool1 = pool1
        self._pool2 = pool2
        self._rotation = rotation
        self.rotatepool()
        self.nuc2point = self.get_nuc2point()
        self.add_paths()
        self.PoolName = self.pool1.PoolName + '_' + self.pool2.PoolName
        self.ActualName = self.pool1.ActualPoolName + '_' + self.pool2.ActualPoolName
    # end def

    def rotatepool(self):
        rotation = self.rotation
        pool = self.pool2
        num_nucs = pool.num_nucs
        for domain in pool.domains:
            n5p = (domain.n2 + rotation) % num_nucs
            n3p = (domain.n1 + rotation) % num_nucs
            domain.set_nucs(n5p, n3p) 
    # end def
    
    def get_nuc2point(self):
            """
            Returns a dictionary mapping nucleotide indices to their corresponding (x, y) coordinates.

            Returns:
                dict: A dictionary where the keys are nucleotide indices and the values are tuples of (x, y) coordinates.
            """
            pool = self.pool1
            num_nucs = pool.num_nucs
            pool.add_pos()
            nuc2point = {}
            for domain in pool.domains:
                #length = abs(domain.n2 - domain.n1) + 1
                length = circ_dist(domain.n1,domain.n2,num_nucs)
                step = abs(domain.rpos.x1 - domain.rpos.x2) / length
                x = domain.rpos.x1
                #y = (domain.v1.rpos.y1 + domain.v1.rpos.y2 + domain.v2.rpos.y1 + domain.v2.rpos.y2) /4
                #y = (domain.v2.rpos.y1 + domain.v1.rpos.y2) /2
                y = domain.v2.rpos.y1 + (domain.v2.rpos.y1-domain.rpos.y1)
                for i in range(0, length+1):
                    nuc = (domain.n1+i) % num_nucs
                    if domain.rpos.x1 < domain.rpos.x2: x+= step
                    else: x-= step
                    nuc2point[nuc] = (x,y)
            return nuc2point
    # end def

    def add_paths(self):
        pool = self.pool2
        nuc2point = self.nuc2point

        for domain in pool.domains:
            path_data = []
            start = (domain.n1)+1
            end = (domain.n2+1)-2
            x,y = nuc2point[start][0],nuc2point[start][1]
            path_data.append((matplotlib.path.Path.MOVETO, (x,y)))
            if domain.n1 < domain.n2:
                myrange = range(start, end)
            else:
                myrange = list(range(start, len(nuc2point)))
                myrange += list(range(0, end))
            for nuc in myrange:
                prev_x,prev_y = x,y
                x , y = nuc2point[nuc][0], nuc2point[nuc][1]
                #if prev_x != x and prev_y != y: x = prev_x
                if abs(prev_y-y) > XY_SCALE: x = prev_x
                path_data.append((matplotlib.path.Path.LINETO, (x,y)))
            codes, verts = zip(*path_data)
            domain.path = matplotlib.path.Path(verts, codes)
    # end def

    def draw(self,missing=None):
        rotation = self.rotation
        self.pool1.set_default_colors()
        self.pool2.set_default_colors()
        nrows, ncols = 1, 1
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharey=False, sharex=False)
        fig.set_size_inches(5 * ncols, 5 * nrows)
        self.pool1.draw_scaffold(ax, layout='rect')
        #self.pool1.draw_crossovers(ax, layout='rect')
        #self.pool1.draw_domains(ax, layout='rect')
        tickness = 0.5
        for crossover in self.pool1.crossovers:
            if crossover.type == 'l': continue
            alpha = crossover.alpha
            if crossover.colour == 'white': alpha = 0
            crossover.add_path()
            path = crossover.rpath
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth = tickness,
                                        linestyle = crossover.linestyle,
                                        edgecolor = crossover.colour,
                                        facecolor = None,
                                        fill = False,
                                        capstyle = 'round',
                                        #capstyle = 'projecting',
                                        alpha=alpha)
            ax.add_patch(patch)
        for domain in self.pool1.domains:
            alpha = 1
            if domain.colour == 'white': alpha = 0
            domain.add_path()
            path = domain.rpath
            patch = matplotlib.patches.PathPatch(path,
                                       linewidth=tickness,
                                       edgecolor=domain.colour,
                                       facecolor=None,
                                       fill=False,
                                       capstyle='round',
                                       # capstyle = 'projecting',
                                       alpha=alpha)
            ax.add_patch(patch)
        tickness = 1.0
        if missing == None:
            missing_name = 'M0'
            missing_doms = []
        else:
            missing_name = missing[0]
            missing_doms = missing[1]
        for domain in self.pool2.domains:
            alpha = 1
            if domain.ind in missing_doms:
                domain.colour = 'red'
                domain.thickness = 4
            else:
                domain.colour = 'red'
                domain.thickness = 0.0
            if domain.colour == 'white': alpha = 0
            path = domain.path
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth=domain.thickness,
                                        edgecolor=domain.colour,
                                        facecolor=None,
                                        fill=False,
                                        capstyle='round',
                                        #capstyle = 'projecting',
                                        alpha=alpha)
            start = (domain.n1)+1
            x1, y1 = self.nuc2point[start][0], self.nuc2point[start][1]
            end = (domain.n2+1)-2
            x2, y2 = self.nuc2point[end][0], self.nuc2point[end][1]
            centerx = (x1 + x2) / 2
            centery = (y1 + y2) / 2
            #ax.text(centerx, centery, str(domain.staple.ind), fontsize=4, color=domain.colour, weight='bold')
            ax.add_patch(patch)
        ax.autoscale()
        ax.set_aspect('equal', adjustable='box')
        ax.set_axis_off()
        axtitle = missing_name+'  $\mathcal{E} \\rightarrow \mathcal{R2}^{H}$'
        ax.set_title(axtitle, pad=15)
        from matplotlib.lines import Line2D
        custom_lines = [Line2D([0], [0], color=default_colours[0], lw=3)]
        custom_names = default_colour_names[:1]
        for n_domains in self.pool2.staple_types:
            custom_lines.append(Line2D([0], [0], color='red', lw=3))
            custom_names.append(default_colour_names[n_domains]+'$\in \mathcal{E}$')
        for n_domains in self.pool1.staple_types:
            custom_lines.append(Line2D([0], [0], color=default_colours[n_domains], lw=3))
            custom_names.append(default_colour_names[n_domains]+'$\in \mathcal{R2}^{H}$')
        legend_cols = 2
        ax.legend(custom_lines, custom_names,
                  loc='upper center', bbox_to_anchor=(0.5, 0), ncol=legend_cols,
                  fontsize='8', handlelength=0.5,
                  labelspacing=0.5, handletextpad=0.6,
                  frameon=False, columnspacing=1)
        fig.tight_layout()
        fig.savefig('Plots/Rect_'+self.ActualName+'_'+missing_name+'_'+str(rotation)+'.pdf')
        plt.close(fig)
    # end def

    def draw_labelled(self,ax,labelled1,labelled2):
        rotation = self.rotation
        self.pool1.set_grey_colors()
        self.pool2.set_grey_colors()
        self.pool1.draw_scaffold(ax, layout='rect')
        #self.pool1.draw_crossovers(ax, layout='rect')
        #self.pool1.draw_domains(ax, layout='rect')
        for domain in self.pool1.domains:
            domain.thickness = 0.1
            domain.alpha = 0.5
        for cr in self.pool1.crossovers:
            cr.thickness = 0.1
            cr.alpha = 0.5
        for domain in self.pool2.domains:
            domain.thickness = 0.1
            domain.alpha = 0.5
        for cr in self.pool2.crossovers:
            cr.thickness = 0.1
            cr.alpha = 0.5
        for labelled in labelled1:
            idx = labelled['id']
            staple = self.pool1.staples[idx]
            staple.colour = labelled['color']
            for domain in staple.domains:
                domain.colour = labelled['color']
                domain.thickness = 2.5
                domain.alpha = 1
            for cr in staple.crossovers:
                cr.colour = labelled['color']
                cr.thickness = 2.5
                cr.alpha = 1
        for labelled in labelled2:
            idx = labelled['id']
            staple = self.pool2.staples[idx]
            staple.colour = labelled['color']
            for domain in staple.domains:
                domain.colour = labelled['color']
                domain.thickness = 2.5
                domain.alpha = 1
            for cr in staple.crossovers:
                cr.colour = labelled['color']
                cr.thickness = 2.5
                cr.alpha = 1
        for crossover in self.pool1.crossovers:
            if crossover.type == 'l': continue
            crossover.add_path()
            path = crossover.rpath
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth = crossover.thickness,
                                        linestyle = crossover.linestyle,
                                        edgecolor = crossover.colour,
                                        facecolor = None,
                                        fill = False,
                                        capstyle = 'round',
                                        #capstyle = 'projecting',
                                        alpha=crossover.alpha)
            ax.add_patch(patch)
        for domain in self.pool1.domains:
            domain.add_path()
            path = domain.rpath
            patch = matplotlib.patches.PathPatch(path,
                                       linewidth=domain.thickness,
                                       edgecolor=domain.colour,
                                       facecolor=None,
                                       fill=False,
                                       capstyle='round',
                                       # capstyle = 'projecting',
                                       alpha=domain.alpha)
            ax.add_patch(patch)
        for domain in self.pool2.domains:
            path = domain.path
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth=domain.thickness,
                                        edgecolor=domain.colour,
                                        facecolor=None,
                                        fill=False,
                                        capstyle='round',
                                        #capstyle = 'projecting',
                                        alpha=domain.alpha)
            start = (domain.n1)+1
            x1, y1 = self.nuc2point[start][0], self.nuc2point[start][1]
            end = (domain.n2+1)-2
            x2, y2 = self.nuc2point[end][0], self.nuc2point[end][1]
            centerx = (x1 + x2) / 2
            centery = (y1 + y2) / 2
            #ax.text(centerx, centery, str(domain.staple.ind), fontsize=4, color=domain.colour, weight='bold')
            ax.add_patch(patch)
        ax.autoscale()
        ax.set_aspect('equal', adjustable='box')
        ax.set_axis_off()
        #axtitle = missing_name+'  $\mathcal{E} \\rightarrow \mathcal{R2}^{H}$'
        #ax.set_title(axtitle, pad=15)
        from matplotlib.lines import Line2D
        handlecolors = ['grey']
        handlecolors = handlecolors + [x['color'] for x in labelled1]
        handlecolors = handlecolors + [x['color'] for x in labelled2]
        handlenames = ['Scaffold']
        handlenames = handlenames + [x['name']+'$\in \mathcal{R2}^{H}$' for x in labelled1]
        handlenames = handlenames + [x['name']+'$\in \mathcal{E}$' for x in labelled2]
        custom_lines = []
        for hcolor in handlecolors:
            custom_lines.append(Line2D([0], [0], color=hcolor, lw=3))
        custom_names = handlenames
        legend_cols = 2
        ax.legend(custom_lines, custom_names,
                  loc='upper center', bbox_to_anchor=(0.5, 0), ncol=legend_cols,
                  fontsize='8', handlelength=0.5,
                  labelspacing=0.5, handletextpad=0.6,
                  frameon=False, columnspacing=1)
    # end def

    def draw_map(self, missing=None):
        self.cmap = 'coolwarm'
        self.cmap2 = plt.cm.coolwarm
        probs1 = [dom.Tm for dom in self.pool1.domains]
        probs2 = [dom.Tm for dom in self.pool2.domains]
        for_norm = probs1+probs2
        norm = get_norm(for_norm)
        colors1 = get_colors(probs1, norm, cmap=self.cmap2)
        colors2 = get_colors(probs2, norm, cmap=self.cmap2)
        self.pool1.set_domain_colors(colors1)
        self.pool2.set_domain_colors(colors2)

        rotation = self.rotation
        nrows, ncols = 1, 1
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharey=False, sharex=False)
        fig.set_size_inches(5 * ncols, 5 * nrows)
        self.pool1.draw_scaffold(ax, layout='rect')
        #self.pool1.draw_crossovers(ax, layout='rect')
        #self.pool1.draw_domains(ax, layout='rect')
        tickness = 1.5
        for domain in self.pool1.domains:
            alpha = 1
            if domain.colour == 'white': alpha = 0
            domain.add_path()
            path = domain.rpath
            patch = matplotlib.patches.PathPatch(path,
                                       linewidth=tickness,
                                       edgecolor=domain.colour,
                                       facecolor=None,
                                       fill=False,
                                       capstyle='round',
                                       # capstyle = 'projecting',
                                       alpha=alpha)
            ax.add_patch(patch)
        tickness = 1.0
        if missing == None:
            missing_name = 'M0'
            missing_doms = []
        else:
            missing_name = missing[0]
            missing_doms = missing[1]
        for domain in self.pool2.domains:
            alpha = 1
            if domain.ind in missing_doms:
                domain.colour = 'grey'
                domain.thickness = 2.5
            else:
                #domain.colour = 'red'
                domain.thickness = 1.5
            if domain.colour == 'white': alpha = 0
            path = domain.path
            patch = matplotlib.patches.PathPatch(path,
                                        linewidth=domain.thickness,
                                        edgecolor=domain.colour,
                                        facecolor=None,
                                        fill=False,
                                        capstyle='round',
                                        #capstyle = 'projecting',
                                        alpha=alpha)
            start = (domain.n1)+1
            x1, y1 = self.nuc2point[start][0], self.nuc2point[start][1]
            end = (domain.n2+1)-2
            x2, y2 = self.nuc2point[end][0], self.nuc2point[end][1]
            centerx = (x1 + x2) / 2
            centery = (y1 + y2) / 2
            #ax.text(centerx, centery, str(domain.staple.ind), fontsize=4, color=domain.colour, weight='bold')
            ax.add_patch(patch)

        sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=norm)
        sm.set_array([])
        cmin, cmax = np.nanmin(np.array(for_norm)), np.nanmax(np.array(for_norm))
        myticks = [cmin, cmax]
        myticklabels = ["{:.2f}".format(cmin), "{:.2f}".format(cmax)]
        cbar = fig.colorbar(sm, ax=ax, shrink=0.75, orientation='horizontal',
                            ticks=myticks, label=r'$T_M$')
        ax.autoscale()
        ax.set_aspect('equal', adjustable='box')
        ax.set_axis_off()

        fig.tight_layout()
        fig.savefig('Plots/Rect_'+self.ActualName+'_'+missing_name+'_'+str(rotation)+'.pdf')
        plt.close(fig)
    # end def

    def draw_maps_help(self,fig,ax,for_norm,norm,draw1,draw2,label=r'$T_M$'):
        self.pool1.draw_scaffold(ax, layout='rect')
        tickness = 1.5
        if draw1:
            for domain in self.pool1.domains:
                domain.add_path()
                path = domain.rpath
                patch = matplotlib.patches.PathPatch(path,
                                           linewidth=tickness,
                                           edgecolor=domain.colour,
                                           facecolor=None,
                                           fill=False,
                                           capstyle='round',
                                           # capstyle = 'projecting',
                                           alpha=1)
                ax.add_patch(patch)
        if draw2:
            for domain in self.pool2.domains:
                path = domain.path
                patch = matplotlib.patches.PathPatch(path,
                                            linewidth=tickness,
                                            edgecolor=domain.colour,
                                            facecolor=None,
                                            fill=False,
                                            capstyle='round',
                                            #capstyle = 'projecting',
                                            alpha=1)
                ax.add_patch(patch)
        sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=norm)
        sm.set_array([])
        cmin, cmax = np.nanmin(np.array(for_norm)), np.nanmax(np.array(for_norm))
        myticks = [cmin, cmax]
        cbar = fig.colorbar(sm, ax=ax, shrink=0.75, orientation='horizontal',
                            ticks=myticks, label=label)
        ax.autoscale()
        ax.set_aspect('equal', adjustable='box')
        ax.set_axis_off()
    # end def

    def draw_maps(self, missing=None):
        self.cmap = 'jet'
        self.cmap2 = plt.cm.jet
        rotation = self.rotation
        nrows, ncols = 2, 3
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharey=False, sharex=False)
        fig.set_size_inches(5 * ncols, 5 * nrows)


        ax = axs[0,0]
        probs2 = [dom.Tm for dom in self.pool2.domains]
        for_norm = probs2
        norm = get_norm(for_norm)
        colors2 = get_colors(probs2, norm, cmap=self.cmap2)
        self.pool2.set_domain_colors(colors2)
        self.draw_maps_help(fig,ax,for_norm,norm,draw1=False,draw2=True)

        ax = axs[0,1]
        probs1 = [dom.Tm for dom in self.pool1.domains]
        for_norm = probs1
        norm = get_norm(for_norm)
        colors1 = get_colors(probs1, norm, cmap=self.cmap2)
        self.pool1.set_domain_colors(colors1)
        self.draw_maps_help(fig,ax,for_norm,norm,draw1=True,draw2=False)

        ax = axs[0,2]
        probs1 = [dom.Tm for dom in self.pool1.domains]
        probs2 = [dom.Tm for dom in self.pool2.domains]
        for_norm = probs1+probs2
        norm = get_norm(for_norm)
        colors1 = get_colors(probs1, norm, cmap=self.cmap2)
        colors2 = get_colors(probs2, norm, cmap=self.cmap2)
        self.pool1.set_domain_colors(colors1)
        self.pool2.set_domain_colors(colors2)
        self.draw_maps_help(fig,ax,for_norm,norm,draw1=True,draw2=True)

        ax = axs[1,0]
        probs1 = [dom.Tm1 for dom in self.pool1.domains]
        for_norm = probs1
        norm = get_norm(for_norm)
        colors1 = get_colors(probs1, norm, cmap=self.cmap2)
        self.pool1.set_domain_colors(colors1)
        self.draw_maps_help(fig,ax,for_norm,norm,draw1=True,draw2=False, label = r'$\Delta T_M$')

        ax = axs[1,1]
        probs1 = [dom.Tm2 for dom in self.pool1.domains]
        for_norm = probs1
        norm = get_norm(for_norm)
        colors1 = get_colors(probs1, norm, cmap=self.cmap2)
        self.pool1.set_domain_colors(colors1)
        self.draw_maps_help(fig,ax,for_norm,norm,draw1=True,draw2=False, label = r'$\Delta T_M$')

        ax = axs[1,2]
        probs1 = [dom.Tma for dom in self.pool1.domains]
        for_norm = probs1
        norm = get_norm(for_norm)
        colors1 = get_colors(probs1, norm, cmap=self.cmap2)
        self.pool1.set_domain_colors(colors1)
        self.draw_maps_help(fig, ax, for_norm, norm, draw1=True, draw2=False, label = r'$\Delta T_M$')

        fig.tight_layout()
        fig.savefig('Plots/Rect_'+self.ActualName+'_'+str(rotation)+'.pdf')
        plt.close(fig)
    # end def

    def draw_frame(self, ax):
        """
        Draw the frame for a movie. This is called from Movie class.

        Parameters:
        - ax: The matplotlib Axes object on which to draw the frame.

        Returns:
        None
        """
        self.pool1.draw_scaffold(ax, layout='rect')
        for crossover in self.pool1.crossovers:
            if crossover.type == 'l': continue
            crossover.add_path()
            crossover.thickness = 8
            path = crossover.rpath
            patch = matplotlib.patches.PathPatch(path,
                                                 linewidth=crossover.thickness,
                                                 linestyle=crossover.linestyle,
                                                 edgecolor=crossover.colour,
                                                 facecolor=None,
                                                 fill=False,
                                                 alpha=crossover.alpha,
                                                 capstyle='round',
                                                 # capstyle = 'projecting',
                                                 )
            ax.add_patch(patch)
        for domain in self.pool1.domains:
            domain.thickness = 8
            domain.add_path()
            path = domain.rpath
            patch = matplotlib.patches.PathPatch(path,
                                                 linewidth=domain.thickness,
                                                 edgecolor=domain.colour,
                                                 facecolor=None,
                                                 fill=False,
                                                 capstyle='round',
                                                 # capstyle = 'projecting',
                                                 alpha=domain.alpha)
            ax.add_patch(patch)
        for domain in self.pool2.domains:
            domain.thickness = 5
            path = domain.path
            patch = matplotlib.patches.PathPatch(path,
                                                 linewidth=domain.thickness,
                                                 edgecolor=domain.colour,
                                                 facecolor=None,
                                                 fill=False,
                                                 capstyle='round',
                                                 # capstyle = 'projecting',
                                                 alpha=domain.alpha)
            ax.add_patch(patch)
        ax.autoscale()
        ax.set_aspect('equal', adjustable='box')
        ax.set_axis_off()
    # end def

    @property
    def pool1(self):
        return self._pool1
    # end def

    @property
    def pool2(self):
        return self._pool2
    # end def

    @property
    def rotation(self):
        return self._rotation