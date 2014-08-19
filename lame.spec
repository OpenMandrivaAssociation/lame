%define major		0
%define libname	%mklibname %{name} %{major}
%define develname	%mklibname -d %{name}
# %define staticname	%mklibname -d -s %{name}

%define expopt 1

Name:		lame
Version:	3.99.5
Release:	6
Summary:	LAME Ain't an MP3 Encoder
License:	LGPL
Group:		Sound
URL:		http://lame.sourceforge.net
Source0:	http://netcologne.dl.sourceforge.net/project/lame/lame/3.99/lame-%version.tar.gz
BuildRequires:	pkgconfig(ncurses)
%ifarch %{ix86}
BuildRequires:	nasm
%endif
BuildRequires:	pkgconfig(xi)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xau)
BuildRequires:	pkgconfig(xdmcp)
BuildRequires:	pkgconfig(xcb)

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

Personal and commercial use of compiled versions of LAME (or any other mp3 
encoder) requires a patent license in some countries.

This package is in restricted, as MP3 encoding is covered by software patents.

%package -n %{libname}
Summary:	Main library for lame
Group:		System/Libraries
Provides:	lib%{name} = %EVRD

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with libmp3lame.

This package is in restricted, as MP3 encoding is covered by software patents.

%package -n %{develname}
Summary:	Headers for developing programs that will use libmp3lame
Group:		Development/C
Requires:	%{libname} = %EVRD
Provides:	%{name}-devel = %EVRD
Provides:	lib%{name}-devel = %EVRD

%description -n %{develname}
This package contains the headers that programmers will need to develop
applications which will use libmp3lame.

This package is in restricted, as MP3 encoding is covered by software patents.

# %package -n %{staticname}
#Summary:	Static library for developing programs based on libmp3lame
#Group:		Development/C
#Requires:	%{develname} = %EVRD
#Provides:	%{name}-static-devel = %EVRD
#Provides:	lib%{name}-static-devel = %EVRD

# %description -n %{staticname}
# This package contains the static library programmers will need to develop
# applications which will use libmp3lame.

# This package is in restricted, as MP3 encoding is covered by software patents.

%prep
%setup -q
ln -s acm ACM
cp -r doc/html .
#clean unneeded files in doc dir
rm -rf html/CVS html/Makefile*
find html -name .cvsignore|xargs %__rm -f

%build
%if !%{expopt}
export CFLAGS="`echo %{optflags} |sed s/-O[23]/-O1/`"
%endif

export GTK_CONFIG=%{_bindir}/gtk-config

%configure2_5x \
%ifarch %{ix86}
	--enable-nasm \
%endif
%if %{expopt}
	--enable-expopt \
%endif
	--without-vorbis --enable-brhist

%make LIBS=-lm

%check
%make test

%install
mkdir -p %{buildroot}%{_bindir}
%makeinstall BINDIR=%{buildroot}%{_bindir}
#clean unpackaged files
rm -rf %{buildroot}%{_datadir}/doc/lame

%files
%doc README TODO USAGE html/
%{_bindir}/lame
%{_mandir}/man1/lame.1*

%files -n %{libname}
%doc README
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%doc STYLEGUIDE API ChangeLog
%{_includedir}/*
%{_libdir}/libmp3lame.so

# %files -n %{staticname}
# %{_libdir}/libmp3lame.a
