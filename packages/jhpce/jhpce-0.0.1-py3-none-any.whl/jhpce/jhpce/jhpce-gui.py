import streamlit as st
import module

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["info", "load", "remote", "local", "sync", "SGE"])


with tab0:
    st.markdown("""## Information
This tool is for working locally and submitting / checking on jobs on JHPCE. First, make sure that you have passwordless logins setup. Secondly, the script currently assumes both the remote and local directories are connected to the same github upstream repository. Then:

1. Click on the load tab to establish a connection
2. Set / check remote directories 
3. Set / check local directory
4. Sync via github
5. Check on / submit jobs using the SGE tab
""")

########################################################################
### Loading the connection
with tab1:
    st.write("Enter your credentials then press connect / reconnect")

    def establish_connection():
        st.session_state['username'] = username
        st.session_state['pkey'] = pkey
        st.session_state['con'] = module.jhpce(username = username, pkey = pkey)
        st.session_state['live'] = True
        

    username = st.text_input('Username', "bcaffo")
    pkey = st.text_input("Full path to your key", "/home/bcaffo/.ssh/id_rsa")
    st.button('connect / reconnect', on_click = establish_connection)


    if 'live' in st.session_state:
        if st.session_state['live']: 
            st.header("✅")
        else :
            st.header("❌")
    else :
        st.header("❌")
    
    
        
########################################################################
### Setting the remove dir
with tab2:
    if 'live' in st.session_state:
        if st.session_state['live']: 
            st.header("✅")
        else :
            st.header("❌")
    else :
        st.header("❌")


    st.write("Set your remote working directory")
    remote_dir = st.text_input("remote directory")

    if st.button('check remote'):
        if st.session_state['live']:
            out = st.session_state['con'].remote.dircheck(remote_dir)

            if out:
                st.write("✅ directory exists on jhpce")
            else :
                st.write("❌ directory does not exist")
        else:
            st.write('Please establish connection')

    if st.button('cd remote'):
        if st.session_state['live']:            
            out = st.session_state['con'].remote.set_dir(remote_dir)
            if not out:
                st.session_state['remote_dir'] = remote_dir
                st.write("❌ directory does not exist")
        else:
            st.write('Please establish connection')

            
    if 'live' in st.session_state:
        if st.session_state['live']:
            st.write("Directory listing for remote working directory:")
            st.write(st.session_state['con'].remote.dir)
            st.write(st.session_state['con'].remote.ls(return_as_pd = True, print_results = False))
        else:
            st.write('Please establish connection')
    

########################################################################
### Setting the local dir
with tab3:
    if 'live' in st.session_state:
        if st.session_state['live']: 
            st.header("✅")
        else :
            st.header("❌")
    else :
        st.header("❌")
    st.write("Set your local working directory")
    local_dir = st.text_input("local directory")


    if st.button('cd local'):
        if st.session_state['live']:            
            out = st.session_state['con'].local.set_dir(local_dir)
            if not out:
                st.session_state['local_dir'] = local_dir
                st.write("❌ directory does not exist")
        else:
            st.write('Please establish connection')


    if 'live' in st.session_state:
        if st.session_state['live']:
            st.write("Directory listing for local working directory:")
            st.write(st.session_state['con'].local.dir)
            st.write(st.session_state['con'].local.ls())
        else:
            st.write('Please establish connection')

with tab4:
    st.header("sync")
            
with tab5:
    if 'live' in st.session_state:
        if st.session_state['live']: 
            st.header("✅")
        else :
            st.header("❌")
    else :
        st.header("❌")

        
    if st.button('qstat'):
        if st.session_state['live']:            
            out = st.session_state['con'].remote.qstat()
            if out is None :
                st.write("No current jobs")
            else :
                st.write(out)
        else:
            st.write('Please establish connection')



