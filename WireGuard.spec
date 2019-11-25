# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools

%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	1
%define		pname	WireGuard
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	0.0.20191012
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
Source0:	https://git.zx2c4.com/WireGuard/snapshot/%{pname}-%{version}.tar.xz
# Source0-md5:	b59c92dbfdcdfd32e3daa987f66540ac
Summary:	WireGuard is an extremely simple yet fast and modern VPN that utilizes state-of-the-art cryptography
License:	GPL v2
Group:		Networking/Daemons
URL:		https://www.wireguard.com/
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:3.10}}
BuildRequires:	libmnl-devel
BuildRequires:	rpmbuild(macros) >= 1.701
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WireGuard is an extremely simple yet fast and modern VPN that utilizes
state-of-the-art cryptography. It aims to be faster, simpler, leaner,
and more useful than IPSec, while avoiding the massive headache. It
intends to be considerably more performant than OpenVPN. WireGuard is
designed as a general purpose VPN for running on embedded interfaces
and super computers alike, fit for many different circumstances.

This package contains user space tools. You need to also install
kernel module from kernel-*-misc-wireguard package.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-misc-wireguard\
Summary:	WireGuard kernel module\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-misc-wireguard\
WireGuard kernel module.\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-misc-wireguard\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/misc/*.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-misc-wireguard\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-misc-wireguard\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -C src -m wireguard\
%install_kernel_modules -D installed -m src/wireguard -d misc\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}

%build
%{?with_kernel:%{expand:%build_kernel_packages}}

%if %{with userspace}
%{make} -C src/tools
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%if %{with userspace}
%{make} -C src/tools install \
	PREFIX=$RPM_BUILD_ROOT%{_prefix} \
	SYSCONFDIR=$RPM_BUILD_ROOT%{_sysconfdir} \
	SYSTEMDUNITDIR=$RPM_BUILD_ROOT%{systemdunitdir} \
	WITH_SYSTEMDUNITS=yes
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%postun
%systemd_reload

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc contrib/examples README.md
%attr(755,root,root) %{_bindir}/wg
%attr(755,root,root) %{_bindir}/wg-quick
%dir %{_sysconfdir}/wireguard
%{systemdunitdir}/wg-quick@.service
%{_mandir}/man8/wg-quick.8*
%{_mandir}/man8/wg.8*
%endif
