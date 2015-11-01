class vormetric_test::agent::linux::install() {

  $vm_management_folder = "/btconfigtest"
  $agent_download_url = "ec2-54-161-187-162.compute-1.amazonaws.com"
  $vm_dns = "$::appstack_server_identifier.$::domain"
  
  #for testing purpose
  notify {"vm_state ${vormetric_test::params::vm_state}, vm_dns: ${vm_dns}, guardpoint_list: ${vormetric_test::params::guardpoint_list}, account_state: ${vormetric_test::params::account_state}":}
  
  if $vormetric_test::params::files_existed == "true" {
    
	#create management folder
    file { "$vm_management_folder":
      ensure => directory, 
    }  
  
    #download python code
    file { "${vm_management_folder}/vormetric_agent_management.py":
      ensure  => file,
      mode    => "0700",
      owner   => 'root',
      group   => 'root',
      source  => "puppet:///modules/vormetric/vormetric_agent_management.py",
      require => File["$vm_management_folder"],
    }
	
	case $vormetric_test::params::vm_state{      
	  'subscribed':{
	    unless "mgmt.appcara.com" in $vm_dns { 
	      exec { "vormetric_service_subscription":
		    cwd     => "$vm_management_folder",
            path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
            creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd",         
	        command => "python vormetric_agent_management.py subscribe $vm_dns",
            require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
	      }
		}
	  }
	
	  'registered':{
	    exec { "vormetric_agent_installation":
		  cwd     => "$vm_management_folder",
          path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
          creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd",         
	      command => "python vormetric_agent_management.py install $agent_download_url $vormetric_test::params::host_ip $vormetric_test::params::host_dns $vm_dns",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
	    }
      }	
	  
	  'Encryption':{
	    exec { "vormetric_data_encryption":
		  cwd     => "$vm_management_folder",
		  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
		  command => "python vormetric_agent_management.py encrypt $vormetric_test::params::guardpoint",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
		}
	  }
		
	  'Decryption':{
		exec { "vormetric_data_decryption":
		  cwd     => "$vm_management_folder",
		  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
		  command => "python vormetric_agent_management.py decrypt update $vormetric_test::params::guardpoint",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
		}
	  }
	  
	  'Clear':{
	    exec { "vormetric_data_clear":
		  cwd     => "$vm_management_folder",
		  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
		  command => "python vormetric_agent_management.py decrypt update $vormetric_test::params::guardpoint",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
		}
	  }
	  
	  'Uninstallation':{
	    exec { "vormetric_data_uninstallation":
		  cwd     => "$vm_management_folder",
		  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
		  command => "python vormetric_agent_management.py uninstall",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
		}
	  }
	  
	  'Unsubscription':{
	    exec { "vormetric_data_decryption_special":
		  cwd     => "$vm_management_folder",
		  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
		  command => "python vormetric_agent_management.py decrypt noupdate $vormetric_test::params::guardpoint",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
		}
		
		exec { "vormetric_data_uninstallation":
		  cwd     => "$vm_management_folder",
		  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
		  command => "python vormetric_agent_management.py uninstall",
          require => [Exec["vormetric_data_decryption_special"]],
		}
	  }
    }
  }
  else{
    #TODO for service un-subscription 
	#remove python code
    file { "${vm_management_folder}/vormetric_agent_management.py":
      ensure  => absent,
    }
  } 
}
