Overview 

  This is spec file for netatalk3 on RHEL6.
  
Request For Comment.

  netatalk use libevent2 library. 
  However, there are only libevent-1.4 library on RHEL6. 

  To avoid conflict libevent, moved libevent libraries to /usr/lib/netatalk.
  And Add LD_LIBRARY_PATH in initscript like the following.
  
    export LD_LIBRARY_PATH=/usr/lib64/netatalk

  Please let me konw if you have more good idea. 
