%define		major 0
%define		libname %mklibname %{name} %{major}
%define		devname %mklibname -d %{name}

%global		_disable_lto 1
%global		_disable_ld_no_undefined 1

%global optflags %{optflags} -O3
%ifarch %{ix86}
%global ldflags %{ldflags} -fuse-ld=bfd
%endif

# (tpg) enable PGO build
%bcond_without	pgo
%bcond_without	expopt

Summary:		LAME Ain't an MP3 Encoder
Name:		lame
Version:		3.100
Release:		7
License:		LGPLv2
Group:		Sound
Url:		https://lame.sourceforge.net
# (tpg) https://github.com/rbrito/lame.git - Archived
Source0:	https://downloads.sourceforge.net/project/lame/lame/%{version}/%{name}-%{version}.tar.gz
# (tpg) patches from debian
Patch3:		07-field-width-fix.patch
Patch6:		privacy-breach.patch
Patch7:		msse.patch
Patch8:		pkg-config.patch
# Let's give it a performance boost...
Patch12:	http://tmkk.undo.jp/lame/lame-3.100-sse-20171014.diff
BuildRequires:		libtool
%ifarch %{ix86} %{x86_64}
BuildRequires:		nasm
%endif
BuildRequires:		gettext-devel
BuildRequires:		pkgconfig(gtk+-2.0)
BuildRequires:		pkgconfig(libmpg123)
BuildRequires:		pkgconfig(ncurses)
BuildRequires:		pkgconfig(x11)
BuildRequires:		pkgconfig(xau)
BuildRequires:		pkgconfig(xcb)
BuildRequires:		pkgconfig(xdmcp)
BuildRequires:		pkgconfig(xext)
BuildRequires:		pkgconfig(xi)

%description
Following the great history of GNU naming, LAME originally stood for LAME
Ain't an Mp3 Encoder. LAME started life as a GPL'd patch against the
dist10 ISO demonstration source, and thus was incapable of producing an
mp3 stream or even being compiled by itself. But in May 2000, the last
remnants of the ISO source code were replaced, and now LAME is the source
code for a fully GPL'd MP3 encoder, with speed and quality to rival all
commercial competitors.

LAME is an educational tool to be used for learning about MP3 encoding.
The goal of the LAME project is to use the open source model to improve
the psycho acoustics, noise shaping and speed of MP3.

LAME is not for everyone - it is distributed as source code only and
requires the ability to use a C compiler. However, many popular ripping
and encoding programs include the LAME encoding engine, see: Software
which uses LAME.

%files
%doc README TODO USAGE html/
%{_bindir}/%{name}
%{_bindir}/mp3rtp
%doc %{_mandir}/man1/%{name}.1*

#-----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Main library for lame
Group:		System/Libraries

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with libmp3lame.

%files -n %{libname}
%{_libdir}/libmp3lame.so.%{major}*

#-----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Headers for developing programs that will use libmp3lame
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
This package contains the headers that programmers will need to develop
applications which will use libmp3lame.

%files -n %{devname}
%doc STYLEGUIDE API ChangeLog
%{_includedir}/%{name}/%{name}.h
%{_libdir}/libmp3lame.so
%{_libdir}/pkgconfig/%{name}.pc

#-----------------------------------------------------------------------------

%prep
%autosetup -p1

ln -s acm ACM

cp -r doc/html .
# Clean unneeded files in doc dir
rm -rf html/CVS html/Makefile*
find html -name .cvsignore|xargs rm -f
find html -name "*.2~"|xargs rm -f


%build
# Needed for P8
autoreconf -vfi
sed -i -e 's/^\(\s*hardcode_libdir_flag_spec\s*=\).*/\1/' configure
export CC=gcc
export CXX=g++
%ifarch %{ix86}
export LD=%{_bindir}/ld.bfd
%endif

%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-generate  -lgcov" \
%configure \
%ifarch %{ix86} %{x86_64}
	--enable-nasm \
%endif
%if %{with expopt}
	--enable-expopt=full \
%endif
	--enable-dynamic-frontends \
	--enable-mp3rtp \
	--disable-gtktest

# The bundled libtool is extremely broken...
rm -f libtool
cp -f /usr/bin/libtool .

%make_build LIBS=-lm

make test

unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw

make clean

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA  -lgcov" \
%endif
%configure \
%ifarch %{ix86} %{x86_64}
	--enable-nasm \
%endif
%if %{with expopt}
	--enable-expopt=full \
%endif
	--enable-dynamic-frontends \
	--enable-mp3rtp \
	--disable-gtktest

# The bundled libtool is extremely broken...
rm -f libtool
cp -f /usr/bin/libtool .

%make_build LIBS=-lm


%check
make test


%install
mkdir -p %{buildroot}%{_bindir}
%make_install BINDIR=%{buildroot}%{_bindir}

# Clean unpackaged files
rm -rf %{buildroot}%{_datadir}/doc/%{name}
