# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0

%define		rel	2
Summary:	WireGuard is an extremely simple yet fast and modern VPN that utilizes state-of-the-art cryptography
Name:		WireGuard%{_alt_kernel}
Version:	1.0.20220627
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Networking/Daemons
Source0:	https://git.zx2c4.com/wireguard-linux-compat/snapshot/wireguard-linux-compat-%{version}.tar.xz
# Source0-md5:	0499a3315b7013e65a07234dc83dec39
Patch0:		kernel-4.9.256.patch
URL:		https://www.wireguard.com/
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:3.10}
BuildRequires:	rpmbuild(macros) >= 1.701
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WireGuard is an extremely simple yet fast and modern VPN that utilizes
state-of-the-art cryptography. It aims to be faster, simpler, leaner,
and more useful than IPSec, while avoiding the massive headache. It
intends to be considerably more performant than OpenVPN. WireGuard is
designed as a general purpose VPN for running on embedded interfaces
and super computers alike, fit for many different circumstances.

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
\
%files -n kernel%{_alt_kernel}-misc-wireguard\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/misc/*.ko*\
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

%{expand:%create_kernel_packages}

%prep
%setup -q -n wireguard-linux-compat-%{version}
%patch -P0 -p1

%build
%{expand:%build_kernel_packages}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT
