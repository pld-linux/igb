# Conditional build:
%bcond_with	verbose		# verbose build (V=1)

# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0

%define		_duplicate_files_terminate_build	0

%define		rel	1
%define		pname	igb
Summary:	Intel(R) PRO/1000 driver for Linux
Summary(pl.UTF-8):	Sterownik do karty Intel(R) PRO/1000
Name:		%{pname}%{_alt_kernel}
Version:	5.3.2
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://downloads.sourceforge.net/e1000/%{pname}-%{version}.tar.gz
# Source0-md5:	dbedbb2cefaf3fa09eb5a4912914cdac
Patch0:		timespec64.patch
URL:		http://sourceforge.net/projects/e1000/
%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpm-build-macros >= 1.701
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
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
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

%{expand:%create_kernel_packages}

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1

cat > src/Makefile <<'EOF'
obj-m := igb.o
igb-objs := igb_main.o e1000_82575.o e1000_i210.o e1000_mac.o e1000_nvm.o e1000_phy.o \
	e1000_manage.o igb_param.o igb_ethtool.o kcompat.o e1000_api.o \
	e1000_mbx.o igb_vmdq.o igb_procfs.o igb_hwmon.o igb_ptp.o igb_debugfs.o

EXTRA_CFLAGS += -DIGB_PTP
EXTRA_CFLAGS += -DDRIVER_IGB
EXTRA_CFLAGS += -DDRIVER_NAME=igb
EXTRA_CFLAGS += -DDRIVER_NAME_CAPS=IGB
EOF

%build
%{expand:%build_kernel_packages}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_mandir}/man7

%{expand:%install_kernel_packages}
cp -a installed/* $RPM_BUILD_ROOT

cp -a igb.7 $RPM_BUILD_ROOT%{_mandir}/man7

%clean
rm -rf $RPM_BUILD_ROOT
