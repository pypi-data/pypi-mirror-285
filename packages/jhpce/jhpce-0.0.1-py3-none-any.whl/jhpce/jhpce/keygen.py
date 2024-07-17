import paramiko
from getpass import getpass
import socket

#writes a private key to a file in the formate JHPCE wants
#filename is the file and path, typically ~/.ssh/keyname
#password is the password for the key and is required
def keygen(filename = "id_jhpce", save_to_file = True, send_to_ak = True) :
    key = paramiko.RSAKey.generate(4096)
    print("Enter a password for your private key")
    print("Note in vs code the input prompts are sent to the command pallette at the top")
    password = getpass("Enter a private key password")
    if save_to_file:
        key.write_private_key_file(filename, password = password)
        f = open(filename+".pub", "w")
        f.write("ssh-rsa " + key.get_base64())
        f.close()
        print("Private key written to " + filename)    
        print("Public key written to " + filename + ".pub") 
    if send_to_ak:
        print("We will now paste your key into your authorized keys file on jhpce")
        print("Make sure that you have your two factor authentication ready")
        print("First enter your username, then password, then 2FA code")
        host = "jhpce03.jhsph.edu"

        ## establish the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, 22))
        ## create the transport object
        ts = paramiko.Transport(sock)   
        ts.start_client(timeout=60)
        print("You will be prompted for your username, password and 2FA")

        def handler(title, instructions, prompt_list):
            resp = []  # Initialize the response container
            ## This is specific to how JHPCE login is currently done    
            for p in prompt_list:
                if str(p) == "('Password: ', False)":
                    resp.append(password)
                elif str(p) == "('Verification code: ', False)":
                    resp.append(otp)
            return tuple(resp)

        username = input("username")
        password = getpass("jhpce password")
        otp = input("verification code")
        ts.auth_interactive(username, handler)
        
        ### The following works, but puts out password as plain text
        ### too insecure to use
        ###ts.auth_interactive_dumb(username)
        ## Assuming that worked start posting the key
        channel = ts.open_session()
        # Execute the command to check if the .ssh directory exists
        print("checking for remote .ssh directory")
        channel.exec_command('if [ -d ~/.ssh ]; then echo ".ssh Directory exists"; else echo ".ssh Directory does not exist, creating"; fi')
        output = channel.recv_exit_status()
        if output == 0:
            print("Directory exists")
        else:
        # Execute the command to create the .ssh directory
            channel = ts.open_session()
            channel.exec_command('mkdir ~/.ssh')
            channel = ts.open_session()
            channel.exec_command('chmod 700 ~/.ssh')
            print(".ssh directory created and permissions set")

        channel = ts.open_session()
        print("Writing key to authorized_keys file")
        channel.exec_command('echo "ssh-rsa ' + key.get_base64() + '" >> ~/.ssh/authorized_keys')
        print("FINISHED. Make sure to save your pulbic and private key files")
        print("They are in the current working directory as " + filename + " and " + filename + ".pub")
        channel.close()
        ts.close()           
        
    #print("Here is your public key which should be on the authorized_keys file on JHPCE")
    #print("ssh-rsa " + key.get_base64())
    return key

## Recommended way to load the password is using getpass
def loadkey(filename):
    from getpass import getpass
    password = getpass()
    return paramiko.RSAKey.from_private_key_file(filename, password)


def colabgetkey(secret_id):
    from getpass import getpass
    import io
    ## Note this is not included in requirements since it
    ## only is useful on colab
    from google.colab import userdata
    keyfile = io.StringIO()
    keyfile.write(userdata.get(secret_id))
    keyfile.seek(0)
    return paramiko.RSAKey.from_private_key(keyfile, getpass())

