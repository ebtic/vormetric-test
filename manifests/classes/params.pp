class vormetric-test::params {

  # these are parameters to be retrieved from hiera
  if $appcara::params::site {
    $site_extsvc_option = $appcara::params::site["extension_service_option"]
    if $site_extsvc_option {
      $site_vormetric_option = $site_extsvc_option["vormetric-test"]
      if $site_vormetric_option {        
        $host_ip = $site_vormetric_option["host_ip"]		
        $host_dns = $site_vormetric_option["host_dns"]        
      }	  
    }	    
  }  
  
  if $appcara::params::account{
    $acct_extsvc_option = $appcara::params::account["extension_service_option"]
    if $acct_extsvc_option {
      $acct_vormetric_option = $acct_extsvc_option['vormetric-test']
      if $acct_vormetric_option {
        $account_state = $acct_vormetric_option["state"] # 'ACTIVE', in general      		
      }
  	  else {
  	    $account_state = "DISABLE"
  	  }
   }
  }
  
  if $appcara::params::server {
    $svr_extsvc_option = $appcara::params::server["extension_service_option"]
    if $svr_extsvc_option {
      $svr_vormetric_option = $svr_extsvc_option['vormetric-test']	  
      if $svr_vormetric_option {
	    if $account_state == "ACTIVE" {
		  $vm_state = $svr_vormetric_option["vm_state"]
		  $guardpoint = $svr_vormetric_option["guardpoint"]
		}
	    else {		  
		  $guardpoint = $svr_vormetric_option["guardpoint_list_desc"]
		  if $guardpoint == ""{
		    $vm_state = "Uninstallation"
		  }
		  else{
		    $vm_state = "Unsubscription"		  
		  }
		}
		
		if $vm_state == "subscribed" or $vm_state == "registered" or $vm_state == "running" or $vm_state == "Encryption" or $vm_state == "Decryption" or $vm_state == "Clear" or $vm_state == "Uninstallation" or $vm_state == "Unsubscription" {
		  $files_existed = "true"
		}
		else{
		  $files_existed = "false"
		}
      }
    }
  }
}
