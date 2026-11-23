import os
from os.path import join

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get


class LspFrameworkConanfile(ConanFile):
    name = "lsp-framework"
    description = "A type-safe C++ implementation of the Language Server Protocol"
    license = "MIT"
    homepage = "https://github.com/leon-bckl/lsp-framework"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        # The framework requires C++20 (concepts); do not inherit the devkit's
        # C++17 default for this package.
        self.settings.compiler.cppstd = "20"

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["LSP_INSTALL"] = True
        tc.variables["LSP_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "*.h", join(self.source_folder, "include"), join(self.package_folder, "include"))

        copy(self, "*.lib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.a",   self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so*", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", self.build_folder, join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", self.build_folder, join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        # Debug builds produce `lspd`; collect_libs finds whatever the build
        # actually installed instead of hard-coding the Release name.
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_target_name", "lsp::liblsp")
        self.cpp_info.set_property("cmake_file_name", "lsp")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Ws2_32"]
