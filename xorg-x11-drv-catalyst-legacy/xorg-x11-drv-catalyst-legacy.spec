%global          atilibdir        %{_libdir}/catalyst-legacy
%global          atixorgdir       %{_libdir}/catalyst-legacy/xorg
%global          amdrun          amd-driver-installer-catalyst-%{version}-legacy-linux-x86.x86_64.run
%global    debug_package %{nil}

%global    __strip /bin/true
Name:            xorg-x11-drv-catalyst-legacy
Version:         13.1
Release:         2.hybridgfx.1%{?dist}
Summary:         AMD's proprietary driver for ATI legacy graphic cards
Group:           User Interface/X Hardware Support
License:         Redistributable, no modification permitted
URL:             http://www.ati.com/support/drivers/linux/radeon-linux.html
Source0:         http://www2.ati.com/drivers/legacy/amd-driver-installer-catalyst-%{version}-legacy-linux-x86.x86_64.zip
Source1:         http://developer.amd.com/downloads/xvba-sdk-0.74-404001.tar.gz
Source2:         catalyst-legacy-README.Fedora
Source3:         amdcccle.desktop
Source4:         catalyst-legacy-atieventsd.init
Source5:         catalyst-legacy-ati-powermode.sh
Source6:         catalyst-legacy-a-ac-aticonfig
Source7:         catalyst-legacy-a-lid-aticonfig
Source8:         00-catalyst-legacy.conf
Source10:        blacklist-radeon.conf

BuildRoot:       %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?fedora} > 11 || 0%{?rhel} > 5
ExclusiveArch: i686 x86_64
%else 0%{?fedora} == 11
ExclusiveArch: i586 x86_64
%else
ExclusiveArch: i386 x86_64
%endif

Requires:        catalyst-legacy-kmod >= %{version}

# Needed in all nvidia or fglrx driver packages
BuildRequires:   desktop-file-utils
# It seems rpaths were introduced into the amdcccle/amdnotifyui binary in 9.12
BuildRequires:   chrpath
%if 0%{?fedora} > 10 || 0%{?rhel} > 5
Requires:        %{name}-libs%{_isa} = %{version}-%{release}
%else
Requires:        %{name}-libs-%{_target_cpu} = %{version}-%{release}
%endif

Requires(post):  chkconfig

Requires(preun): chkconfig

Requires(post):  %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

Provides:        fglrx-hybrid-drivers%{_isa}

Provides:        catalyst-legacy-kmod-common = %{version}
Conflicts:       xorg-x11-drv-nvidia
Conflicts:       xorg-x11-drv-catalyst
Conflicts:       xorg-x11-drv-nvidia-legacy
Conflicts:       xorg-x11-drv-nvidia-71xx
Conflicts:       xorg-x11-drv-nvidia-96xx
Conflicts:       xorg-x11-drv-nvidia-173xx
Conflicts:       xorg-x11-drv-nvidia-beta
Conflicts:       xorg-x11-drv-nvidia-newest
Conflicts:       xorg-x11-drv-nvidia-custom
Conflicts:       xorg-x11-drv-fglrx
Obsoletes:       catalyst-legacy-kmod < %{version}

# ATI auto-generated RPMs
Conflicts:       ATI-fglrx
Conflicts:       ATI-fglrx-control-panel
Conflicts:       ATI-fglrx-devel
Conflicts:       kernel-module-ATI-fglrx
Conflicts:       ATI-fglrx-IA32-libs

%{?filter_setup:
%filter_from_provides /^libGL\.so/d;
%filter_from_requires /^libGL\.so/d;
%filter_setup
}

%description
This package provides the legacy proprietary AMD display driver which
allows for hardware accelerated rendering with ATI Mobility, FireGL and
Desktop GPUs. Some of the Desktop and Mobility GPUs supported are the
Radeon HD 2xxx series to the Radeon HD 6xxx series.

For the full product support list, please consult the release notes
for release %{version}.


%package devel
Summary:         Development files for %{name}
Group:           Development/Libraries
%if 0%{?fedora} > 10 || 0%{?rhel} > 5
Requires:        %{name}-libs%{_isa} = %{version}-%{release}
%else
Requires:        %{name}-libs-%{_target_cpu} = %{version}-%{release}
%endif

%description devel
This package provides the development files of the %{name}
package, such as OpenGL headers.


%package libs
Summary:         Libraries for %{name}
Group:           User Interface/X Hardware Support
Requires:        %{name} = %{version}-%{release}
Requires(post):  ldconfig
Provides:        %{name}-libs-%{_target_cpu} = %{version}-%{release}

Requires(post):  %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description libs
This package provides the shared libraries for %{name}.


%prep
%setup -q -c -T
# Unzip fglrx driver
unzip %{SOURCE0}
# Extract fglrx driver
sh %{amdrun} --extract fglrx

# Extract XvBA devel files
mkdir amdxvba
pushd amdxvba
tar xfz %{SOURCE1}
# rename docs
mv -f LICENSE AMD_XvBA_LICENSE
mv -f README AMD_XvBA_README
popd

# fix end line encoding
 sed -i "s|\r||g" fglrx/common/usr/share/doc/amdcccle/ccc_copyrights.txt

# Create tarball of kmod data for use later
tar -cjf catalyst-legacy-kmod-data-%{version}.tar.bz2 fglrx/common/usr/share/doc/fglrx/LICENSE.TXT \
                                            fglrx/common/*/modules/fglrx/ \
                                            fglrx/arch/*/*/modules/fglrx/

mkdir fglrxpkg
%ifarch %{ix86}
cp -r fglrx/common/* fglrx/xpic/* fglrx/arch/x86/* fglrxpkg/
%endif

%ifarch x86_64
cp -r fglrx/common/* fglrx/xpic_64a/* fglrx/arch/x86_64/* fglrxpkg/
%endif

# fix doc perms & copy README.Fedora
find fglrxpkg/usr/share/doc/fglrx -type f -exec chmod 0644 {} \;
install -pm 0644 %{SOURCE2} ./README.Fedora

# Set the correct path for gdm's Xauth file before we install it in the loop below
sed -i -e 's|GDM_AUTH_FILE=/var/lib/gdm/$1.Xauth|GDM_AUTH_FILE=/var/gdm/$1.Xauth|' fglrxpkg/etc/ati/authatieventsd.sh

%build
# Nothing to build
echo "Nothing to build"

%install
rm -rf $RPM_BUILD_ROOT ./__doc

set +x
for file in $(cd fglrxpkg &> /dev/null; find . -type f | grep -v -e 'amdcccle.kdelnk$' -e 'amdcccle.desktop$' -e 'lib/modules/fglrx$' -e 'fireglcontrolpanel$' -e '/usr/share/doc/fglrx/' -e 'fglrx_panel_sources.tgz$' -e 'amdcccle.*.desktop$' -e 'amdcccle.*.kdelnk' -e 'fglrx_sample_source.tgz$' -e '^./lib/modules/fglrx' -e '/usr/share/icons/ccc_' -e '^./usr/share/ati/lib')
do
  if [[ ! "/${file##}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} ./__doc/${file##./usr/share/doc/fglrx/}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/modules/drivers}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_libdir}/xorg/modules/drivers/${file##./usr/X11R6/%{_lib}/modules/drivers}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/modules/dri}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_prefix}/%{_lib}/dri/${file##./usr/X11R6/%{_lib}/modules/dri}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/modules/extensions/fglrx}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{atixorgdir}/${file##./usr/X11R6/%{_lib}/modules/extensions/fglrx}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/modules/extensions}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{atixorgdir}/${file##./usr/X11R6/%{_lib}/modules/extensions}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/modules}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_libdir}/xorg/modules/${file##./usr/X11R6/%{_lib}/modules}
%ifarch %{ix86}
  elif [[ ! "/${file##./usr/X11R6/lib/modules/dri}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_prefix}/lib/dri/${file##./usr/X11R6/lib/modules/dri}
%endif
  elif [[ ! "/${file##./usr/X11R6/include/X11/extensions}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_includedir}/fglrx/X11/extensions/${file##./usr/X11R6/include/X11/extensions}
  elif [[ ! "/${file##./usr/%{_lib}/fglrx}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{atilibdir}/${file##./usr/%{_lib}/fglrx}
  elif [[ ! "/${file##./usr/%{_lib}}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{atilibdir}/${file##./usr/%{_lib}/}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/fglrx}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{atilibdir}/${file##./usr/X11R6/%{_lib}/fglrx}
  elif [[ ! "/${file##./usr/X11R6/%{_lib}/}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{atilibdir}/${file##./usr/X11R6/%{_lib}/}
  elif [[ ! "/${file##./usr/X11R6/bin/}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_bindir}/${file##./usr/X11R6/bin/}
  elif [[ ! "/${file##./usr/bin/}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_sbindir}/${file##./usr/bin/}
  elif [[ ! "/${file##./usr/sbin/}" = "/${file}" ]]
  then
    install -D -p -m 0755 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_sbindir}/${file##./usr/sbin/}
  elif [[ ! "/${file##./etc/}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_sysconfdir}/${file##./etc/}
  elif [[ ! "/${file##./usr/include/}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_includedir}/fglrx/${file##./usr/include/}
  elif [[ ! "/${file##./usr/share/man/}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} $RPM_BUILD_ROOT/%{_mandir}/${file##./usr/share/man/}
  elif [[ ! "/${file##./usr/share/ati/amdcccle}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} $RPM_BUILD_ROOT/${file}
  elif [[ ! "/${file##./usr/share/doc/amdcccle}" = "/${file}" ]]
  then
    install -D -p -m 0644 fglrxpkg/${file} $RPM_BUILD_ROOT/${file}
  else
    echo ${file} found -- don\'t know how to handle
    exit 1
  fi
done
set -x

# Install XvBA headers
install -D -p -m 0644 amdxvba/include/amdxvba.h $RPM_BUILD_ROOT%{_includedir}/fglrx

# Remove switching scripts
rm -f $RPM_BUILD_ROOT%{atilibdir}/switchlibGL
rm -f $RPM_BUILD_ROOT%{atilibdir}/switchlibglx

# ATI says this is a 64-bit binary, but it's not.
rm -rf $RPM_BUILD_ROOT%{atilibdir}/libSlotMaximizerBe.so


# Remove some 'fglrx-' prefixes
mv $RPM_BUILD_ROOT%{atilibdir}/{fglrx-,}libGL.so.1.2
mv $RPM_BUILD_ROOT%{atixorgdir}/{fglrx-,}libglx.so

# Move XvBA data file to correct location
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib
mv $RPM_BUILD_ROOT%{atilibdir}/libAMDXvBA.cap $RPM_BUILD_ROOT%{_prefix}/lib
chmod 0644 $RPM_BUILD_ROOT%{_prefix}/lib/libAMDXvBA.cap

# Change perms on static libs. Can't fathom how to do it nicely above.
find $RPM_BUILD_ROOT%{atilibdir} -type f -name "*.a" -exec chmod 0644 '{}' \;

# If we want versioned libs, then we need to change this and the loop above
# to install the libs as soname.so.%%{version}
ln -s libGL.so.1.2 $RPM_BUILD_ROOT%{atilibdir}/libGL.so.1
ln -s libGL.so.1.2 $RPM_BUILD_ROOT%{atilibdir}/libGL.so
ln -s libfglrx_dm.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libfglrx_dm.so.1
ln -s libfglrx_dm.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libfglrx_dm.so
ln -s libAMDXvBA.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libAMDXvBA.so.1
ln -s libAMDXvBA.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libAMDXvBA.so
ln -s libXvBAW.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libXvBAW.so.1
ln -s libXvBAW.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libXvBAW.so
ln -s libatiuki.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libatiuki.so.1
ln -s libatiuki.so.1.0 $RPM_BUILD_ROOT%{atilibdir}/libatiuki.so

# move authatieventsd.sh to /usr/bin
mv $RPM_BUILD_ROOT%{_sysconfdir}/ati/authatieventsd.sh $RPM_BUILD_ROOT%{_bindir}

install -D -p -m 0644 fglrxpkg/usr/share/icons/ccc_large.xpm $RPM_BUILD_ROOT/%{_datadir}/icons/ccc_large.xpm
install -D -p -m 0755 %{SOURCE4} $RPM_BUILD_ROOT%{_initrddir}/atieventsd
install -D -p -m 0755 %{SOURCE5} $RPM_BUILD_ROOT%{_bindir}/ati-powermode.sh
install -D -p -m 0644 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/acpi/events/a-ac-aticonfig.conf
install -D -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/acpi/events/a-lid-aticonfig.conf

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
desktop-file-install --vendor rpmfusion \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications \
    %{SOURCE3}

# Install static driver dependant configuration files
install -m 0755 -d $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/
install -pm 0644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/X11/modulepath.fglrx.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/X11/modulepath.fglrx.conf
touch -r %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/X11/modulepath.fglrx.conf

# Fix odd perms
find fglrxpkg -type f -perm 0555 -exec chmod 0755 '{}' \;
find fglrxpkg -type f -perm 0744 -exec chmod 0755 '{}' \;
chmod 644 fglrxpkg/usr/src/ati/fglrx_sample_source.tgz
find $RPM_BUILD_ROOT -type f -name '*.a' -exec chmod 0644 '{}' \;
chmod 644 $RPM_BUILD_ROOT/%{_sysconfdir}/ati/*.xbm.example
chmod 755 $RPM_BUILD_ROOT/%{_bindir}/*.sh

# Remove rpaths (see comment on chrpath BR above)
chrpath --delete $RPM_BUILD_ROOT%{_bindir}/amdcccle
chrpath --delete $RPM_BUILD_ROOT%{_sbindir}/amdnotifyui

#Blacklist radeon
install -m 0755 -d $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d/
install -p -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d/

# Allow hybrid-detect package to add hybrid graphics functionality
install -m 0755 -d    $RPM_BUILD_ROOT%{_datadir}/fglrx/
echo "%{atilibdir}" > $RPM_BUILD_ROOT%{_datadir}/fglrx/fglrx-%{_lib}.conf

# For update-alternatives
install -m 0755 -d $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/
touch              $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/fglrx-%{_lib}.conf

# Alternative for Xorg configuration file
install -m 0755 -d $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/
touch              $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/00-gfx.conf


%clean
rm -rf $RPM_BUILD_ROOT


%post
# Install default alternative for Xorg configuration file
%{_sbindir}/update-alternatives --install \
  %{_sysconfdir}/X11/xorg.conf.d/00-gfx.conf \
  00-gfx.conf \
  %{_sysconfdir}/X11/modulepath.fglrx.conf \
  10

# Update the user's version numbers in the AMD Control Center.
if [ -f %{_sysconfdir}/amdpcsdb ];then
  ReleaseVersion=$(sed '/ReleaseVersion=S/!d; s/ReleaseVersion=S//' %{_sysconfdir}/ati/amdpcsdb.default 2>/dev/null)
  if [ -n "${ReleaseVersion}" ]; then
    %{_bindir}/aticonfig --del-pcs-key=LDC,ReleaseVersion >/dev/null 2>&1
    %{_bindir}/aticonfig --set-pcs-str=LDC,ReleaseVersion,${ReleaseVersion} >/dev/null 2>&1
  fi
  Catalyst_Version=$(sed '/Catalyst_Version=S/!d; s/Catalyst_Version=S//' %{_sysconfdir}/ati/amdpcsdb.default 2>/dev/null)
  if [ -n "${Catalyst_Version}" ]; then
    %{_bindir}/aticonfig --del-pcs-key=LDC,Catalyst_Version >/dev/null 2>&1
    %{_bindir}/aticonfig --set-pcs-str=LDC,Catalyst_Version,${Catalyst_Version} >/dev/null 2>&1
  fi
fi ||:

if [ "${1}" -eq 1 ]; then
  # Add init script(s) and start it
  /sbin/chkconfig --add atieventsd
  /sbin/service atieventsd start >/dev/null 2>&1
  if [ -x /sbin/grubby ] ; then
    GRUBBYLASTKERNEL=`/sbin/grubby --default-kernel`
    /sbin/grubby --update-kernel=${GRUBBYLASTKERNEL} --args='radeon.modeset=0' &>/dev/null
  fi
fi ||:

%post libs
# Ensure that the old ldconfig configuration file is removed
rm -f %{_sysconfdir}/ld.so.conf.d/catalyst-legacy-%{_lib}.conf

# Install default alternatives for libraries
%{_sbindir}/update-alternatives --install \
  %{_sysconfdir}/ld.so.conf.d/fglrx-%{_lib}.conf \
  fglrx-%{_lib}.conf \
  %{_datadir}/fglrx/fglrx-%{_lib}.conf \
  10

/sbin/ldconfig

%preun
# Remove alternative
%{_sbindir}/update-alternatives --remove \
  00-gfx.conf \
  %{_sysconfdir}/X11/modulepath.fglrx.conf

if [ "${1}" -eq 0 ]; then
  /sbin/service atieventsd stop >/dev/null 2>&1
  /sbin/chkconfig --del atieventsd
  if [ -x /sbin/grubby ] ; then
    # remove rdblacklist from boot params in case they installed with v10.7, which blacklisted radeon upon installation
    GRUBBYLASTKERNEL=`/sbin/grubby --default-kernel`
    /sbin/grubby --update-kernel=${GRUBBYLASTKERNEL} --remove-args='radeon.modeset=0 rdblacklist=radeon' &>/dev/null
  fi
fi ||:

%postun libs
# Remove alternative
%{_sbindir}/update-alternatives --remove \
  fglrx-%{_lib}.conf \
  %{_datadir}/fglrx/fglrx-%{_lib}.conf

/sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc fglrxpkg/usr/share/doc/fglrx/* README.Fedora
%dir %{_sysconfdir}/ati/
%doc %{_docdir}/amdcccle/ccc_copyrights.txt
%config(noreplace) %{_sysconfdir}/security/console.apps/amdcccle-su
%config %{_sysconfdir}/X11/modulepath.fglrx.conf
%{_prefix}/lib/modprobe.d/blacklist-radeon.conf
%{_sysconfdir}/ati/atiogl.xml
%{_sysconfdir}/ati/logo.xbm.example
%{_sysconfdir}/ati/logo_mask.xbm.example
%{_sysconfdir}/ati/amdpcsdb.default
# OpenCL files
%dir %{_sysconfdir}/OpenCL
%dir %{_sysconfdir}/OpenCL/vendors
%config %{_sysconfdir}/OpenCL/vendors/amd*.icd
# These next two files control "supported hardware" verification
%{_sysconfdir}/ati/signature
%{_sysconfdir}/ati/control
%config(noreplace) %{_sysconfdir}/acpi/events/*aticonfig.conf
%{_initrddir}/*
%{_sbindir}/*
%{_bindir}/*
# no_multilib
%{_libdir}/xorg/modules/drivers/fglrx_drv.so
%{_libdir}/xorg/modules/linux/libfglrxdrm.so
%{atixorgdir}/
%{_libdir}/xorg/modules/*.so
%{_prefix}/lib/libAMDXvBA.cap
# /no_multilib
%{_datadir}/applications/*amdcccle.desktop
%{_datadir}/ati/amdcccle/*
%{_datadir}/icons/*
%{_mandir}/man[1-9]/atieventsd.*

# For update-alternatives
%ghost %{_sysconfdir}/X11/xorg.conf.d/00-gfx.conf

%files libs
%defattr(-,root,root,-)
%dir %{atilibdir}
%{atilibdir}/*.so*
%{_libdir}/dri/

# For update-alternatives
%ghost %{_sysconfdir}/ld.so.conf.d/fglrx-%{_lib}.conf
%{_datadir}/fglrx/fglrx-%{_lib}.conf
%dir %{_datadir}/fglrx/

%files devel
%defattr(-,root,root,-)
%doc fglrxpkg/usr/src/ati/fglrx_sample_source.tgz
%doc amdxvba/doc/AMD_XvBA_Spec_v0_74_01_AES_2.pdf
%doc amdxvba/AMD_XvBA_LICENSE amdxvba/AMD_XvBA_README
%{atilibdir}/*.a
%{_includedir}/fglrx/
# enumerate development symlinks
%{atilibdir}/libGL.so
%{atilibdir}/libfglrx_dm.so
%{atilibdir}/libAMDXvBA.so
%{atilibdir}/libXvBAW.so
%{atilibdir}/libatiuki.so


%changelog
* Wed May 01 2013 Xiao-Long Chen <chenxiaolong@cxl.epac.to> - 13.1-2.hybridgfx.1
- Use 'fglrx' instead of 'catalyst-legacy' for paths that use the alternatives
  system
  - I won't need to hardcode 'catalyst' and 'catalyst-legacy' in hybrid-detect

* Tue Apr 30 2013 Xiao-Long Chen <chenxiaolong@cxl.epac.to> - 13.1-2.hybridgfx
- Add hacky hybrid graphics support using alternatives

* Mon Feb 04 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.1-2
- add blacklist file to %%{_prefix}/lib/modprobe.d/

* Mon Feb 04 2013 Leigh Scott <leigh123linux@googlemail.com> - 13.1-1
- Update to Catalyst legacy (internal version 13.1 8.97.100.7)

* Fri Sep 21 2012 Leigh Scott <leigh123linux@googlemail.com> - 12.6-3
- make review changes

* Wed Aug 22 2012 Leigh Scott <leigh123linux@googlemail.com> - 12.6-2
- make review changes

* Fri Aug 17 2012 Leigh Scott <leigh123linux@googlemail.com> - 12.6-1
- 12.6 released
- Change how the amd source is unpacked
- Fix source url
- change %%define to %%global

* Sun Jun 24 2012 leigh scott <leigh123linux@googlemail.com> - 12.6-0.1
- Based on xorg-x11-drv-catalyst
- Update to Catalyst legacy 12.6 beta (internal version 8.97.100.3)
