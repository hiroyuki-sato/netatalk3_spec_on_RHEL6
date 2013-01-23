Name:	netatalk	
Version: 3.0.2
Release: 2%{?dist}
Summary: Netatalk is a freely-available Open Source AFP fileserver. 
Group: System Environment/Daemons
License: GPL2	
URL: http://netatalk.sourceforge.net/
Source0: http://download.sourceforge.net/netatalk/netatalk-%{version}.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: cracklib-devel openssl-devel pam quota-devel libtool automake
BuildRequires: autoconf db4-devel pam-devel tcp_wrappers-devel libgcrypt-devel
BuildRequires: avahi-devel libacl-devel openldap-devel
Requires:	pam

%description
Netatalk is a freely-available Open Source AFP fileserver. A *NIX/*BSD system running Netatalk is capable of serving many Macintosh clients simultaneously as an AppleShare file server (AFP).

%package devel
Summary: Headers for Appletalk development
Group: Development/Libraries

%description devel
Headers for Netatalk


%prep
%setup -q

%build
#env LDFLAGS="-Wl,-R%{_libdir}/netatalk"  \
  ./configure --with-init-style=redhat-sysv \
  --bindir=%{_bindir} \
  --libdir=%{_libdir}/netatalk \
  --with-uams-path=%{_libdir}/netatalk \
  --sbindir=%{_sbindir} \
  --sysconfdir=%{_sysconfdir} \
  --mandir=%{_mandir} \
  --localstatedir=%{_var} \
  --includedir=%{_includedir} \
  --datarootdir=%{_datarootdir} 

#
# Add Library search path for libevent.
#
perl -i -pe 's!^LDFLAGS = !LDFLAGS = -rpath %{_libdir}/netatalk!' \
  etc/netatalk/Makefile

make

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Clean up .a and .la files
find $RPM_BUILD_ROOT -name \*.a -exec rm {} \;
find $RPM_BUILD_ROOT -name \*.la -exec rm {} \;

%clean
rm -rf %{buildroot}

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
%{_var}/netatalk/*
%{_sysconfdir}/rc.d/init.d/netatalk
#
# TODO: How to deal this script.
#
%exclude %{_bindir}/event_rpcgen.py

%files devel
%defattr(-,root,root)
%dir %{_includedir}/atalk
%attr(0644,root,root) %{_includedir}/atalk/*
%{_datadir}/aclocal/netatalk.m4
%{_bindir}/netatalk-config
%{_mandir}/man*/netatalk-config.1*
#
# TODO: How to deal these files.
#
%exclude %{_includedir}/event2
%exclude %{_libdir}/netatalk/pkgconfig
%exclude /usr/include/ev*

%doc

%changelog
* Fri Jan 23 2013 Hiroyuki Sato <hiroysato at gmail.com> 
- patch removed. libevent search automatically. Thanks HAT.

* Fri Jan 23 2013 Hiroyuki Sato <hiroysato at gmail.com> 
- Update for 3.0.2. Thanks Svavar Orn.

* Fri Jan 11 2013 Initial Hiroyuki Sato <hiroysato at gmail.com> 
- Initial version.
