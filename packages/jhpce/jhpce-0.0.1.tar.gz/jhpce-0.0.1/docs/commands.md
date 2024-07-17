# Attributes
  - `local_rid` : Local working directory
  - 'remote_dir` : Working remote directory

# Commands

## Connections commands
- `jhpce` : Establish a connection to the JHPCE cluster
- `close` : Close the connection
- `reconnect` : Reconnect to the JHPCE cluster

## Local commands
- `local_set_dir` : Set the local directory

## Git commands
- `local_set_repo` : Set the local git repository
- `local_git_pull` : Pull from the local git repository
- `local_git_push` : Push to the local git repository
- `remote_set_repo` : Set the remote git repository
- `remote_git_pull` : Pull from the remote git repository
- `remote_git_push` : Push to the remote git repository

## Remote commands
- `remote_dircheck` : Check if a remote directory exists
- `remote_ls` : List the files in the remote directory
- `remote_set_dir` : Set the remote directory
- `remote_touch` : Send text to a file on the remote server

## Slurm commands
- `remote_squeue` : List the jobs in the queue
- `remote_sinfo` : List the nodes in the cluster
- `remote_sstat` : Get the status of a job    
- `remote_sbatch` : Submit a job
- `remote_scancel` : Cancel a job
- `remote_sacct` : Get the accounting of a job 
