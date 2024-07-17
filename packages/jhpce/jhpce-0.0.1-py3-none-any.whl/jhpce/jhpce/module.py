from io import StringIO
import os
import pandas as pd
import paramiko 
## pip install GitPython to install this
import git

class jhpce():
    # Class for connecting to jhpce
    # Currently only connects to jhpce01
    def __init__(self,  username, pkey):
        self.username = username
        self.pkey = pkey
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect("jhpce03.jhsph.edu", username = self.username, pkey = self.pkey)
        self.local_dir = os.getcwd()
        self.remote_dir = "/users/" + username + "/"
        self.local_remote_mappings = {}        

    ##############################################################
    ## Connection commands
    ##############################################################
    def close(self):
        self.ssh.close()

    ## if the connection gets closed
    def reconnect(self, address = "jhpce03.jhsph.edu"):
        self.ssh.connect(address, username = self.username, pkey = self.pkey)                      

    ##############################################################
    ## Local commands
    ##############################################################
    def local_ls(self, opts = "-alh", pandas = True, print_results = True):
        if pandas:
            cmd = "ls -alh "
        else :
            cmd = "ls " 


    def local_set_dir(self, path):
        if os.path.isdir(path):
            self.local_dir = path
        else :
            print("Path does not exist " + path)

    ##############################################################
    ## Remote commands
    ##############################################################
    def remote_set_dir(self, subdir = "", fullpath = ""):
        if subdir != "":            
            if self.remote_dircheck(subdir, print_results = False):
                print("Success")
                self.remote_dir = self.remote_dir + subdir + "/"
            else :
                print("Remote path does not exist " + path)
        elif fullpath != "":
            if self.remote_dircheck(fullpath, print_results = False):
                print("Success")
                self.remote_dir = fullpath
            else :
                print("Remote path does not exist " + path)
        else:
            print("One of subdir or full path must be specified")
            
                    
    def remote_ls(self, opts = "-alh", return_as_pd = True, print_results = False):
        ## Force alh if returning as pd
        if return_as_pd:
            cmd = "ls -alh "
        else :
            cmd = "ls " 

        stdin, stdout, stderr = self.ssh.exec_command(cmd + opts + " " + self.remote_dir)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        
        if print_results: print(stdout)

        if return_as_pd :
            return pd.read_csv(StringIO(stdout), sep = "\s+",  skiprows = 1,  header = None)    
        
    ### checks if a remote directory is present
    def remote_dircheck(self, path, print_results = True):
        cmd = "test -d " + path + " && echo 1"
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        
        if stdout.readline() == "1\n":
            if print_results: print("Directory exists on jhpce")
            rval = True
        else :
            if print_results: print("Directory does not exist on jhpce")
            rval = False
        return rval
    
    ### Writes a file on the remote
    def remote_touch(self, text, filename, path = ""):
        sftp = self.ssh.open_sftp()
        if path == "":
            path = self.remote_dir
            # Open the remote file for writing (this will create the file if it doesn't exist)
        with sftp.file(path + "/" + filename, 'w') as remote_file:
            # Write the string content to the file
            remote_file.write(text)
        
        
    
    ##############################################################
    ## Git commands
    ##############################################################
    ### Allows you to change the director of the get repo
    def local_set_repo(self, path):
        if os.path.isdir(path):
            self.local_repo = git.Repo(path)
        else :
            print("Path does not exist " + path)
    def local_git_pull(self, ):
        ## Assumes you're in the correct local directory
        os.system("git pull")    
    def local_git_push(self, branch = "main"):
        os.system("git push origin " + branch)
    def local_git_origin(self):        
        return [r.url for r in self.local_repo.remotes][0]
    def remote_git_pull(self):
        cmd = "cd " + self.remote_dir + "; git pull"
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        print(stdout)
        print(stderr)

    ##############################################################
    ## Slurm commands            
    ##############################################################
    def remote_squeue(self, opts = "", print_results = False, pandas = True):
        cmd = "squeue " + opts
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if print_results:
            print(stdout)
        if pandas :
            ## The white space gets confused for this case
            stdout = stdout.replace("(launch failed requeued held)", "(launch_failed_requeued_held)")
            rval = pd.read_table(StringIO(stdout), delim_whitespace=True)
        else :
            rval = {"stdout" : stdout, "stderr" : stderr}

        return rval
    
    def remote_sinfo(self, opts = "", print_results = False, pandas = True):
        cmd = "sinfo " + opts
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if print_results:
            print(stdout)
        if pandas :
            rval = {"stdout" : pd.read_table(StringIO(stdout), delim_whitespace=True)}
        else :
            rval = {"stdout" : stdout, "stderr" : stderr}

        return rval

    def remote_sstat(self, jobid, opts = "", print_results = False, pandas = True):
        cmd = "sstat " + opts + " " + jobid
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if print_results:
            print(stdout)
        if pandas :
            rval = pd.read_table(StringIO(stdout), delim_whitespace=True)
        else :
            rval = {"stdout" : stdout, "stderr" : stderr}

        return rval
    
    def remote_sbatch(self, script, opts = "", print_results = False):
        cmd = "cd " + self.remote_dir + "; " + "sbatch " + opts + " " + script
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if print_results:
            print(stdout)
        rval = {"stdin": stdin, "stdout" : stdout, "stderr" : stderr}
        return rval
    
    def remote_scancel(self, jobid, opts = "", print_results = False):
        cmd = "scancel " + opts + " " + jobid
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if print_results:
            print(stdout)
        rval = {"stdout" : stdout, "stderr" : stderr}
        return rval
    
    def remote_sacct(self, opts = "", print_results = False, pandas = True):
        cmd = "sacct " + opts + " " 
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        if print_results:
            print(stdout)
        if pandas :
            rval = pd.read_table(StringIO(stdout), delim_whitespace=True)
        else :
            rval = {"stdout" : stdout, "stderr" : stderr}

        return rval
