�HDF

         ���������F      0       �W
�OHDRH"            ������������������������
          �            <                  altitude�      1          molecular_oxygen_concentration�      &          ozone_concentration�;      %          o_3p_concentration�=      %          o_1d_concentration@                pressureeB      $          air_concentration�D       �                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ���4FRHP               ��������5      b       @              (                                                            (         $}BTHD       d(�              �i��BTHD 	      d(�              V*U�FSHD  �	                            P x (        �
      :       :       -0tHBTLF     @     (7 *   Q  
   l3�- �   N     I�7= �    �     tF �   @     0Ds X   6     �곁 �   7     Q�ń `    ?     H�7�     � 	   �/`� E   �     z}#�     J      l��ۯ$                                                                                                                                                                                                                                                                                                                           BTLF 	     J       `    ?      �    �      X   6      �   7      �   @         @      E   �      �   N          � 	    *   Q  
   ��Y�                                                                                                                                                                                                                                                                                                                                                                       OHDR                      ?      @ 4 4�     *         �    �      �            �!      }"      �"       �                                                                    +                                              #                                      +                                              D                                                                       ,                                                                               "                                     u	��FSSE b      �  {    e �&    �              �a�0FHDB �           �>��     comment    h     ==== Special Comments follow ====
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
==== Normal Comments end ====                                                                                                                                                                                                                                                                                                                                                                     FHDB �           ^&B%     no_of_nasa_ames_header_lines                        -        file_format_index                        �       institution    �      De Rudder, Anne (ONAME from NASA Ames file); Rutherford Appleton Laboratory, Chilton OX11 0QX, UK - Tel.: +44 (0) 1235 445837 (ORG from NASA Ames file).     source          BISA 1-D atmospheric model     title          NERC Data Grid (NDG) project     file_number_in_set                                total_files_in_set                                history    z      2002-10-30 - NASA Ames File created/revised.

2024-02-06 15:13:56 - Converted to Xarray (NetCDF) format using nappy-2.0.2.     first_valid_date_of_data                        �             _NCProperties    .      version=2,netcdf=4.9.3-development,hdf5=1.12.2                                                                                                                                     FHIB �                 ��������������������������������������������������������      ������������������������y�nz      $@      .@      4@      9@      >@     �A@      D@     �F@      I@     �K@      N@     @P@     �Q@     �R@      T@     @U@     �V@     �W@      Y@ *6����C "�je{�C ��^���C ��7yÁC@��x�D ��!_C @�x�2NC @����?C  ��1C  �X_y"C  ���PC  �INC  �����B  �ļ�B  聰v�B  ��]��B  �ļ�B  `R7�B  �3�{B   ��mB  ���pB  @«�B   �vH�B  �ļ�B   ��}B   ��mB    _�RB   �vH7B    e�B    e��A    ���A    e��A    ��A    v��A    �חA    �9�A    ��hA    ��9A     d�@     ��@    ��,A    ��YA   ��mB    8��A    ���A   �0��A   �6�A   @�J�A   �6�A    _��A    e��A   ��O�A   `�
B   ���B   .YvQB   b5SB    _�RB     ��@     ��@�������?      @     ��@      Y@     �t@     ��@     �@     �{@     @p@     �b@      X@     �P@     �Q@      ^@     @z@     �~@     ��@     �p@fffffF^@fffff�K@     �9@      (@������@ffffff@      �?�������?��Q���?)\���(�?)\���(�?9��v���?�~j�t��?�I+��?;�O��nr?��H�}]?���W�H?�h㈵�4?@wX7��C J.L{�C y�2���C �S,��C ���B�C X��`Q�C ��}�mC ����KbC `���SC �iT~#EC  ͦ=�6C �C��L(C �C��LC  BX��C  ��k��B  ��ۍ�B  Hʽ�B  ��B  ��^��B                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        OHDRT                      ?      @ 4 4�     *       �חA    #      �            ������������������������A         _Netcdf4Coordinates                            D        _FillValue  ?      @ 4 4�                    �חA        units          cm-3=    
    long_name          molecular_oxygen_concentration9        title          molecular_oxygen_concentrationB        nasa_ames_var_number                            L        DIMENSION_LIST                              �'         ����FRHP               ���������      �"                            	                                                      (  �7        �W#BTHD       d(#      	 	       r�!�BTHD 	      d(%      	 	       }�FSHD  �                             P x (        '                    T�bBTLF     ,     L�  �    D     �$ W    +     ��< �    #     _��� �    +     e>� @         i��    �     ��� ]   "     ���     A      c���$o\�                                                                                                                                                                                                                                                                                                                                                             BTLF 	     A       W    +      �    #      �    +      �    D         ,      @         ]   "         �     C��~                                                                                                                                                                                                                                                                                                                                                                                                 FSSE �"      � ;    ���                                                                                     GCOL                        �                    �                    �                    �                    �                    �              `                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      FHDB �!           y)�     _Netcdf4Coordinates                                 CLASS          DIMENSION_SCALE      NAME    	      altitude      _Netcdf4Dimid                      _FillValue  ?      @ 4 4�                      � 
    long_name          Altitude (km)     units          km     name          altitude  0   REFERENCE_LIST 6     dataset        dimension                         �              �;              �=              @              eB              �D                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   OHDR>                      ?      @ 4 4�     *       �חA    �      �            ������������������������A         _Netcdf4Coordinates                            D        _FillValue  ?      @ 4 4�                    �חA        units          cm-32    
    long_name          ozone_concentration.        title          ozone_concentrationB        nasa_ames_var_number                           L        DIMENSION_LIST                              �'         ���OHDR<                      ?      @ 4 4�     *       �חA    S      �            ������������������������A         _Netcdf4Coordinates                            D        _FillValue  ?      @ 4 4�                    �חA        units          cm-31    
    long_name          o_3p_concentration-        title          o_3p_concentrationB        nasa_ames_var_number                           L        DIMENSION_LIST                              �'         K��OHDR<                      ?      @ 4 4�     *        ��@    �      �            ������������������������A         _Netcdf4Coordinates                            D        _FillValue  ?      @ 4 4�                     ��@        units          cm-31    
    long_name          o_1d_concentration-        title          o_1d_concentrationB        nasa_ames_var_number                           L        DIMENSION_LIST                              �'         �9�&OHDR+                      ?      @ 4 4�     *        ��@    �      �            ������������������������A         _Netcdf4Coordinates                            D        _FillValue  ?      @ 4 4�                     ��@        units          hPa'    
    long_name          pressure#        title          pressureF        nasa_ames_aux_var_number                            L        DIMENSION_LIST                              �'         ��L�OHDR>                      ?      @ 4 4�     *       �חA          �            ������������������������A         _Netcdf4Coordinates                            D        _FillValue  ?      @ 4 4�                    �חA        units          cm-30    
    long_name          air_concentration,        title          air_concentrationF        nasa_ames_aux_var_number                           L        DIMENSION_LIST                              �'         [AY�