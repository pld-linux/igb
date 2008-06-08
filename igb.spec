# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_with	verbose		# verbose build (V=1)

%ifarch sparc
%undefine	with_smp
%endif

%if %{without kernel}
%undefine with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		rel	3
%define		pname	igb
Summary:	Intel(R) PRO/1000 driver for Linux
Summary(pl.UTF-8):	Sterownik do karty Intel(R) PRO/1000
Name:		%{pname}%{_alt_kernel}
Version:	1.2.24
Release:	%{rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/e1000/%{pname}-%{version}.tar.gz
# Source0-md5:	34fcb212775902a8747129d265e4f0c6
URL:		http://sourceforge.net/projects/e1000/
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains the Linux driver for the Intel(R) PRO/1000
adapters with 82575 chipset.

%description -l pl.UTF-8
Ten pakiet zawiera sterownik dla Linuksa do kart sieciowych z rodziny
Intel(R) PRO/1000 opartych o układ 82575.

%package -n kernel%{_alt_kernel}-net-igb
Summary:	Intel(R) PRO/1000 driver for Linux
Summary(pl.UTF-8):	Sterownik do karty Intel(R) PRO/1000
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-net-igb
This package contains the Linux driver for the Intel(R) PRO/1000
adapters with 82575 chipset.

%description -n kernel%{_alt_kernel}-net-igb -l pl.UTF-8
Ten pakiet zawiera sterownik dla Linuksa do kart sieciowych z rodziny
Intel(R) PRO/1000 opartych o układ 82575.

%prep
%setup -q -n %{pname}-%{version}
cat > src/Makefile <<'EOF'
obj-m := igb.o
igb-objs := e1000_82575.o e1000_mac.o e1000_nvm.o e1000_phy.o e1000_manage.o \
kcompat.o e1000_api.o igb_main.o igb_param.o igb_ethtool.o

EXTRA_CFLAGS=-DDRIVER_IGB
EOF

%build
%build_kernel_modules -C src -m %{pname}

%install
rm -rf $RPM_BUILD_ROOT
%install_kernel_modules -m src/%{pname} -d kernel/drivers/net -n %{pname} -s current
# blacklist kernel module
cat > $RPM_BUILD_ROOT/etc/modprobe.d/%{_kernel_ver}/%{pname}.conf <<'EOF'
blacklist igb
alias igb igb-current
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-igb
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-igb
%depmod %{_kernel_ver}

%files	-n kernel%{_alt_kernel}-net-igb
%defattr(644,root,root,755)
%doc igb.7 README
/etc/modprobe.d/%{_kernel_ver}/%{pname}.conf
/lib/modules/%{_kernel_ver}/kernel/drivers/net/%{pname}*.ko*
