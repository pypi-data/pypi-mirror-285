from setuptools import setup
import os
import re
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

# import os
# import distutils
# distutils.log.set_verbosity(1)

# from distutils.command.build_ext import build_ext
# compiler/linker args depending on the platform: check how to set it up
# compiler_args = ['-std=c++11', '-fopenmp', '-O3']
# compiler_args = ['/openmp', '/O2', '/arch:AVX512']
# compiler_args = ['-std=c++11', '-stdlib=libc++', '-mmacosx-version-min=10.7', '/openmp', '/Ox']

# From https://github.com/pybind/cmake_example/blob/master/setup.py
# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}

       
# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())

class CMakeBuild(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        print('CMakeBuild.build_extension')
        # Must be in this form due to bug in .resolve() only fixed in Python 3.10+
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.resolve()
        print(f'{ext_fullpath=} {extdir=}')

        # Using this requires trailing slash for auto-detection & inclusion of
        # auxiliary "native" libs

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"
        print(f'{cfg=}')

        # CMake lets you override the generator - we need to check this.
        # Can be set with Conda-Build, for example.
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        print(f'{cmake_generator=}')

        # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
        # EXAMPLE_VERSION_INFO shows you how to pass a value into the C++ code
        # from Python.
        cmake_args = [
            # f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
        ]
        build_args = []
        if os.environ.get('FFMPEG_ROOT', False):
            print(f"Adding FFMPEG_ROOT as {os.environ['FFMPEG_ROOT']}")
            cmake_args.append(f"-DFFMPEG_ROOT={os.environ['FFMPEG_ROOT']}")

        # Adding CMake arguments set as environment variable
        # (needed e.g. to build for ARM OSx on conda-forge)
        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        # In this example, we pass in the version to C++. You might not need to.
        # cmake_args += [f"-DEXAMPLE_VERSION_INFO={self.distribution.get_version()}"]

        if self.compiler.compiler_type != "msvc":
            # Using Ninja-build since it a) is available as a wheel and b)
            # multithreads automatically. MSVC would require all variables be
            # exported for Ninja to pick it up, which is a little tricky to do.
            # Users can override the generator with CMAKE_GENERATOR in CMake
            # 3.15+.
            if not cmake_generator or cmake_generator == "Ninja":
                try:
                    import ninja

                    ninja_executable_path = Path(ninja.BIN_DIR) / "ninja"
                    cmake_args += [
                        "-GNinja",
                        f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                    ]
                except ImportError:
                    pass

        else:
            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

            # Multi-config generators have a different way to specify configs
            if not single_config:
                cmake_args += [
                    f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
                ]
                build_args += ["--config", cfg]

        if sys.platform.startswith("darwin"):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += [f"-j{self.parallel}"]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)

        # Be sure to have openml on macos
        if sys.platform.startswith("darwin"):
            subprocess.run(["brew","install","libomp"])
        print(f"running cmake {build_temp=}")
        subprocess.run(
            ["cmake", ext.sourcedir, *cmake_args], cwd=build_temp, check=True
        )
        print("running cmake --build")
        subprocess.run(
            ["cmake", "--build", ".", "-v", *build_args], cwd=build_temp, check=True
        )
        print("running cmake --install")
        print(f"editable_mode={self.editable_mode}")
        install_dir = extdir # Path.cwd() if self.editable_mode else extdir
        print(f"{extdir=} {install_dir=} {build_temp=}")
        subprocess.run(
            ["cmake", "--install", ".", "--prefix", f"{install_dir}"], cwd=build_temp, check=True
        )
        print("done")


class build_ext_subclass( build_ext ):
    # win32, linux, darwin
    # msvc, unix
    copt =  {
        'win32' : ['/openmp',  '/O2', ],  # , '/fp:fast','/favor:INTEL64','/Og'],
        'linux' : ['-fopenmp', '-O3', '-std=c++17', ],
        'darwin': [            '-O3', '-std=c++17', ],
    }
    lopt =  {
        'darwin' : ['-L/usr/local/opt/libomp/lib'],
        'linux' : ['-fopenmp', ],
    }

    def build_extensions(self):
        # c = self.compiler.compiler_type
        # print(f"compiler_type {c}")
        import sys
        print(f" *** platform {sys.platform}")
        c = sys.platform
        if c in self.copt:
           for e in self.extensions:
               e.extra_compile_args = self.copt[ c ]
        if c in self.lopt:
            for e in self.extensions:
                e.extra_link_args = self.lopt[ c ]
        build_ext.build_extensions(self)

setup_args = dict(
    ext_modules = [
        # Pybind11Extension("qimview_cpp",
        #     ["qimview/cpp_bind/qimview_cpp.cpp"],
        #     depends = [ 
        #         'qimview/cpp_bind/image_histogram.hpp',
        #         'qimview/cpp_bind/image_resize.hpp',
        #         'qimview/cpp_bind/image_to_rgb.hpp',
        #         ],
        #     # Example: passing in the version to the compiled code
        #     # define_macros = [('VERSION_INFO', __version__)],
        #     include_dirs=['qimview/cpp_bind','/usr/local/opt/libomp/include'],
        #     ),
        CMakeExtension(name="qimview_cpp",     sourcedir="qimview/cpp_bind"),
        # CMakeExtension(name="decode_video_py", sourcedir="qimview/ffmpeg_cpp"),
    ],
    cmdclass = {'build_ext': CMakeBuild
                 # build_ext_subclass 
                 },
)

if os.environ.get('FFMPEG_ROOT', False):
    setup_args['ext_modules'].append(
        CMakeExtension(name="decode_video_py", sourcedir="qimview/ffmpeg_cpp"))


setup(**setup_args)
