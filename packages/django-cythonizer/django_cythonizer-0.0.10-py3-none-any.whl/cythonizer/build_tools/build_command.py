import os
import sys
import shutil
import time
import traceback
from setuptools import Command
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from Cython.Compiler.Errors import CompileError, PyrexError
from .config import BUILD_PATH
from .logging_setup import logger
from .file_operations import custom_copy, fix_cython_issues, delete_python_files, should_exclude
from .cython_compiler import capture_cython_errors, create_extension
from .spinner import Spinner

class BuildCommand(Command):
    description = 'Copy project to build folder and convert to Cython'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        unconvertible_files = []
        
        logger.info("Starting copy and build process for the entire project")
        
        spinner = Spinner("Initializing")
        spinner.start()

        spinner.update_message("Preparing build directory")
        time.sleep(1)
        if os.path.exists(BUILD_PATH):
            logger.info(f"Removing existing build directory: {BUILD_PATH}")
            shutil.rmtree(BUILD_PATH)
        
        spinner.update_message("Copying project files")
        time.sleep(1)
        logger.info(f"Copying project to {BUILD_PATH}")
        os.makedirs(BUILD_PATH, exist_ok=True)
        custom_copy('.', BUILD_PATH)
        
        spinner.update_message("Converting and compiling files")
        time.sleep(1)
        logger.info("Starting conversion and compilation of files")
        extensions = []
        conversion_count = 0
        for root, dirs, files in os.walk(BUILD_PATH):
            for file in files:
                if file.endswith('.py') and not should_exclude(os.path.join(root, file)):
                    py_file = os.path.join(root, file)
                    pyx_file = py_file.replace('.py', '.pyx')
                    try:
                        shutil.copy2(py_file, pyx_file)
                        fix_cython_issues(pyx_file)
                        module_name = os.path.relpath(pyx_file, BUILD_PATH).replace(os.path.sep, '.').replace('.pyx', '')
                        extension = create_extension(pyx_file, module_name)
                        
                        success, error_message = capture_cython_errors(extension)
                        if success:
                            extensions.append(extension)
                            conversion_count += 1
                            logger.info(f"Converted and compiled {py_file} to {pyx_file}")
                        else:
                            logger.error(f"Error compiling Cython file {pyx_file}:\n{error_message}")
                            os.remove(pyx_file)  # Remove the .pyx file
                            unconvertible_files.append(py_file)
                            logger.info(f"Keeping {py_file} as a Python file")
                    except Exception as e:
                        logger.error(f"Failed to process {py_file}: {str(e)}")
                        logger.error(traceback.format_exc())
                        unconvertible_files.append(py_file)
                        if os.path.exists(pyx_file):
                            os.remove(pyx_file)
        
        logger.info(f"Total files converted and compiled: {conversion_count}")
        logger.info(f"Total unconvertible files: {len(unconvertible_files)}")
        
        logger.info("Creating temporary distribution for building extensions")
        from distutils.dist import Distribution
        dist = Distribution({'ext_modules': extensions})
        
        logger.info("Building extensions")
        cmd = build_ext(dist)
        cmd.build_lib = BUILD_PATH
        cmd.ensure_finalized()
        
        logger.info("Running build_ext command")
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        try:
            cmd.run()
        except Exception as e:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            logger.error(f"Build extensions process failed: {str(e)}")
            logger.error(traceback.format_exc())
            spinner.stop()
            print("Build process failed during extension building. Check the log for details.")
            return
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        spinner.update_message("Cleaning up")
        time.sleep(1)
        logger.info("Deleting original Python files")
        delete_python_files(BUILD_PATH, unconvertible_files)
        print(BUILD_PATH)
        if BUILD_PATH != os.path.abspath('build'):
            print(build_path)
            os.system('rm -rf build')
        
        
        logger.info("Copy and build process completed successfully")
        spinner.stop()
        print("Build process completed successfully.")
        if unconvertible_files:
            print(f"Note: {len(unconvertible_files)} files could not be converted to Cython and remain as Python files.")
            logger.info("Unconvertible files:")
            for file in unconvertible_files:
                logger.info(file)