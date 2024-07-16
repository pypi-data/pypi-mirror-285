v0.5.0 (2024-07-15)
===================




- L1 output files are now remapped, 3D IFU cubes with coordinates (LAT, LON, WAVE). The WCS information for the two spatial axes
  comes directly from the raw L0 frames and pre-computed IFU remapping files. (`#8 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/8>`__)


v0.1.0 (2024-06-06)
===================

- Initial release. Pipeline supports both BIFOS and MISI data and produces valid L1 frames. IFU-remapping is not yet implemented
  so the L1 files are presented as a single slit. WCS header values not guaranteed.
