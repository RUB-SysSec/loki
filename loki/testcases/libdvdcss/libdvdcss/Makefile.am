ACLOCAL_AMFLAGS = -I m4
AM_CPPFLAGS = -I$(top_srcdir)/src -I$(top_builddir)/src/dvdcss

EXTRA_DIST = msvc libdvdcss.spec INSTALL

dist_doc_DATA = AUTHORS COPYING NEWS README.md ChangeLog

MAINTAINERCLEANFILES = ChangeLog

ChangeLog: $(wildcard $(srcdir)/.git/logs/HEAD)
if GIT
	-cd $(srcdir) && git log > $(abs_builddir)/$(@)-tmp
	test -s $(@)-tmp && mv $(@)-tmp $(@)
	-rm -f $(@)-tmp
endif
	test -e $(@) || touch $(@)

lib_LTLIBRARIES = libdvdcss.la
EXTRA_PROGRAMS = test/csstest test/dvd_region

libdvdcss_la_SOURCES = \
	src/libdvdcss.c \
	src/libdvdcss.h \
	src/device.c \
	src/device.h \
	src/css.c \
	src/css.h \
	src/csstables.h \
	src/ioctl.c \
	src/ioctl.h \
	src/error.c \
	src/common.h

libdvdcss_la_LDFLAGS = -version-info $(DVDCSS_LTVERSION) $(DVDCSS_LDFLAGS)
libdvdcss_la_LIBADD =

if !SYS_MSVC
libdvdcss_la_LDFLAGS += -no-undefined
endif

test_csstest_SOURCES = test/csstest.c
test_csstest_LDADD = libdvdcss.la
test_csstest_CFLAGS = -I $(top_srcdir)/src

test_dvd_region_SOURCES = test/dvd_region.c
test_dvd_region_LDADD = libdvdcss.la
test_dvd_region_CFLAGS = -I $(top_srcdir)/src

pkgincludedir = $(includedir)/dvdcss
pkginclude_HEADERS = \
	src/dvdcss/dvdcss.h \
	src/dvdcss/version.h

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = src/libdvdcss.pc

if APIDOC
all-local: apidoc
install-data-local: install-apidoc
uninstall-hook: uninstall-apidoc
endif

apidoc: stamp-doxygen

stamp-doxygen: doc/doxygen.cfg src/libdvdcss.c src/dvdcss/dvdcss.h
	doxygen $<
	touch $@

tools: test/csstest$(EXEEXT) test/dvd_region$(EXEEXT)

clean-local:
	-rm -Rf stamp-doxygen doc/doxygen_sqlite3.db libdvdcss.spec doc/html

install-apidoc:
	$(MKDIR_P) $(DESTDIR)$(htmldir)
	for file in doc/html/*; do \
		$(INSTALL_DATA) $$file "$(DESTDIR)$(htmldir)" || exit 1; \
	done;

uninstall-apidoc:
	-rm -Rf $(DESTDIR)$(htmldir)/*.png $(DESTDIR)$(htmldir)/*.html $(DESTDIR)$(htmldir)/*.css $(DESTDIR)$(htmldir)/*.js

.PHONY: apidoc tools
