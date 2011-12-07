%define formats rom
# ne is only for backwards compat with older versions of qemu
%define qemuroms rtl8029 ne e1000-0x100e pcnet32 rtl8139 virtio-net
%define buildarches x86_64

# debugging firmwares does not goes the same way as a normal program.
# moreover, all architectures providing debuginfo for a single noarch
# package is currently clashing in koji, so don't bother.
%global debug_package %{nil}

Name:    gpxe
Version: 0.9.7
Release: 6.3%{?dist}
Summary: A network boot loader

Group:   System Environment/Base
License: GPLv2 and BSD
URL:     http://etherboot.org/

Source0: http://git.etherboot.org/releases/%{name}/%{name}-%{version}.tar.bz2
Source1: USAGE
# For bz#579964 - Keyboard cannot be used during pxe boot when using one kind of pxe server
Patch1: gpxe-Don-t-use-lret-2-to-return-from-an-interrupt.patch
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

ExclusiveArch: %{buildarches}

%ifarch %{buildarches}
BuildRequires: perl syslinux mtools mkisofs

%package bootimgs
Summary: Network boot loader images in bootable USB, CD, floppy and GRUB formats
Group:   Development/Tools
BuildArch: noarch

%package roms
Summary: Network boot loader roms in .rom format
Group:  Development/Tools
Requires: %{name}-roms-qemu = %{version}-%{release}
BuildArch: noarch

%package roms-qemu
Summary: Network boot loader roms supported by QEMU, .rom format
Group:  Development/Tools
BuildArch: noarch


%description bootimgs
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the gPXE boot images in USB, CD, floppy, and PXE
UNDI formats.

%description roms
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the gPXE roms in .rom format.


%description roms-qemu
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

This package contains the gPXE ROMs for devices emulated by QEMU, in
.rom format.
%endif

%description
gPXE is an open source network bootloader. It provides a direct
replacement for proprietary PXE ROMs, with many extra features such as
DNS, HTTP, iSCSI, etc.

%prep
%setup -q
%patch1 -p1
cp -a %{SOURCE1} .

%build
%ifarch %{buildarches}
# Fedora 10 and newer, location is in /usr/share.  Older is in /usr/lib.
ISOLINUX_BIN=/usr/share/syslinux/isolinux.bin
[ -e /usr/lib/syslinux/isolinux.bin ] && ISOLINUX_BIN=/usr/lib/syslinux/isolinux.bin
cd src
make %{?_smp_mflags} ISOLINUX_BIN=${ISOLINUX_BIN}
make %{?_smp_mflags} bin/gpxe.lkrn
# The bnx2 firmware is too large to fit into an option ROM.
rm drivers/net/bnx2*.[ch]
make %{?_smp_mflags} allroms
%endif

%install
rm -rf $RPM_BUILD_ROOT
%ifarch %{buildarches}
mkdir -p %{buildroot}/%{_datadir}/%{name}/
pushd src/bin/

cp -a undionly.kpxe gpxe.{iso,usb,dsk,lkrn} %{buildroot}/%{_datadir}/%{name}/

for fmt in %{formats};do
 for img in *.${fmt};do
      if [ -e $img ]; then
   cp -a $img %{buildroot}/%{_datadir}/%{name}/
   echo %{_datadir}/%{name}/$img >> ../../${fmt}.list
  fi   
 done
done
popd

# the roms supported by qemu will be packaged separatedly
# remove from the main rom list and add them to qemu.list
for fmt in rom ;do 
 for rom in %{qemuroms} ; do
  sed -i -e "/\/${rom}.${fmt}/d" ${fmt}.list
  echo %{_datadir}/%{name}/${rom}.${fmt} >> qemu.${fmt}.list
 done
done
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%ifarch %{buildarches}
%files bootimgs
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/gpxe.iso
%{_datadir}/%{name}/gpxe.usb
%{_datadir}/%{name}/gpxe.dsk
%{_datadir}/%{name}/gpxe.lkrn
%{_datadir}/%{name}/undionly.kpxe
%doc COPYING COPYRIGHTS USAGE

%files roms -f rom.list
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%doc COPYING COPYRIGHTS

%files roms-qemu -f qemu.rom.list
%defattr(-,root,root,-)
%dir %{_datadir}/%{name}
%doc COPYING COPYRIGHTS
%endif

%changelog
* Mon Apr 26 2010 Eduardo Habkost <ehabkost@redhat.com> - gpxe-0.9.7-6.3.el6
- gpxe-Don-t-use-lret-2-to-return-from-an-interrupt.patch [bz#579964]
- Resolves: bz#579964
  (Keyboard cannot be used during pxe boot when using one kind of pxe server)

* Wed Jan 13 2010 Eduardo Habkost <ehabkost@redhat.com> - gpxe-0.9.7-6.2.el6
- Build only on x86_64
- Resolves: bz#554863
  (gpxe should not be shipped on i686/ppc64/s390x, only on x86_64)

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0.9.7-6.1
- Rebuilt for RHEL 6

* Mon Oct  5 2009 Matt Domsch <mdomsch@fedoraproject.org> - 0.9.7-6
- move rtl8029 from -roms to -roms-qemu for qemu ne2k_pci NIC (BZ 526776)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 19 2009 Matt Domsch <mdomsch@fedoraproject.org> - 0.9.7-4
- add undionly.kpxe to -bootimgs

* Tue May 12 2009 Matt Domsch <mdomsch@fedoraproject.org> - 0.9.7-3
- handle isolinux changing paths

* Sat May  9 2009 Matt Domsch <mdomsch@fedoraproject.org> - 0.9.7-2
- add dist tag

* Thu Mar 26 2009 Matt Domsch <mdomsch@fedoraproject.org> - 0.9.7-1
- Initial release based on etherboot spec
