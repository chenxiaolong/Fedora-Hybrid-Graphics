# Written by: Xiao-Long Chen <chenxiaolong@cxl.epac.to>

Name:		hybrid-detect-fglrx
Version:	1.0
Release:	1%{?dist}
Summary:	Utility for automatic graphics switching on systems with Intel and ATI/AMD graphics

Group:		User Interface/X Hardware Support
License:	GPLv2+
# Based on Ubuntu's nvidia-common package
#URL:		
Source0:	hybrid-detect-fglrx.c
Source1:        hybrid-detect.service
Source2:        modulepath.intel.conf

BuildRequires:	libpciaccess-devel
BuildRequires:  systemd-units

Requires(post):  %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
Requires(post):  systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

Requires:       fglrx-hybrid-drivers%{_isa}
Requires:	xorg-x11-drv-intel%{_isa}

Conflicts:	hybrid-detect
Conflicts:	hybrid-detect-nvidia


%description
This package contains a utility that allows laptops with hybrid graphics and
a hardware mux to switch between the integrated and dedicated graphics cards
without removing the fglrx packages.


%prep
%setup -q -c -T -n %{name}-%{version}
cp %{SOURCE0} .


%build
gcc -o hybrid-detect hybrid-detect-fglrx.c $(pkg-config --cflags --libs pciaccess)


%install
install -m 0755 -d               $RPM_BUILD_ROOT%{_sbindir}/
install -m 0755    hybrid-detect $RPM_BUILD_ROOT%{_sbindir}/

# systemd service
install -m 0755 -d            $RPM_BUILD_ROOT%{_unitdir}/
install -m 0644    %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/

# File required by hybrid-detect (ghosted in the files section)
install -m 0755 -d $RPM_BUILD_ROOT%{_sharedstatedir}/hybrid-detect/
touch              $RPM_BUILD_ROOT%{_sharedstatedir}/hybrid-detect/last_gfx_boot

# Xorg modulepath configuration for Intel
install -m 0755 -d         $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/X11/
sed -i -e 's|@LIBDIR@|%{_libdir}|g' \
                           $RPM_BUILD_ROOT%{_sysconfdir}/X11/modulepath.intel.conf

# For update-alternatives
touch $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/00-gfx.conf
install -m 0755 -d $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/
touch $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/fglrx-lib.conf
%ifarch x86_64
touch $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/fglrx-lib64.conf
%endif


%post
rm %{_sharedstatedir}/hybrid-detect/last_gfx_boot &>/dev/null || :

# Install alternative for Xorg configuration file
%{_sbindir}/update-alternatives --install \
  %{_sysconfdir}/X11/xorg.conf.d/00-gfx.conf \
  00-gfx.conf \
  %{_sysconfdir}/X11/modulepath.intel.conf \
  10

# Install alternatives for nVidia libraries
%{_sbindir}/update-alternatives --install \
  %{_sysconfdir}/ld.so.conf.d/fglrx-lib.conf \
  fglrx-lib.conf \
  /dev/null \
  10

%ifarch x86_64
%{_sbindir}/update-alternatives --install \
  %{_sysconfdir}/ld.so.conf.d/fglrx-lib64.conf \
  fglrx-lib64.conf \
  /dev/null \
  10
%endif

# Run hybrid-detect to set the alternatives based on whether the Intel or AMD
# graphics card is enabled.
%{_sbindir}/hybrid-detect &>/dev/null || :

if [ ${1} -eq 1 ]; then
  # Initial installation
  /bin/systemctl daemon-reload &>/dev/null || :
  # Enable service
  /bin/systemctl enable hybrid-detect.service &>/dev/null || :
fi


%preun
# Remove alternative for Xorg configuration file
%{_sbindir}/update-alternatives --remove \
  00-gfx.conf \
  %{_sysconfdir}/X11/modulepath.intel.conf

# Remove alternatives for nVidia libraries
%{_sbindir}/update-alternatives --remove \
  fglrx-lib.conf \
  /dev/null

%ifarch x86_64
%{_sbindir}/update-alternatives --remove \
  fglrx-lib64.conf \
  /dev/null
%endif

/sbin/ldconfig

if [ ${1} -eq 0 ]; then
  # Package removal
  /bin/systemctl --no-reload disable hybrid-detect.service &>/dev/null || :
fi


%postun
/bin/systemctl daemon-reload &>/dev/null || :


%files
%defattr(-,root,root,-)
%{_sbindir}/hybrid-detect
%{_unitdir}/hybrid-detect.service
%ghost %{_sharedstatedir}/hybrid-detect/last_gfx_boot
%dir %{_sharedstatedir}/hybrid-detect/

# For update-alternatives
%ghost %{_sysconfdir}/X11/xorg.conf.d/00-gfx.conf
%{_sysconfdir}/X11/modulepath.intel.conf
%ghost %{_sysconfdir}/ld.so.conf.d/fglrx-lib.conf
%ifarch x86_64
%ghost %{_sysconfdir}/ld.so.conf.d/fglrx-lib64.conf
%endif


%changelog
* Wed May 01 2013 Xiao-Long Chen <chenxiaolong@cxl.epac.to> - 1.0-1
- Initial release for AMD/ATI graphics
