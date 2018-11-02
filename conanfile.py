from conans import ConanFile, CMake, tools, Meson
import os

class OrcConan(ConanFile):
    name = "orc"
    version = "0.4.28"
    description = "Optimized Inner Loop Runtime Compiler"
    url = "https://github.com/conanos/orc"
    homepage = 'https://cgit.freedesktop.org/gstreamer/orc'
    license = "BSD"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

    source_subfolder = "source_subfolder"

    def source(self):
        tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'https://gstreamer.freedesktop.org/src/orc/%s'%(archive_name)
        tools.download(url_, archive_name)

        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('%s-%s' %(self.name, self.version), self.source_subfolder)
        os.unlink(archive_name)

    def build(self):
        with tools.chdir(self.source_subfolder):
            meson = Meson(self)
            meson.configure(
                defs={'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib'},
                source_dir = '%s'%(os.getcwd()),
                build_dir= '%s/builddir'%(os.getcwd()),
                )
            meson.build(args=['-j2'])
            self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

