import subprocess
import time
import os
import socket
import platform
import asyncio
from urllib.parse import urlparse, urlunparse, urljoin, quote
from evo_framework.core.evo_core_log.utility.IuLog import IuLog
from evo_framework.core.evo_core_text.utility.IuText import IuText
class IuSystem:
    @staticmethod
    def doCheck(filePath: str, requirementsPath: str = '/../requirements.txt'):
        print(filePath)
        current_path = os.path.dirname(os.path.abspath(filePath))
        
        file_name = os.path.basename(os.path.splitext(filePath)[0])
        print(file_name)

        print(current_path)
        env_var_name = f"CYBORGAI_{file_name.upper()}"
        print(env_var_name)

        if env_var_name not in os.environ:
            requirements_full_path =IuSystem.do_sanitize_path(f"{current_path}{requirementsPath}","") #os.path.join(current_path, requirementsPath)
            print(requirements_full_path)
            IuSystem.do_install_requirements(requirements_full_path)
            os.environ[env_var_name] = "1"
    
    @staticmethod
    def do_install_requirements(pathRequirements:str):
        safe_path = IuSystem.sanitize_path_space(pathRequirements)
        command = [
        "python",
        "-m",
        "pip",
        "install", 
        "-r",
        safe_path
        ]  
        IuSystem.do_exec(command)

    @staticmethod
    def sanitize_path_space(path):   
      if ' ' in path and not (path.startswith('"') and path.endswith('"')):
          return f'""{path}""'
      return path
          
    @staticmethod
    def do_exec(command):
        start_time = time.time()
        print("\ndo_exec:\n", " ".join(command), "\n")

        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) as proc:
                for line in proc.stdout:
                    print("Output:", line, end='')

                for line in proc.stderr:
                    print("Error:", line, end='')

            proc.wait()
        except Exception as exception:
            print("Exception occurred:", exception)
        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"\nTime Elapsed: {elapsed_time} seconds")
    
    @staticmethod
    async def do_exec_async(command):
        start_time = time.time()
        IuLog.doDebug(__name__, f"\ndo_exec:\n{command}\n")

        try:
            # Execute command through the shell with unbuffered output
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                bufsize=0  # Unbuffered
            )
            stdOutStr = ""
            stdOutErrStr = ""
            
            # Handle arbitrary output efficiently
            async def read_stream(stream, callback):
                partial_line = ''
                while True:
                    char = await stream.read(1)  # Read one byte at a time
                    if not char:  # EOF
                        if partial_line:
                            callback(partial_line)  # Process any remaining output
                        break
                    char = char.decode('utf-8', errors='replace')
                    if char == '\r' or char == '\n':
                        if partial_line:
                            callback(partial_line)  # Process the line
                            partial_line = ''  # Reset for the next line
                        if char == '\n':
                            continue  # Skip newline characters (after processing line)
                    else:
                        partial_line += char

            def print_stdout(line):
                nonlocal stdOutStr
                stdOutStr += line
                print("Output:", line, flush=True)

            def print_stderr(line):
                nonlocal stdOutErrStr
                stdOutErrStr += line
                print(line, flush=True)

            # Concurrently process stdout and stderr
            await asyncio.gather(
                read_stream(proc.stdout, print_stdout),
                read_stream(proc.stderr, print_stderr)
            )

            # Wait for the subprocess to finish
            await proc.wait()

        except Exception as exception:
            print("Exception occurred:", exception, flush=True)
            raise exception
           
        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            IuLog.doDebug(__name__, f"\nTime Elapsed: {elapsed_time} seconds")
            return stdOutStr, stdOutErrStr

        
    @staticmethod
    def do_exec_str(command_str:str):
        command = command_str.split(" ")
        IuSystem.do_exec(command)
        
    @staticmethod
    def do_sanitize_path(file_path,append_str="/"):
        absolute_path = os.path.abspath(file_path)
        return absolute_path + append_str
    
        
    @staticmethod
    def do_sanatize_url(url):
        parsed_url = urlparse(url)
        normalized_path = urljoin(parsed_url.path, '')
        sanitized_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            normalized_path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))

        # Encode special characters in the path
        sanitized_url = urljoin(sanitized_url, quote(normalized_path))

        return sanitized_url 
    @staticmethod
    def extract_details_from_url(url):
        # Split the URL by '/' and get the last part (filename)
        filename = url.split('/')[-1]

        # Split the filename by '.' to separate the name and extension
        name, extension = filename.split('.')

        return name, '.' + extension
    
    
    import socket

    @staticmethod
    def get_local_ip():
        try:
            # Creating a socket to connect to a public DNS server
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # Connect to the server
                s.connect(("8.8.8.8", 80))
                # Get the local IP address of the machine
                return s.getsockname()[0]
        except Exception as e:
            # In case of any exception, return the error
            return str(e)
    @staticmethod
    def get_os_info():
        # Getting the system's OS name, version, and architecture
        os_name = platform.system().lower()
        os_version = platform.version().lower()
        # architecture() returns a tuple, we're interested in the first element for this example
        os_architecture = platform.architecture()[0].lower()
        
        # You can add more OS details here
        processor = platform.processor()
        machine = platform.machine().lower()
        
        # Formatting the OS information into a string
        os_info = f"{os_name} {os_version} {os_architecture} Processor: {processor} Machine: {machine}"
        
        return os_info
    
    # --------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def doCreateDirs(directoryPath:str) :   
        if not os.path.exists(directoryPath):
            os.makedirs(directoryPath)  


 