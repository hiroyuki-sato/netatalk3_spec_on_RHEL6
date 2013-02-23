Summary: AFP fileserver for Macintosh clients
Name:    netatalk
Version: 3.0.2
Release: 0.0.2%{?dist}
Epoch:   4
License: GPLv2+
Group:   System Environment/Daemons
Source0: http://download.sourceforge.net/netatalk/netatalk-%{version}.tar.bz2
Source2: netatalk.pam-system-auth

#
# Temporary
#  compile libevent2 statically.
#
Patch0: netatalk-3.0.2-rc.patch
Patch1: netatalk-3.0.2-libevent.patch

Url:	 http://netatalk.sourceforge.net/
Requires: pam
Requires(post): /sbin/chkconfig /sbin/ldconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service /sbin/ldconfig
BuildRequires: cracklib-devel openssl-devel pam quota-devel libtool automake
BuildRequires: autoconf db4-devel pam-devel tcp_wrappers-devel libgcrypt-devel
BuildRequires: avahi-devel libacl-devel openldap-devel
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Netatalk is a freely-available Open Source AFP fileserver. A *NIX/*BSD
system running Netatalk is capable of serving many Macintosh clients
simultaneously as an AppleShare file server (AFP).

%package devel
Summary: Headers for Netatalk development
Group: Development/Libraries

%description devel
This package contains the header files for Netatalk.

%prep
%setup -q

#
# temporary until release 3.0.3
#
%patch0  -p1 -b .rc

%build
# Commented autoconf too old.
# Build fail if regenrate configure script.
#   https://gist.github.com/hiroyuki-sato/4960699
#
#touch AUTHORS
#libtoolize --force
#aclocal -I macros
#automake --add-missing
#autoconf
#autoheader
export CFLAGS="$RPM_OPT_FLAGS"
%ifnarch x86_64
# XXX : enable for x86_64 when glibc bug 149284 is fixed!
export CFLAGS="$CFLAGS -fPIE"
export LDFLAGS="-pie -Wl,-z,relro,-z,now,-z,noexecstack,-z,nodlopen"
%endif
%ifarch ppc ppc64 s390 s390x
export CFLAGS="$CFLAGS -fsigned-char"
%endif

%configure \
	--with-cracklib \
	--with-pam \
	--with-shadow \
	--with-uams-path=%{_libdir}/netatalk \
	--enable-shared \
	--enable-krbV-uam \
	--enable-overwrite \
	--with-gnu-ld \
	--with-init-style=redhat-sysv \
	--with-libgcrypt \
	--bindir=%{_bindir} \
	--sbindir=%{_sbindir} \
	--sysconfdir=%{_sysconfdir} \
	--mandir=%{_mandir} \
	--localstatedir=%{_var} \
	--includedir=%{_includedir} \
	--datarootdir=%{_datarootdir} 

#
# temporary until release 3.0.3
#
patch -p0 < %{PATCH1}

# Grrrr. Fix broken libtool/autoFOO Makefiles.
if [ "%{_lib}" != lib ]; then
	find . -name Makefile | xargs perl -pi \
	-e 's,-L/usr/lib,-L%{_libdir},g'
	find . -name Makefile | xargs perl -pi \
	-e 's,-L/lib,-L/%{_lib},g'
fi

make %{?_smp_mflags} all

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=%{buildroot}

# Clean up .a and .la files
find $RPM_BUILD_ROOT -name \*.a -exec rm {} \;
find $RPM_BUILD_ROOT -name \*.la -exec rm {} \;

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -e /etc/netatalk/afp_signature.conf -a ! -e /var/netatalk/afp_signature.conf ]; then
  mv -f /etc/netatalk/afp_signature.conf /var/netatalk/
fi
if [ -e /etc/netatalk/afp_voluuid.conf -a ! -e /var/netatalk/afp_voluuid.conf ]; then
  mv -f /etc/netatalk/afp_voluuid.conf /var/netatalk/
fi
/sbin/chkconfig --add netatalk
/sbin/ldconfig

%preun
if [ "$1" = "0" ] ; then
  # check for existence due to renaming initscritp
  if [ -x  %{_initrddir}/netatalk ] ; then
    /sbin/service netatalk stop > /dev/null 2>&1
    /sbin/chkconfig --del netatalk
  fi
fi

%postun
if [ -e /etc/netatalk/afp_signature.conf -a ! -e /var/netatalk/afp_signature.conf ]; then
  mv -f /etc/netatalk/afp_signature.conf /var/netatalk/
fi
if [ -e /etc/netatalk/afp_voluuid.conf -a ! -e /var/netatalk/afp_voluuid.conf ]; then
  mv -f /etc/netatalk/afp_voluuid.conf /var/netatalk/
fi
if [ "$1" -ge "1" ]; then
  /sbin/service netatalk condrestart > /dev/null 2>&1 || :
fi
/sbin/ldconfig

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/extmap.conf
%config(noreplace) %{_sysconfdir}/afp.conf
%config(noreplace) %{_sysconfdir}/pam.d/netatalk
%{_sbindir}/*
%{_bindir}/*
%exclude %{_bindir}/netatalk-config
%{_mandir}/man*/*
%exclude %{_mandir}/man*/netatalk-config*
%{_libdir}/netatalk/*
%{_libdir}/*
%{_var}/netatalk/*
%{_sysconfdir}/rc.d/init.d/netatalk

%files devel
%defattr(-,root,root)
%dir %{_includedir}/atalk
%attr(0644,root,root) %{_includedir}/atalk/*
%{_datadir}/aclocal/netatalk.m4
%{_bindir}/netatalk-config
%{_mandir}/man*/netatalk-config.1*

%changelog
* Tue Feb 19 2013 HAT <hat@fa2.so-net.ne.jp> - 4:3.0.2-0.0.2
- small fixes

* Fri Feb 15 2013 Hiroyuki Sato <hiroysato at gmail.com> -4:3.0.2-0.0.1
- bump version

* Fri Jan 23 2013 Hiroyuki Sato <hiroysato at gmail.com> 
- Update for 3.0.2. Thanks Svavar Orn.

* Fri Oct 19 2012 HAT <hat@fa2.so-net.ne.jp> - 4:2.2.4-0.0.1
- updated to upstream 2.2.4

* Wed May 23 2012 HAT <hat@fa2.so-net.ne.jp> - 4:2.2.3-0.0.1
- updated to latest upstream 2.2.3

* Mon Jan 16 2012 HAT <hat@fa2.so-net.ne.jp> - 4:2.2.2-0.1.1
- updated to latest upstream 2.2.2

* Wed Sep 07 2011 HAT <hat@fa2.so-net.ne.jp> - 4:2.2.1-0.1.5
- updated to latest upstream 2.2.1

* Fri Aug 19 2011 Jiri Skala <jskala@redhat.com> - 4:2.2.0-2
- fixes #726928 - BuildRequires: avahi-devel libacl-devel openldap-devel

* Fri Jul 22 2011 Jiri Skala <jskala@redhat.com> - 4:2.2.0-1
- updated to latest upstream 2.2.0

* Fri Jul 22 2011 Jiri Skala <jskala@redhat.com> - 4:2.1.5-2
- add --with-libgcrypt option

* Tue Jan 25 2011 Jiri Skala <jskala@redhat.com> - 4:2.1.5-1
- updated to latest upstream 2.1.5 - initial version of EPEL 6

* Mon Nov 23 2009 Jiri Skala <jskala@redhat.com> - 4:2.0.4-5
- fixed #538842 -  BuildRequires: libgcrypt-devel
- fixed #537402 -  unnecessary files in SRPM

* Tue Sep 15 2009 Jiri Skala <jskala@redhat.com> - 4:2.0.4-4
- fixed #473943

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 4:2.0.4-3
- rebuilt with new openssl

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4:2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Jiri Skala <jskala@redhat.com> - 4:2.0.4-1
- updated to latest upstream version

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4:2.0.3-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Jiri Skala <jskala@redhat.com> -4:2.0.3-26
- Resolves #480641 - CVE-2008-5718 netatalk: papd command injection vulnerability

* Tue Jan 27 2009 Jiri Skala <jskala@redhat.com> -4:2.0.3-25
- fixed epoch in the subpackage requires

* Fri Jan 23 2009 Jiri Skala <jskala@redhat.com> -4:2.0.3-24
- fix #473186 conflict timeout with coreutils

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 4:2.0.3-23
- rebuild with new openssl

* Wed Dec 03 2008 Jiri Skala <jskala@redhat.com> -4:2.0.3-22
- fix #473939 netatalk-2.0.3-21.fc10 disable quota

* Mon Oct 13 2008 Jiri Skala <jskala@redhat.com> - 4:2.0.3-21
- fix #465050 - FTBFS netatalk-2.0.3-19 - regenerated patches

* Mon Aug 11 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 4:2.0.3-20
- fix license tag

* Thu Mar 06 2008 Martin Nagy <mnagy@redhat.com> - 4:2.0.3-19
- fix chmod o+x (#225085)
- increase the maximum number of cnid_dbd processes to 512 (#232805)
- papd now writes debugging output to stderr when invoked with -d (#150021)
- fix multiarch conflict for netatalk-devel (#342681)

* Mon Feb 25 2008 Martin Nagy <mnagy@redhat.com> - 4:2.0.3-18
- make init script LSB compliant (#246993)

* Mon Feb 25 2008 Martin Nagy <mnagy@redhat.com> - 4:2.0.3-17
- fix unowned directories (#233889)

* Mon Feb 11 2008 Martin Nagy <mnagy@redhat.com> - 4:2.0.3-16
- rebuild for gcc-4.3

* Tue Dec 04 2007 Martin Nagy <mnagy@redhat.com> - 4:2.0.3-15.1
- rebuild

* Wed Sep 12 2007 Maros Barabas <mbarabas@redhat.com> -4:2.0.3-15
- patch to build on FC, bad open call 

* Tue Sep 11 2007 Maros Barabas <mbarabas@redhat.com> - 4:2.0.3-13
- rebuild

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 4:2.0.3-12
- Rebuild for selinux ppc32 issue.

* Thu May 10 2007 Maros Barabas <mbarabas@redhat.com> - 4:2.0.4-11
- fix from merge review
- Resolves #226190

* Tue Apr 17 2007 Maros Barabas <mbarabas@redhat.com> - 4:2.0.3-10
- fix fiew problems in spec

* Tue Jan 23 2007 Jindrich Novy <jnovy@redhat.com> - 4:2.0.3-9
- rebuild against new db4

* Mon Dec 04 2006 Maros Barabas	<mbarabas@redhat.com> - 4:2.0.3-8
- BuildRequires changed from cracklib to cracklib-devel

* Fri Aug 18 2006 Jesse Keating <jkeating@redhat.com> - 4:2.0.3-7
- rebuilt with latest binutils to pick up 64K -z commonpagesize on ppc*
  (#203001)
- Add dist tag

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 4:2.0.3-6.fc6.1
- rebuild

* Fri Jun 09 2006 Jason Vas Dias <jvdias@redhat.com> - 4:2.0.3-6.fc6
- rebuild for broken libgssapi deps and brew build

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 4:2.0.3-4.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jason Vas Dias <jvdias@redhat.com>
- rebuild for new gcc, glibc, glibc-kernheaders

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 09 2005 Jason Vas Dias <jvdias@redhat.com>
- Rebuild for new openssl dependencies

* Thu Oct 13 2005 Tomas Mraz <tmraz@redhat.com>
- use include instead of pam_stack in pam config

* Wed Jul 20 2005 Bill Nottingham <notting@redhat.com>
- don't run by default

* Thu Jun 16 2005 Jason Vas Dias <jvdias@redhat.com>
- Upgrade to upstream version 2.0.3
- fix bug 160486: use netatalk's initscript

* Wed Mar 30 2005 Florian La Roche <laroche@redhat.com>
- quick fix: rm -f /usr/include/netatalk/at.h until this
  is resolved the correct way

* Mon Mar 07 2005 Jason Vas Dias <jvdias@redhat.com>
- Fix for gcc4 compilation: extern_ucreator.patch

* Mon Feb 21 2005 Jason Vas Dias <jvdias@redhat.com>
- Upgraded to upstream version 2.0.2 .

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 07 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- 1.6.4

* Fri Aug 1 2003 Charlie Bennett <ccb@redhat.com>
- Update with 1.6.3 upstream sources

* Tue Jul 29 2003 Elliot Lee <sopwith@redhat.com>
- Rebuild
- Fix perl multilib path editing
- Add pathcat patch

* Thu May  1 2003 Elliot Lee <sopwith@redhat.com> 1.5.5-7
- Make multilib generic
- Add builddep on quota (for rpcsvc/rquota.h)

* Wed Feb 18 2003 Bill Nottingham <notting@redhat.com> 1.5.5-5
- fix initscript error (#82118)

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan  7 2003 Nalin Dahyabhai <nalin@redhat.com> 1.5.5-3
- patch for compile errors with new ssl libs
- rebuild

* Mon Dec 02 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- postun should never fail

* Thu Nov 28 2002 Phil Knirsch <pknirsch@redhat.com> 1.5.5-1
- Updated to 1.5.5

* Tue Jun 25 2002 Phil Knirsch <pknirsch@redhat.com> 1.5.3.1-4
- Fixed dependancy problem on /usr/bin/rc by removing acleandir.[1|rc] (#67243)
- Fixed missing /usr/share/netatalk dir (#67222)

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 1.5.3.1-2
- automated rebuild

* Tue Jun 18 2002 Phil Knirsch <pknirsch@redhat.com> 1.5.3.1-1
- Updated to latest version 1.5.3.1.
- Fixed bug for nls file lookup (#66300).

* Mon May 27 2002 Phil Knirsch <pknirsch@redhat.com> 1.5.2-4
- Fixed initscript bug where you can't use blanks inside of names (#64926).

* Wed Apr 10 2002 Phil Knirsch <pknirsch@redhat.com> 1.5.2-3
- Fixed initscript to use correct config files from /etc/atalk (#62803)
- Changed initscript to use $0 instead of direct string (#61734)
- Change Copyright to Licencse and switch from BSD to GPL (#61746)

* Thu Mar 14 2002 Bill Nottingham <notting@redhat.com>
- don't run by default

* Wed Mar 13 2002 Bill Nottingham <notting@redhat.com>
- it's back 

* Fri Mar  2 2001 Tim Powers <timp@redhat.com>
- rebuilt against openssl-0.9.6-1

* Sun Feb 25 2001 Tim Powers <timp@redhat.com>
- fixed bug 29370. This package is trying to include a file glibc already includes

* Tue Jan 23 2001 Tim Powers <timp@redhat.com>
- updated initscript

* Thu Jan 04 2001 Than Ngo <than@redhat.com>
- fixed uams-path
- added noreplace to %%config

* Mon Nov 20 2000 Tim Powers <timp@redhat.com>
- rebuilt to fix bad dir perms

* Fri Nov 10 2000 Than Ngo <than@redhat.com>
- update to 1.5pre2 (bug #19737, #20397)
- update Url and ftp site
- clean up specfile
- netatalk-1.4b2+asun obsolete

* Mon Aug 07 2000 Than Ngo <than@redhat.de>
- fix dependency with glibc-devel (Bug #15589)
- fix typo in description (Bug #15479)

* Wed Aug 2 2000 Tim Powers <timp@redhat.com>
- fix symlinks not being relative.

* Fri Jul 28 2000 Than Ngo <than@redhat.de>
- add missing restart function in startup script

* Fri Jul 28 2000 Tim Powers <timp@redhat.com>
- fixed initscripts so that condrestart doesn't return 1 when the test fails

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Sun Jul 23 2000 Tim Powers <timp@redhat.com>
- rebuilt 

* Mon Jul 17 2000 Tim Powers <timp@redhat.com>
- inits back to rc.d/init.d, using service to start inits

* Wed Jul 12 2000 Than Ngo <than@redhat.de>
- rebuilt

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- fixed broken PreReq, now PreReq's /etc/init.d

* Tue Jun 27 2000 Than Ngo <than@redhat.de>
- remove prereq initscripts, add requires initscripts
- clean up specfile

* Mon Jun 26 2000 Than Ngo <than@redhat.de>
- /etc/rc.d/init.d -> /etc/init.d
- add condrestart directive
- fix post/preun/postun scripts
- prereq initscripts >= 5.20

* Tue Jun 20 2000 Tim Powers <timp@redhat.com>
- fixed bug 11420 concerning the building with -O2.

* Thu Jun 8 2000 Tim Powers <timp@redhat.com>
- fix bug #11978 
- fix man page locations to be FHS compliant

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- modify PAM setup to use system-auth

* Thu Dec 16 1999 Tim Powers <timp@redhat.com>
- renewed source so it is pristine, delete the problematic files in spec file
	instead
- general spec file cleanups, create buildroot and dirs in the %%install
	section
- strip binaries
- gzip man pages
- fixed netatalk-asun.librpcsvc.patch, -lnss_nis too
- changed group
- added %%defattr to %%files section

* Tue Aug 3 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- rpm-3.0 needs to remove vogus files from source.
  Removed files: etc/papd/.#magics.c, etc/.#diff
* Fri Jul 30 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Change Copyright tag to BSD.
  Add /usr/bin/adv1tov2.
* Thu Apr 22 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Correct librpcsvc.patch.  Move %%changelog section last.
  Uncomment again -DNEED_QUOTA_WRAPPER in sys/linux/Makefile since
  LinuxPPC may need.
* Wed Mar 31 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Comment out -DNEED_QUOTA_WRAPPER in sys/linux/Makefile.
* Sat Mar 20 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Correct symbolic links to psf.
  Remove asciize function from nbplkup so as to display Japanese hostname.
* Thu Mar 11 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- Included MacPerl 5 script ICDumpSuffixMap which dumps suffix mapping
  containd in Internet Config Preference.
* Tue Mar 2 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- [asun2.1.3]
* Mon Feb 15 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2-8]
* Sun Feb 7 1999 iNOUE Koich! <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2-6]
* Mon Jan 25 1999 iNOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2-3]
* Thu Dec 17 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- [pre-asun2.1.2]
  Remove crlf patch. It is now a server's option.
* Thu Dec 3 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use stable version source netatalk-1.4b2+asun2.1.1.tar.gz
  Add uams directory
* Sat Nov 28 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.1-3 source.
* Mon Nov 23 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.1-2 source.
* Mon Nov 16 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Fix rcX.d's symbolic links.
* Wed Oct 28 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0a-2 source. Remove '%%exclusiveos linux' line.
* Sat Oct 24 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use stable version source netatalk-1.4b2+asun2.1.0.tar.gz.
* Mon Oct 5 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-10a source.
* Thu Sep 19 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-8 source. Add chkconfig support.
* Sat Sep 12 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Comment out -DCRLF. Use RPM_OPT_FLAGS.
* Mon Sep 8 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-7 source. Rename atalk.init to atalk.
* Mon Aug 22 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-6 source.
* Mon Jul 27 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use pre-asun2.1.0-5 source.
* Tue Jul 21 1998 INOUE Koichi <inoue@ma.ns.musashi-techa.c.jp>
- Use pre-asun2.1.0-3 source.
* Tue Jul 7 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Add afpovertcp entries to /etc/services
- Remove BuildRoot in man8 pages
* Mon Jun 29 1998 INOUE Koichi <inoue@ma.ns.musashi-tech.ac.jp>
- Use modified sources 1.4b2+asun2.1.0 produced by Adrian Sun
  <asun@saul9.u.washington.edu> to provide an AppleShareIP file server
- Included AppleVolumes.system file maintained by Johnson
  <johnson@stpt.usf.edu>
* Mon Aug 25 1997 David Gibson <D.Gibson@student.anu.edu.au>
- Used a buildroot
- Use RPM_OPT_FLAGS
- Moved configuration parameters/files from atalk.init to /etc/atalk
- Separated devel package
- Built with shared libraries
* Sun Jul 13 1997 Paul H. Hargrove <hargrove@sccm.Stanford.EDU>
- Updated sources from 1.3.3 to 1.4b2
- Included endian patch for Linux/SPARC
- Use all the configuration files supplied in the source.  This has the
  following advantages over the ones in the previous rpm release:
	+ The printer 'lp' isn't automatically placed in papd.conf
	+ The default file conversion is binary rather than text.
- Automatically add and remove DDP services from /etc/services
- Placed the recommended /etc/services in the documentation
- Changed atalk.init to give daemons a soft kill
- Changed atalk.init to make configuration easier

* Wed May 28 1997 Mark Cornick <mcornick@zorak.gsfc.nasa.gov>
Updated for /etc/pam.d
