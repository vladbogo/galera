# Copyright (c) 2011-2014, Codership Oy <info@codership.com>.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License or later.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston
# MA  02110-1301  USA.

%define name galera
# use "rpmbuild --define 'version xxxx'" to define version
%{!?version: %define version 3.x}
%{!?release: %define release 1}
%define copyright Copyright 2007-2014 Codership Oy. All rights reserved. Use is subject to license terms under GPLv2 license.
%define libs %{_libdir}/%{name}
%define docs /usr/share/doc/%{name}

# Define dist tag if not given by platform

# For suse versions see:
# https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} == 1110
%define dist .sle11
%endif
%if 0%{?suse_version} == 1310
%define dist .suse13.1
%endif
%if 0%{?suse_version} == 1315
%define dist .sle12
%endif
%if 0%{?suse_version} == 1320
%define dist .suse13.2
%endif
%if 0%{?suse_version} == 1500
%define dist .suse15.0
%endif

Name:          %{name}
Summary:       Galera: a synchronous multi-master wsrep provider (replication engine)
Group:         System Environment/Libraries
Version:       %{version}
Release:       %{release}%{dist}
License:       GPL-2.0
Source:        http://www.codership.com/downloads/download-mysqlgalera/
URL:           http://www.codership.com/
Packager:      Codership Oy
Vendor:        Codership Oy

BuildRoot:     %{_tmppath}/%{name}-%{version}

#BuildRequires: boost-devel
#BuildRequires: check-devel
BuildRequires: glibc-devel
BuildRequires: openssl-devel

%if 0%{?rhel} == 8
BuildRequires: python3-scons
%else
BuildRequires: scons
%endif

%if 0%{?suse_version} == 1110
# On SLES11 SPx use the linked gcc47 to build instead of default gcc43
#BuildRequires: gcc47 gcc47-c++
# On SLES11 SP2 the libgfortran.3.so provider must be explicitly defined
BuildRequires: libgfortran3
# On SLES11 we got error "conflict for provider of libgcc_s1 >= 4.7.4_20140612-2.1
# needed by gcc47, (provider libgcc_s1 conflicts with installed libgcc43),
# conflict for provider of libgomp1 >= 4.7.4_20140612-2.1 needed by gcc47,
# (provider libgomp1 conflicts with installed libgomp43), conflict for provider
# of libstdc++6 >= 4.7.4_20140612-2.1 needed by libstdc++47-devel,
# (provider libstdc++6 conflicts with installed libstdc++43)
# therefore:
#BuildRequires: libgcc_s1
BuildRequires: libgomp1
BuildRequires: libstdc++6
#!BuildIgnore: libgcc43
%else
BuildRequires: gcc-c++
%endif

%if %{defined fedora}
BuildRequires: python
%endif

# Systemd
%if 0%{?suse_version} >= 1220 || 0%{?centos} >= 7 || 0%{?rhel} >= 7
%define systemd 1
BuildRequires: systemd
%else
%define systemd 0
%endif

Requires:      openssl

Provides:      wsrep, %{name} = %{version}-%{release}

%description
Galera is a fast synchronous multimaster wsrep provider (replication engine)
for transactional databases and similar applications. For more information
about wsrep API see http://launchpad.net/wsrep. For a description of Galera
replication engine see http://www.codership.com.

%{copyright}

This software comes with ABSOLUTELY NO WARRANTY. This is free software,
and you are welcome to modify and redistribute it under the GPLv2 license.

%prep
#%setup -T -a 0 -c -n galera-%{version}

%build
Build() {
CFLAGS=${CFLAGS:-$RPM_OPT_FLAGS}
CXXFLAGS=${CXXFLAGS:-$RPM_OPT_FLAGS}
# We assume that Galera is built already by the top build.sh script
}

%install
RBR=$RPM_BUILD_ROOT
RBD=$RPM_BUILD_DIR

# Clean up the BuildRoot first
[ "$RBR" != "/" ] && [ -d $RBR ] && rm -rf $RBR;
mkdir -p $RBR

%if 0%{?systemd}
install -D -m 644 $RBD/garb/files/garb.service $RBR%{_unitdir}/garb.service
install -D -m 755 $RBD/garb/files/garb-systemd $RBR%{_bindir}/garb-systemd
%else
install -d $RBR%{_sysconfdir}/init.d
install -m 755 $RBD/garb/files/garb.sh  $RBR%{_sysconfdir}/init.d/garb

# Symlink required by SUSE policy
%if 0%{?suse_version}
install -d $RBR/usr/sbin
ln -sf /etc/init.d/garb $RBR/usr/sbin/rcgarb
%endif
%endif

%if 0%{?suse_version}
install -d $RBR/var/adm/fillup-templates/
install -m 644 $RBD/garb/files/garb.cnf $RBR/var/adm/fillup-templates/sysconfig.%{name}
%else
install -d $RBR%{_sysconfdir}/sysconfig
install -m 644 $RBD/garb/files/garb.cnf $RBR%{_sysconfdir}/sysconfig/garb
%endif

install -d $RBR%{_bindir}
install -m 755 $RBD/garb/garbd                    $RBR%{_bindir}/garbd

install -d $RBR%{libs}
install -m 755 $RBD/libgalera_smm.so              $RBR%{libs}/libgalera_smm.so

install -d $RBR%{docs}
install -m 644 $RBD/COPYING                       $RBR%{docs}/COPYING
install -m 644 $RBD/asio/LICENSE_1_0.txt          $RBR%{docs}/LICENSE.asio
install -m 644 $RBD/chromium/LICENSE              $RBR%{docs}/LICENSE.chromium
install -m 644 $RBD/scripts/packages/README       $RBR%{docs}/README
install -m 644 $RBD/scripts/packages/README-MySQL $RBR%{docs}/README-MySQL

install -d $RBR%{_mandir}
install -d $RBR%{_mandir}/man8
install -m 644 $RBD/man/garbd.8        $RBR%{_mandir}/man8/garbd.8

%pre

%post

%preun
rm -f $(find %{libs} -type l)

%files
%defattr(-,root,root,0755)
%if 0%{?suse_version}
%config(noreplace,missingok) /var/adm/fillup-templates/sysconfig.%{name}
%else
%config(noreplace,missingok) %{_sysconfdir}/sysconfig/garb
%endif


%if 0%{?systemd}
%attr(0644,root,root) %{_unitdir}/garb.service
%attr(0755,root,root) %{_bindir}/garb-systemd
%else
%attr(0755,root,root) %{_sysconfdir}/init.d/garb

# Symlink required by SUSE policy
%if 0%{?suse_version}
%attr(0755,root,root) /usr/sbin/rcgarb
%endif
%endif

%attr(0755,root,root) %{_bindir}/garbd

%attr(0755,root,root) %dir %{libs}
%attr(0755,root,root) %{libs}/libgalera_smm.so

%attr(0755,root,root) %dir %{docs}
%doc %attr(0644,root,root) %{docs}/COPYING
%doc %attr(0644,root,root) %{docs}/LICENSE.asio
%doc %attr(0644,root,root) %{docs}/LICENSE.chromium
%doc %attr(0644,root,root) %{docs}/README
%doc %attr(0644,root,root) %{docs}/README-MySQL

%doc %attr(644, root, man) %{_mandir}/man8/garbd.8*

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && [ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;

