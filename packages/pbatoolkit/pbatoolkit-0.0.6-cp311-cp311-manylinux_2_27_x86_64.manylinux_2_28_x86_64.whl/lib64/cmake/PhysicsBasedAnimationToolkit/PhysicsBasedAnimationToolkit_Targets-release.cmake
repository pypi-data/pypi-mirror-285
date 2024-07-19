#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "PhysicsBasedAnimationToolkit::PhysicsBasedAnimationToolkit" for configuration "Release"
set_property(TARGET PhysicsBasedAnimationToolkit::PhysicsBasedAnimationToolkit APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(PhysicsBasedAnimationToolkit::PhysicsBasedAnimationToolkit PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/libPhysicsBasedAnimationToolkit.a"
  )

list(APPEND _cmake_import_check_targets PhysicsBasedAnimationToolkit::PhysicsBasedAnimationToolkit )
list(APPEND _cmake_import_check_files_for_PhysicsBasedAnimationToolkit::PhysicsBasedAnimationToolkit "${_IMPORT_PREFIX}/lib64/libPhysicsBasedAnimationToolkit.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
