Summary:	Lazarus Component Library and IDE for Freepascal
Name:		lazarus
Version:	1.8.0
Release:	1
# GNU Classpath style exception, see COPYING.modifiedLGPL
License:	GPLv2+ and MPLv1.1 and LGPLv2+ with exceptions
Group:		Development/Pascal
Url:		http://www.lazarus-ide.org/
# Source0:	https://sourceforge.net/projects/lazarus/files/Lazarus%20Zip%20_%20GZip/Lazarus%201.6.4/lazarus-1.6.4-0.tar.gz/download
Source0:	%{name}-%{version}.tar.gz
Source1:	lazarus-miscellaneousoptions
Source10:	lazarus.rpmlintrc
Patch0:		lazarus-1.4.4-makefile.patch
Patch1:		lazarus-1.4.4-desktop.patch
Patch3:		add_gdb_settings.patch
BuildRequires:	desktop-file-utils
BuildRequires:	fpc >= 2.6.4
BuildRequires:	fpc-src >= 2.6.4
BuildRequires:	gdb
BuildRequires:	pkgconfig(gdk-pixbuf-2.0)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
Requires:	binutils
Requires:	fpc >= 2.6.4
Requires:	fpc-src >= 2.6.4
Requires:	gdb
Requires:	pkgconfig(gdk-pixbuf-2.0)
Requires:	pkgconfig(glib-2.0)
Requires:	pkgconfig(gtk+-2.0)
Requires:	glibc-devel

%description
Lazarus is a free and opensource RAD tool for freepascal using the lazarus
component library - LCL, which is also included in this package.

%files
%doc lazarus/COPYING* lazarus/README.txt
%{_libdir}/%{name}
%{_bindir}/%{name}-ide
%{_bindir}/startlazarus
%{_bindir}/lazbuild
%{_bindir}/%{name}-miscellaneousoptions
%{_datadir}/pixmaps/lazarus.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/mime/packages/lazarus.xml
%dir %{_sysconfdir}/lazarus
#%config(noreplace) %{_sysconfdir}/lazarus/editoroptions.xml
%config(noreplace) %{_sysconfdir}/lazarus/environmentoptions.xml
%{_mandir}/*/*

%postun
if [ $1 = 0 ]
then
rm -rf %{_libdir}/%{name}
fi

#----------------------------------------------------------------------------

%prep
%setup -qc
%patch0 -p1
%patch1 -p1
%patch3 -p0

%build
cd lazarus
# Remove the files for building debian-repositories
rm -rf debian
pushd tools
find install -depth -type d ! \( -path "install/linux/*" -o -path "install/linux" -o -path "install" \) -exec rm -rf '{}' \;
popd

export FPCDIR=%{_datadir}/fpcsrc/
fpcmake -Tall

MAKEOPTS="-gl -gw -Fl/usr/%{_lib}"

make bigide OPT="$MAKEOPTS"
make tools OPT="$MAKEOPTS"
make lazbuild OPT="$MAKEOPTS"

# Add the ability to create gtk2-applications
export LCL_PLATFORM=gtk2
make packager/registration lazutils lcl codetools bigidecomponents OPT='-gl -gw'
export LCL_PLATFORM=
strip lazarus
strip startlazarus
strip lazbuild

%install
LAZARUSDIR=%{_libdir}/%{name}
FPCDIR=%{_datadir}/fpcsrc/
mkdir -p %{buildroot}$LAZARUSDIR
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/pixmaps
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/mime/packages
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_sysconfdir}/lazarus
cp -a lazarus/* %{buildroot}$LAZARUSDIR/
install -m 0644 lazarus/images/ide_icon48x48.png %{buildroot}%{_datadir}/pixmaps/lazarus.png
install -m 0644 lazarus/install/lazarus.desktop %{buildroot}%{_datadir}/applications/lazarus.desktop
install -m 0644 lazarus/install/lazarus-mime.xml $LazBuildDir%{buildroot}%{_datadir}/mime/packages/lazarus.xml
ln -sf $LAZARUSDIR/lazarus %{buildroot}%{_bindir}/lazarus-ide
ln -sf $LAZARUSDIR/startlazarus %{buildroot}%{_bindir}/startlazarus
ln -sf $LAZARUSDIR/lazbuild %{buildroot}%{_bindir}/lazbuild
cat lazarus/install/man/man1/lazbuild.1 | gzip > %{buildroot}%{_mandir}/man1/lazbuild.1.gz
cat lazarus/install/man/man1/lazarus-ide.1 | gzip > %{buildroot}%{_mandir}/man1/lazarus-ide.1.gz
cat lazarus/install/man/man1/startlazarus.1 | gzip > %{buildroot}%{_mandir}/man1/startlazarus.1.gz
#install lazarus/tools/install/linux/editoroptions.xml %{buildroot}%{_sysconfdir}/lazarus/editoroptions.xml

# fix fpc and lazarus path
install lazarus/tools/install/linux/environmentoptions.xml %{buildroot}%{_sysconfdir}/lazarus/environmentoptions.xml
sed -i 's/\$(FPCVER)\///g' %{buildroot}%{_sysconfdir}/lazarus/environmentoptions.xml
sed -i 's/%LazarusVersion%//g' %{buildroot}%{_sysconfdir}/lazarus/environmentoptions.xml

#Fix config path (akdengi)
sed -i 's#__LAZARUSDIR__#'$LAZARUSDIR/'#g' %{buildroot}%{_sysconfdir}/lazarus/environmentoptions.xml
sed -i 's#__FPCSRCDIR__#'$FPCDIR'#g' %{buildroot}%{_sysconfdir}/lazarus/environmentoptions.xml

chmod 755 %{buildroot}%{_libdir}/%{name}/components/lazreport/tools/localize.sh

pushd %{buildroot}%{_libdir}/%{name}
rm -f *.txt
rm -rf install
popd

install -m 755 %{SOURCE1} %{buildroot}%{_bindir}/

%changelog
