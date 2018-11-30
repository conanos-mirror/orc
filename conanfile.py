from conans import ConanFile, CMake, tools, Meson
from conanos.build import config_scheme
import os
import shutil

class OrcConan(ConanFile):
    name = "orc"
    version = "0.4.28"
    description = "Optimized Inner Loop Runtime Compiler"
    url = "https://github.com/conanos/orc"
    homepage = 'https://github.com/GStreamer/orc'
    license = "BSD"
    patch = "gtkdoc-disabled.patch"
    patch_def = "windows-dllexport-def.patch"
    windows_def = "orc.def"
    exports = ["COPYING", patch, patch_def]
    exports_sources = windows_def
    generators = "gcc","visual_studio"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': False, 'fPIC': True }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        config_scheme(self)
    
    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        url_ = 'https://github.com/GStreamer/orc/archive/orc-{version}.tar.gz'.format(version=self.version)
        tools.get(url_)
        tools.patch(patch_file=self.patch)
        if self.settings.os == "Windows":
            tools.patch(patch_file=self.patch_def)
        extracted_dir = self.name + "-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == "Windows":
            shutil.copyfile(os.path.join(self.source_folder,self.windows_def), 
                            os.path.join(self.source_folder,self._source_subfolder,"orc",self.windows_def))

    def build(self):
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson = Meson(self)
        meson.configure(defs=defs, source_dir = self._source_subfolder,build_dir=self._build_subfolder)
        meson.build()
        self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

