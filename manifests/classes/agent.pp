# Class:vormetric::agent
#
# This module manages TrendMicro DeepSecurity Agent 9.0
#
# Parameters:
#
# Actions:
#
# Requires:
#
# Sample Usage:
#   (See test/init.pp)
class vormetric-test::agent(
) inherits vormetric-test::params {

  # perform this only when node tagging is completed
  #if $appcara::params::server {

    case $::operatingsystem {
        # Linux-based computers
        'debian','ubuntu','redhat','centos','Amazon': {
            class { 'vormetric-test::agent::linux::install': }
            class { 'vormetric-test::agent::linux::config': }
            Class['vormetric-test::agent::linux::install']
              -> Class['vormetric-test::agent::linux::config']
        }
		'windows': {
            class { 'vormetric-test::agent::windows::install': }
            class { 'vormetric-test::agent::windows::config': }
            Class['vormetric-test::agent::windows::install']
              -> Class['vormetric-test::agent::windows::config']
	    }
        # Other OS
        default: {
            notice("Unsupported OS: $::operatingsystem")
        }
    } # end case
    
  #} # end if $appcara::params::server

} # end of class
