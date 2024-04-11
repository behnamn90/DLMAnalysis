import matplotlib.pyplot as plt
from dlm.origami.pool import Pool
from dlm.origami.mixed import Mixed
from dlm.common.myfuncs import cd
import subprocess, os, warnings


def get_confs(trajfile):
    with open(trajfile,'r') as myfile:
        all = myfile.read()
    confs = all.split('}\ntime')
    return confs

def pool_names_match(pools, tops):
    """
    Check if the pool names match across the provided staple pool and the trajectory file.

    Args:
        pools (list): A list of pool objects.
        tops (list): A list of topology names from the trajectory file.

    Returns:
        bool: True if the pool names match the tops, False otherwise.
    """
    pool_names = [pool.ActualPoolName for pool in pools]
    return len(pool_names) == len(tops) and all(a == b for a, b in zip(pool_names, tops))

class Movie:
    """
    Represents a movie created from a trajectory file and staple pools.

    Args:
        staple_pools (list): A list of staple pools.
        path_to_traj (str): The path to the trajectory file.
        output_directory (str): The output directory for the movie.
        create_dir (bool, optional): Whether to create the output directory if it doesn't exist. Defaults to False.

    Raises:
        ValueError: If the pool names from the given staple pools do not match the trajectory file.
        FileNotFoundError: If the output directory does not exist and create_dir is set to False.

    Attributes:
        out_dir (str): The output directory.
        stepdir (str): The step directory.

    Methods:
        check_output_directory: Checks if the output directory exists and creates it if necessary.
        get_times: Retrieves the initial time and total time from the trajectory file.
        get_tops: Retrieves the top names from the trajectory file.
        set_pool_colors: Sets the colors for the staple pools.
        create_frames: Creates frames for the movie.
        create_const_movie: Creates a constant frame rate movie.
        create_timed_movie: Creates a movie with a specified scaling factor.
        create_unique_states: Creates frames for specific steps in the trajectory file.
    """

    def __init__(self, staple_pools, path_to_traj, output_directory, create_dir=False):
        self.out_dir, self.stepdir = self.check_output_directory(output_directory, create_dir)
        self.confs = get_confs(path_to_traj)
        self.initial_time, self.total_time = self.get_times()
        self.tops = self.get_tops()
        self.pools = staple_pools
        if not pool_names_match(self.pools, self.tops):
            raise ValueError('Pool names from the given staple pools do not match the trajectory file.')
        if len(self.pools)>1: 
            self.mixed = Mixed(pool1=self.pools[0],pool2=self.pools[1])
        self.set_pool_colors()

    def check_output_directory(self, output_directory, create_dir):
        """
        Checks if the output directory exists and creates it if necessary.

        Args:
            output_directory (str): The output directory.
            create_dir (bool): Whether to create the output directory if it doesn't exist.

        Returns:
            tuple: A tuple containing the output directory and the step directory.
        """
        if not os.path.exists(output_directory):
            if create_dir:
                os.makedirs(output_directory, exist_ok=True)
            else:
                raise FileNotFoundError('Output directory does not exist. Set create_dir=True to create it.')
        step_directory = '/'.join([output_directory,'Steps'])
        if not os.path.exists(step_directory): 
            os.makedirs(step_directory, exist_ok=True)
        return output_directory, step_directory

    def get_times(self):
        """
        Retrieves the initial time and total time from the trajectory file.

        Returns:
            tuple: A tuple containing the initial time and the total time.
        """
        conf = self.confs[0]
        sections = conf.split('{')
        lines = sections[0].split('\n')
        initial_time = lines[0].split('=')[1].strip()
        conf = self.confs[-1]
        sections = conf.split('{')
        lines = sections[0].split('\n')
        total_time = lines[0].split('=')[1].strip()
        return initial_time, total_time

    def get_tops(self):
        """
        Retrieves the topology names from the trajectory file.

        Returns:
            list: A list of topology names.
        """
        tops = []
        conf = self.confs[0]
        sections = conf.split('{')
        for section in sections[1:]:
            lines = section.split('\n')
            top = lines[0].strip()
            tops.append(top)
        return tops
    
    def set_pool_colors(self):
        """
        Sets the colors for the staple pools.
        """
        colours = ['blue', 'red']
        for i, pool in enumerate(self.pools):
            pool.add_pos()
            if len(self.pools)>1: pool.set_custom_color(colours[i])
            else: pool.set_default_colors()

    
    def create_frames(self):
        """
        Creates frames for the movie.
        """
        scaling = 6
        colours = ['blue','red']
        n_digits = len(str(len(self.confs)))
        times = []
        n_domains = {}
        average_dt = float(self.total_time) / len(self.confs)
        for top in self.tops: n_domains[top] = []
        for conf in self.confs:
            sections = conf.split('{')
            lines = sections[0].split('\n')
            step = lines[1].split('=')[1].strip()
            str_step = str(step)
            str_step = '0'*(n_digits-len(str_step)) + str_step
            framepath = self.stepdir + '/img' + str_step + '.png'
            #if os.path.exists(framepath): continue
            print(str_step)
            time = lines[0].split('=')[1].strip()
            times.append(float(time))
            nrows,ncols = 1,2
            fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharey=False, sharex=False)
            fig.set_size_inches(ncols*scaling*2, scaling)
            ax = axs[0]
            for i, section in enumerate(sections[1:]):
                lines = section.split('\n')
                top = lines[0].strip()
                domains = list(map(int,lines[2].split(' ')))
                try: crossovers = list(map(int, lines[3].split(' ')))
                except: crossovers = []
                n_domains[top].append(domains.count(1))
                ax.plot(times, n_domains[top], label=top, color=colours[i])
                ax.grid()
                ax.set_xlabel('Time / s')
                ax.set_ylabel('Bound Domains')
                ax.set_xlim(float(self.initial_time), float(time)+average_dt)
                ax.set_ylim(0,len(domains))

                self.pools[i].set_domain_alphas(domains)
                self.pools[i].set_crossover_alphas(crossovers)
            ax = axs[1]
            if len(self.pools)==1:
                self.pools[0].draw_scaffold(ax, layout='rect')
                self.pools[0].draw_crossovers(ax, layout='rect')
                self.pools[0].draw_domains(ax, layout='rect')
                ax.autoscale()
                ax.set_aspect('equal', adjustable='box')
                ax.set_axis_off()
            else:
                self.mixed.draw_frame(ax)
            fig.savefig(framepath)
            plt.close(fig)
        concat_file_string = 'ffconcat version 1.0\n'
        durations = [times[i]-times[i-1] for i in range(1,len(times))]
        for step, time in enumerate(times[:-1]):
            str_step = str(step)
            str_step = '0'*(n_digits-len(str_step)) + str_step
            concat_file_string += 'file ' + 'img' + str_step + '.png\n'
            concat_file_string += 'duration ' + str(durations[step]) + '\n'
        step = len(times)
        str_step = str(step)
        str_step = '0' * (n_digits - len(str_step)) + str_step
        concat_file_string += 'file ' + 'img' + str_step + '.png\n'
        with open(self.stepdir+'/in.ffconcat','w') as myfile:
            myfile.write(concat_file_string)

    def create_const_movie(self, name, screenTime=0):
        """
        Creates a constant frame rate movie.

        Args:
            name (str): The name of the movie.
            screenTime (int, optional): The screen time of the movie in seconds. Defaults to 0.
        """
        n_digits = len(str(len(self.confs)))
        if screenTime == 0: framerate = 5
        else: framerate = len(self.confs) / screenTime
        print('Creating '+name+'.mp4'+' | '+'FrameRate '+str(framerate)+' | '+'Length ~'+str(len(self.confs) / framerate))
        command = 'ffmpeg '
        command+= '-framerate ' + str(framerate) + ' '
        command+= '-i img%0'+str(n_digits)+'d.png '
        command += '-vcodec libx264 '
        command += '-acodec aac '
        command+= name+'.mp4'
        with cd(self.stepdir):
            subprocess.call(command, shell=True)

    def create_timed_movie(self, name, scaling):
        """
        Creates a movie with a specified scaling factor.

        Args:
            name (str): The name of the movie.
            scaling (int): The scaling factor.
        """
        if scaling == 0:
            command = 'ffmpeg '
            command += '-i in.ffconcat '
            command += '-vcodec libx264 '
            command += '-acodec aac '
            command += name + '.mp4'
        else:
            with open(self.stepdir+'/'+'in.ffconcat', 'r') as infile:
                instr = infile.read()
            lines = instr.split('\n')
            newlines = []
            for line in lines:
                if 'duration' in line:
                    duration = line.split(' ')[1]
                    newduration = "{:10.4f}".format(float(duration)/(scaling*1.))
                    newline = line.replace(duration,newduration)
                    newlines.append(newline)
                else:
                    newlines.append(line)
            newfilename = 'in'+str(scaling)+'.ffconcat'
            with open(self.stepdir+'/'+newfilename,'w') as outfile:
                outfile.write('\n'.join(newlines))
            command = 'ffmpeg '
            command += '-i '+newfilename+' '
            command += '-vcodec libx264 '
            command += '-acodec aac '
            command += name + '.m4v'
        with cd(self.stepdir):
            subprocess.call(command, shell=True)

    def create_unique_states(self):
        """
        Creates frames for specific steps in the trajectory file.
        """
        wantedsteps = [493,494,495,498,913,944,990,991,994,996,998,1000,1006]
        wantedsteps+= list(range(1013,1018,1))

        n_digits = len(str(len(self.confs)))
        times = []
        n_domains = {}
        for top in self.tops: n_domains[top] = []
        for conf in self.confs:
            sections = conf.split('{')
            lines = sections[0].split('\n')
            step = int(lines[1].split('=')[1].strip())
            if step in wantedsteps:
                str_step = str(step)
                str_step = '0'*(n_digits-len(str_step)) + str_step
                framepath = self.out_dir + '/HighRes' + str_step + '.png'
                #if os.path.exists(framepath): continue
                print(str_step)
                time = lines[0].split('=')[1].strip()
                times.append(float(time))
                nrows,ncols = 1,1
                fig, ax = plt.subplots(nrows=nrows, ncols=ncols, sharey=False, sharex=False)
                fig.set_size_inches(20, 12)
                for i, section in enumerate(sections[1:]):
                    lines = section.split('\n')
                    top = lines[0].strip()
                    domains = list(map(int,lines[2].split(' ')))
                    try: crossovers = list(map(int, lines[3].split(' ')))
                    except: crossovers = []
                    n_domains[top].append(domains.count(1))
                    self.pools[i].set_domain_alphas(domains)
                    self.pools[i].set_crossover_alphas(crossovers)#[k-1 for k in crossovers])
                    print(top,'dom:',domains)
                    print(top,'cr:',crossovers)
                if len(self.pools)==1:
                    self.pools[0].draw_scaffold(ax, layout='rect')
                    self.pools[0].draw_crossovers(ax, layout='rect')
                    self.pools[0].draw_domains(ax, layout='rect')
                    ax.autoscale()
                    ax.set_aspect('equal', adjustable='box')
                    ax.set_axis_off()
                else:
                    self.mixed.draw_frame(ax)
                #fig.subplots_adjust(left=0.3, bottom=0.2, right=0.7, top=0.8, wspace=0.1, hspace=-0.95)
                fig.tight_layout()
                fig.savefig(framepath)
                plt.close(fig)

if __name__ == '__main__':

    input_directory = '/Users/behnamnajafi/Code/DLM/DLMAnalysis/demo_input/movies/compete'
    output_directory = '/Users/behnamnajafi/Code/DLM/DLMAnalysis/demo_output/movies/compete'

    trajectory_path = input_directory + '/Trajectory.dat'
    topologies = ['RcUa','RcH']
    json_files = [input_directory + '/'+top+'.json' for top in topologies]
    pools = [Pool(json_file) for json_file in json_files]
    movie = Movie(pools, trajectory_path, output_directory, create_dir=True)
    movie.create_frames()
    movie.create_const_movie('const_movie')
