CDF       
      altitude            Conventions       CF-1.0     comment      h==== Special Comments follow ====
Example of FFI 1010.
This example illustrating NASA Ames file format index 1010 combines the US Standard
Atmosphere 1976 (for the auxiliary variables Pressure and Air Concentration) and some
results of a 1-D model (for the dependent variables - oxygen compounds concentrations),
as quoted in G. Brasseur and S. Solomon, Aeronomy of the Middle Atmosphere,
Reidel, 1984 (pp. 46 & 211). The first date on line 7 (1st of January 1976) is fictitious
since the parameters are yearly averages. We have signalled the absence of calculated
value at 30 km by using the "missing value" flags (see line 12). The missing value flag
is also used to give account for the fact that there is virtually no O(1D) present below
the altitude of 20 km.
==== Special Comments end ====
==== Normal Comments follow ====
The files included in this data set illustrate each of the 9 NASA Ames file format indices
(FFI). A detailed description of the NASA Ames format can be found on the Web site of the
British Atmospheric Data Centre (BADC) at http://www.badc.rl.ac.uk/help/formats/NASA-Ames/
E-mail contact: badc@rl.ac.uk
Reference: S. E. Gaines and R. S. Hipskind, Format Specification for Data Exchange,
Version 1.3, 1998. The work referenced above can be found at
http://cloud1.arc.nasa.gov/solve/archiv/archive.tutorial.html and a copy of it at
http://www.badc.rl.ac.uk/help/formats/NASA-Ames/G-and-H-June-1998.html
Altitude (km) Pressure (mb)    [M] (cm-3)                 < 2 auxiliary dependent variables >
O2 (cm-3)     O3 (cm-3)  O(3P) (cm-3)  O(1D) (cm-3)   < 4 primary dependent variables >
==== Normal Comments end ====   title         NERC Data Grid (NDG) project   file_number_in_set              source        BISA 1-D atmospheric model     first_valid_date_of_data        �         total_files_in_set              no_of_nasa_ames_header_lines         -   file_format_index           �   institution       �De Rudder, Anne (ONAME from NASA Ames file); Rutherford Appleton Laboratory, Chilton OX11 0QX, UK - Tel.: +44 (0) 1235 445837 (ORG from NASA Ames file).   history       x2002-10-30 - NASA Ames File created/revised.

2021-05-10 15:13:41 - Converted to CDMS (NetCDF) format using nappy-0.3.0.         altitude                units         km     	long_name         Altitude   name      Altitude      �      molecular_oxygen_concentration                  title         Molecular oxygen concentration     	long_name         Molecular oxygen concentration     units         cm-3   missing_value         A�ׄ       nasa_ames_var_number                �  �   ozone_concentration                 title         Ozone concentration    	long_name         Ozone concentration    units         cm-3   missing_value         A�ׄ       nasa_ames_var_number               �  P   o_3p_concentration                  title         O(3P) concentration    	long_name         O(3P) concentration    units         cm-3   missing_value         A�ׄ       nasa_ames_var_number               �  �   o_1d_concentration                  title         O(1D) concentration    	long_name         O(1D) concentration    units         cm-3   missing_value         @È        nasa_ames_var_number               �  �   pressure                title         Pressure   nasa_ames_aux_var_number             	long_name         Pressure   units         hPa    missing_value         @È           �     air_concentration                   title         Air concentration      nasa_ames_aux_var_number            	long_name         Air concentration      units         cm-3   missing_value         A�ׄ          �  �@$      @.      @4      @9      @>      @A�     @D      @F�     @I      @K�     @N      @P@     @Q�     @R�     @T      @U@     @V�     @W�     @Y      C����6* C�{ej�" C���^ܐ C��y7�� D�x��@C_!�� CN2�x�@ C?����@ C1��  C"y_X�  CP�ܧ  CNI�  B�����  B���  B�v���  B��]��  B����  B�7R`  B{�3�  Bm��   Bpѿ�  B���@  B�Hv�   Bּ��  B}��   Bm��   BR�_    B7Hv�   B�e    A��e    A�ׄ    A��e    A��    A��v    A�ׄ    A�9�    Ah˨    A9�    @�d     @��     A,��    AY��    Bm��   A��8    A��    A�0�   A�6�   A�J�@   A�6�   A�_    A��e    A�O��   B
�`   B���   BQvY.   BS5b   BR�_    @È     @È     ?�������@      @È     @Y      @t�     @��     @�     @{�     @p@     @b�     @X      @P�     @Q�     @^      @z@     @~�     @��     @p�     @^Ffffff@K�fffff@9�     @(      @������@ffffff?�      ?陙����?ۅ�Q�?�(�\)?�(�\)?���vȴ9?��t�j~�?��+I�?rn��O�;?]}�H˒?H�W���?4����h�C��7Xw@C�{L.J C���2�y C��,S� C�B��� C�Q`��X Cm��}И CbK�З� CS��` CE#~Ti� C6�=��  C(L�C� CL�C� C³XB  B��k��  B����  BϽ�H  B����  B��^��  