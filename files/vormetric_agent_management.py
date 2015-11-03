# 
# Copyright (C) 2015 British Telecom plc. - All Rights Reserved
# Author: Quang Hieu Vu
# Version: 1.0
# Date: July 15, 2015
#
 
import os, sys, stat
import subprocess
import platform
import logging

if sys.version_info >= (3,):
  import urllib.request as urllib2
  import urllib.parse as urlparse
else:
  import urllib2
  import urlparse

#input parameters
AGENT_DOWNLOAD_URL   = 'NONE'
SERVER_DNS           = 'NONE'
SERVER_IP            = 'NONE'
VM_DNS               = 'NONE'
GUARD_POINT          = 'NONE' 
GUARD_POINT_LIST     = []
DECRYPT_UPDATE_FLAG  = 'NONE'

#other supporting parameters
CONFIG_FOLDER        = 'NONE'
TMP_FOLDER           = 'NONE'
LOG_FILE             = 'NONE'
AGENT_FILE           = 'NONE'
SETUP_FILE           = 'NONE'
HOSTS_FILE           = 'NONE'

#show usage text
#*************************************************
def show_usage():
  print 'Usage: python vormetric_agent_management [install, activate, encrypt, decrypt, uninstall, help]'
#*************************************************

#notify error and show usage after that
#*************************************************
def show_error(error_message):
  print error_message
  show_usage()
  sys.exit(2)
#*************************************************

#*************************************************
def get_previous_command(command_file):
  try:
    cfile = open(command_file, 'r')
    command = cfile.readline()
    cfile.close()
    return command
  except:
    return 'NONE'
#*************************************************

#*************************************************
def update_command(command_file, command):
  cfile = open(command_file, "w")
  cfile.write(command)
  cfile.close()
#*************************************************

#set variables and parse inputs to determine running mode
#*************************************************
def parse_parameters(argv):
  global CONFIG_FOLDER
  global AGENT_FILE
  global TMP_FOLDER
  global LOG_FILE
  global SETUP_FILE
  global HOSTS_FILE
  global AGENT_DOWNLOAD_URL  
  global SERVER_DNS
  global SERVER_IP
  global GUARD_POINT
  global GUARD_POINT_LIST
  global DECRYPT_UPDATE_FLAG
  global VM_DNS
  
  #set variables
  if platform.system() == 'Windows':
    CONFIG_FOLDER = 'C:\\btconfigtest'
    LOG_FILE = CONFIG_FOLDER + '\\btconfig.log'
    COMMAND_FILE = CONFIG_FOLDER + '\\command.log'
    AGENT_FILE = 'C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\vmd\\bin\\vmd.exe'
    HOSTS_FILE = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
    TMP_FOLDER = 'C:\\tmpdir'
    SETUP_FILE = TMP_FOLDER + '\\fsagent.msi'
    if not (os.path.exists(TMP_FOLDER)):
      os.mkdir(TMP_FOLDER)    
  else:
    CONFIG_FOLDER = '/btconfigtest'   
    LOG_FILE = CONFIG_FOLDER + '/btconfig.log'
    COMMAND_FILE = CONFIG_FOLDER + '/command.log'
    AGENT_FILE = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd'
    SETUP_FILE = CONFIG_FOLDER + '/veefs.bin'
    HOSTS_FILE = '/etc/hosts'
    props_filename = CONFIG_FOLDER + '/general.properties'
  
  #get previous command
  pre_command = get_previous_command(COMMAND_FILE)

  #parse inputs
  if len(sys.argv) == 1:    
    show_error('Error: parameters are required')
  else:
    if sys.argv[1] == 'subscribe' and len(sys.argv) == 3:
      if pre_command == 'subscribe':      
        #to avoid duplication in running the command
        return 99
      else:
        VM_DNS = sys.argv[2]
        if len(VM_DNS) > 54:
          VM_DNS = VM_DNS[9:]
        update_command(COMMAND_FILE, 'subscribe')
      return 0
    elif sys.argv[1] == 'install' and len(sys.argv) == 6:
      AGENT_DOWNLOAD_URL = sys.argv[2]
      SERVER_IP = sys.argv[3]
      SERVER_DNS = sys.argv[4]
      VM_DNS = sys.argv[5]
      if len(VM_DNS) > 54:
        VM_DNS = VM_DNS[9:]
      return 1        
    elif sys.argv[1] == 'register' and len(sys.argv) == 4:
      SERVER_DNS = sys.argv[2]
      VM_DNS = sys.argv[3]
      if len(VM_DNS) > 54:
        VM_DNS = VM_DNS[9:]
      return 2
    elif sys.argv[1] == 'encrypt' and len(sys.argv) == 3:
      GUARD_POINT = sys.argv[2]
      command = 'encrypt ' + GUARD_POINT
      if pre_command == command:
        return 99
      else:
        update_command(COMMAND_FILE, command)
        return 3
    elif sys.argv[1] == 'decrypt' and len(sys.argv) >= 4:
      DECRYPT_UPDATE_FLAG = sys.argv[2]
      command = 'decrypt'
      for i in range(3, len(sys.argv)):
        GUARD_POINT_LIST.append(sys.argv[i])
        command = command + ' ' + sys.argv[i]
      if pre_command == command:
        return 99
      else:
        if DECRYPT_UPDATE_FLAG == 'update': 
          update_command(COMMAND_FILE, command)
        else:
          #DECRYPT_UPDATE_FLAG == 'noupdate'
          if pre_command == 'uninstall':
            return 99  
        return 4
    elif sys.argv[1] == 'uninstall' and len(sys.argv) == 2:
      if pre_command == 'uninstall':
        return 99
      else:
        update_command(COMMAND_FILE, 'uninstall')
        return 5
    elif sys.argv[1] == 'help':
      show_usage()
      sys.exit(0)	
    else:
      show_error('Incorrect parameters')
#*************************************************

#*************************************************
def update_linux_lib():
  distribution = platform.linux_distribution()[0]
  if 'Ubuntu' in distribution:
    os.system('apt-get install -y python-pexpect')
  elif 'SUSE' in distribution:
    os.system('zypper install -y python-pexpect')
  elif 'Red Hat' in distribution:
    os.system('yum install -y pexpect')
  elif 'CentOS' in distribution:
    os.system('yum install -y pexpect')
#*************************************************

#*************************************************
#check if there is a mapping to Vormetric Server
def check_hosts(host_file, server_dns):
  if server_dns != 'None':
    hosts = open(host_file, 'r')
    for line in hosts:
      if not line.startswith('#'):     
        try:
          if line.split()[1:] == [server_dns]:
            return True
        except:
          pass
    return False
  else:
    return True
#*************************************************

#*************************************************
#update hosts to include a mapping to SCM3
def update_hosts(server_ip, server_dns, host_file):
  with open(host_file, "a") as hosts:
    hosts.write(os.linesep)
    hosts.write(server_ip + ' ' + server_dns)
#*************************************************

#*************************************************
#update facts for agent status
def update_facts(status, operating_system):
  if operating_system == 'Windows':
    fact_file = 'C:\\ProgramData\\PuppetLabs\\facter\\facts.d\\vormetric_facts.txt'
    with open(fact_file, "w") as facts:
      facts.write('appstack:extsvc:vormetric:agent_status=' + status)
  else:
    fact_file = '/etc/facter/facts.d/vormetric_facts.txt'
    with open(fact_file, "w") as facts:
      facts.write('appstack:extsvc:vormetric:agent_status=' + status)
#*************************************************

#*************************************************
#generate URL for downloading SecureCloud agent
def generate_download_URL():
  download_URL = 'http://' + AGENT_DOWNLOAD_URL
  download_URL = download_URL + ':8080/BTSecureCloudServer/BTSecureCloud/downloadVor?'
  download_URL = download_URL + '&operatingSystem=' + platform.system()
  	
  if platform.system() == 'Windows':
    download_URL = download_URL + '&distribution=N/A' 
    #platform.architecture()[0] == '64bit' does not work if python 32bit is used
    if platform.architecture()[0] == '64bit' or '(x86)' in os.environ['PROGRAMFILES']: 
      download_URL = download_URL + '&architecture=64bit'
    else:
      download_URL = download_URL + '&architecture=32bit'
  else:
    distribution = platform.linux_distribution()[0]
    if 'Ubuntu' in distribution:
      download_URL = download_URL + '&distribution=Ubuntu'
    elif 'SUSE' in distribution:
      download_URL = download_URL + '&distribution=Suse'
    elif 'Red Hat' in distribution:
      download_URL = download_URL + '&distribution=Red%20hat6'
    elif 'CentOS' in distribution:
      download_URL = download_URL + '&distribution=CentOS'
    download_URL = download_URL + '&architecture=' + platform.architecture()[0] #platform.machine()
  
  #download_URL = download_URL + '&kernelversion=' + platform.platform()
  #download_URL = download_URL + '&agentversion=' + agent_version
  return download_URL
#*************************************************

#*************************************************
#download SecureCloud agent
def download_file(download_url, filename):
  #if the file has already been existed, delete it
  if os.path.exists(filename):
    os.remove(filename)
    
  u = urllib2.urlopen(download_url)

  with open(filename, 'wb') as f:
    meta = u.info()
    meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
    meta_length = meta_func("Content-Length")
    file_size = None
    if meta_length:
      file_size = int(meta_length[0])
    print("Downloading File: {0} (bytes)".format(file_size))

    file_size_dl = 0
    block_sz = 8192
    while True:
      buffer = u.read(block_sz)
      if not buffer:
        break

      file_size_dl += len(buffer)
      f.write(buffer)

      status = "{0:16}".format(file_size_dl)
      if file_size:
         status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
      status += chr(13)
      sys.stdout.write(status)
    print('')

  #make sure that the file is executable
  file_mode = os.stat(filename).st_mode | stat.S_IXUSR
  os.chmod(filename, file_mode)
#*************************************************

#*************************************************
def generate_installation_command(operating_system):
  execution_command = SETUP_FILE

  if operating_system == 'Windows':
    os.chdir(TMP_FOLDER)
    execution_command = 'C:\\Windows\\System32\\msiexec /i '
    execution_command = execution_command + TMP_FOLDER + '\\fsagent.msi '
    execution_command = execution_command + '/qn /l*v C:\\btconfig\\installationlog.txt'
    #execution_command = 'veefs.exe'
    #execution_command = execution_command + ' /s'
    #execution_command = execution_command + ' /v'
    #execution_command = execution_command + '"/qn'
    #execution_command = execution_command + ' REGISTERHOSTOPTS=\\"' + SERVER_DNS + ' -agent=' + VM_DNS + ' -log=c:\\btconfig\\vmlog.txt\\""'
  else:
    os.chdir(CONFIG_FOLDER)
    execution_command = execution_command + ' -s'
    execution_command = execution_command + ' unattended.txt'
    uafile = open('unattended.txt', 'w')
    uafile.write('SERVER_HOSTNAME=' + SERVER_DNS + '\n')
    uafile.write('AGENT_HOST_NAME=' + VM_DNS + '\n')
    uafile.close()
  return execution_command
#*************************************************

#*************************************************
#main program
if __name__ == "__main__":
  running_mode = parse_parameters(sys.argv[1:])    
  
  #open log file
  logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='[%m/%d/%y, %H:%M:%S]',)  
  #logging.info('Parameters: ' + AGENT_DOWNLOAD_URL + ',' + SERVER_DNS + ',' + SERVER_IP + ',' + VM_DNS)

  if running_mode == 0:     
    logging.info('Subscribed: DNS=' + VM_DNS) 
    update_facts('installation.' + VM_DNS, platform.system())

  elif running_mode == 1:        
    #make sure that DSM mapping exists in the hosts file
    if not check_hosts(HOSTS_FILE, SERVER_DNS): 
      logging.info('Adding server DNS-IP mapping to hosts file') 
      update_hosts(SERVER_IP, SERVER_DNS, HOSTS_FILE)

    #download installation file
    if not os.path.exists(SETUP_FILE):
      if AGENT_DOWNLOAD_URL != 'NONE':
        download_url = generate_download_URL()
        logging.info('Download Vormetric Agent: ' + download_url)
        download_file(download_url, SETUP_FILE)

    #install Vormetric agent
    if os.path.exists(SETUP_FILE):
      execution_command = generate_installation_command(platform.system())
      logging.info('Install Vormetric Agent: ' + execution_command)
      if platform.system() == 'Windows':
        open(CONFIG_FOLDER + '\\waitforrestart', 'w').close()
        os.system(execution_command)
      else:
        #not registered: /opt/vormetric/DataSecurityExpert/agent/vmd/pem/agent.pem does not exist		
        update_linux_lib()
        import pexpect
        distribution = platform.linux_distribution()[0]		
        if 'Ubuntu' in distribution:  
          try:
            cont = True
            child = pexpect.spawn(execution_command, timeout=60)
            while cont:
              i = child.expect(['Do you want to continue with agent registration\? \(Y/N\)'], timeout=60)
              if i == 0:
                child.sendline('Y')
                cont = False
              else:
                child.sendline('')
            child.expect(pexpect.EOF)
            update_facts('running', platform.system())
          except pexpect.EOF, pexpect.TIMEOUT:
            pass       
        else:
          try:
            cont = True
            child = pexpect.spawn(execution_command, timeout=None)
            while cont:
              i = child.expect(['Do you want to continue with agent registration\? \(Y/N\)'], timeout=None)
              if i == 0:
                child.sendline('Y')
                cont = False
              else:
                child.sendline('')
            child.expect(pexpect.EOF)
            update_facts('running', platform.system())
          except pexpect.EOF:
            pass
    else:
      logging.info('Failed to get the agent installer')

  elif running_mode == 5:
    logging.info('Uninstall Vormetric Agent')
    if platform.system() == 'Windows':
      os.system('C:\Windows\System32\msiexec.exe /x {EDAA46C4-E8FD-417D-ADB9-7E250D45F7C9} /quiet')
    else:
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/uninstall'
      import pexpect	  
      try:
        cont = True
        child = pexpect.spawn(execution_command, timeout=None)
        while cont:
          i = child.expect(['Would you like to uninstall the vee-fs package\? \(Y/N\)'], timeout=None)
          if i == 0:
            child.sendline('Y')
            cont = False
          else:
            child.sendline('')
        child.expect(pexpect.EOF)
      except pexpect.EOF:
        pass
    update_facts('uninstallation.', platform.system())

  elif running_mode == 2:
    if os.path.exists(CONFIG_FOLDER + '\\waitforrestart'):
      os.remove(CONFIG_FOLDER + '\\waitforrestart')
    else:
      if not os.path.exists(AGENT_FILE):
        logging.info('Vormetric agent has not been installed')
      else: 
        if not os.path.exists('C:\\ProgramData\\Vormetric\\DataSecurityExpert\\agent\\vmd\\pem\\agent.pem'):	  
          os.chdir('C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\shared\\bin')
          execution_command = 'register_host.exe -vmd -agent=' + VM_DNS + ' ' + SERVER_DNS + ' -silent'
          logging.info('Register Vormetric Agent: ' + execution_command)
          os.system(execution_command)
          update_facts('running', platform.system())
        else:
          logging.info('Vormetric Agent has been previously registered')	
        
  elif running_mode == 3:
    logging.info('Run dataxform to encrypt data ' + GUARD_POINT)
    if platform.system() == 'Windows':
      os.chdir('C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\vmd\\bin')        
      execution_command = 'dataxform --rekey --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      process = subprocess.Popen(['dataxform', '--rekey', '--nq', '--gp', GUARD_POINT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if stdout is not None:
        lines = stdout.split('\r\n')
        for line in lines:
          if line != '':
            logging.info(line)       
      execution_command = 'dataxform --cleanup --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      process = subprocess.Popen(['dataxform', '--cleanup', '--nq', '--gp', GUARD_POINT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if stdout is not None:
        lines = stdout.split('\r\n')
        for line in lines:
          if line != '':
            logging.info(line)     
    else:
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform --rekey --nq --gp ' + GUARD_POINT      
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform --cleanup --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      os.system(execution_command)    
    #update facter
    update_facts('encryption.' + GUARD_POINT, platform.system())
    
  elif running_mode == 4:
    logging.info('Run dataxform to decrypt data ' + ' '.join(GUARD_POINT_LIST))
    fact_value = 'decryption'    
    if platform.system() == 'Windows':
      os.chdir('C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\vmd\\bin')
      for GUARD_POINT in GUARD_POINT_LIST:
        execution_command = 'dataxform --rekey --nq --gp ' + GUARD_POINT
        logging.info('Command: ' + execution_command)
        process = subprocess.Popen(['dataxform', '--rekey', '--nq', '--gp', GUARD_POINT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout is not None:
          lines = stdout.split('\r\n')
          for line in lines:
            if line != '':
              logging.info(line)       
        execution_command = 'dataxform --cleanup --nq --gp ' + GUARD_POINT
        logging.info('Command: ' + execution_command)
        process = subprocess.Popen(['dataxform', '--cleanup', '--nq', '--gp', GUARD_POINT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout is not None:
          lines = stdout.split('\r\n')
          for line in lines:
            if line != '':
              logging.info(line)
        fact_value = fact_value + "." + GUARD_POINT
    else:
      for GUARD_POINT in GUARD_POINT_LIST:
        execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform/dataxform --rekey --nq --gp ' + GUARD_POINT      
        logging.info('Command: ' + execution_command)
        os.system(execution_command)
        execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform/dataxform --cleanup --nq --gp ' + GUARD_POINT
        logging.info('Command: ' + execution_command)
        os.system(execution_command)
        fact_value = fact_value + "." + GUARD_POINT
    #update facter
    if DECRYPT_UPDATE_FLAG == 'update':
      update_facts(fact_value, platform.system()) 
#*************************************************