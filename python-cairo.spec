%if 0%{?qubes_builder}
%define _sourcedir %(pwd)
%endif

%global cairo_version 1.10.2

Name:		python34-cairo
Version:	1.10.0
Release:	2%{?dist}
Summary:	Python 3 bindings for the cairo library

License:	MPLv1.1 or LGPLv2
URL:		http://cairographics.org/pycairo
Source0:	http://cairographics.org/releases/pycairo-%{version}.tar.bz2

# Since Python 3.4, pythonX.Y-config is shell script, not Python script,
#  so prevent waf from trying to invoke it as a Python script
Patch0:		cairo-waf-use-python-config-as-shell-script.patch
Patch1:		pycairo-1.10.0-test-python3.patch
# https://bugs.freedesktop.org/show_bug.cgi?id=91561
Patch2:		pycairo-1.10.0-pickle-python3.patch

BuildRequires:	cairo-devel >= %{cairo_version}
BuildRequires:	python34-devel
BuildRequires:	python34-pytest
BuildRequires:	lyx-fonts

%description
Python 3 bindings for the cairo library.


%package devel
Summary:	Libraries and headers for python3-cairo
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	cairo-devel%{?_isa}
Requires:	python34-devel%{?_isa}

%description devel
This package contains files required to build wrappers for cairo add-on
libraries so that they interoperate with python3-cairo.


%prep
%setup -qn pycairo-%{version}

# Ensure that ./waf has created the cached unpacked version
# of the wafadmin source tree.
# This will be created to a subdirectory like
#    .waf3-1.5.18-a7b91e2a913ce55fa6ecdf310df95752
%{__python3} ./waf --version

%patch0 -p0
%patch1 -p1
%patch2 -p1

# Make sure we explicitly use Python34.
for f in $(%{__grep} -Rl '#!.*python$') ; do
  %{__sed} -e 's~#!.*python$~#!%{__python3}~g' < ${f} > ${f}.new
  /bin/touch -r ${f}.new ${f}
  mode="$(%{_bindir}/stat -c '%a' ${f})"
  %{__mv} -f ${f}.new ${f}
  %{__chmod} -c ${mode} ${f}
done


%build
%configure || :
export PYTHON=%{__python3}
%{__python3} ./waf		\
	--prefix=%{_usr}	\
	--libdir=%{_libdir}	\
	configure

# do not fail on utf-8 encoded files
LANG=en_US.utf8 %{__python3} ./waf build -v

# remove executable bits from examples
%{_bindir}/find ./examples/ -type f -print0 | %{_bindir}/xargs -0 %{__chmod} -c -x


%install
DESTDIR=%{buildroot} %{__python3} ./waf install

# add executable bit to the .so libraries so we strip the debug info
%{_bindir}/find %{buildroot} -name '*.so' | %{_bindir}/xargs %{__chmod} -c +x

%{_bindir}/find %{buildroot} -name '*.la' | %{_bindir}/xargs %{__rm} -f

# Remove stowaway py2 build artifacts
%{_bindir}/find %{buildroot} -name '*.pyc' | %{_bindir}/xargs %{__rm} -f
%{_bindir}/find %{buildroot} -name '*.pyo' | %{_bindir}/xargs %{__rm} -f


%check
cd test
PYTHONPATH=%{buildroot}%{python3_sitearch} %{_bindir}/py.test-3


%files
%license COPYING*
%doc AUTHORS NEWS README
%doc examples doc/faq.rst doc/overview.rst doc/README
%{python3_sitearch}/cairo/


%files devel
%dir %{_includedir}/pycairo
%{_includedir}/pycairo/py3cairo.h
%{_libdir}/pkgconfig/py3cairo.pc


%changelog
* Mon Sep 04 2017 Björn Esser <besser82@fedoraproject.org> - 1.10.0-2
- Initial import (rhbz#1487581)

* Fri Sep 01 2017 Björn Esser <besser82@fedoraproject.org> - 1.10.0-1
- Updated to v1.10.0, since python34-gobject requires at least that version

* Fri Sep 01 2017 Björn Esser <besser82@fedoraproject.org> - 1.8.10-1
- Initial rpm release for EPEL7 (rhbz#1487581)
