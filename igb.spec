# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	verbose		# verbose build (V=1)

%if "%{_alt_kernel}" != "%{nil}"
%if 0%{?build_kernels:1}
%{error:alt_kernel and build_kernels are mutually exclusive}
exit 1
%endif
%global		_build_kernels		%{alt_kernel}
%else
%global		_build_kernels		%{?build_kernels:,%{?build_kernels}}
%endif

%define		kpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%kernel_pkg ; done)
%define		bkpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%build_kernel_pkg ; done)
%define		ikpkg	%(echo %{_build_kernels} | tr , '\\n' | while read n ; do echo %%undefine alt_kernel ; [ -z "$n" ] || echo %%define alt_kernel $n ; echo %%install_kernel_pkg ; done)

# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0

%define		_duplicate_files_terminate_build	0

%define		rel	8
%define		pname	igb
Summary:	Intel(R) PRO/1000 driver for Linux
Summary(pl.UTF-8):	Sterownik do karty Intel(R) PRO/1000
Name:		%{pname}%{_alt_kernel}
Version:	5.0.5
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://downloads.sourceforge.net/e1000/%{pname}-%{version}.tar.gz
# Source0-md5:	cff8b7f54d25c47888b96466ff69a950
URL:		http://sourceforge.net/projects/e1000/
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpm-build-macros >= 1.678
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains the Linux driver for the Intel(R) PRO/1000
adapters with 82575EB/GB or 82576 chipsets.

%description -l pl.UTF-8
Ten pakiet zawiera sterownik dla Linuksa do kart sieciowych z rodziny
Intel(R) PRO/1000 opartych o układy 82575EB/GB lub 82576.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-net-igb\
Summary:	Intel(R) PRO/1000 driver for Linux\
Summary(pl.UTF-8):	Sterownik do karty Intel(R) PRO/1000\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%if %{with dist_kernel}\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
%endif\
\
%description -n kernel%{_alt_kernel}-net-igb\
This package contains the Linux driver for the Intel(R) PRO/1000\
adapters with 82575EB/GB or 82576 chipsets.\
\
%description -n kernel%{_alt_kernel}-net-igb -l pl.UTF-8\
Ten pakiet zawiera sterownik dla Linuksa do kart sieciowych z rodziny\
Intel(R) PRO/1000 opartych o układy 82575EB/GB lub 82576.\
\
%files	-n kernel%{_alt_kernel}-net-igb\
%defattr(644,root,root,755)\
%doc README\
%config(noreplace,missingok) %verify(not md5 mtime size) /etc/modprobe.d/%{_kernel_ver}/%{pname}.conf\
/lib/modules/%{_kernel_ver}/kernel/drivers/net/%{pname}*.ko*\
%{_mandir}/man7/igb.7*\
\
%post	-n kernel%{_alt_kernel}-net-igb\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-net-igb\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -C src -m %{pname}\
%install_kernel_modules -D installed -m src/%{pname} -d kernel/drivers/net -n %{pname} -s current\
%{nil}

%define install_kernel_pkg()\
install -d $RPM_BUILD_ROOT/etc/modprobe.d/%{_kernel_ver}\
# blacklist kernel module\
cat > $RPM_BUILD_ROOT/etc/modprobe.d/%{_kernel_ver}/%{pname}.conf <<'EOF'\
blacklist igb\
alias igb igb-current\
EOF\
%{nil}

%{expand:%kpkg}

%prep
%setup -q -n %{pname}-%{version}
cat > src/Makefile <<'EOF'
obj-m := igb.o
igb-objs := igb_main.o e1000_82575.o e1000_i210.o e1000_mac.o e1000_nvm.o e1000_phy.o \
	e1000_manage.o igb_param.o igb_ethtool.o kcompat.o e1000_api.o \
	e1000_mbx.o igb_vmdq.o igb_procfs.o igb_hwmon.o igb_ptp.o

EXTRA_CFLAGS += -DIGB_PTP
EXTRA_CFLAGS += -DDRIVER_IGB
EXTRA_CFLAGS += -DDRIVER_NAME=igb
EXTRA_CFLAGS += -DDRIVER_NAME_CAPS=IGB
EOF

%build
%{expand:%bkpkg}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_mandir}/man7

%{expand:%ikpkg}
cp -a installed/* $RPM_BUILD_ROOT

cp -a igb.7 $RPM_BUILD_ROOT%{_mandir}/man7

%clean
rm -rf $RPM_BUILD_ROOT
